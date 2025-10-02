import pytest
import pytest_asyncio


from app.core import security
from app.models.user import User
from app.schemas.asset import AssetNew, AssetVersionNew, AssetUpdate
from app.test.test_config import async_client, clean_db, get_test_session


ADMINUSER = {"username":"admin", "password":"admin", "roles": "admin", "id":1}
ARTUSER ={"username":"art", "password":"art", "roles": "artist", "id":2}


ASSET1 = {"name":"asset1", "description":"oh describe it","asset_type":"model", "id": 0, "versions":[]}
Ver1 = {"version_number": 1, "file_path": "/somewhere/imp", "status": "Published","id":0,  "asset_id": 0}
ver2 = {"version_number": 2, "file_path": "/somewhere/imp2", "status": "ReadyForReview","id":0,  "asset_id": 0}
ver3 = {"version_number": 3, "file_path": "/somewhere/imp3", "status": "Published","id":0,  "asset_id": 0}

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
async def test_add_new_asset(async_client, create_admin, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = AssetNew(name=ASSET1["name"], description=ASSET1["description"], asset_type=ASSET1["asset_type"]).model_dump()
    response = await async_client.post("/assets", headers=headers, json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["asset_type"] == payload["asset_type"]

    assert "id" in data
    ASSET1["id"] = data["id"]

@pytest.mark.asyncio
async def test_add_version(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = AssetVersionNew(version_number=Ver1["version_number"], file_path=Ver1["file_path"], status=Ver1["status"]).model_dump()
    response = await async_client.post(f"/assets/{ASSET1["id"]}", headers = headers, json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["asset_id"] == ASSET1["id"]
    ASSET1['versions'].append(response_data)

    #TODO the following is fucked I have no idea why!
    # payload = AssetVersionNew(version_number=Ver1["version_number"], file_path=Ver1["file_path"], status=Ver1["status"]).model_dump()
    # response = await async_client.post(f"/assets/{100}", headers = headers, json=payload)
    # print(response.json())

@pytest.mark.asyncio
async def test_get_assete(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get(f"/assets/{ASSET1['id']}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == ASSET1["name"]
    assert data["description"] == ASSET1["description"]

    response = await async_client.get(f"/assets/{100}", headers=headers)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Asset Not Found'}

@pytest.mark.asyncio
async def test_update_asset(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = AssetUpdate(description="oh changes!").model_dump(exclude_unset=True)
    response = await async_client.put(f"/assets/{ASSET1['id']}", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == ASSET1["name"]
    assert data["versions"] == ASSET1["versions"]
    assert data["description"] == "oh changes!"
    ASSET1["description"] = "oh changes!"

    payload = AssetUpdate(description="oh changes!").model_dump(exclude_unset=True)
    response = await async_client.put(f"/assets/{100}", headers=headers, json=payload)
    assert response.status_code == 404

