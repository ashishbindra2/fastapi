from fastapi import FastAPI, Depends, Request, HTTPException
import uvicorn
from sqlalchemy.orm import Session
from core.dendency import get_db
from model.UserDB import UserDB
from schema.UserModel import User

app = FastAPI(title="RESTAPITEST", description="for intervire")


@app.get("/test")
def hello():
    return {"msg": "Tesing fine"}


@app.get("/check")
def check(request: Request, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).all()

    if not db_user:
        raise HTTPException(404, "User not found")

    return {"user_datail": db_user}


@app.post("/add_user")
async def add_user(user: User, db: Session = Depends(get_db)):
    user_exist = db.query(UserDB).filter(UserDB.email == user.email).first()
    if user_exist:
        raise HTTPException(400, "User laready available")

    new_user = UserDB(name=user.name, email=user.email)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "usercreated", "user": new_user}


@app.put("/user/{id}")
async def update_user(id:int ,user: User, db: Session = Depends(get_db)):
    exist = db.query(UserDB).filter(UserDB.id == id).first()
    if not exist:
        raise HTTPException(400, "user not found")
    exist.id = id
    exist.name = user.name
    exist.email = user.email
    db.commit()
    return {"message": "User updated"}


@app.delete("/user/{user_email}")
async def update_user(user_email: str, db: Session = Depends(get_db)):
    exist = db.query(UserDB).filter(UserDB.email == user_email).first()
    if not exist:
        raise HTTPException(400, "user not found")
    db.delete(exist)
    db.commit()
    return {"message": "User deleted"}


@app.get("/user/{id}")
def get_user(id:int, db:Session= Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.id==id).first()
    if not db_user:
        return {"msg":"No user found"}
    return db_user
if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="127.0.0.1", port=8084)
