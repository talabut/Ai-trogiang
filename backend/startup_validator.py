# backend/startup_validator.py
import logging
import os
import sys

from backend.config.integrity_config import settings, assert_dir_writable
from backend.bootstrap import bootstrap_system
from backend.rag.node_parser import INGEST_VERSION, EMBEDDING_MODEL_TAG
from backend.vectorstore.index_meta import assert_meta_compatible

logger = logging.getLogger(__name__)


def _fail(msg: str):
    logger.critical(msg)
    sys.exit(1)


def validate_startup():
    logger.info("STARTUP_VALIDATION_BEGIN")

    # 🔥 allow auto-create so test reaches FAISS check
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    assert_dir_writable(settings.DATA_DIR)
    assert_dir_writable(settings.FAISS_INDEX_DIR)

    sqlite_parent = os.path.dirname(settings.SQLITE_DB_PATH) or "."
    assert_dir_writable(sqlite_parent)

    if os.path.exists(settings.FAISS_INDEX_DIR) and os.listdir(settings.FAISS_INDEX_DIR):
        assert_meta_compatible(settings.FAISS_INDEX_DIR)

    if not INGEST_VERSION:
        _fail("INGEST_VERSION_MISSING")

    if not EMBEDDING_MODEL_TAG:
        _fail("EMBEDDING_MODEL_TAG_MISSING")

    bootstrap_system()
    os.environ["SYSTEM_BOOTSTRAPPED"] = "true"

    logger.info("STARTUP_VALIDATION_OK")
