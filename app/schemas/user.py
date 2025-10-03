from pydantic import BaseModel, ConfigDict

class UserInput(BaseModel):
    username: str
    password: str

class UserInDb(UserInput):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    roles: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    roles: str

class UserUpdate(BaseModel):
    username: str | None = None
    roles: str | None = None

class UserSearch(BaseModel):
    id: int | None = None
    username: str | None = None
    roles: str | None =  None
    offset: int | None = 0
    limit: int | None = 10

