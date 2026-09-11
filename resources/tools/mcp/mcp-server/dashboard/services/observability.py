"""Structured operational logging helpers."""

import json
import logging
from pathlib import Path
import resource
import sys
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


def process_rss_bytes() -> int | None:
    """Return best-effort peak resident memory for operational events."""

    try:
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (AttributeError, OSError, ValueError):
        return None
    multiplier = 1 if sys.platform == "darwin" else 1024
    return int(value * multiplier)


def current_process_rss_bytes() -> int | None:
    """Return current resident memory on Linux, falling back to peak RSS."""

    try:
        resident_pages = int(Path("/proc/self/statm").read_text().split()[1])
        return resident_pages * resource.getpagesize()
    except (OSError, ValueError, IndexError):
        return process_rss_bytes()


def cgroup_memory_status() -> dict[str, Any]:
    """Return best-effort cgroup v2 memory use and limit metadata."""

    try:
        current_text = Path("/sys/fs/cgroup/memory.current").read_text().strip()
        maximum_text = Path("/sys/fs/cgroup/memory.max").read_text().strip()
        current = int(current_text)
        maximum = None if maximum_text == "max" else int(maximum_text)
    except (OSError, ValueError):
        current = current_process_rss_bytes()
        maximum = None
    percent = (
        round((current / maximum) * 100, 2)
        if current is not None and maximum not in (None, 0)
        else None
    )
    events: dict[str, int] = {}
    try:
        for line in Path("/sys/fs/cgroup/memory.events").read_text().splitlines():
            key, value = line.split(maxsplit=1)
            events[key] = int(value)
    except (OSError, ValueError):
        pass
    return {
        "current_bytes": current,
        "max_bytes": maximum,
        "used_percent": percent,
        "events": events,
    }


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
