from pydantic_settings import BaseSettings, SettingsConfigDict
# from urllib.parse import quote_plus

class AppSettings(BaseSettings):
    APP_NAME: str = "Callify"
    APP_DOMAIN: str = "localhost:8000"
    APP_MODE: str = "dev"  # dev, stage, prod

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )


class DatabaseSettings(BaseSettings):
    """
    Configuration settings for connecting to a MySQL database.

    Attributes:
        MYSQL_SERVER (str): Hostname or IP address of the MySQL server.
        MYSQL_PORT (int): Port number on which the MySQL server is listening.
        MYSQL_USER (str): Username for authenticating with the MySQL server.
        MYSQL_PASSWORD (str): Password for authenticating with the MySQL server.
        MYSQL_DB (str): Name of the MySQL database to connect to.

    The configuration is loaded from environment variables, optionally using a .env file.
    """

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
        """
        Constructs the asynchronous SQLAlchemy connection string for MySQL using aiomysql.

        Returns:
            str: The async connection URL for SQLAlchemy.
        """
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )

    @property
    def MYSQL_URL_SYNC(self) -> str:
        """
        Constructs the synchronous SQLAlchemy connection string for MySQL using pymysql.
        Typically used for database migrations (e.g., with Alembic).

        Returns:
            str: The sync connection URL for SQLAlchemy.
        """
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )
    
# class DatabaseSettings(BaseSettings):
#     MYSQL_SERVER: str
#     MYSQL_PORT: int
#     MYSQL_USER: str
#     MYSQL_PASSWORD: str
#     MYSQL_DB: str

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_ignore_empty=True,
#         extra="ignore"
#     )

#     @property
#     def MYSQL_URL(self) -> str:
#         encoded_pw = quote_plus(self.MYSQL_PASSWORD)
#         return (
#             f"mysql+aiomysql://{self.MYSQL_USER}:{encoded_pw}"
#             f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
#         )

#     @property
#     def MYSQL_URL_SYNC(self) -> str:
#         encoded_pw = quote_plus(self.MYSQL_PASSWORD)
#         return (
#             f"mysql+pymysql://{self.MYSQL_USER}:{encoded_pw}"
#             f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
#         )


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
