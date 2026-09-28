import json
import logging
import re
from shared.config import config
from shared.ollama_client import ollama
from shared.qdrant_client import qdrant

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """Ты — помощник по литературе. Отвечай кратко (1-3 предложения).
Верни ответ СТРОГО в формате JSON:
{"text": "твой ответ"}

ВАЖНО:
- Только JSON, без пояснений
- Не используй кавычки внутри text
- Экранируй специальные символы

Не указывай voice, speed, volume, pitch, format."""


def lambda_handler(event, context):
    command = event.get("command", "synthesize")
    params = event.get("params", {})
    
    if command == "synthesize":
        return build_answer(params.get("text", ""), event, params)
    
    question = params.get("question", params.get("text", ""))
    if not question:
        raise ValueError("question is required")
    
    logger.info(f"Answering: {question[:100]}")
    
    rag_context = ""
    try:
        query_vec = ollama.embed(question)
        hits = qdrant.search(query_vec, top_k=2)
        rag_context = "\n".join(
            h["payload"].get("text", "")[:300]
            for h in hits
        )
        logger.info(f"RAG: found {len(hits)} documents")
    except Exception as e:
        logger.warning(f"RAG failed: {e}")
    
    user_prompt = question
    if rag_context:
        user_prompt = f"Контекст:\n{rag_context}\n\nВопрос: {question}"
    
    try:
        raw = ollama.chat(
            model=config.OLLAMA_EXECUTE_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
            temperature=0.3,
        )
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON invalid: {e}")
        text = extract_text(raw) if 'raw' in locals() else question
        parsed = {"text": text}
    except Exception as e:
        logger.warning(f"LLM failed: {e}")
        parsed = {"text": question}

    logger.info(f"RAG context (first 500 chars): {rag_context[:500]}")
    logger.info(f"User prompt (first 500 chars): {user_prompt[:500]}")
    
    return build_answer(parsed.get("text", ""), event, params, parsed)


def extract_text(raw):
    match = re.search(r'"text"\s*:\s*"([^"]+)"', raw)
    if match:
        return match.group(1)
    return raw.strip()


def build_answer(text, event, params, parsed=None):
    parsed = parsed or {}
    
    def pick(key, default):
        return parsed.get(key) or params.get(key) or event.get(key) or default
    
    return {
        "text": text,
        "voice": pick("voice", "ru_RU-irina-medium"),
        "speed": pick("speed", 1.0),
        "volume": pick("volume", 1.0),
        "pitch": pick("pitch", 1.0),
        "format": pick("format", "mp3"),
        "request_id": event.get("request_id"),
    }