from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserInDb, UserUpdate, UserInput, UserSearch
from app.core import security


class UsernameAlreadyExists(Exception):
    pass

async def add_new_user(user_input: UserInput, db_session: AsyncSession) -> User:
    hashed_pass = security.hash_plain_password(user_input.password)
    new_user = User(username = user_input.username, password=hashed_pass, roles = "guest")
    try:
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return new_user
    except IntegrityError:
        await db_session.rollback()
        raise UsernameAlreadyExists
    except Exception:
        await db_session.rollback()
        raise Exception

async def get_user_by_id(id:int, db_session: AsyncSession) -> User:
    result = await db_session.execute(select(User).where(User.id == id))
    user_db = result.scalar_one_or_none()
    if not user_db:
        return None
    
    return user_db


async def get_user_by_username(username: str, db_session: AsyncSession) -> User:
    result = await db_session.execute(select(User).where(User.username == username))
    user_db = result.scalar_one_or_none()
    if not user_db:
        return None
    
    return user_db

async def delete_user_with_id(id: int, db_session: AsyncSession) -> bool:
    result = await db_session.execute(select(User).where(User.id == id))
    user_in_db = result.scalar_one_or_none()
    if not user_in_db:
        return False
    
    await db_session.delete(user_in_db)
    await db_session.commit()
    return True

async def update_user(id: int, user_update: UserUpdate, db_session: AsyncSession) -> User:
    result = await db_session.execute(select(User).where(User.id == id))
    user_db = result.scalar_one_or_none()
    if not user_db:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_db, key, value)
    db_session.add(user_db)
    await db_session.commit()
    await db_session.refresh(user_db) 
    return user_db

async def find_user(
            db_session: AsyncSession, 
            user_search: UserSearch) -> list[User]:
    query = select(User)
    if user_search.id:
        query = query.where(User.id == user_search.id)
    if user_search.roles:
        query = query.where((User.roles.ilike(f"%{user_search.roles}%")))
    if user_search.username:
        query = query.where(User.username == user_search.username)

    query = query.limit(user_search.limit).offset(user_search.offset)
    users = await db_session.execute(query)
    res = users.scalars().all()
    return res