# backend/locks/ingest_lock.py

import os
from contextlib import contextmanager
from filelock import FileLock, Timeout

LOCK_ROOT = ".ingest_locks"


class IngestLocked(Exception):
    pass


def _lock_path(course_id: str) -> str:
    os.makedirs(LOCK_ROOT, exist_ok=True)
    return os.path.join(LOCK_ROOT, f"{course_id}.lock")


@contextmanager
def ingest_lock(course_id: str, timeout: int = 10):
    """
    Prevent concurrent ingest for the same course.
    Must wrap the entire ingest + persist pipeline.
    """
    lock = FileLock(_lock_path(course_id))

    try:
        lock.acquire(timeout=timeout)
    except Timeout:
        raise IngestLocked(f"INGEST_IN_PROGRESS: {course_id}")

    try:
        yield
    finally:
        lock.release()