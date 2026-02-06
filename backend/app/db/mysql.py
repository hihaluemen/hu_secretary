from contextlib import contextmanager
from typing import Iterator

import pymysql
from pymysql.connections import Connection
from pymysql.err import OperationalError

from app.core.config import get_settings


def get_mysql_conn() -> Connection:
    settings = get_settings()
    retry_count = 3
    while retry_count > 0:
        try:
            return pymysql.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DB,
                charset=settings.MYSQL_CHARSET,
                autocommit=False,
            )
        except OperationalError:
            retry_count -= 1
            if retry_count == 0:
                raise
    raise OperationalError("Unable to connect mysql")


@contextmanager
def mysql_conn_context() -> Iterator[Connection]:
    conn = get_mysql_conn()
    try:
        yield conn
    finally:
        conn.close()

