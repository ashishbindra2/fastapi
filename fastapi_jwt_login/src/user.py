import logging
import os
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
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


# point Jinja2Templates to src/templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

users_router = APIRouter()
logger = logging.getLogger(__name__)


@users_router.get("/", include_in_schema=False)
async def index():
    return {"Hi": "TODO SQL"}


@users_router.get("/health", include_in_schema=False)
async def health():
    return {"Heath": "Good"}


@users_router.get("/login/", response_class=HTMLResponse, tags=["Authentication"], include_in_schema=False)
async def login_page(
    request: Request,
    message: str | None = None,
    csrf_protect: CsrfProtect = Depends(),
):
    try:
        # Generate CSRF tokens (unsigned for form, signed for cookie)
        csrf_token, signed_token = csrf_protect.generate_csrf_tokens()

        # If no message is passed, try to fetch from session
        if not message:
            message = request.session.pop("message", None)
            if message:
                logger.info(f"Message retrieved from session: {message}")

        logger.info(f"Rendering login page with message: {message}")

        response = templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "message": message,
                "csrf_token": csrf_token,
            },
        )

        # Set the signed CSRF token as a cookie
        csrf_protect.set_csrf_cookie(signed_token, response)

        return response

    except Exception as e:
        logger.error(f"Error rendering login page: {e}")
        raise HTTPException(status_code=500, detail="Error rendering login page")


@users_router.post("/login/", response_class=HTMLResponse, tags=["Authentication"], include_in_schema=False)
async def submit(
    request: Request,
    user_email: str = Form(..., min_length=1, max_length=255),
    user_password: str = Form(..., min_length=1, max_length=255),
    db: Session = Depends(get_db_session),
):
    user = get_user_by_email(
        db, user_email
    )  # db.query(User).filter(User.user_email == user_email).first()

    # ❌ Invalid credentials → reload login page with error
    if not user or not verify_password(user_password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Invalid username or password"},
        )

    # ✅ Valid credentials → create tokens
    user_dict = {"sub": user_email}
    access_token = create_access_token(user_dict)
    refresh_token = create_refresh_token(user_dict)

    # Create redirect response and attach cookies to THAT response
    redirect_response = RedirectResponse(url="/dashboard", status_code=303)
    redirect_response.set_cookie(
        key="token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )
    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return redirect_response


@users_router.post("/refresh/", include_in_schema=False)
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")

    try:
        payload = jwt.decode(
            refresh_token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token({"sub": user_email})

        response.set_cookie(
            key="token",
            value=new_access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        )

        return {"message": "Token refreshed"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")


@users_router.post("/users/", response_model=UserResponse, include_in_schema=False)
def create_user(user: UserCreate, db: Session = Depends(get_db_session)):
    # check if email exists
    new_user = create_user_db(db, user)
    return new_user


@users_router.get("/dashboard/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request, user: User = Depends(get_current_user)):
    # if isinstance(user, RedirectResponse):
    #     return user  # send redirect immediately
    
    logger.info(f"Dashboard accessed by user: {user.user_email}")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user.username},
    )


@users_router.post("/logout", include_in_schema=False)
async def logout(request: Request):
    request.session.clear()  # Clear session
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("token")
    response.delete_cookie("refresh_token")
    return response
