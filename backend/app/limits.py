import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

WINDOW_SECONDS = 60
MAX_QUESTIONS = 6  # per visitor per minute, protects your Groq quota on a public site

_hits: dict[str, deque] = defaultdict(deque)


def rate_limit(request: Request) -> None:
    """Allow each visitor (by IP address) a few questions per minute."""
    visitor = request.client.host if request.client else "unknown"
    now = time.time()
    recent = _hits[visitor]
    while recent and now - recent[0] > WINDOW_SECONDS:
        recent.popleft()
    if len(recent) >= MAX_QUESTIONS:
        raise HTTPException(status_code=429, detail="Too many questions in a short time. Please wait a minute and try again.")
    recent.append(now)