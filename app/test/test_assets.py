import pytest
import pytest_asyncio


from app.core import security
from app.models.user import User
from app.schemas.asset import AssetNew, AssetVersionNew, AssetUpdate, AssetVersionUpdate, AssetSearch
from app.test.test_config import async_client, clean_db, get_test_session


ADMINUSER = {"username":"admin", "password":"admin", "roles": "admin", "id":1}
ARTUSER ={"username":"art", "password":"art", "roles": "artist", "id":2}


ASSET1 = {"name":"asset1", "description":"oh describe it","asset_type":"model", "id": 0, "versions":[]}
ASSET2 = {"name":"asset2", "description":"oh describe it2","asset_type":"texture", "id": 0, "versions":[]}

Ver1 = {"version_number": 1, "file_path": "/somewhere/imp", "status": "Published", "id":0, "asset_id": 0}
ver2 = {"version_number": 2, "file_path": "/somewhere/imp2", "status": "ReadyForReview", "id":0, "asset_id": 0}
ver3 = {"version_number": 3, "file_path": "/somewhere/imp3", "status": "Published", "id":0, "asset_id": 0}

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

    payload = AssetNew(name=ASSET2["name"], description=ASSET2["description"], asset_type=ASSET2["asset_type"]).model_dump()
    response = await async_client.post("/assets", headers=headers, json=payload)
    assert response.status_code == 200

    data = response.json()

    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["asset_type"] == payload["asset_type"]

    assert "id" in data
    ASSET2["id"] = data["id"]

@pytest.mark.asyncio
async def test_add_version(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = AssetVersionNew(version_number=Ver1["version_number"], file_path=Ver1["file_path"], status=Ver1["status"]).model_dump()
    response = await async_client.post(f"/assets/{ASSET1["id"]}", headers = headers, json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["asset_id"] == ASSET1["id"]
    Ver1["id"] = response_data['id']
    Ver1["asset_id"] = response_data['asset_id']
    ASSET1['versions'].append(response_data)

    payload = AssetVersionNew(version_number=ver2["version_number"], file_path=ver2["file_path"], status=ver2["status"]).model_dump()
    response = await async_client.post(f"/assets/{ASSET1["id"]}", headers = headers, json=payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["asset_id"] == ASSET1["id"]
    ver2["id"] = response_data['id']
    ver2["asset_id"] = response_data['asset_id']
    ASSET1['versions'].append(response_data)


@pytest.mark.asyncio
async def test_get_asset(async_client, admin_token):
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


@pytest.mark.asyncio
async def test_get_asset_version(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    reponse = await async_client.get(f"/assets/{ASSET1['id']}/{Ver1['id']}", headers=headers)
    assert reponse.status_code == 200
    response_data = reponse.json()
    assert response_data['asset_id'] == ASSET1["id"]
    assert response_data['id'] == Ver1["id"]

    reponse = await async_client.get(f"/assets/{100}/{Ver1['id']}", headers=headers)
    assert reponse.status_code == 404
    assert reponse.json() == {'detail': 'Asset Or Version Not Found!'}

    reponse = await async_client.get(f"/assets/{ASSET1['id']}/{500}", headers=headers)
    assert reponse.status_code == 404
    assert reponse.json() == {'detail': 'Asset Or Version Not Found!'}




@pytest.mark.asyncio
async def test_update_asset_version(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = AssetVersionUpdate(status="ReadyForReview").model_dump(exclude_unset=True)
    response = await async_client.put(f"/assets/{ASSET1['id']}/{Ver1['id']}", headers=headers, json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['status'] == "ReadyForReview"
    Ver1["status"] = "ReadyForReview"
    ASSET1["versions"][0] = Ver1

    response = await async_client.put(f"/assets/{ASSET1['id']}/{200}", headers=headers, json=payload)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Asset Not Found'}

    response = await async_client.put(f"/assets/{123}/{Ver1['id']}", headers=headers, json=payload)
    assert response.status_code == 404
    assert response.json() == {'detail': 'Asset Not Found'}

@pytest.mark.asyncio
async def test_search_asset(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = AssetSearch().model_dump()
    response = await async_client.get("/assets/", headers=headers)
    assert response.status_code == 200
    assert response.json() == [ASSET1, ASSET2]

@pytest.mark.asyncio
async def test_delete_version(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.delete(f"/assets/{ASSET1['id']}/{Ver1['id']}", headers=headers)
    assert response.status_code == 200

    response = await async_client.get(f"assets/{ASSET1['id']}/{Ver1['id']}", headers=headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_asset_version(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.delete(f"/assets/{ASSET1['id']}", headers=headers)
    assert response.status_code == 200

    response = await async_client.get(f"/assets/{ASSET1['id']}", headers=headers)
    assert response.status_code == 404

    response = await async_client.get(f"assets/{ASSET1}/{Ver1['id']}")
    assert response.status_code == 404