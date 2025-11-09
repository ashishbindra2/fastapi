from pydantic import BaseModel,EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    class Config:
        orm_mode = True