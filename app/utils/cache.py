import hashlib
import json
import os
from typing import Optional

# Local JSON fallback (kept for offline/dev)
CACHE_FILE = "cache.json"

# Redis (Upstash) configuration
REDIS_URL = os.getenv("REDIS_URL")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))  # 0 = no expiry

_redis_client = None
_redis_error: Optional[Exception] = None


def _get_redis():
    """
    Lazy-initialize Redis only when a URL is provided.
    Falls back to local file cache if Redis can't be created.
    """
    global _redis_client, _redis_error

    if REDIS_URL is None:
        return None

    if _redis_client or _redis_error:
        return _redis_client

    try:
        import redis  # Imported lazily so local dev works without redis installed

        _redis_client = redis.from_url(
            REDIS_URL,
            decode_responses=True,  # Return strings instead of bytes
        )
    except Exception as exc:  # Broad except to ensure fallback is available
        _redis_error = exc
        print(f"[cache] Redis disabled, falling back to file cache: {exc}")
        _redis_client = None

    return _redis_client


def get_cache_key(query: str) -> str:
    return hashlib.md5(query.encode()).hexdigest()


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE) as f:
        return json.load(f)


def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def get_cached_answer(query: str) -> Optional[str]:
    key = get_cache_key(query)

    # Try Redis first
    redis_client = _get_redis()
    if redis_client:
        cached = redis_client.get(key)
        if cached is not None:
            return cached

    # Fallback: local file cache
    cache = load_cache()
    return cache.get(key)


def store_cached_answer(query: str, answer: str) -> None:
    key = get_cache_key(query)

    # Try Redis first
    redis_client = _get_redis()
    if redis_client:
        if CACHE_TTL_SECONDS > 0:
            redis_client.setex(key, CACHE_TTL_SECONDS, answer)
        else:
            redis_client.set(key, answer)
        return

    # Fallback: local file cache
    cache = load_cache()
    cache[key] = answer
    save_cache(cache)
