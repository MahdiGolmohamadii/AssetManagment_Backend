import jwt
from datetime import timedelta, datetime, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import Annotated

from app.core.database import get_db_session
from app.core.config import Settings, get_settings
from app.models.user import User
from app.schemas.token import TokenData
from app.schemas.user import UserInDb

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_cntx = CryptContext(schemes=["bcrypt"], deprecated="auto")

CREDENTIAL_EXCEPTION = HTTPException(status_code=401, detail="not a valid user", headers={"WWW-Authenticate": "Bearer"})


def hash_plain_password(password: str):
    return pwd_cntx.hash(password)

def check_plain_password(plain_password: str, hashed_password:str) -> bool:
    return pwd_cntx.verify(plain_password, hashed_password)


def create_access_token(settings: Settings, data: dict, expires_delta: timedelta|None=None):
    to_be_encoded = data.copy()

    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_be_encoded.update({"exp": expires})
    encoded_jwt = jwt.encode(to_be_encoded, settings.secrete_key, algorithm=settings.algorithm)
    return encoded_jwt

async def authenticate_user(username: str, password: str, db_session: AsyncSession):
    user_db = await db_session.execute(select(User).where(User.username == username))
    user_db = user_db.scalar_one_or_none()
    if user_db is None:
        raise CREDENTIAL_EXCEPTION
    # user_in_db = UserInDb(**user_db)
    user_in_db = UserInDb.model_validate(user_db)
    
    if not check_plain_password(password, user_in_db.password):
        raise CREDENTIAL_EXCEPTION
    return user_in_db
    


async def get_user_from_db(db_session: AsyncSession, username: str):
    user = await db_session.execute(select(User).where(User.username == username))
    user = user.scalar_one_or_none()
    if user is None:
        raise CREDENTIAL_EXCEPTION
    return UserInDb.model_validate(user)


async def get_current_user(
            token: Annotated[str, Depends(oauth_scheme)],
            db_session: Annotated[AsyncSession, Depends(get_db_session)],
            settings: Annotated[Settings, Depends(get_settings)]) -> UserInDb:
    try:
        payload = jwt.decode(token, settings.secrete_key, algorithms=settings.algorithm)
        username = payload.get("sub")
        if username is None:
            raise CREDENTIAL_EXCEPTION
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise CREDENTIAL_EXCEPTION
    user_in_db = await get_user_from_db(db_session=db_session, username=token_data.username)
    return user_in_db
    
    