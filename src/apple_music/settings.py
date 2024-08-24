from typing import ClassVar

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="APPLE_MUSIC_", env_file=".env", extra="ignore"
    )

    private_key: SecretStr
    key_id: str
    team_id: str


class Settings(BaseSettings):
    auth: AuthSettings = Field(default_factory=AuthSettings)  # type: ignore


settings = Settings()  # type: ignore # see https://github.com/pydantic/pydantic-settings/issues/201
