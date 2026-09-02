from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    environment: str = "development"
    database_url: str = "postgresql://signaltrade:signaltrade-local@localhost:5432/signaltrade"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me"
    master_encryption_key: str = ""
    telegram_chat_id: str = ""
    security_event_retention_seconds: int = 86400
    strategy_service_url: str = "http://strategy-api:8000"
    portfolio_service_url: str = "http://portfolio-api:8000"
    identity_service_timeout_seconds: float = 5.0


settings = Settings()

