from fastapi import APIRouter, Request, HTTPException
from app.controllers.auth import users
from app.utils.security import decode_token

router = APIRouter()

@router.get("/users")
async def get_users(request: Request):

    access_token = request.headers.get("Authorization")

    if not access_token:
        raise HTTPException(401, "Unauthorized")

    payload = await decode_token(access_token)

    if payload.get("role") != "admin":
        raise HTTPException(403, "Forbidden")

    return {"users": users}



