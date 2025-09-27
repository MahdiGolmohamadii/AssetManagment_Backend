from pydantic import BaseModel

class UserInput(BaseModel):
    username: str
    password: str

class UserInDb(UserInput):
    id: int
    roles: str

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    username: str
    roles: str

class UserUpdate(BaseModel):
    username: str | None = None
    roles: str | None = None

