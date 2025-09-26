from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: int | None = None
    scopes: list[str] = []
    role: list[str] = []