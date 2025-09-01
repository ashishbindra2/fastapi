# src/routers/auth.py
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.crud import get_user_by_email
from src.depedency import (
    verify_password,
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_HOURS,
    REFRESH_TOKEN_EXPIRE_DAYS,
    get_current_user,
)
from src.database import get_db_session
from src.model import User

api_router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme for Bearer tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ------------------------------
# Common Login Handler
# ------------------------------
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# ------------------------------
# Cookie-based login (browser)
# ------------------------------
@api_router.post("/login", tags=["Authentication"])
async def login_with_cookies(
    user_email: str = Form(...),
    user_password: str = Form(...),
    db: Session = Depends(get_db_session),
):
    user = authenticate_user(db, user_email, user_password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_dict = {"sub": user.user_email}
    access_token = create_access_token(user_dict, expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS))
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


# ------------------------------
# Bearer-token login (API/mobile)
# ------------------------------
@api_router.post("/token", tags=["Authentication"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db_session),
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.user_email}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ------------------------------
# Protected routes
# ------------------------------
@api_router.get("/me", tags=["Authentication"])
async def read_users_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.user_email,
    }


@api_router.get("/dashboard", tags=["Authentication"])
async def dashboard(user: User = Depends(get_current_user)):
    return {"message": "Dashboard accessed successfully", "user": user.username}


@api_router.post("/logout", tags=["Authentication"])
async def logout(request: Request):
    request.session.clear()
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("token")
    response.delete_cookie("refresh_token")
    return response
