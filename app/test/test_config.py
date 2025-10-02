import pytest
import pytest_asyncio
import json

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User
from app.schemas.user import UserUpdate
from app.core.database import Base
from app.core.security import get_db_session
from app.core import security
from app.repositories import user as user_repo




DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)

@pytest_asyncio.fixture
async def clean_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


AsyncTestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)



@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client



async def get_test_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncTestSessionLocal()
    try:
        yield db
    finally:
        await db.close()

app.dependency_overrides[get_db_session] = get_test_session