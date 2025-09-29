from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import asset as asset_repo
from app.schemas.asset import AssetNew
from app.core.database import get_db_session
router = APIRouter(tags=["Assets"])


@router.get("/assets/root")
async def get_asset_root():
    return{"we are alive": "assets"}

@router.post("/assets")
async def add_new_asset(new_asset: AssetNew, db_session: Annotated[AsyncSession,Depends(get_db_session)]):
    await asset_repo.add_new_asset(new_asset, db_session)