from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_url: str = "http://localhost:8000"
    api_url: str = "http://localhost:8000"
    log_level: str = "debug"
    secret_key: str = "change-me"

    # Database
    database_url: str = (
        "postgresql+asyncpg://courtflow:courtflow@localhost:5432/courtflow"
    )
    database_pool_size: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret: str = "change-me"
    jwt_expiry_minutes: int = 60
    refresh_token_expiry_days: int = 30

    # WeChat
    wechat_app_id: str = ""
    wechat_app_secret: str = ""
    wechat_pay_mch_id: str = ""
    wechat_pay_api_key: str = ""
    wechat_pay_cert_serial: str = ""
    wechat_pay_private_key_path: str = ""

    # Storage
    s3_bucket: str = "courtflow"
    s3_region: str = "auto"
    s3_endpoint_url: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
