from fastapi import APIRouter, Depends, Body, HTTPException, Security
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


from app.core import utils
from app.schemas.user import UserInput, UserInDb, UserOut, UserUpdate
from app.models.user import User
from app.core import security
from app.core.database import get_db_session
from app.core.security import get_current_user, one_or_more_scopes
from app.repositories import user as userRepo


router = APIRouter(tags=["Users"])


@router.post("/signup")
async def create_new_account(
            db_session: Annotated[AsyncSession, Depends(get_db_session)],
            user_input: Annotated[UserInput, Body()]):
    
    hashed_pass = security.hash_plain_password(user_input.password)
    new_user = User(username = user_input.username, password=hashed_pass, roles = "guest")
    
    try:
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user
    except IntegrityError:
        await db_session.rollback()
        raise HTTPException(status_code=400, detail="username already exists")
    except Exception as e:
        await db_session.rollback()
        raise HTTPException(status_code=500, detail=f"something whent wrong; {e}")
    

@router.get("/user/me", response_model=UserOut)
async def scopes_artist_test(user: Annotated[UserInDb, Depends(get_current_user)]):
    user = user.model_dump()
    return UserOut(**user)

@router.get("/user/{user_id}", response_model=UserOut)
async def get_user(
            user_id:int, 
            user: Annotated[UserInDb, Depends(one_or_more_scopes(["user:*", "user:me"]))], 
            db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    
    user_scopes = utils.get_scopes(user.roles)
    user_scopes_list = user_scopes.split(" ")
    user_in_db = await userRepo.get_user_by_id(user_id, db_session)
    user_in_db = UserInDb.model_validate(user_in_db)
    if user_in_db is None:
        raise HTTPException(status_code=401, detail="user not found")
    if "user:*" in user_scopes_list:
        return UserOut(**user_in_db.model_dump())
    elif "user:me" in user_scopes_list and user.id == user_id:
        return UserOut(**user_in_db.model_dump())
    raise HTTPException(status_code=401, detail="you do not have access to user you wanted")



@router.delete("/users/{user_id}")
async def delete_user(
                user_id:int, 
                user: Annotated[UserInDb, Depends(one_or_more_scopes(["user:*"]))], 
                db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    deleted = await userRepo.delete_user_with_id(user_id, db_session)
    if not deleted:
        raise HTTPException(status_code=404, detail="user not found!")
    return {"deleted id:": user_id}


@router.put("/users/{user_id}")
async def update_user(
            user_id: int,
            updated_user: UserUpdate,
            user: Annotated[UserInDb, Depends(one_or_more_scopes(["user:*"]))],
            db_session: Annotated[AsyncSession, Depends(get_db_session)]):

    await userRepo.update_user(user_id, updated_user, db_session)
    return {"Updated:": updated_user}