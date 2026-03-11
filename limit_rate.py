# Add In-Memory Rate Limiting Middleware

# simple in-memory rate limiter to protect an internal API from abuse.
# Max requests per user per minute: 100
import math
from threading import Lock
import time
from collections import defaultdict
from collections import deque
from typing import Deque, Dict, Optional, Tuple

class TooManyRequests(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"429 Too Many Requests. Retry after {retry_after} seconds.")

# class RateLimitMiddleware:
#     _requests = defaultdict(list)

#     def __init__(self, max_requests=100):
#        self.max_requests = max_requests

#     def is_allowed(self, user_id: str) -> bool:
#         now = time.time()

#         # Remove old requests
#         self._requests[user_id] = [
#             ts for ts in self._requests[user_id]
#              if now - ts < 60
#         ]

#         if len(self._requests[user_id]) > self.max_requests:
#              return False

#         self._requests[user_id].append(now)
#         return True
    
class RateLimitMiddleware:

    def __init__(self, max_requests:int=3, window_seconds:int=60):
       self.max_requests = max_requests
       self.window_seconds=int(window_seconds)
       self._requests: Dict[str, Deque[float]] = defaultdict(deque)
       self._lock=Lock()

    def is_allowed(self, user_id: str) -> Tuple[bool, Optional[int]]:
        """Returns (is_allowed, retry_after_seconds)"""
        now = time.monotonic()
        time_struct = time.localtime(now)
        window = self.window_seconds
        dq = self._requests[user_id]

        print("\n------ RATE LIMIT CHECK ------")
        print(f"User: {user_id}")
        print(f"Current time: {now}")
        print(f"Before prune | dq: {list(dq)} | len: {len(dq)}")

        with self._lock:
            # Prune old timestamps
            while dq and now-dq[0] >= window:
                removed = dq.popleft()
                print(f"Pruned timestamp: {removed}")

            print(f"After prune  | dq: {list(dq)} | len: {len(dq)}")    

            if len(dq)>= self.max_requests:
                retry_after = math.ceil(window -(now - dq[0])) if dq else None
                # If remaining time is < 1 second, int() truncates it to 0.
                print("❌ BLOCKED | Retry after:", retry_after)
                return False, retry_after
            dq.append(now) 
            print(f"✅ ALLOWED | Appended: {now}")
            print(f"After append | dq: {list(dq)} | len: {len(dq)}")  
        return True, None
    
    def cleanup_user(self, user_id: str)->None:
        """optional cleanup to remove empty deques and avoid memory growth"""
        with self._lock:
            dq = self._requests.get(user_id)
            if dq and not dq:
                del self._requests[user_id]

# def handle_request(middleware: RateLimitMiddleware, user_id: str):
    # for i in range(5):
    #     allowed, retry = middleware.is_allowed(user_id)
    #     print("Result:", allowed, "Retry:", retry)
    #     time.sleep(1)
    # allowed, retry_after = middleware.is_allowed(user_id)
    # if not allowed:
    #      # return HTTP 429 with Retry-After header
    #     raise TooManyRequests(retry_after)
    # return "OK"

if __name__ =="__main__":
    middleware = RateLimitMiddleware(3, window_seconds=5)
    for i in range(7):
        allowed, retry = middleware.is_allowed("user1")
        print("Result:", allowed, "Retry:", retry)
        time.sleep(1)
        if i==4:
          time.sleep(2)
    