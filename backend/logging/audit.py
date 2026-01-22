import json
from datetime import datetime

LOG_FILE = "logs/audit.log"

def audit_log(user_id, action, payload):
    record = {
        "time": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "payload": payload
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
