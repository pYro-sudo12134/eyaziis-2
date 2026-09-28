import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api_client import api_client
from app.audio import webm_to_wav_base64
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await api_client.aclose()


app = FastAPI(title="Speech Web Client", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))


# ===== Страницы =====


@app.get("/", response_class=HTMLResponse)
async def page_synthesize(request: Request):
    return templates.TemplateResponse("synthesize.html", {"request": request})


@app.get("/recognize", response_class=HTMLResponse)
async def page_recognize(request: Request):
    return templates.TemplateResponse("recognize.html", {"request": request})


# ===== Прокси к API Gateway =====


@app.post("/api/ask")
async def api_ask(body: dict):
    try:
        return await api_client.ask_text(body)
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(502, f"upstream unreachable: {e}")


@app.post("/api/ask-audio")
async def api_ask_audio(
    audio: UploadFile = File(...),
    voice: str = Form("ru_RU-irina-medium"),
    speed: float = Form(1.0),
    volume: float = Form(1.0),
    pitch: float = Form(1.0),
    format: str = Form("mp3"),
):
    webm_bytes = await audio.read()
    if not webm_bytes:
        raise HTTPException(400, "empty audio")

    try:
        audio_b64 = webm_to_wav_base64(webm_bytes)
    except RuntimeError as e:
        raise HTTPException(500, str(e))

    payload = {
        "audio": audio_b64,
        "voice": voice,
        "speed": speed,
        "volume": volume,
        "pitch": pitch,
        "format": format,
    }

    try:
        return await api_client.ask_audio(payload)
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(502, f"upstream unreachable: {e}")


@app.get("/api/result/{request_id}")
async def api_result(request_id: str):
    try:
        return await api_client.get_result(request_id)
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(502, f"upstream unreachable: {e}")


@app.get("/api/voices")
async def api_voices():
    try:
        return await api_client.get_voices()
    except httpx.HTTPStatusError as e:
        raise HTTPException(e.response.status_code, e.response.text)
    except httpx.RequestError as e:
        raise HTTPException(502, f"upstream unreachable: {e}")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
