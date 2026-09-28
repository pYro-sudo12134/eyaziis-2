import pytest
from app.cache import TTSCache


@pytest.fixture
def cache():
    c = TTSCache()
    c._client = None
    return c


@pytest.mark.parametrize(
    "field, new_value",
    [
        ("text", "другой"),
        ("voice", "voice-b"),
        ("speed", 1.5),
        ("volume", 0.5),
        ("pitch", 1.2),
        ("fmt", "wav"),
    ],
)
def test_key_changes_with_any_parameter(cache, field, new_value):
    """Если параметр забыли включить в payload — тест падает."""
    base = {"text": "привет", "voice": "voice-a", "speed": 1.0, "volume": 1.0, "pitch": 1.0, "fmt": "mp3"}
    assert cache._key(**base) != cache._key(**{**base, field: new_value})
