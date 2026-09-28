import json
import logging
from shared.config import config
from shared.ollama_client import ollama

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """Ты — формализатор команд для системы синтеза речи.
Преобразуй текст пользователя в JSON.

Доступные команды:
- synthesize: озвучить текст
- ask: ответить на вопрос

Доступные голоса:
- ru_RU-irina-medium — женский (по умолчанию)
- ru_RU-dmitri-medium — мужской

Если голос не указан — используется ru_RU-irina-medium.

Примеры:
Вход: "озвучь текст привет мир"
Выход: {"command": "synthesize", "params": {"text": "привет мир"}}

Вход: "прочитай это вслух голосом дмитрия"
Выход: {"command": "synthesize", "params": {"text": "это", "voice": "ru_RU-dmitri-medium"}}

Вход: "озвучь голосом ирины: добрый вечер"
Выход: {"command": "synthesize", "params": {"text": "добрый вечер", "voice": "ru_RU-irina-medium"}}

Вход: "что такое луна"
Выход: {"command": "ask", "params": {"question": "что такое луна"}}

Вход: "расскажи про Пушкина голосом дмитрия"
Выход: {"command": "ask", "params": {"question": "расскажи про Пушкина", "voice": "ru_RU-dmitri-medium"}}

Отвечай ТОЛЬКО JSON, без пояснений."""


def lambda_handler(event, context):
    text = event.get("text", "").strip()
    if not text:
        raise ValueError("text is required")
    
    logger.info(f"Formalizing: {text[:100]}")
    
    try:
        raw = ollama.chat(
            model=config.OLLAMA_FORMALIZE_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            format="json",
            temperature=0.1,
        )
        parsed = json.loads(raw)
        logger.info(f"Formalized: {parsed}")
    except Exception as e:
        logger.warning(f"Formalization failed: {e}, using fallback")
        parsed = {"command": "synthesize", "params": {"text": text}}
    
    params = parsed.get("params", {})
    for key in ["voice", "speed", "volume", "pitch", "format"]:
        if key in event and key not in params:
            params[key] = event[key]
    
    return {
        "command": parsed.get("command", "synthesize"),
        "params": params,
        "request_id": event.get("request_id"),
        "input_type": event.get("input_type", "text"),
    }