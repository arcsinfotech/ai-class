from fastapi import APIRouter
from app.schemas.auth import LoginRequest, RegisterRequest

router = APIRouter()

@router.post("/login")
def login(args: LoginRequest):
    return {"message": "Hello, World!"}

@router.post("/register")
def register(args: RegisterRequest):
    return {"message": "Hello, World!"}