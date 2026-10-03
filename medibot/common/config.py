import os

import dotenv
from pydantic_settings import BaseSettings

from .logger import logger


class Config(BaseSettings):
    def __init__(self):
        if "ENVIRONMENT" not in os.environ:
            env_path = ".env"
        elif "staging" in os.environ["ENVIRONMENT"]:
            env_path = ".staging.env"
        elif "dev" in os.environ["ENVIRONMENT"]:
            env_path = ".dev.env"
        else:
            env_path = ".env"
        logger.info(f"Loading env from {env_path}")
        if os.path.exists(env_path):
            dotenv.load_dotenv(env_path)
        else:
            logger.warning(f"Environment file not found at {env_path}")
        super().__init__()

    ENVIRONMENT: str = "local"
    CORS_ALLOWED_ORIGINS: str = "*"

    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]


config = Config()
