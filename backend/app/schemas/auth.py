from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str
    role: str

class RefreshRequest(BaseModel):
    refresh_token: str

class VerifyRequest(BaseModel):
    access_token: str