import base64
import logging
import subprocess
import tempfile
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def webm_to_wav_base64(webm_bytes: bytes) -> str:
    """Конвертирует webm/opus (из MediaRecorder) в WAV 16kHz mono и кодирует в base64."""
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "input.webm"
        dst = Path(tmp) / "output.wav"
        src.write_bytes(webm_bytes)

        cmd = [
            settings.FFMPEG_BIN, "-y",
            "-i", str(src),
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(dst),
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            logger.error("ffmpeg failed: %s", result.stderr.decode(errors="ignore"))
            raise RuntimeError("ffmpeg conversion failed")

        wav_bytes = dst.read_bytes()

    logger.info("Converted webm→wav: %d → %d bytes", len(webm_bytes), len(wav_bytes))
    return base64.b64encode(wav_bytes).decode("ascii")