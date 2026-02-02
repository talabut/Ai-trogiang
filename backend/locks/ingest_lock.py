# backend/locks/ingest_lock.py
import os
from filelock import FileLock, Timeout

LOCK_ROOT = ".ingest_locks"


class IngestLocked(Exception):
    pass


def acquire_ingest_lock(course_id: str, timeout: int = 1):
    os.makedirs(LOCK_ROOT, exist_ok=True)
    lock_path = os.path.join(LOCK_ROOT, f"{course_id}.lock")

    lock = FileLock(lock_path, timeout=timeout)

    try:
        lock.acquire()
        return lock
    except Timeout:
        raise IngestLocked(f"INGEST_IN_PROGRESS: {course_id}")
