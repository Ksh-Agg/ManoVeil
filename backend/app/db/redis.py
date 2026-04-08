import redis.asyncio as aioredis
from app.config import get_settings

settings = get_settings()

redis_pool = aioredis.from_url(
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    max_connections=20,
)


async def get_redis() -> aioredis.Redis:
    return redis_pool
