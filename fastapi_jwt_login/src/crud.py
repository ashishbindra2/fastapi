from sqlalchemy.orm import Session
from src.model import User
from src.depedency import get_password_hash
from fastapi import HTTPException
from sqlalchemy import select
 
def get_user_by_email(db: Session, user_email: str):
    stmt = select(User).where(User.user_email == user_email)
    return db.scalar(stmt)   # returns first matching row or None
def get_all_users(db: Session):
    stmt = select(User)
    return db.scalars(stmt).all()
def get_all_users_dict(db: Session):
    stmt = select(User)
    users = db.scalars(stmt).all()

    users_dict = {
        user.user_email: {
            "username": user.username,
            "user_email": user.user_email,
            "hashed_password": user.hashed_password,
        }
        for user in users
    }

    return users_dict

def create_user_db(db, user):
    existing = db.query(User).filter(User.user_email == user.user_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        user_email=user.user_email,
        hashed_password=get_password_hash(user.password),  # ⚠️ you should hash this before saving
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user