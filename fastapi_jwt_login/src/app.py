from fastapi import FastAPI, Depends, HTTPException, Request, Form, Response
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from datetime import timedelta
from jose import jwt
from sqlalchemy.orm import Session

# Import your project modules
from src.crud import get_user_by_email
from src.depedency import verify_password
from src.database import get_db_session

app = FastAPI()

# JWT settings
SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class CsrfSettings(BaseModel):
    secret_key: str = "another-secret-key"


# Initialize CSRF protection
@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


from datetime import datetime, timedelta, timezone

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# ------------------------
# Login: JWT in HttpOnly cookie + CSRF token
# ------------------------
@app.post("/login")
async def login(
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    csrf_protect: CsrfProtect = Depends(),
    db: Session = Depends(get_db_session)
):
    # ✅ Fetch user from DB
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # ✅ Issue JWT
    access_token = create_access_token({"sub": user.user_email})

    # ✅ Set cookie (HttpOnly)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="strict",
        secure=False  # 👉 Set True in production (HTTPS)
    )

    # ✅ Correct CSRF generation
    csrf_token = csrf_protect.generate_csrf_tokens()

    return {"message": "Login successful", "csrf_token": csrf_token}



# ------------------------
# Protected Route (JWT + CSRF required)
# ------------------------
@app.post("/protected")
async def protected(request: Request, csrf_protect: CsrfProtect = Depends()):
    # Verify CSRF token from headers
    csrf_protect.validate_csrf(request.headers.get("X-CSRF-Token"))

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"message": "Access granted", "user": payload["sub"]}
from jose import jwt, JWTError

# ------------------------
# Dashboard (Protected)
# ------------------------
@app.get("/dashboard")
async def dashboard(
    request: Request,
    db: Session = Depends(get_db_session)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # ✅ Fetch user from DB
    user = get_user_by_email(db, user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ✅ Return full user info
    return {
        "id": user.id,
        "username": user.username,
        "email": user.user_email,
        "created_at": getattr(user, "created_at", None),
        "updated_at": getattr(user, "updated_at", None),
    }


# ------------------------
# Logout (Clear cookies)
# ------------------------
@app.post("/logout")
async def logout(response: Response, request: Request):
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("access_token")
    # If you add refresh tokens later, also clear here:
    # response.delete_cookie("refresh_token")
    return response