from contextlib import contextmanager
from os import environ

import psycopg
from psycopg.types import TypeInfo
from psycopg.types.shapely import register_shapely

POSTGIS_CONN_STR = environ["POSTGIS_CONN_STR"]


@contextmanager
def get_connection():
    with psycopg.connect(POSTGIS_CONN_STR) as conn:
        info = TypeInfo.fetch(conn, "geometry")
        register_shapely(info, conn)
        yield conn


def run_query(query, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
