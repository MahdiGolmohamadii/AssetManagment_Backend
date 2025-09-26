from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserInDb, UserUpdate

async def get_user_by_id(id:int, db_session: AsyncSession) -> User:
    user_db = await db_session.execute(select(User).where(User.id == id))
    user_db = user_db.scalar_one_or_none()
    if not user_db:
        return None
    return user_db


async def get_user_by_username(username: str, db_session: AsyncSession) -> User:
    user_db = await db_session.execute(select(User).where(User.username == username))
    user_db = user_db.scalar_one_or_none()
    if not user_db:
        return None
    return user_db

async def delete_user_with_id(id: int, db_session: AsyncSession) -> bool:
    resualt = await db_session.execute(select(User).where(User.id == id))
    user_in_db = resualt.scalar_one_or_none()
    if not user_in_db:
        return False
    await db_session.delete(user_in_db)
    await db_session.commit()
    return True

async def update_user(id: int, user_update: UserUpdate, db_session: AsyncSession) -> User:

    resualt = await db_session.execute(select(User).where(User.id == id))
    user_db = resualt.scalar_one_or_none()
    if not user_db:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_db, key, value)

    db_session.add(user_db)
    await db_session.commit()
    await db_session.refresh(user_db) 
    return user_db