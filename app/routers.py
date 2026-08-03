from fastapi import APIRouter
from app.controllers import health_check, auth, users, sse, ws

root_api_router = APIRouter()

root_api_router.include_router(health_check.router)
root_api_router.include_router(auth.router)
root_api_router.include_router(users.router)
root_api_router.include_router(sse.router)
root_api_router.include_router(ws.router)