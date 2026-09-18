from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated
from contextlib import asynccontextmanager,contextmanager

from app.database.config.session import (
    AsyncWriteSessionLocal,
    get_read_sessionmaker,
    ScopedSession
)


class PostgresDb:

    async def get_write_session(self):
        async with AsyncWriteSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


    async def get_read_session(self):
        SessionLocal = get_read_sessionmaker()
        async with SessionLocal() as session:
            yield session 


    @asynccontextmanager
    async def write_session_ctx(self):
        async with AsyncWriteSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


    @asynccontextmanager
    async def read_session_ctx(self):
        SessionLocal = get_read_sessionmaker()
        async with SessionLocal() as session:
            yield session


_db = PostgresDb()

db_write = Annotated[AsyncSession, Depends(_db.get_write_session, use_cache=False)]
db_read = Annotated[AsyncSession, Depends(_db.get_read_session, use_cache=False)]

@contextmanager
def celery_session():
    session = ScopedSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        ScopedSession.remove()