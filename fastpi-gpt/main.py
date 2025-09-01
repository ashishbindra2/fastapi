from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from authlib.integrations.starlette_client import OAuth
import bcrypt
import uvicorn

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# In-Memory User Database
fake_users_db = {
    "user1": {
        "username": "user1",
        "full_name": "User One",
        "email": "user1@example.com",
        "hashed_password": get_password_hash("password123"),
        "disabled": False,
    }
}

# Generate JWT Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify Token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return fake_users_db.get(username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# FastAPI App
app = FastAPI()

# OAuth2 (Google Authentication)
oauth = OAuth()
oauth.register(
    name="google",
    client_id="your_google_client_id",
    client_secret="your_google_client_secret",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    refresh_token_url=None,
    redirect_uri="http://localhost:8000/auth/callback",
    client_kwargs={"scope": "openid email profile"},
)

# Login Route (JWT Token)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token({"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# Google OAuth Login
@app.get("/login/google")
async def login_google(request: Request):
    return await oauth.google.authorize_redirect(request, "http://localhost:8000/auth/callback")

@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    return {"email": user["email"], "name": user["name"]}

# Session-Based Login (Cookie Authentication)
@app.post("/login")
async def session_login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    response.set_cookie(key="session", value=username, httponly=True)
    return {"message": "Logged in successfully"}

@app.get("/logout")
async def logout(response: Response):
    response.delete_cookie("session")
    return {"message": "Logged out successfully"}

@app.get("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {"message": f"Welcome {user['username']}!"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
