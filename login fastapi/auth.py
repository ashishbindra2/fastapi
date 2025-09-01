from typing import Optional, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
import logging

from User import User  # Assuming User is your custom class for user-related operations

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

app = FastAPI()

logger = logging.getLogger(__name__)

def fake_hash_password(password: str):
    # Use a secure hashing library like bcrypt in a real application
    # return "fakehashed" + password
    return password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserModel1(BaseModel):
    _id: str
    username: str = Field(..., description="The user name", min_length=3)
    email: Optional[str] = None
    password: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserModel(BaseModel):
    username: str = Field(..., description="The user name", min_length=3)
    email: Optional[str] = None
    password: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


# Dependency to inject the User instance into the route function
def get_user_instance():
    return User()


class UserInDB(UserModel1):
    password: str


def fake_decode_token(token):
    user = User().get_user_name(token)
    logger.debug("Decoded token: %s", user)

    if user:
        return UserInDB(**{k: str(v) for k, v in user.items()})
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    logger.debug("Current user: %s", user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: UserModel1 = Depends(get_current_user)):
    logger.debug("Current active user: %s", current_user)

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = User().get_user_name(form_data.username)
    logger.debug("User dict: %s", user_dict)

    if not user_dict or not fake_hash_password(form_data.password) == user_dict.get('password'):
        logger.warning("Incorrect username or password")
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user_dict.get('username'), "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user


@app.get("/user_details")
def api_get_all_users(
    user_instance: User = Depends(get_user_instance),
    current_user: UserModel = Depends(get_current_active_user)
):
    data = user_instance.get_users()

    # Check if data is not None and is a list
    if data is not None and isinstance(data, List):
        # Convert each user's data into a set of key-value pairs
        user_details_list = [{k: str(v) for k, v in user.items()} for user in data]
        return user_details_list
    else:
        raise HTTPException(status_code=404, detail="No user details found")
