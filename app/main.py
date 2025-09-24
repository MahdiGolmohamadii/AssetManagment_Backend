from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from app.routers import users, auth

from app.core import config


from typing import Annotated

from app.core import database
from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with database.db_engine.begin() as connection:
        await connection.run_sync(database.Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(auth.router)

@app.get("/root")
async def get_root():
    return {"we are alive!": "from Root"}

