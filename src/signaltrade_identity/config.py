from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    environment: str = "development"
    database_url: str = "postgresql://signaltrade:signaltrade-local@localhost:5432/signaltrade"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me"
    master_encryption_key: str = ""
    internal_service_token: str = ""
    telegram_chat_id: str = ""
    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    security_event_retention_seconds: int = 86400
    access_token_expire_minutes: int = 60
    login_max_failures: int = 5
    login_lockout_minutes: int = 5
    password_reset_token_expire_minutes: int = 3
    password_reset_max_attempts: int = 5
    sensitive_endpoint_rate_limit_window_seconds: int = 60
    sensitive_endpoint_rate_limit_max_requests: int = 10
    upbit_api_base_url: str = "https://api.upbit.com"
    allowed_hosts: str = "localhost,127.0.0.1,testserver,identity-api"
    trusted_proxy_cidrs: str = "127.0.0.1/32,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    strategy_service_url: str = "http://strategy-api:8000"
    portfolio_service_url: str = "http://portfolio-api:8000"
    identity_service_timeout_seconds: float = 5.0

    @property
    def allowed_host_list(self) -> list[str]:
        return [value.strip() for value in self.allowed_hosts.split(",") if value.strip()]

    @property
    def trusted_proxy_cidr_list(self) -> list[str]:
        return [value.strip() for value in self.trusted_proxy_cidrs.split(",") if value.strip()]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}


settings = Settings()
