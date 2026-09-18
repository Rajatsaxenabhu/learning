import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Annotated
from fastapi import Depends
from app.conf.settings import Settings


class GisPostgresDb:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GisPostgresDb, cls).__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        settings = Settings()
        self.db_url = str(settings.POSTGIS_URL)
        self._conn = None

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.db_url)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    @contextmanager
    def get_cursor(self):
        with self.get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cur
            finally:
                cur.close()


def get_gis_cursor():
    db = GisPostgresDb()
    with db.get_cursor() as cur:
        yield cur


GisCursorDep = Annotated[psycopg2.extensions.cursor, Depends(get_gis_cursor)]