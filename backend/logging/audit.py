import json
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("data/audit.log")


def audit_log(user: str, action: str, payload: dict):
    """
    Append audit log for academic integrity
    """
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user,
        "action": action,
        "payload": payload,
    }

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
