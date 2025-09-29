import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.asset import Asset, AssetVersion
from app.core.database import get_db_session
from app.schemas.asset import AssetNew, AssetVersionNew



async def add_new_asset(new_asset: AssetNew, db_session: AsyncSession):
    
    new_asset = Asset(name = new_asset.name)
    try:
        db_session.add(new_asset)
        await db_session.commit()
        await db_session.refresh(new_asset)
    except IntegrityError:
        await db_session.rollback()
        # raise UsernameAlreadyExists
    except Exception:
        await db_session.rollback()

    default_version = AssetVersion(version_number=0.1, file_path=f"/assets/{new_asset.id}/v0.1", parent_asset=new_asset)
    try:
        db_session.add(default_version)
        await db_session.commit()
        await db_session.refresh(default_version)
    except IntegrityError:
        await db_session.rollback()
        # raise UsernameAlreadyExists
    except Exception:
        await db_session.rollback()

async def add_new_version(new_version: AssetVersionNew, asset_id: int, db_session: AsyncSession):
    new_version = AssetVersion(asset_id = asset_id,  **new_version.model_dump())

    try:
        db_session.add(new_version)
        await db_session.commit()
        await db_session.refresh(new_version)
    except IntegrityError:
        await db_session.rollback()
    except Exception:
        await db_session.rollback()
  

