from fastapi import APIRouter
from app.controllers import health_check

root_api_router = APIRouter()

root_api_router.include_router(health_check.router)