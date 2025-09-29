from pydantic import BaseModel, ConfigDict

class UserInput(BaseModel):
    username: str
    password: str

class UserInDb(UserInput):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    roles: str

    # class Config:
    #     from_attributes = True



class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    roles: str

    # class Config:
    #     from_attributes = True

class UserUpdate(BaseModel):
    username: str | None = None
    roles: str | None = None

