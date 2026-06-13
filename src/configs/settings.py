from datetime import datetime, timedelta, UTC

from pydantic_settings import BaseSettings, SettingsConfigDict


# Class to handle the application settings using Pydantic's BaseSettings for easy configuration management.
class Settings(BaseSettings):
    # Database configuration parameters for PostgreSQL, which will be loaded from environment variables.
    POSTGRES_USERNAME: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""

    # JWT configuration parameters, including the secret key and algorithm used for token generation and validation.
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Set the configuration for the settings, specifying the .env file to load environment variables from.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )  # Specify the .env file for environment variables

    @property
    def database_url(self) -> str:
        # Construct the database URL using the provided configuration parameters.
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def get_access_token_expiry_minutes(self) -> datetime:
        return datetime.now(UTC) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def get_refresh_token_expiry_days(self) -> datetime:
        return datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)


# Configure the settings class
settings = Settings()
