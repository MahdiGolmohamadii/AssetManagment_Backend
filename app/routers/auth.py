from datetime import timedelta
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.database import get_db_session
from app.core.config import Settings, get_settings
from app.core import security
from app.schemas.token import Token


router = APIRouter(tags=["authentication"])

@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                    db_session: Annotated[AsyncSession, Depends(get_db_session)],
                    settings: Annotated[Settings, Depends(get_settings)]):
    
    user_in_db = await security.authenticate_user(form_data.username, form_data.password, db_session)
    access_token_expires = timedelta(minutes=settings.access_key_expire_minutes)
    access_token = security.create_access_token(settings, 
                                        data={"sub": str(user_in_db.id), "role":user_in_db.roles}, 
                                        expires_delta=access_token_expires)
    # access_token = security.create_access_token(settings, data={"sub": user_in_db.username, "scope":" ".join(form_data.scopes)}, expires_delta=access_token_expires)

    return Token(access_token=access_token, token_type="bearer")