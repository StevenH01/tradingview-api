# app/utils/cache.py

import json
import os
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "30"))

redis_client = redis.from_url(REDIS_URL)

def _make_cache_key(symbol: str, interval: str) -> str:
    return f"price:{symbol}:{interval}"

async def get_cached_data(symbol: str, interval: str):
    key = _make_cache_key(symbol, interval)
    cached = await redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

async def set_cached_data(symbol: str, interval: str, data: dict):
    key = _make_cache_key(symbol, interval)
    await redis_client.set(key, json.dumps(data), ex=CACHE_TTL_SECONDS)
