import jwt
from datetime import timedelta, datetime, timezone
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from typing import Annotated
from pydantic import ValidationError

import app.core.utils as util
from app.core.database import get_db_session
from app.core.config import Settings, get_settings
from app.models.user import User
from app.schemas.token import TokenData
from app.schemas.user import UserInDb
import app.repositories as repositories

oauth_scheme = OAuth2PasswordBearer(
                        tokenUrl="/token",
                        scopes={"me": "read info about current user", "items": "read items"},
                        )
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


def one_or_more_scopes(required_scopes: list[str]):
    async def _one_or_more_scopes(user: Annotated[UserInDb, Depends(get_current_user)]):
        user_avaiable_scopes = util.get_scopes(user.roles)
        if not any(scope in user_avaiable_scopes for scope in required_scopes):
            raise HTTPException(status_code=401, detail="User Not Authorized To Access")
        return user
    return _one_or_more_scopes
        

async def authenticate_user(username: str, password: str, db_session: AsyncSession) -> UserInDb:
    user_in_db = await repositories.user.get_user_by_username(username, db_session)
    if user_in_db is None:
        raise CREDENTIAL_EXCEPTION

    if not check_plain_password(password, user_in_db.password):
        raise CREDENTIAL_EXCEPTION
    user_in_db = UserInDb.model_validate(user_in_db)
    return user_in_db



async def get_current_user(
            security_scopes: SecurityScopes,
            token: Annotated[str, Depends(oauth_scheme)],
            db_session: Annotated[AsyncSession, Depends(get_db_session)],
            settings: Annotated[Settings, Depends(get_settings)]) -> UserInDb:
    
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope={security_scopes.scope_str}"
    else:
        authenticate_value = "Bearer"
    
    CREDENTIAL_EXCEPTION = HTTPException(
        status_code=401,
        detail="invalid user credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, settings.secrete_key, algorithms=[settings.algorithm])
        userid = payload.get("sub")
        if userid is None:
            raise CREDENTIAL_EXCEPTION
        
        userid = int(userid)
        role: str = payload.get("role", "")
        token_scopes = util.get_scopes(role)
        token_scope_list = token_scopes.split()
        token_data = TokenData(user_id=userid, scopes=token_scope_list, role=[role])
    except (InvalidTokenError, ValidationError):
        raise CREDENTIAL_EXCEPTION
    
    user_in_db = await repositories.user.get_user_by_id(userid, db_session)
    user_in_db = UserInDb.model_validate(user_in_db)
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=401,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user_in_db
    
    