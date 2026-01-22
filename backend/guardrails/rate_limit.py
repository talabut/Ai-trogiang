import time

REQUEST_LIMIT = 20
WINDOW_SECONDS = 60

_user_requests = {}

def check_rate_limit(user_id: str):
    now = time.time()
    timestamps = _user_requests.get(user_id, [])

    timestamps = [t for t in timestamps if now - t < WINDOW_SECONDS]

    if len(timestamps) >= REQUEST_LIMIT:
        raise ValueError("Bạn gửi quá nhiều yêu cầu. Vui lòng thử lại sau.")

    timestamps.append(now)
    _user_requests[user_id] = timestamps
