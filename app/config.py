from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    APP_NAME: str = "Callify"
    APP_DOMAIN: str = "localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )


class DatabaseSettings(BaseSettings):
    MYSQL_SERVER: str
    MYSQL_PORT: int
    MYSQL_USER: str
    MYSQL_PASSWORD: str
    MYSQL_DB: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    @property
    def MYSQL_URL(self) -> str:
        # Async connection string for SQLAlchemy
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    @property
    def MYSQL_URL_SYNC(self) -> str:
        # Sync connection string (for Alembic migrations)
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )


class CronSettings(BaseSettings):
    THREE_MONTHS: int = 90
    SEVEN_DAYS: int = 7

    CRON_DAY_OF_WEEK: str = "sat"
    CRON_HOUR: int = 0
    CRON_MINUTE: int = 0
    CRON_SECOND: int = 0
    CRON_TIMEZONE: str = "Asia/Kolkata"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

# These will now be filled by env vars or Docker Compose .env
app_settings = AppSettings()
db_settings = DatabaseSettings()  # type: ignore
