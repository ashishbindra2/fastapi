import logging
from functools import wraps

from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from fastapi import Request, Depends, status, HTTPException
from fastapi.responses import RedirectResponse

from src.config import settings
from src.model import User
from src.database import Session, get_db_session
from src import RedirectException
logger = logging.getLogger(__name__)

ACCESS_TOKEN_EXPIRE_HOURS = 10
REFRESH_TOKEN_EXPIRE_DAYS = 1

# Define the hashing scheme
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Generate a hashed password"""
    return pwd_context.hash(password)  # Login Page with CSRF Token


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def set_flash(request: Request, message: str):
    request.session["message"] = message

def get_flash(request: Request):
    msg = request.session.pop("message", None)
    return msg

# -------- Token Creation --------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm
    )


def create_refresh_token(data: dict):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": data["sub"], "exp": expire}
    return jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), algorithm=settings.algorithm
    )



def get_current_user(request: Request, db: Session = Depends(get_db_session)) -> User:
    from src.crud import get_user_by_email

    token = request.cookies.get("token")
    if not token:
        set_flash(request, "Not authenticated")
        raise RedirectException("/login")

    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
        user_email = payload.get("sub")
        if not user_email:
            set_flash(request, "Invalid token")
            raise RedirectException("/login")

        user = get_user_by_email(db, user_email)
        if not user:
            set_flash(request, "User not found")
            raise RedirectException("/login")

        return user
    except JWTError:
        set_flash(request, "Invalid token")
        raise RedirectException("/login")



# ================= Decorator =================
def user_authenticated_decorator(func):
    """
    Decorator to ensure user is authenticated before accessing protected routes
    """

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        db = next(get_db_session())

        user = await get_current_user(request, db)

        if isinstance(user, RedirectResponse):
            return user  # Redirect if unauthenticated

        kwargs["user"] = user  # Inject authenticated user
        return await func(request, *args, **kwargs)

    return wrapper
