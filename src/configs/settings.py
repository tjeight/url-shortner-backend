from pydantic_settings import BaseSettings, SettingsConfigDict


# Class to handle the application settings using Pydantic's BaseSettings for easy configuration management.
class Settings(BaseSettings):
    # Database configuration parameters for PostgreSQL, which will be loaded from environment variables.
    POSTGRES_USERNAME: str = ""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = ""
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = ""

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


# Configure the settings class
settings = Settings()
