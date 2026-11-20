from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from .config import Config


def connection_kwargs():
    return {
        "host": Config.DB_HOST,
        "port": Config.DB_PORT,
        "dbname": Config.DB_NAME,
        "user": Config.DB_USER,
        "password": Config.DB_PASSWORD,
        "row_factory": dict_row,
        "connect_timeout": 5,
    }


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    with psycopg.connect(**connection_kwargs()) as connection:
        yield connection
