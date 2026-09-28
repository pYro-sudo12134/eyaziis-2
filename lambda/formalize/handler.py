import json
import logging

from shared.config import config
from shared.ollama_client import ollama

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """Ты — формализатор команд для системы синтеза речи.
Преобразуй текст пользователя в JSON.

Доступные команды:
- synthesize: озвучить текст БЕЗ ответа (когда просят "озвучь", "прочитай", "скажи")
- ask: ответить на вопрос (когда спрашивают "что", "как", "почему", "расскажи", "объясни")

Правило:
- Если в тексте есть вопрос, просьба рассказать/объяснить/описать → ask
- Если просто просят озвучить готовый текст → synthesize

Примеры:
Вход: "озвучь текст привет мир"
Выход: {"command": "synthesize", "params": {"text": "привет мир"}}

Вход: "прочитай это вслух"
Выход: {"command": "synthesize", "params": {"text": "это"}}

Вход: "что такое луна"
Выход: {"command": "ask", "params": {"question": "что такое луна"}}

Вход: "расскажи про Пушкина"
Выход: {"command": "ask", "params": {"question": "расскажи про Пушкина"}}

Вход: "объясни, почему небо голубое"
Выход: {"command": "ask", "params": {"question": "почему небо голубое"}}

Вход: "расскажи про сына Обломова"
Выход: {"command": "ask", "params": {"question": "расскажи про сына Обломова"}}

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
