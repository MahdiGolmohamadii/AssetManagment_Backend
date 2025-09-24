from pydantic import BaseModel

class UserInput(BaseModel):
    username: str
    password: str

class UserInDb(UserInput):
    id: int

    class Config:
        from_attributes = True

