import time
import logging
import asyncio

from redis import asyncio as aioredis
from app.configs.settings import settings

log = logging.getLogger(__name__)

redis_client: aioredis.Redis | None = None
_redis_lock = asyncio.Lock()

_last_ping = 0.0
_PING_EVERY = 15.0

async def connect_to_redis() -> aioredis.Redis:
    
    global redis_client

    async with _redis_lock:
        
        if redis_client is not None:
            return redis_client
        
        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URI,
                encoding='utf-8',
                decode_responses=True,
                socket_keepalive=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                max_connections=40,
                health_check_interval=30,
                retry_on_timeout=True,
            )

            await redis_client.ping()
            print("Connected to Redis")
            return redis_client
        except Exception as e:
            log.exception("Redis connection failed")
            redis_client = None
            raise

async def get_redis() -> aioredis.Redis:
    global redis_client, _last_ping

    if redis_client is None:
        return await connect_to_redis()

    # throttle ping to avoid connection/command storms
    now = time.monotonic()
    if now - _last_ping >= _PING_EVERY:
        _last_ping = now
        try:
            await redis_client.ping()
        except ConnectionError as e:
            # If maxclients reached, reconnecting usually makes it worse
            if "max number of clients reached" in str(e).lower():
                raise
            async with _redis_lock:
                # Close any existing pool before recreating it
                await close_redis_connection()
            return await connect_to_redis()

    return redis_client


async def close_redis_connection():
    global redis_client

    if redis_client is not None:
        try:
            await redis_client.aclose()
            await redis_client.connection_pool.disconnect()
            log.warning("Redis connection closed")
        finally:
            redis_client = None