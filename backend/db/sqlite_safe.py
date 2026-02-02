# backend/db/sqlite_safe.py
import sqlite3
import time
import random

MAX_RETRY = 5


def connect_sqlite(path: str):
    conn = sqlite3.connect(
        path,
        timeout=30,
        isolation_level=None,
        check_same_thread=False,
    )
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def execute_with_retry(conn, sql, params=()):
    for attempt in range(MAX_RETRY):
        try:
            conn.execute(sql, params)
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                time.sleep(0.1 * (attempt + 1) + random.random() * 0.05)
                continue
            raise
    raise RuntimeError("SQLITE_BUSY_TIMEOUT")
