import pytest
import pytest_asyncio

from app.schemas.user import UserUpdate
from app.models.user import User
from app.core import security

from app.test.test_config import async_client, get_test_session, clean_db


ADMINUSER = {"username":"admin", "password":"admin", "roles": "admin", "id":1}
VALIDUSER ={"username":"validuser", "password":"validuser", "roles": "guest", "id":2}
INVALIDUSER = {"username":"notvalid", "password":"notvalid", "id": 100}


@pytest_asyncio.fixture
async def user_token(async_client):
    data = {"username": VALIDUSER["username"], "password": VALIDUSER["password"]}
    response = await async_client.post("/token", data=data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def admin_token(async_client):
    data = {"username": ADMINUSER["username"], "password": ADMINUSER["password"]}
    response = await async_client.post("/token", data=data)
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest_asyncio.fixture
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


@pytest.mark.asyncio
async def test_users_me(async_client, clean_db, create_admin, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/user/me", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"username": ADMINUSER["username"], "roles": ADMINUSER["roles"], "id": ADMINUSER["id"]}


@pytest.mark.asyncio
async def test_create_new_account(async_client):
    payload = {"username": VALIDUSER["username"], "password": VALIDUSER["password"]}
    response = await async_client.post("/signup", json=payload)
    assert response.status_code == 200

    assert response.json() == {"username": VALIDUSER["username"], "roles": VALIDUSER["roles"], "id":VALIDUSER["id"]}

@pytest.mark.asyncio
async def test_get_user(async_client, admin_token, user_token):
    # admin
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"users/{VALIDUSER["id"]}", headers = headers)
    assert response.status_code == 200
    assert response.json() == {"username": VALIDUSER["username"], "roles": VALIDUSER["roles"], "id":VALIDUSER["id"]}
    response = await async_client.get(f"/users/{INVALIDUSER["id"]}", headers=headers)
    assert response.status_code == 404

    # check roles access
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"users/{ADMINUSER['id']}", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "User Not Authorized To Access"}

@pytest.mark.asyncio
async def test_update_user(async_client, admin_token, user_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    data = UserUpdate(roles="artist").model_dump(exclude_unset=True)
    response = await async_client.put(f"/users/{VALIDUSER['id']}", json=data, headers=headers)
    assert response.status_code == 200
    VALIDUSER["roles"] = "artist"
    assert response.json() == {"username": VALIDUSER["username"], "roles": VALIDUSER["roles"], "id":VALIDUSER["id"]}

    # Check VALIDUSER new access
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.get(f"users/{VALIDUSER['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"username": VALIDUSER["username"], "roles": VALIDUSER["roles"], "id":VALIDUSER["id"]}

@pytest.mark.asyncio
async def test_delete_user(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.delete(f"users/{VALIDUSER['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"deleted id:": VALIDUSER["id"]}

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"users/{VALIDUSER["id"]}", headers = headers)
    assert response.status_code == 404
    assert response.json() == {"detail":"user not found"}