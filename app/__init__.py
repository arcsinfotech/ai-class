import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.configs import settings
from app.routers import root_api_router
from app.models.connection import check_database_connection, cleanup_connections
from app.models.redis import connect_to_redis, close_redis_connection

from app.exception.http import GlobalExceptionMiddleware

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Define FastAPI lifespan events (startup and shutdown).
    Handles database connection pool and other cleanup tasks.
    """
    # Startup
    log.info("Execute FastAPI startup event handler.")

    await check_database_connection()
    await connect_to_redis()

    yield

    await cleanup_connections()
    await close_redis_connection()

    # ---- SHUTDOWN START ----
        
    # Shutdown
    log.warning("Execute FastAPI shutdown event handler.")

    
def get_application() -> FastAPI:
    """
    Initialize FastAPI application.
    """
    log.debug("Initialize FastAPI application node.")
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        servers=[{'url': f'http://127.0.0.1:{settings.PORT}'}],
        docs_url=settings.DOCS_URL if settings.ENV == "development" else None,
        redoc_url=settings.REDOC_URL if settings.ENV == "development" else None,
        openapi_url=settings.OPENAPI_URL if settings.ENV == "development" else None,
        lifespan=lifespan
    )

    app.add_middleware(GlobalExceptionMiddleware)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    log.debug("Add application routes.")
    app.include_router(root_api_router)
    
    app.add_middleware( CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"]
    )
    
    return app

__all__ = ("get_application",)