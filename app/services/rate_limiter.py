import time
from collections import defaultdict

from fastapi import HTTPException

RATE_LIMIT = 5
WINDOW_SIZE = 60
request_counter = defaultdict(list)


def limit_requests(user_id: int):
    current_time = time.time()
    request_counter[user_id] = [t for t in request_counter[user_id] if current_time - t < WINDOW_SIZE]
    if len(request_counter[user_id]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    request_counter[user_id].append(current_time)
