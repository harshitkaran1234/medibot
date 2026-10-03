from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    CORS_ALLOWED_ORIGINS: str = "*"
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None

    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",")]


config = Config()
