from fastapi import APIRouter, Depends, Body, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import utils
from app.schemas.user import UserInput, UserInDb, UserOut, UserUpdate
from app.core.database import get_db_session
from app.core.security import get_current_user, one_or_more_scopes
from app.repositories import user as userRepo


router = APIRouter(tags=["Users"])


@router.post("/signup")
async def create_new_account(
            db_session: Annotated[AsyncSession, Depends(get_db_session)],
            user_input: Annotated[UserInput, Body()]):
    
    try:
        new_user = await userRepo.add_new_user(user_input, db_session)
    except userRepo.UsernameAlreadyExists:
        raise HTTPException(status_code=400, detail="username already exists")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"something whent wrong; {e}")
    
    new_user_in_db = UserInDb.model_validate(new_user)
    return UserOut(**new_user_in_db.model_dump())
    

@router.get("/user/me", response_model=UserOut)
async def get_user_me(
            user: Annotated[UserInDb, Depends(get_current_user)]):
    
    user = user.model_dump()
    return UserOut(**user)

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(
            user_id:int, 
            user: Annotated[UserInDb, Depends(one_or_more_scopes(["user:*", "user:me"]))], 
            db_session: Annotated[AsyncSession, Depends(get_db_session)]):
    
    user_scopes = utils.get_scopes(user.roles)
    user_scopes_list = user_scopes.split(" ")
    user_in_db = await userRepo.get_user_by_id(user_id, db_session)
    if user_in_db is None:
        raise HTTPException(status_code=404, detail="user not found")
    user_in_db = UserInDb.model_validate(user_in_db)
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

    user_updated = await userRepo.update_user(user_id, updated_user, db_session)
    if not user_updated:
        raise HTTPException(status_code=404, detail="user not found")
    user_in_db = UserInDb.model_validate(user_updated)
    return UserOut(**user_in_db.model_dump())

@router.get("/users/")
async def search_user(
            db_session: Annotated[AsyncSession, Depends(get_db_session)], 
            user: Annotated[UserInDb, Depends(get_current_user)],
            id: int | None = None, 
            username: str | None = None, 
            role: str | None = None):
    
    users = await userRepo.find_user(db_session=db_session, id=id, username=username, role=role)
    return [UserOut.model_validate(user) for user in users]