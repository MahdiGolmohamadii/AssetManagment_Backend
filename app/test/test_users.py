import pytest
import pytest_asyncio
import json

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User
from app.core.database import Base
from app.core.security import get_db_session
from app.core import security
from app.repositories import user as user_repo


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)

VALIDUSER ={"username":"validuser", "password":"validuser", "roles": "guest"}
INVALIDUSER = {"username":"notvalid", "password":"notvalid"}
ADMINUSER = {"username":"admin", "password":"admin", "roles": "admin"}
AsyncTestSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_test_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncTestSessionLocal()
    try:
        yield db
    finally:
        await db.close()

@pytest_asyncio.fixture()
async def create_admin():
    async for session in get_test_session():
        hashed_pass = security.hash_plain_password(ADMINUSER["password"])
        admin = User(
            username=ADMINUSER["username"],
            password=hashed_pass,
            roles=ADMINUSER["roles"],
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin

@pytest_asyncio.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def user_token(async_client):
    data = {"username": VALIDUSER["username"], "password": VALIDUSER["password"]}
    response = await async_client.post("/token", data=data)
    assert response.status_code == 200
    return response.json()["access_token"]

app.dependency_overrides[get_db_session] = get_test_session

async def get_test_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    db = AsyncTestSessionLocal()
    try:
        yield db
    finally:
        await db.close()

@pytest_asyncio.fixture()
async def admin_token(async_client):
    data = {"username": ADMINUSER["username"], "password": ADMINUSER["password"]}
    response = await async_client.post("/token", data=data)
    assert response.status_code == 200
    return response.json()["access_token"]



@pytest.mark.asyncio
async def test_create_new_account(async_client):
    payload = {"username": VALIDUSER["username"], "password": VALIDUSER["password"]}
    response = await async_client.post("/signup", json=payload)
    assert response.status_code == 200
    assert response.json() == {"username": VALIDUSER["username"], "roles": VALIDUSER["roles"]}

@pytest.mark.asyncio
async def test_users_me(async_client, create_admin, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/user/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"username": ADMINUSER["username"], "roles": ADMINUSER["roles"]}