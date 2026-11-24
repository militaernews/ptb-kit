"""Logging for bots. httpx logs every request URL at INFO, and Telegram's URLs contain the bot
token, so it is held at WARNING."""

from __future__ import annotations

import logging
from pathlib import Path

FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
QUIET = ("httpx", "httpcore", "apscheduler.executors.default")


def setup_logging(level: int = logging.INFO, file: str | Path | None = None) -> logging.Logger:
    """Console logging (plus a log file when given) and quiet HTTP clients; returns the root logger."""
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if file:
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))
    logging.basicConfig(level=level, format=FORMAT, handlers=handlers, force=True)
    for name in QUIET:
        logging.getLogger(name).setLevel(logging.WARNING)
    return logging.getLogger()
