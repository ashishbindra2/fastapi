import logging
import os
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from src.model import User
from src.database import get_db_session
from src.config import settings
from src.crud import get_user_by_email, create_user_db
from src.Schemas import UserResponse, UserCreate
from src.depedency import (
    verify_password,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_HOURS,
    REFRESH_TOKEN_EXPIRE_DAYS,
    get_current_user,
)

api_router = APIRouter(
    prefix="/api",
    tags=["Authentication"]  # optional global tag
)
logger = logging.getLogger(__name__)

@api_router.get("/", include_in_schema=False)
async def index():
    return {"Hi": "TODO SQL"}


@api_router.get("/health", include_in_schema=False)
async def health():
    return {"Health": "Good"}


@api_router.post("/login/", tags=["Authentication"])
async def login(
    user_email: str = Form(..., min_length=1, max_length=255),
    user_password: str = Form(..., min_length=1, max_length=255),
    db: Session = Depends(get_db_session),
):
    user = get_user_by_email(db, user_email)

    # ❌ Invalid credentials
    if not user or not verify_password(user_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # ✅ Valid credentials
    user_dict = {"sub": user_email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user_dict)

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return response


@api_router.get("/dashboard/", tags=["Authentication"])
async def dashboard(user: User = Depends(get_current_user)):
    return {
        "message": "Dashboard accessed successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.user_email
        }
    }


@api_router.post("/logout", tags=["Authentication"])
async def logout(request: Request):
    request.session.clear()
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("token")
    response.delete_cookie("refresh_token")
    return response
