from core.database import Base, engine
from sqlalchemy import Integer, String,Column

class UserDB(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    

Base.metadata.create_all(bind=engine)