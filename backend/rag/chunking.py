import hashlib
import sqlite3
from filelock import FileLock
from backend.config.integrity_config import settings

LOCK_PATH = f"{settings.DATA_DIR}/ingest.lock"

def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def is_duplicate(h: str) -> bool:
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM ingested_hash WHERE hash = ?", (h,))
    found = cur.fetchone() is not None
    conn.close()
    return found

def register_hash(h: str):
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO ingested_hash(hash) VALUES (?)", (h,))
    conn.commit()
    conn.close()

def ingest_with_lock(text: str, ingest_fn):
    h = content_hash(text)

    with FileLock(LOCK_PATH):
        if is_duplicate(h):
            return {"status": "skipped", "reason": "duplicate"}

        ingest_fn(text)
        register_hash(h)
        return {"status": "ingested"}
