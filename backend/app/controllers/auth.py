from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest, VerifyRequest
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.users import Users
from app.models.connection import get_async_db
from sqlalchemy import select


router = APIRouter()

refresh_tokens = {}

async def get_user_by_email(db, email:str):
    result = await db.execute(select(Users).where(Users.email == email))
    return result.scalar_one_or_none()

@router.post("/login")
async def login(args: LoginRequest):

    async with get_async_db() as db:
        user = await get_user_by_email(db, args.email)

    if not user:
        raise HTTPException(401, "Invalid username or password")
    
    if not await verify_password(args.password, user.password):
        raise HTTPException(401, "Invalid username or password")

    access_token = await create_access_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    refresh_token = await create_refresh_token(
        {
            "sub": user.email,
            "role": user.role
        }
    )

    refresh_tokens[user.email] = refresh_token

    return {
        "message": "Login successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }


@router.post("/register")
async def register(args: RegisterRequest):

    async with get_async_db() as db:
        user = await get_user_by_email(db, args.email)

        if user:
            raise HTTPException(400, "User already exists")

        hashed_pass = await hash_password(args.password)

        user = Users(
            username = args.username,
            email = args.email,
            password = hashed_pass,
            role = args.role
        )
        db.add(user)
        await db.commit()

    return {"message": "User created successfully"}

@router.post("/refresh")
async def refresh(args: RefreshRequest):

    payload = await decode_token(args.refresh_token)

    if payload["type"] != "refresh":
        raise HTTPException(401, "Invalid token")
    
    email = payload["sub"]

    stored = refresh_tokens.get(email)

    if stored != args.refresh_token:
        raise HTTPException(401, "Session is revoked")
    
    async with get_async_db() as db:
        user = await get_user_by_email(db, email)
        if not user:
            raise HTTPException(401, "Invalid token")
    
    access_token = await create_access_token(
        {
            "sub": email,
            "role": user.role
        }
    )
        
    return {
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }    
    }

@router.post("/verify")
async def verify(args: VerifyRequest):

    payload = await decode_token(args.access_token)

    if payload["type"] != "access":
        raise HTTPException(401, "Invalid token")
    
    email = payload["sub"]

    async with get_async_db() as db:
        user = await get_user_by_email(db, email)
        if not user:
            raise HTTPException(401, "Invalid token")
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }