import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List

LOG_PATH = Path("data/audit.log")

def audit_log(
    user: str,
    action: str,
    payload: dict,
    course_id: str | None = None,
    chunk_ids: List[str] | None = None,
    model_name: str | None = None,
    request_id: str | None = None
):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": request_id or str(uuid.uuid4()),
        "user": user,
        "action": action,
        "course_id": course_id,
        "chunk_ids": chunk_ids or [],
        "model": model_name or "offline_stub",
        "payload": payload,
        "schema": "academic_audit_v3"
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
