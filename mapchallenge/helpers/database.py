from contextlib import contextmanager
from os import environ
from typing import Generator

import psycopg
from psycopg import Connection
from psycopg.abc import Params, Query
from psycopg.rows import TupleRow
from psycopg.types import TypeInfo
from psycopg.types.shapely import register_shapely

POSTGIS_CONN_STR = environ["POSTGIS_CONN_STR"]


@contextmanager
def get_connection() -> Generator[Connection[TupleRow], None, None]:
    with psycopg.connect(POSTGIS_CONN_STR) as conn:
        info = TypeInfo.fetch(conn, "geometry")
        assert (
            info is not None
        ), "Could not fetch geometry type info, is PostGIS installed?"
        register_shapely(info, conn)
        yield conn


def run_query(query: Query, params: Params | None = None) -> list[TupleRow]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
