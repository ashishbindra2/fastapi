from core.database import sessioMakerLocal
def get_db():
    db = sessioMakerLocal()
    try:
        yield db
    finally:
        db.close()