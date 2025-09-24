from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_url: str
    secrete_key: str
    algorithm : str
    access_key_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")




@lru_cache
def get_settings():
    return Settings()