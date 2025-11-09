from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine 
from sqlalchemy.ext.declarative import declarative_base

engine  = create_engine("sqlite:///.user.db")

sessioMakerLocal = sessionmaker(bind=engine)
Base = declarative_base()