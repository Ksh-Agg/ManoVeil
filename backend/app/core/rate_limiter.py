import time
from fastapi import Request, HTTPException, status
from app.db.redis import redis_pool


async def rate_limit(request: Request, limit: int = 60, window: int = 60):
    client_ip = request.client.host if request.client else "unknown"
    key = f"rate_limit:{client_ip}:{request.url.path}"
    try:
        current = await redis_pool.get(key)
        if current and int(current) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )
        pipe = redis_pool.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()
    except HTTPException:
        raise
    except Exception:
        pass  # Redis down — fail open
