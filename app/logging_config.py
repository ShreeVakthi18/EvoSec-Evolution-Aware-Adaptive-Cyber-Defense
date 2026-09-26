"""
Structured logging for EAACD.

Emits one JSON object per log line (when settings.log_json is True) so logs
can be ingested by any log aggregator. Deliberately never logs request
bodies, headers, or any credential-like value - only path, method, a
truncated/opaque client identifier, computed risk, and classification.
"""
from __future__ import annotations

import json
import logging
import sys
import time

from app.config import settings

_LOGGER_NAME = "eaacd"


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": round(time.time(), 3),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if extra:
            payload.update(extra)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if logger.handlers:
        return logger  # already configured (e.g. re-imported in tests)

    logger.setLevel(settings.log_level.upper())
    handler = logging.StreamHandler(sys.stdout)
    if settings.log_json:
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


logger = configure_logging()


def log_event(event: str, **fields) -> None:
    """Log a structured security/application event.

    Never pass secrets/credentials/full request bodies into `fields`.
    """
    logger.info(event, extra={"extra_fields": {"event": event, **fields}})
