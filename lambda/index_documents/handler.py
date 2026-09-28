import json
import logging
import uuid
from shared.config import config
from shared.ollama_client import ollama
from shared.qdrant_client import qdrant
from shared.aws_clients import get_s3_client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = get_s3_client()

CHUNK_SIZE = 500


def lambda_handler(event, context):
    """
    event: {"bucket": "rag-documents", "prefix": "optional/"}
    Вызывается вручную.
    """
    bucket = event.get("bucket", config.S3_RAG_DOCS)
    prefix = event.get("prefix", "")
    
    logger.info(f"Indexing: bucket={bucket}, prefix={prefix}")
    
    qdrant.ensure_collection(vector_size=768)
    
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objects = response.get("Contents", [])
    
    total_chunks = 0
    
    for obj in objects:
        key = obj["Key"]
        if not key.endswith((".txt", ".md")):
            continue
        
        logger.info(f"Processing: {key}")
        data = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
        chunks = split_into_chunks(data, CHUNK_SIZE)
        
        points = []
        for i, chunk in enumerate(chunks):
            vector = ollama.embed(chunk)
            points.append({
                "id": str(uuid.uuid4()),
                "vector": vector,
                "payload": {
                    "text": chunk,
                    "source": key,
                    "chunk_index": i,
                },
            })
        
        qdrant.upsert(points)
        total_chunks += len(points)
        logger.info(f"Indexed {len(points)} chunks from {key}")
    
    return {
        "status": "ok",
        "documents": len(objects),
        "chunks": total_chunks,
    }


def split_into_chunks(text: str, size: int) -> list[str]:
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    
    for p in paragraphs:
        if len(current) + len(p) + 2 <= size:
            current += p + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = p + "\n\n"
    
    if current:
        chunks.append(current.strip())
    
    return chunks