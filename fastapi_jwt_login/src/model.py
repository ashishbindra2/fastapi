from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    user_email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, email={self.user_email!r})"