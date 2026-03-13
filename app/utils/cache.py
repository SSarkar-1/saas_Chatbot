import hashlib
import json
import os

CACHE_FILE = "cache.json"


def get_cache_key(query):

    return hashlib.md5(query.encode()).hexdigest()


def load_cache():

    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE) as f:
        return json.load(f)


def save_cache(cache):

    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


def get_cached_answer(query):

    cache = load_cache()

    key = get_cache_key(query)

    return cache.get(key)


def store_cached_answer(query, answer):

    cache = load_cache()

    key = get_cache_key(query)

    cache[key] = answer

    save_cache(cache)