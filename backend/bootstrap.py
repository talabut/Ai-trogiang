import os
import logging
from backend.config.integrity_config import settings
from backend.db.sqlite_safe import connect_sqlite

logger = logging.getLogger(__name__)

def bootstrap_system():
    logger.info("BOOTSTRAP_START")

    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)

    try:
        conn = connect_sqlite(settings.SQLITE_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingested_hash (
                hash TEXT PRIMARY KEY
            )
        """)
        conn.close()
    except Exception as e:
        logger.critical(f"BOOTSTRAP_FAILED: {e}")
        raise SystemExit(1)

    if not os.access(settings.FAISS_INDEX_DIR, os.W_OK):
        raise SystemExit("FAISS_INDEX_NOT_WRITABLE")

    logger.info("BOOTSTRAP_OK")
