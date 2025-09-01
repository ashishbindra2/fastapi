from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Union
from User import User
from typing import List

app = FastAPI()

user_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "password": "somepassword",
        "disabled": False,
    }
}


class UserModel(BaseModel):
    username: str = Field(..., description="The user name", min_length=3)
    email: Union[str, None] = None
    password: str
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


# Dependency to inject the User instance into the route function
def get_user_instance():
    return User()

@app.post("/add_user")
async def api_add_user(user_detail: UserModel, user_instance: User = Depends(get_user_instance)):
    try:
        response = user_instance.add_user(dict(user_detail))
        return response
    except Exception as e:
        print(e)
        # Adjust the exception type based on what your add_user method might raise
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user")
def api_get_user(username: str = None, user_instance: User = Depends(get_user_instance)):
    if not username:
        raise HTTPException(status_code=422, detail="Username cannot be empty")

    data = user_instance.get_user_name(username)

    if data is not None:  # Check if data is not None before iterating
        temp = {}
        for k, v in data.items():
            temp[k] = str(v)
        return temp
    else:
        raise HTTPException(status_code=404, detail="User not found")



@app.get("/user_details")
def api_get_all_users(user_instance: User = Depends(get_user_instance)):
    data = user_instance.get_users()

    # Check if data is not None and is a list
    if data is not None and isinstance(data, List):
        # Convert each user's data into a set of key-value pairs
        user_details_list = [{k: str(v) for k, v in user.items()} for user in data]
        return user_details_list
    else:
        raise HTTPException(status_code=404, detail="No user details found")
