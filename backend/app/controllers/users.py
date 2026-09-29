from fastapi import APIRouter, Request, HTTPException, Query
from app.utils.security import decode_token

from app.models.users import Users
from app.models.connection import get_async_db
from sqlalchemy import select

router = APIRouter()

@router.get("/users")
async def get_users(request: Request, offset: int = Query(default=0, ge=0), limit: int = Query(default=10, ge=1, le=10)):

    access_token = request.headers.get("Authorization")

    if not access_token:
        raise HTTPException(401, "Unauthorized")

    payload = await decode_token(access_token)

    if payload.get("role") != "admin":
        raise HTTPException(403, "Forbidden")
    
    async with get_async_db() as db:
        result = await db.execute(select(Users).offset(offset).limit(limit))
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


    return {"users": users, "offset": offset, "limit": limit}
