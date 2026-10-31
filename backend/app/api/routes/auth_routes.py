from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.auth_service import create_user, authenticate, issue_token, read_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterBody(BaseModel):
    name: str
    email: str
    password: str

class LoginBody(BaseModel):
    email: str
    password: str

def current_user(authorization: Optional[str] = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    user = read_token(authorization.split(" ", 1)[1].strip())
    if not user:
        raise HTTPException(status_code=401, detail="Your session expired. Please sign in again.")
    return user

@router.post("/register")
def register(body: RegisterBody):
    try:
        user = create_user(body.name, body.email, body.password)
        return {"access_token": issue_token(user), "token_type": "bearer", "user": user}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@router.post("/login")
def login(body: LoginBody):
    user = authenticate(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"access_token": issue_token(user), "token_type": "bearer", "user": user}

@router.get("/me")
def me(user=Depends(current_user)):
    return user
