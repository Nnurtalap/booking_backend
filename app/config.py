from typing import Literal

from pydantic import ConfigDict, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        from_attributes=True
    )
    MODE: Literal['DEV', 'TEST', 'PROD']
    LOG_LEVEL: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] 

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    TEST_DB_HOST: str
    TEST_DB_PORT: int
    TEST_DB_USER: str
    TEST_DB_PASS: str
    TEST_DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str 

    SMTP_POST:int
    SMTP_USER:str
    SMTP_HOST:str
    SMTP_PASS:str

    REDIS_HOST:str
    REDIS_PORT:int

    @computed_field 
    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @computed_field 
    @property
    def TEST_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.TEST_DB_USER}:{self.TEST_DB_PASS}@{self.TEST_DB_HOST}:{self.TEST_DB_PORT}/{self.TEST_DB_NAME}'



settings = Settings()