import base64
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.audio import webm_to_wav_base64


def _ok():
    return MagicMock(returncode=0, stdout=b"", stderr=b"")


def _fail(msg=b"bad"):
    return MagicMock(returncode=1, stdout=b"", stderr=msg)


def test_uses_expected_ffmpeg_flags():
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        Path(cmd[-1]).write_bytes(b"WAVDATA")
        return _ok()

    with patch("app.audio.subprocess.run", side_effect=fake_run):
        webm_to_wav_base64(b"\x00webm")

    cmd = captured["cmd"]
    assert cmd[cmd.index("-ar") + 1] == "16000"
    assert cmd[cmd.index("-ac") + 1] == "1"
    assert cmd[cmd.index("-c:a") + 1] == "pcm_s16le"


def test_returns_base64_of_output_not_input():
    def fake_run(cmd, **kwargs):
        Path(cmd[-1]).write_bytes(b"WAVDATA")
        return _ok()

    with patch("app.audio.subprocess.run", side_effect=fake_run):
        result = webm_to_wav_base64(b"\x00webm")

    assert base64.b64decode(result) == b"WAVDATA"


def test_ffmpeg_failure_raises():
    with patch("app.audio.subprocess.run", return_value=_fail(b"nope")):
        with pytest.raises(RuntimeError, match="ffmpeg conversion failed"):
            webm_to_wav_base64(b"\x00webm")