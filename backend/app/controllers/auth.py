import httpx
import secrets

from fastapi import APIRouter, HTTPException, Request, Cookie
from fastapi.responses import RedirectResponse, JSONResponse
from app.schemas.auth import LoginRequest, RegisterRequest
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.users import Users
from app.models.connection import get_async_db
from sqlalchemy import select

from app.configs.settings import settings


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

    response = JSONResponse({
        "message": "Login successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXP * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        path="/",
        max_age=settings.REFRES_TOKEN_EXP * 60 * 60 * 24
    )

    return response

@router.get("/logout")
async def logout():

    response = JSONResponse({
        "message": "Logout successfully"
    })

    response.delete_cookie(
        key="access_token",
        path="/",
    )

    response.delete_cookie(
        key="refresh_token",
        path="/",
    )

    return response


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
async def refresh(
    refresh_token: str = Cookie(default=None)
):
    
    if not refresh_token:
        raise HTTPException(401, "Unauthorized")

    payload = await decode_token(refresh_token)

    if payload["type"] != "refresh":
        raise HTTPException(401, "Invalid token")
    
    email = payload["sub"]

    stored = refresh_tokens.get(email)

    if stored != refresh_token:
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

    response = JSONResponse({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    })

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        path="/",
        max_age=settings.ACCESS_TOKEN_EXP * 60
    )
        
    return response

@router.post("/verify")
async def verify(
    access_token: str = Cookie(default=None)
):
    
    if not access_token:
        raise HTTPException(401, "Unauthorized")

    payload = await decode_token(access_token)

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

@router.get("/auth/github")
async def github_auth():

    state = secrets.token_urlsafe(32)

    github_url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        "&scope=read:user user:email"
        f"&state={state}"
    )

    response = RedirectResponse(github_url)

    response.set_cookie(
        "oauth_state",
        state,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax"
    )

    return response

@router.get("/auth/github/callback")
async def github_callback(
    request: Request,
    code: str,
    state: str,
):
    
    saved_state = request.cookies.get("oauth_state")

    if not saved_state:
        raise HTTPException(400, "Missing Oauth state")
    
    if not secrets.compare_digest(saved_state, state):
        raise HTTPException(400, "Invalid Oauth state")
    
    async with httpx.AsyncClient() as client:
        token_response =  await client.post(
            "https://github.com/login/oauth/access_token",
            headers={
                "Accept": "application/json"
            },
            data={
                "client_id":settings.GITHUB_CLIENT_ID,
                "client_secret":settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri":settings.GITHUB_REDIRECT_URI
            },
        )

        if token_response.status_code != 200:
            raise HTTPException(400, "Failed to exchange GitHub authorization code")

        token_data = token_response.json()

        github_access_token = token_data.get("access_token")

        if not github_access_token:
            raise HTTPException(400, "Failed to exchange GitHub authorization code")
        
        github_user_response = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {github_access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            }
        )

        if github_user_response.status_code != 200:
            raise HTTPException(400, "Failed to fetch GitHub user information")
        
        github_user = github_user_response.json()

        github_username = github_user.get("name") or github_user.get("login")

        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {github_access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2026-03-10",
            },
        )

        if email_response.status_code != 200:
            raise HTTPException(400, "Failed to fetch GitHub user email")
        
        github_emails = email_response.json()

    github_email = None

    for email_data in github_emails:
        if email_data.get("primary") is True and email_data.get("verified") is True:
            github_email = email_data.get("email")
            break
    
    if not github_email:
        raise HTTPException(400, "Failed to fetch GitHub user email")
    

    async with get_async_db() as db:

        user = await get_user_by_email(db, github_email)

        if not user:

            random_password = secrets.token_urlsafe(12)

            hashed_password = await hash_password(random_password)

            user = Users(
                username = github_username,
                email = github_email,
                password = hashed_password,
                role = "user"
            )

            db.add(user)

            await db.commit()
            await db.refresh(user)
    
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

    response = RedirectResponse(
        url=f"{settings.FRONTEND_URL}"
    )

    response.delete_cookie("oauth_state")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXP * 60
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENV == "production",
        samesite="lax",
        max_age=settings.REFRES_TOKEN_EXP * 60 * 60 * 24
    )

    return response