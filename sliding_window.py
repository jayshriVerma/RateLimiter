import time


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_size: int):
        self.limit = limit
        self.window_size = window_size
        self.current_window_count = 0
        self.previous_window_count = 0
        self.window_start = time.time()

    def allow_request(self) -> bool:
        now = time.time()
        elapsed = now - self.window_start

        # Move window if needed
        if elapsed >= self.window_size:
            windows_passed = int(elapsed // self.window_size)

            if windows_passed == 1:
                self.previous_window_count = self.current_window_count
            else:
                self.previous_window_count = 0

            self.current_window_count = 0
            self.window_start = now
            elapsed = 0

        remaining_time = self.window_size - elapsed

        weighted_previous = (
            self.previous_window_count * (remaining_time / self.window_size)
        )

        effective_count = weighted_previous + self.current_window_count

        if effective_count >= self.limit:
            return False

        self.current_window_count += 1
        return True
    
if __name__ == "__main__":
    limiter = SlidingWindowRateLimiter(limit=5, window_size=10)

    for i in range(10):
        allowed = limiter.allow_request()
        print(f"Request {i}:", "Allowed" if allowed else "Blocked")
        time.sleep(1)