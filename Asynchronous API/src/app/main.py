from fastapi import FastAPI

from app.api import notes, ping
from app.db import engine, database, metadata

metadata.create_all(engine)

app = FastAPI()

app.include_router(ping.router)

# @app.get("/ping")
# def pong():
#     return {"ping": "pong!"}

@app.get("/ping")
async def pong():
    # some async operation could happen here
    # example: `notes = await get_all_notes()`
    return {"ping": "pong!"}

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(ping.router)
app.include_router(notes.router, prefix="/notes", tags=["notes"])