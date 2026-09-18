import json
import logging
import logging.handlers
import os
from datetime import datetime, timezone
from pathlib import Path

from app.conf.logging.context import ContextFilter

_log_dir = Path(__file__).resolve().parents[3] / "logs"
_log_dir.mkdir(exist_ok=True)

_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

_STANDARD_RECORD_FIELDS = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__)


class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "service": record.name,
            "environment": _ENVIRONMENT,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in _STANDARD_RECORD_FIELDS and key not in payload:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


_FORMATTER = _JSONFormatter()

_loggers: dict[str, logging.Logger] = {}


def setup_logging(service_type: str) -> logging.Logger:
    if service_type in _loggers:
        return _loggers[service_type]

    logger = logging.getLogger(f"slcr.{service_type}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addFilter(ContextFilter())

    console = logging.StreamHandler()
    console.setFormatter(_FORMATTER)
    console.setLevel(logging.INFO)
    logger.addHandler(console)

    file_h = logging.handlers.RotatingFileHandler(
        str(_log_dir / f"{service_type}.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_h.setFormatter(_FORMATTER)
    file_h.setLevel(logging.INFO)
    logger.addHandler(file_h)

    error_h = logging.handlers.RotatingFileHandler(
        str(_log_dir / "errors.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_h.setFormatter(_FORMATTER)
    error_h.setLevel(logging.ERROR)
    logger.addHandler(error_h)

    _loggers[service_type] = logger
    return logger
