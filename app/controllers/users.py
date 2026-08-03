from fastapi import APIRouter, Request, HTTPException
from app.utils.security import decode_token

from app.models.users import Users
from app.models.connection import get_async_db
from sqlalchemy import select

router = APIRouter()

@router.get("/users")
async def get_users(request: Request):

    access_token = request.headers.get("Authorization")

    if not access_token:
        raise HTTPException(401, "Unauthorized")

    payload = await decode_token(access_token)

    if payload.get("role") != "admin":
        raise HTTPException(403, "Forbidden")
    
    async with get_async_db() as db:
        result = await db.execute(select(Users))
        users = result.scalars().all()

    formated_users = []    

    for user in users:
        formated_users.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        })


    return {"users": users}
