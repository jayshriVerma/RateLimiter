import threading
import time


class LeakyBucketRateLimiter:
    def __init__(self, capacity: int, leak_rate: float):
        """
        capacity: max bucket size
        leak_rate: requests per second leaving bucket
        """
        self.capacity = capacity
        self.leak_rate = leak_rate

        self.request = 0
        self.last_check = time.time()
        self.lock = threading.Lock()

    def allow_request(self) -> bool:
        with self.lock:
            now = time.time()
            elapsed = now - self.last_check
            self.last_check = now

            # leak request
            leaked = elapsed * self.leak_rate
            self.request = max(0, self.request - leaked)

            if self.request < self.capacity:
                self.request += 1
                return True

            return False

if __name__ == "__main__":
    limiter = LeakyBucketRateLimiter(capacity=5, leak_rate=1)

    for i in range(10):
        allowed = limiter.allow_request()
        print(f"Request {i}:", "Allowed" if allowed else "Blocked")
        time.sleep(0.5)

# Leaky bucket is commonly used in:
# network traffic shaping
# API request smoothing
# load balancing systems  
# operation:allow_request complexity is O(1) due to constant time operations and no data structures that grow with requests.
# memory usage is O(1) since we only store a few variables regardless of the number of requests.