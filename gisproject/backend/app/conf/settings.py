from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


def get_db_url(drivername, username, password, host, database, port) -> URL:
    return URL.create(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        database=database,
        port=port,
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # postgres
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432

    # redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_USERNAME: str = "default"
    REDIS_PASSWORD: str = ""

    def _db_url(self, drivername: str) -> URL:
        return get_db_url(
            drivername=drivername,
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            database=self.POSTGRES_DB,
            port=self.POSTGRES_PORT,
        )

    @property
    def DATABASE_WRITE_URL(self) -> URL:
        return self._db_url("postgresql+asyncpg")

    @property
    def DATABASE_CELERY_URL(self) -> URL:
        return self._db_url("postgresql+psycopg2")

    @property
    def POSTGIS_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
