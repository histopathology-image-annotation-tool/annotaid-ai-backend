from pathlib import Path
from typing import Literal

from pydantic import (
    AnyHttpUrl,
    PostgresDsn,
    RedisDsn,
    ValidationInfo,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )

    BASE_DIR: Path = Path(__file__).parent.parent

    API_V1_STR: str = '/api/v1'
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] | AnyHttpUrl = []

    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str) and not value.startswith('['):
            return [i.strip() for i in value.split(",")]
        elif isinstance(value, list):
            return value

        raise ValueError(value)

    CELERY_BROKER_URL: RedisDsn
    CELERY_BACKEND_URL: RedisDsn

    READER_URL: AnyHttpUrl

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str | None = None
    SQLALCHEMY_DATABASE_URI_ASYNC: str | None = None
    SQLALCHEMY_DATABASE_URI: str | None = None

    @field_validator(
        'SQLALCHEMY_DATABASE_URI_ASYNC',
        'SQLALCHEMY_DATABASE_URI',
        mode="before"
    )
    @classmethod
    def assemble_db_async_connection(
        cls,
        _: str | None,
        values: ValidationInfo
    ) -> str:
        """Assemble the database connection string for asyncpg or psycopg2.

        Args:
            _: The value of the field.
            values (ValidationInfo): The validation information.

        Returns:
            str: The database connection string.
        """
        scheme = 'postgresql+asyncpg' \
            if values.field_name == 'SQLALCHEMY_DATABASE_URI_ASYNC' \
            else 'postgresql+psycopg2'

        return PostgresDsn.build(
            scheme=scheme,
            username=values.data.get('POSTGRES_USER'),
            password=values.data.get('POSTGRES_PASSWORD'),
            host=values.data.get('POSTGRES_SERVER'),
            path=values.data.get('POSTGRES_DB') or ''
        ).unicode_string()

    NUCLICK_MODEL_PATH: Path = Path('./models/nuclick_40x.pth')
    MC_FIRST_STAGE_MODEL_PATH: Path = Path('./models/MC_first_stage.pt')
    MC_SECOND_STAGE_MODEL_PATH: Path = Path('./models/MC_second_stage.pt')
    NP_MODEL_PATH: Path = Path('./models/NP_model.pt')
    SAM_MODEL_PATH: Path = Path('./models/sam_vit_b_01ec64.pth')
    SAM_MODEL_VARIANT: Literal['vit_h', 'vit_b', 'vit_l'] = 'vit_b'


settings = Settings()
