from unittest.mock import patch


def test_cache_hit_skips_synthesis(app_client):
    """Главная логика кэша: на HIT синтез не вызывается."""
    with patch("app.main.piper_tts.synthesize", return_value=b"A") as synth:
        app_client.post("/synthesize", json={"text": "привет"})
        app_client.post("/synthesize", json={"text": "привет"})
        assert synth.call_count == 1


def test_cache_miss_on_different_params(app_client):
    """Разные speed → разные ключи → второй синтез."""
    with patch("app.main.piper_tts.synthesize", return_value=b"A") as synth:
        app_client.post("/synthesize", json={"text": "x", "speed": 1.0})
        app_client.post("/synthesize", json={"text": "x", "speed": 1.5})
        assert synth.call_count == 2


def test_voice_not_found_maps_to_400(app_client):
    with patch(
        "app.main.piper_tts.synthesize",
        side_effect=FileNotFoundError("Voice not found: nope"),
    ):
        r = app_client.post("/synthesize", json={"text": "x", "voice": "nope"})
    assert r.status_code == 400


def test_piper_error_maps_to_500(app_client):
    with patch(
        "app.main.piper_tts.synthesize",
        side_effect=RuntimeError("Piper failed: segfault"),
    ):
        r = app_client.post("/synthesize", json={"text": "x"})
    assert r.status_code == 500


def test_rate_limit_blocks_synthesize(app_client):
    from app.config import settings

    with patch("app.main.piper_tts.synthesize", return_value=b"A"):
        for i in range(settings.RATE_LIMIT_REQUESTS):
            app_client.post("/synthesize", json={"text": f"t{i}"})
        r = app_client.post("/synthesize", json={"text": "over"})
    assert r.status_code == 429
