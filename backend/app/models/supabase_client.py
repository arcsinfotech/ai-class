from supabase import create_async_client, AsyncClient
from app.configs.settings import settings
import logging

logger = logging.getLogger(__name__)

supabase: AsyncClient | None = None

async def init_supabase():
    global supabase

    supabase = await create_async_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_KEY
    )

async def check_supabase_connection() -> bool:
    try:
        if supabase is None:
            raise RuntimeError("Supabase client not initialized")
        
        await supabase.storage.list_buckets()
        logger.warning("Supabase connection ok")
        return True
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        return False

async def close_supabase_connection():
    global supabase
    if supabase:
        await supabase.close()
        supabase = None
        logger.warning("Supabase connection closed")