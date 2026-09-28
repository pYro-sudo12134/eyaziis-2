import subprocess
import tempfile
from pathlib import Path
from app.config import settings

class PiperTTS:
    def __init__(self):
        self.voices_dir = settings.VOICES_DIR
        self.piper_bin = settings.PIPER_BIN
        self.ffmpeg_bin = settings.FFMPEG_BIN

    def _voice_path(self, voice: str) -> Path:
        path = self.voices_dir / f"{voice}.onnx"
        if not path.exists():
            raise FileNotFoundError(f"Voice not found: {voice}")
        return path

    def _apply_effects(
        self,
        input_path: str,
        output_path: str,
        volume: float,
        pitch: float,
    ) -> None:
        """Применяет громкость и pitch через ffmpeg."""
        filters = []
        
        if volume != 1.0:
            filters.append(f"volume={volume}")
        
        if pitch != 1.0:
            sample_rate = 22050
            new_rate = int(sample_rate * pitch)
            filters.append(f"asetrate={new_rate}")
            filters.append(f"atempo={1.0 / pitch}")
        
        if filters:
            filter_str = ",".join(filters)
            cmd = [
                self.ffmpeg_bin, "-y",
                "-i", input_path,
                "-filter:a", filter_str,
                output_path,
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg effects failed: {result.stderr.decode()}")
        else:
            Path(output_path).write_bytes(Path(input_path).read_bytes())

    def _convert_format(
        self,
        input_path: str,
        output_path: str,
        fmt: str,
    ) -> None:
        """Конвертирует WAV в нужный формат."""
        if fmt == "wav":
            Path(output_path).write_bytes(Path(input_path).read_bytes())
            return
        
        codec_map = {
            "mp3": ["-codec:a", "libmp3lame", "-b:a", "192k"],
            "ogg": ["-codec:a", "libvorbis", "-q:a", "5"],
        }
        
        cmd = [
            self.ffmpeg_bin, "-y",
            "-i", input_path,
            *codec_map[fmt],
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg convert failed: {result.stderr.decode()}")

    def synthesize(
        self,
        text: str,
        voice: str,
        speed: float,
        volume: float,
        pitch: float,
        fmt: str,
    ) -> bytes:
        voice_path = self._voice_path(voice)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_wav = f"{tmpdir}/raw.wav"
            effected_wav = f"{tmpdir}/effected.wav"
            final_file = f"{tmpdir}/final.{fmt}"
            
            cmd = [
                self.piper_bin,
                "--model", str(voice_path),
                "--output_file", raw_wav,
                "--length_scale", str(1.0 / speed),
            ]
            result = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Piper failed: {result.stderr.decode()}")
            
            self._apply_effects(raw_wav, effected_wav, volume, pitch)
            
            self._convert_format(effected_wav, final_file, fmt)
            
            return Path(final_file).read_bytes()

piper_tts = PiperTTS()