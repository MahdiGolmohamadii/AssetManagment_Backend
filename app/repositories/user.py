from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserInDb

async def get_user_by_id(id:int, db_session: AsyncSession):
    user_db = await db_session.execute(select(User).where(User.id == id))
    user_db = user_db.scalar_one_or_none()
    if not user_db:
        return None
    user_in_db = UserInDb.model_validate(user_db)
    return user_in_db