from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.asset import Asset, AssetVersion
from app.schemas.asset import AssetNew, AssetVersionNew, AssetUpdate, AssetVersionUpdate, AssetSearch, AssetVersionSearch



class AssetNotFound(Exception):
    pass

async def add_new_asset(new_asset: AssetNew, db_session: AsyncSession) -> Asset:
    
    new_asset = Asset(**new_asset.model_dump())
    try:
        db_session.add(new_asset)
        await db_session.commit()
        await db_session.refresh(new_asset, attribute_names=["versions"])
        return new_asset        
    except Exception as e:
        await db_session.rollback()
        raise e
    


async def get_assets(db_session: AsyncSession, asset_id: int | None = None) -> Asset:
    if not asset_id:
        all_assets = await db_session.execute(select(Asset).options(selectinload(Asset.versions)))
        return all_assets.scalars().all()
        
    else:
        try:
            asset = await db_session.execute(select(Asset).options(selectinload(Asset.versions)).where(Asset.id == asset_id))
            return asset.scalar_one_or_none()
        except IntegrityError:
            raise AssetNotFound
        
async def update_asset(asset_id: int, asset_update: AssetUpdate, db_session: AsyncSession) -> Asset:
    asset_to_update = await db_session.execute(select(Asset).options(selectinload(Asset.versions)).where(Asset.id == asset_id))
    asset_to_update = asset_to_update.scalar_one_or_none()
    if asset_to_update is None:
        raise AssetNotFound
    
    updated_data_dict = asset_update.model_dump(exclude_unset=True)
    for key, val in updated_data_dict.items():
        setattr(asset_to_update, key, val)
    
    try:
        db_session.add(asset_to_update)
        await db_session.commit()
        await db_session.refresh(asset_to_update)
        return asset_to_update
    except Exception as e:
        await db_session.rollback()
        raise e
    
   
async def delete_asset(asset_id: int , db_session: AsyncSession) -> Asset:
    result = await db_session.execute(select(Asset).options(selectinload(Asset.versions)).where(Asset.id==asset_id))
    asset_in_db = result.scalar_one_or_none()
    if asset_in_db is None:
        raise AssetNotFound
    
    await db_session.delete(asset_in_db)
    await db_session.commit()

    return asset_in_db


async def search_assets(asset_search: AssetSearch, db_session: AsyncSession) list[Asset]:
    query = select(Asset).options(selectinload(Asset.versions))

    if asset_search.id:
        query = query.where(Asset.id == asset_search.id)
    if asset_search.asset_type:
        query = query.where(Asset.asset_type == asset_search.asset_type)
    if asset_search.name:
        query = query.where(Asset.name == asset_search.name)
    
    query.limit(asset_search.limit).offset(asset_search.offset)
    users = await db_session.execute(query)
    result = users.scalars().all()
    return result

async def add_new_version(new_version: AssetVersionNew, asset_id: int, db_session: AsyncSession) -> AssetVersion:

    # asset_in_db = await db_session.execute(select(Asset).where(Asset.id == asset_id))
    # if not asset_in_db:
    #     raise AssetNotFound

    new_version = AssetVersion(asset_id = asset_id,  **new_version.model_dump())

    try:
        db_session.add(new_version)
        await db_session.commit()
        await db_session.refresh(new_version)
        return new_version
    except IntegrityError:
        await db_session.rollback()
        raise AssetNotFound
    except Exception as e:
        await db_session.rollback()
        raise e

async def get_asset_verison(asset_id: int, version_id: int, db_session: AsyncSession) -> AssetVersion:
    try:
        result = await db_session.execute(select(AssetVersion).where(AssetVersion.asset_id == asset_id).where(AssetVersion.id == version_id))
        version_in_db = result.scalar_one_or_none()
        return version_in_db
    except IntegrityError:
        raise AssetNotFound
    except Exception as e:
        await db_session.rollback()
        raise e

async def update_asset_version(asset_id: int, version_id: int, version_update: AssetVersionUpdate, db_session: AsyncSession) -> AssetVersion:
    version_in_db = await get_asset_verison(asset_id,version_id, db_session)

    if version_in_db is None:
        raise AssetNotFound
    
    updated_version_dict = version_update.model_dump(exclude_unset=True)
    for key, val in updated_version_dict.items():
        setattr(version_in_db, key, val)

    try:
        db_session.add(version_in_db)
        await db_session.commit()
        await db_session.refresh(version_in_db)
        return version_in_db
    except IntegrityError:
        raise AssetNotFound
    except Exception as e:
        await db_session.rollback()
        raise e
    
async def delete_asset_version(asset_id: int, version_id: int, db_sesssion: AsyncSession) -> AssetVersion:
    version_in_db = await get_asset_verison(asset_id, version_id, db_sesssion)
    if version_in_db is None:
        raise AssetNotFound
    
    try:
        await db_sesssion.delete(version_in_db)
        await db_sesssion.commit()
        return version_in_db
    except IntegrityError:
        raise AssetNotFound
    except Exception as e:
        await db_sesssion.rollback()
        raise e
    

async def search_assets_version(asset_id:int, version_search: AssetVersionSearch, db_session: AsyncSession) -> list[AssetVersion]:
    query = select(AssetVersion).where(AssetVersion.asset_id == asset_id)

    if version_search.id:
        query = query.where(AssetVersion.id == version_search.id)
    if version_search.version_number:
        query = query.where(AssetVersion.version_number == version_search.version_number)
    if version_search.status:
        query = query.where(AssetVersion.status == version_search.status)
    
    query.limit(version_search.limit).offset(version_search.offset)
    users = await db_session.execute(query)
    result = users.scalars().all()
    return result