
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

DB_URL = get_settings().db_url

Base = declarative_base()

db_engine = create_async_engine(DB_URL, echo = False)

async_session_local = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db_session():
    
    db = async_session_local()
    try:
        yield db
    finally:
        await db.close()

