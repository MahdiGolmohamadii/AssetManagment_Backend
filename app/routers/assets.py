from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import asset as asset_repo
from app.schemas.asset import AssetNew, AssetOut, AssetInDb, AssetUpdate
from app.schemas.asset import AssetVersionInDb, AssetVersionNew, AssetVersionOut, AssetVersionUpdate
from app.core.database import get_db_session


router = APIRouter(tags=["Assets"])


@router.post("/assets")
async def add_new_asset(new_asset: AssetNew, db_session: Annotated[AsyncSession,Depends(get_db_session)]):
    new_asset = await asset_repo.add_new_asset(new_asset, db_session)
    new_asset_in_db = AssetInDb.model_validate(new_asset)
    return AssetOut(**new_asset_in_db.model_dump())

@router.post("/assets/{asset_id}")
async def add_new_version(asset_id:int, new_version: AssetVersionNew, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        new_version = await asset_repo.add_new_version(new_version, asset_id, db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found!")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"There Was An Internal Error: {e}")
    
    new_version_in_db = AssetVersionInDb.model_validate(new_version)
    return AssetVersionOut(**new_version_in_db.model_dump())


@router.get("/assets/")
async def get_all_assets(db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    all_assets = await asset_repo.get_assets(db_session=db_session)
    return [AssetOut.model_validate(asset) for asset in all_assets]

@router.get("/assets/{asset_id}")
async def get_asset_by_id(db_session: Annotated[AsyncSession, Depends(get_db_session)], asset_id: int):
    try:    
        asset = await asset_repo.get_assets(asset_id=asset_id, db_session=db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    
    return AssetOut.model_validate(asset)


@router.put("/assets/{asset_id}")
async def update_asset(asset_id: int, asset_updat:AssetUpdate, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        updated_asset = await asset_repo.update_asset(asset_id, asset_updat, db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Somethin Went Wrong: {e}")
    
    if update_asset is None:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    
    return AssetOut.model_validate(updated_asset)

@router.delete("/assets/{asset_id}")
async def delete_asset(asset_id: int, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        deleted_asset = await asset_repo.delete_asset(asset_id, db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something Went Wrong: {e}")
    
    return AssetOut.model_validate(deleted_asset)

@router.get("/users/{asset_id}/{version_id}")
async def get_asset_version(asset_id: int, version_id: int, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        version_in_db = await asset_repo.get_asset_verison(asset_id, version_id, db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something Went Wrong: {e}")
    
    if version_in_db is None:
        raise HTTPException(status_code=404, detail="Asset Or Version Not Found!")
    return version_in_db

@router.put("/users/{asset_id}/{version_id}")
async def update_asset_version(asset_id: int, version_id: int, version_update: AssetVersionUpdate, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        updated_version = await asset_repo.update_asset_version(asset_id,version_id,version_update, db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something Went Wrong: {e}")
    if updated_version is None:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    
    return AssetVersionOut.model_validate(updated_version)

@router.delete("/users/{asset_id}/{version_id}")
async def delete_asset_version(asset_id: int, version_id: int, db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    try:
        deleted_version = await asset_repo.delete_asset_version(asset_id,version_id,db_session)
    except asset_repo.AssetNotFound:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Something Went Wrong")
    

    if deleted_version is None:
        raise HTTPException(status_code=404, detail="Asset Not Found")
    
    return AssetVersionOut.model_validate(deleted_version)