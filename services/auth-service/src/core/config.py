from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache

class DbSettings(BaseSettings):

    DBURL : str

    model_config = SettingsConfigDict(  
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )
    
    @field_validator("DBURL")
    @classmethod
    def urlValidator(cls, value):
        if not value.startswith("postgresql://"):
            raise ValueError("DBURL must start with 'postgresql://'")
        return value


class JWTSettings(BaseSettings):

    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES : int

    model_config = SettingsConfigDict(  
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )


@lru_cache()
def getDbSettings():
    return DbSettings()

@lru_cache()
def getJWTSettings():
    return JWTSettings()