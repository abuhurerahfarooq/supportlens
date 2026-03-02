import json
import logging
import sys
from datetime import datetime, timezone
from flask import g, has_request_context


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event_name", record.getMessage()),
        }

        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            payload.update(fields)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging(level=logging.INFO):
    root = logging.getLogger()
    root.setLevel(level)

    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def log_event(logger, level, event_name, **fields):
    if "request_id" not in fields and has_request_context():
        fields["request_id"] = getattr(g, "request_id", None)
    logger.log(level, event_name, extra={"event_name": event_name, "fields": fields})
