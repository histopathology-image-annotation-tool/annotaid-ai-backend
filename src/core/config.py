from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

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

    NUCLICK_MODEL_PATH: Path = Path('./models/nuclick_40x.pth')
    MC_FIRST_STAGE_MODEL_PATH: Path = Path('./models/MC_first_stage.pt')
    MC_SECOND_STAGE_MODEL_PATH: Path = Path('./models/MC_second_stage.pt')
    NP_MODEL_PATH: Path = Path('./models/NP_model.pt')
    SAM_MODEL_PATH: Path = Path('./models/sam_vit_b_01ec64.pth')
    SAM_MODEL_VARIANT: Literal['vit_h', 'vit_b', 'vit_l'] = 'vit_b'


settings = Settings()