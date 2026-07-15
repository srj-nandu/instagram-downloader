from __future__ import annotations

import os


def _int_from_env(*names: str, default: int) -> int:
    for name in names:
        value = os.getenv(name)
        if value:
            return int(value)
    return default


chdir = "story-service"
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
worker_class = "uvicorn.workers.UvicornWorker"
workers = _int_from_env("WEB_CONCURRENCY", "RENDER_WEB_CONCURRENCY", default=1)

timeout = 180
graceful_timeout = 30
keepalive = 5

max_requests = 1000
max_requests_jitter = 50

accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
