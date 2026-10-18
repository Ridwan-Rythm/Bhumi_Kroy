"""In-memory sliding-window rate limit: 30 requests per minute per IP on /check and /verify (contract 5).

One process, one dict: enough for the one-day demo. Behind a reverse proxy the client IP would come
from a trusted X-Forwarded-For; we deliberately do not trust that header here.
"""
from __future__ import annotations

import os
import time
from collections import defaultdict, deque

from fastapi import Request

from app.core.errors import AppError

WINDOW_S = 60.0
DEFAULT_LIMIT = 30


class RateLimiter:
    def __init__(self, clock=time.monotonic):
        self._clock = clock
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    @staticmethod
    def limit() -> int:
        try:
            return int(os.environ.get("RATE_LIMIT_PER_MIN", DEFAULT_LIMIT))
        except ValueError:
            return DEFAULT_LIMIT

    def hit(self, key: str) -> None:
        now = self._clock()
        q = self._hits[key]
        while q and now - q[0] >= WINDOW_S:
            q.popleft()
        if len(q) >= self.limit():
            raise AppError("RATE_LIMITED", "Too many requests. Please wait a minute and try again.")
        q.append(now)

    def reset(self) -> None:
        self._hits.clear()


limiter = RateLimiter()


async def rate_limit(request: Request) -> None:
    limiter.hit(request.client.host if request.client else "unknown")
