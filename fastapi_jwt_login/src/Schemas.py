from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    user_email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    user_email: EmailStr

    class Config:
        orm_mode = True
