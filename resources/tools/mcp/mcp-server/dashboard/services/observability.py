"""Structured operational logging helpers."""

import json
import logging
from datetime import UTC, datetime
from typing import Any, Mapping


LOGGER = logging.getLogger("csit_mcp.observability")
REDACTED_KEYS = {"records", "payload", "body", "credentials", "authorization"}


def log_event(event: str, **fields: Any) -> None:
    """Emit one JSON object for an operational event."""

    payload = {
        "event": event,
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }
    payload.update(_json_safe_mapping(fields))
    LOGGER.info(json.dumps(payload, sort_keys=True))


def _json_safe_mapping(fields: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): (
            "[redacted]" if str(key).lower() in REDACTED_KEYS
            else _json_safe(value)
        )
        for key, value in fields.items()
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        return _json_safe_mapping(value)
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if not isinstance(value, (str, bytes)) and hasattr(value, "item"):
        try:
            return _json_safe(value.item())
        except (TypeError, ValueError):
            pass
    if not isinstance(value, (str, bytes)) and hasattr(value, "tolist"):
        try:
            return _json_safe(value.tolist())
        except (TypeError, ValueError):
            pass
    return str(value)
