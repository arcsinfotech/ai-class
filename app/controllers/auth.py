from fastapi import APIRouter, HTTPException
from app.schemas.auth import LoginRequest, RegisterRequest, RefreshRequest
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

router = APIRouter()

users ={
    "john@example.com": {
        "username": "john",
        "email": "john@example.com",
        "password": "password",
        "role": "user"
    }
}

refresh_tokens = {}

@router.post("/login")
async def login(args: LoginRequest):

    user = users.get(args.email)

    if not user:
        raise HTTPException(401, "Invalid username or password")
    
    if not await verify_password(args.password, user['password']):
        raise HTTPException(401, "Invalid username or password")

    access_token = await create_access_token(
        {
            "sub": user["email"],
            "role": user["role"]
        }
    )

    refresh_token = await create_refresh_token(
        {
            "sub": user["email"],
            "role": user["role"]
        }
    )

    refresh_tokens[user["email"]] = refresh_token

    return {
        "message": "Login successfully",
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/register")
async def register(args: RegisterRequest):

    if args.email in users:
        raise HTTPException(400, "User already exists")

    hashed_pass = await hash_password(args.password)
        
    users[args.email] = {
        "username": args.username,
        "email": args.email,
        "password": hashed_pass,
        "role": args.role
    }

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
    
    access_token = await create_access_token(
        {
            "sub": email,
            "role": users[email]["role"]
        }
    )
        
    return {"access_token": access_token}