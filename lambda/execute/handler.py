import json
import logging
from shared.config import config
from shared.ollama_client import ollama
from shared.qdrant_client import qdrant

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SYSTEM_PROMPT = """Ты — помощник по литературе. Отвечай кратко (1-10 предложений).
Верни ответ в формате JSON:
{"text": "твой ответ"}

Не указывай voice, speed, volume, pitch, format — они будут добавлены системой.

Отвечай ТОЛЬКО JSON."""


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
        hits = qdrant.search(query_vec, top_k=3)
        rag_context = "\n".join(h["payload"].get("text", "") for h in hits)
        logger.info(f"RAG: found {len(hits)} documents")
    except Exception as e:
        logger.warning(f"RAG failed: {e}, continuing without context")
    
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
            temperature=0.7,
        )
        parsed = json.loads(raw)
    except Exception as e:
        logger.warning(f"LLM failed: {e}, using fallback")
        parsed = {"text": question}
    
    return build_answer(parsed.get("text", ""), event, params, parsed)


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