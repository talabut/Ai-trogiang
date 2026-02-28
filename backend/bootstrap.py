# backend/bootstrap.py
import sys
import logging

from backend.config.integrity_config import settings, assert_dir_writable
from backend.db.sqlite_safe import connect_sqlite
logger = logging.getLogger(__name__)


def bootstrap_system():
    logger.info("BOOTSTRAP_START")

    # 🔒 Integrity checks (FAIL FAST)
    assert_dir_writable(settings.DATA_DIR)
    assert_dir_writable(settings.FAISS_INDEX_DIR)

    try:
        conn = connect_sqlite(settings.SQLITE_DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ingested_hash (
                hash TEXT PRIMARY KEY
            )
        """)
        conn.close()
    except Exception as e:
        logger.critical(f"BOOTSTRAP_FAILED: DB_ERROR {e}")
        sys.exit(1)

    logger.info("BOOTSTRAP_OK")
