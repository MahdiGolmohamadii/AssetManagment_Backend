from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models.asset import Asset, AssetVersion
from app.schemas.asset import AssetNew, AssetVersionNew, AssetUpdate



class AssetNotFound(Exception):
    pass

async def add_new_asset(new_asset: AssetNew, db_session: AsyncSession):
    
    new_asset = Asset(**new_asset.model_dump())
    try:
        db_session.add(new_asset)
        await db_session.commit()
        await db_session.refresh(new_asset, attribute_names=["versions"])
        return new_asset
    except IntegrityError:
        await db_session.rollback()
        # raise UsernameAlreadyExists
    except Exception:
        await db_session.rollback()
    
    return None

async def add_new_version(new_version: AssetVersionNew, asset_id: int, db_session: AsyncSession):
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


async def get_assets(db_session: AsyncSession, asset_id: int | None = None):
    if not asset_id:
        all_assets = await db_session.execute(select(Asset).options(selectinload(Asset.versions)))
        return all_assets.scalars().all()
        
    else:
        try:
            asset = await db_session.execute(select(Asset).options(selectinload(Asset.versions)).where(Asset.id == asset_id))
            return asset.scalar_one_or_none()
        except IntegrityError:
            raise AssetNotFound
        
async def update_asset(asset_id: int, asset_update: AssetUpdate, db_session: AsyncSession):
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
    
   
async def delete_asset(asset_id: int , db_session: AsyncSession):
    result = await db_session.execute(select(Asset).options(selectinload(Asset.versions)).where(Asset.id==asset_id))
    asset_in_db = result.scalar_one_or_none()
    if asset_in_db is None:
        raise AssetNotFound
    
    await db_session.delete(asset_in_db)
    await db_session.commit()

    return asset_in_db

async def get_asset_verison(asset_id: int, version_id: int, db_session: AsyncSession):
    result = await db_session.execute(select(AssetVersion).where(AssetVersion.asset_id == asset_id).where(AssetVersion.id == version_id))
    version_in_db = result.scalar_one_or_none()
    return version_in_db