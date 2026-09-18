from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.conf.settings import Settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

settings = Settings()
DB_URL=settings.DATABASE_CELERY_URL


write_engine = create_async_engine(
    settings.DATABASE_WRITE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


AsyncWriteSessionLocal = async_sessionmaker(
    bind=write_engine,
    expire_on_commit=False
)

def get_read_sessionmaker():
    return AsyncWriteSessionLocal


# celery db cionnection
sync_engine=create_engine(
    settings.DATABASE_CELERY_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)
ScopedSession=scoped_session(SyncSessionLocal)