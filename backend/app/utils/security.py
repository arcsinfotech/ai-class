import jwt
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from app.configs.settings import settings

from pwdlib import PasswordHash

ph = PasswordHash.recommended()

ACCESS_TOKEN_EXP = settings.ACCESS_TOKEN_EXP
REFRES_TOKEN_EXP = settings.REFRES_TOKEN_EXP

SECRET_KEY = settings.SECRET_KEY
ALGO = settings.ALGO

async def hash_password(password: str):
    return ph.hash(password)

async def verify_password(password: str, hashed: str):
    return ph.verify(password, hashed)

async def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXP
    )
    payload["type"] = "access"

    return jwt.encode(payload, SECRET_KEY, ALGO)

async def create_refresh_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(
        days=REFRES_TOKEN_EXP
    )
    payload["type"] = "refresh"

    return jwt.encode(payload, SECRET_KEY, ALGO)

async def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, ALGO)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token Expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid Token")