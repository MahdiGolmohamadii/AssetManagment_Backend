from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.schemas.user import UserInput
from app.models.user import User
from app.core import security
from app.core.database import get_db_session


router = APIRouter(tags=["Users"])


@router.post("/signup")
async def create_new_account(
            db_session: Annotated[AsyncSession, Depends(get_db_session)],
            user_input: Annotated[UserInput, Body()]):
    
    hashed_pass = security.hash_plain_password(user_input.password)
    new_user = User(username = user_input.username, password=hashed_pass)
    
    try:
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(status_code=400, detail="username already exists")
    # except Exception as e:
    #     await db_session.rollback()
    #     raise HTTPException(status_code=500, detail=f"something whent wrong; {e}")