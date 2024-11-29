import os
from http import HTTPMethod
from pathlib import Path
from typing import Any, Final, Literal

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ENVIRONMENTS: Final[dict[str, str]] = {"dev": ".env.dev", "preprod": ".env.preprod", "prod": ".env.prod"}
BASE_DIR: Final[Path] = Path(__file__).parent
ENV_PATH: Final[Path] = BASE_DIR / ENVIRONMENTS.get(str(os.environ.get("ENV")), ".env")
LOGGING_CONFIG_PATH: Final[Path] = BASE_DIR.parent / "logging.yaml"
HTTP_METHODS_TO_ACCEPT: Final[list[str]] = list(HTTPMethod.__members__.values())


class AppConfig(BaseSettings):
    type _LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING"]
    type _API_VERSIONS = Literal["1.0.0"]

    model_config = SettingsConfigDict(
        env_prefix="app_",
        env_file=ENV_PATH,
        extra="allow",
        env_file_encoding="utf-8",
    )

    debug: bool = False
    host: str = "localhost"
    port: int = 8000
    enable_swagger: bool = False
    log_level: _LOG_LEVELS = "INFO"
    version: _API_VERSIONS = "1.0.0"


class ProxyConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="proxy_",
        env_file=ENV_PATH,
        extra="allow",
        env_file_encoding="utf-8",
    )

    request_timeout: int = 3
    user_service_host: str = "localhost"
    user_service_port: int = 8001
    resume_service_host: str = "localhost"
    resume_service_port: int = 8002
    event_service_host: str = "localhost"
    event_service_port: int = 8003

    @property
    def user_service_url(self) -> str:
        return f"https://{self.user_service_host}:{self.user_service_port}"

    @property
    def resume_service_url(self) -> str:
        return f"https://{self.resume_service_host}:{self.resume_service_port}"

    @property
    def event_service_url(self) -> str:
        return f"https://{self.event_service_host}:{self.event_service_port}"


class CORSConfig(BaseSettings):
    type _METHODS = Literal["*", "DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]

    model_config = SettingsConfigDict(
        env_prefix="cors_",
        env_file=ENV_PATH,
        extra="allow",
        env_file_encoding="utf-8",
    )

    allow_origins: tuple[str, ...] = ("*",)
    allow_credentials: bool = False
    allow_methods: tuple[_METHODS, ...] = ("*",)
    allow_headers: tuple[str, ...] = ("*",)

    @field_validator(*("allow_origins", "allow_methods", "allow_headers"), mode="before")
    def split_origins(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.split(",")

        return v


class Config(BaseModel):
    app: AppConfig = AppConfig()
    proxy: ProxyConfig = ProxyConfig()
    cors: CORSConfig = CORSConfig()


config = Config()
