"""
Semantic cache backed by Redis (cloud) with an in-memory FAISS index for fast ANN.
Embeddings live in Redis so the cache survives process restarts, while FAISS is
rebuilt from Redis on import.
"""

import hashlib
import os
from typing import List, Optional

import faiss
import numpy as np
import redis
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
EMB_DIM = 384
SIM_THRESHOLD = 0.90
REDIS_URL = os.getenv("REDIS_URL")
SEM_CACHE_TTL_SECONDS = int(os.getenv("SEM_CACHE_TTL_SECONDS", "86400"))
NAMESPACE = "semcache"

model = SentenceTransformer(MODEL_NAME)
index = faiss.IndexFlatL2(EMB_DIM)

redis_client: Optional[redis.Redis] = None
keys: List[str] = []

if REDIS_URL:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    except Exception as exc:
        print(f"[semantic-cache] Redis unavailable, semantic cache disabled: {exc}")
        redis_client = None
else:
    print("[semantic-cache] REDIS_URL not set, semantic cache disabled.")


def _load_index_from_redis():
    """Rebuild FAISS index from vectors persisted in Redis."""
    if not redis_client:
        return

    # Ensure clean state in case of hot reload
    index.reset()
    keys.clear()

    try:
        for key in redis_client.scan_iter(f"{NAMESPACE}:*"):
            payload = redis_client.hgetall(key)
            emb_hex = payload.get("emb")
            if not emb_hex:
                continue
            emb = np.frombuffer(bytes.fromhex(emb_hex), dtype="float32").reshape(1, -1)
            index.add(emb)
            keys.append(key)
    except Exception as exc:
        print(f"[semantic-cache] Failed to warm index: {exc}")


def _encode(query: str) -> np.ndarray:
    emb = model.encode([query])
    return np.array(emb).astype("float32")


def semantic_cache_lookup(query: str) -> Optional[str]:
    """
    Return a semantically similar cached answer if cosine similarity exceeds threshold.
    """
    if not redis_client or len(keys) == 0:
        return None

    emb = _encode(query)
    D, I = index.search(emb, k=1)
    similarity = 1 - D[0][0]  # FAISS IndexFlatL2 returns squared L2 distance

    if similarity < SIM_THRESHOLD:
        return None

    key = keys[I[0][0]]
    answer = redis_client.hget(key, "answer")
    return answer


def store_semantic_cache(query: str, answer: str) -> None:
    """
    Persist embedding + answer in Redis and add embedding to FAISS for fast hits.
    """
    if not redis_client:
        return

    emb = _encode(query)
    key = f"{NAMESPACE}:{hashlib.md5(query.encode()).hexdigest()}"

    # Avoid duplicating embeddings for the same query
    if key in keys:
        return

    if redis_client.exists(key):
        # Redis already has the item (another worker wrote it); hydrate FAISS once
        index.add(emb)
        keys.append(key)
        return

    index.add(emb)
    redis_client.hset(
        key,
        mapping={
            "query": query,
            "answer": answer,
            "emb": emb.tobytes().hex(),
        },
    )
    if SEM_CACHE_TTL_SECONDS > 0:
        redis_client.expire(key, SEM_CACHE_TTL_SECONDS)

    keys.append(key)


# Warm the FAISS index once on import so workers share the same Redis-backed cache.
_load_index_from_redis()
