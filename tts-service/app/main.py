from fastapi import FastAPI, HTTPException, Response, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.models import SynthesizeRequest, VoicesResponse, VoiceInfo
from app.tts import piper_tts
from app.cache import cache
from app.rate_limit import rate_limiter
from app.config import settings
from app.voices import VOICES_METADATA, SUPPORTED_FORMATS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="TTS Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MEDIA_TYPES = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
}


@app.get("/health")
async def health():
    try:
        await cache.client.ping()
        redis_ok = True
    except Exception:
        redis_ok = False

    return {
        "status": "ok" if redis_ok else "degraded",
        "redis": redis_ok,
    }


@app.get("/voices", response_model=VoicesResponse)
async def list_voices():
    voices = [
        VoiceInfo(id=voice_id, **meta)
        for voice_id, meta in VOICES_METADATA.items()
        if (settings.VOICES_DIR / f"{voice_id}.onnx").exists()
    ]
    return VoicesResponse(
        voices=voices,
        default=settings.DEFAULT_VOICE,
        formats=SUPPORTED_FORMATS,
    )


@app.post("/synthesize")
async def synthesize(request: Request, body: SynthesizeRequest):
    await rate_limiter.check(request)

    cached = await cache.get(
        body.text,
        body.voice,
        body.speed,
        body.volume,
        body.pitch,
        body.format,
    )
    if cached:
        logger.info(f"Cache hit: voice={body.voice}, len={len(cached)}")
        return Response(
            content=cached,
            media_type=MEDIA_TYPES[body.format],
            headers={
                "Content-Disposition": f"attachment; filename=output.{body.format}",
                "X-Cache": "HIT",
            },
        )

    logger.info(
        f"Synthesize: voice={body.voice}, speed={body.speed}, "
        f"volume={body.volume}, pitch={body.pitch}, format={body.format}"
    )

    try:
        audio_bytes = piper_tts.synthesize(
            text=body.text,
            voice=body.voice,
            speed=body.speed,
            volume=body.volume,
            pitch=body.pitch,
            fmt=body.format,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    await cache.set(
        body.text,
        body.voice,
        body.speed,
        body.volume,
        body.pitch,
        body.format,
        audio_bytes,
    )

    return Response(
        content=audio_bytes,
        media_type=MEDIA_TYPES[body.format],
        headers={
            "Content-Disposition": f"attachment; filename=output.{body.format}",
            "X-Cache": "MISS",
        },
    )
