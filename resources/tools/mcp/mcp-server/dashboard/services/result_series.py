"""Shared parsing helpers for semantic CSIT result series."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from ..utils.constants import Constants
from .statistics import parse_job_dimensions


DUT_ORDER = ("dpdk", "trex", "vpp")
PREFERRED_DUTS = ("vpp", "dpdk", "trex")
TEST_TYPE_ORDER = ("hoststack", "mrr", "ndr", "pdr", "soak")
LOGICAL_TEST_TYPES = {
    "ndrpdr": ("ndr", "pdr"),
    "ndr": ("ndr",),
    "pdr": ("pdr",),
    "mrr": ("mrr",),
    "soak": ("soak",),
    "hoststack": ("hoststack",),
}
METRIC_COLUMNS = {
    "mrr": {
        "throughput": (
            "result_receive_rate_rate_avg",
            "result_receive_rate_rate_unit",
        ),
        "bandwidth": (
            "result_receive_rate_bandwidth_avg",
            "result_receive_rate_bandwidth_unit",
        ),
    },
    "ndr": {
        "throughput": (
            "result_ndr_lower_rate_value",
            "result_ndr_lower_rate_unit",
        ),
        "bandwidth": (
            "result_ndr_lower_bandwidth_value",
            "result_ndr_lower_bandwidth_unit",
        ),
    },
    "pdr": {
        "throughput": (
            "result_pdr_lower_rate_value",
            "result_pdr_lower_rate_unit",
        ),
        "bandwidth": (
            "result_pdr_lower_bandwidth_value",
            "result_pdr_lower_bandwidth_unit",
        ),
        "latency": (
            "result_latency_forward_pdr_50_avg",
            "result_latency_forward_pdr_50_unit",
        ),
    },
    "soak": {
        "throughput": (
            "result_critical_rate_lower_rate_value",
            "result_critical_rate_lower_rate_unit",
        ),
        "bandwidth": (
            "result_critical_rate_lower_bandwidth_value",
            "result_critical_rate_lower_bandwidth_unit",
        ),
    },
    "hoststack": {
        "throughput": ("result_rate_value", "result_rate_unit"),
        "bandwidth": ("result_bandwidth_value", "result_bandwidth_unit"),
        "latency": ("result_latency_value", "result_latency_unit"),
    },
}

_TOPOLOGY_PREFIX = re.compile(r"^\d+n\d+l[a-z]*$")
_FRAME_SIZE = re.compile(r"^(?:\d+b|imix|jumbo)$")
_CORE_COUNT = re.compile(r"^\d+c$")
_NATURAL_PART = re.compile(r"(\d+)")


def parse_result_dimensions(row: dict[str, Any]) -> dict[str, str] | None:
    """Parse stable dimensions shared by Trending and Iterative rows."""

    test_id = text_value(row.get("test_id"))
    dut = text_value(row.get("dut_type"))
    job = text_value(row.get("job"))
    if not test_id or not dut or not job or dut not in DUT_ORDER:
        return None
    parts = test_id.split(".")
    if len(parts) < 5:
        return None
    area = "dpdk" if dut == "dpdk" else parts[3].strip().lower()
    identity_tokens = [token for token in parts[4].lower().split("-") if token]
    if identity_tokens and _TOPOLOGY_PREFIX.fullmatch(identity_tokens[0]):
        identity_tokens.pop(0)
    if not identity_tokens:
        return None
    nic = identity_tokens.pop(0)
    driver, _remaining = consume_driver(identity_tokens)
    final_tokens = [token for token in parts[-1].lower().split("-") if token]
    framesize = final_tokens.pop(0) if final_tokens else None
    if not framesize or not _FRAME_SIZE.fullmatch(framesize):
        return None
    framesize = framesize[:-1] + "B" if framesize.endswith("b") else framesize
    cores = (
        final_tokens.pop(0)
        if final_tokens and _CORE_COUNT.fullmatch(final_tokens[0])
        else "0c"
    )
    _final_driver, final_tokens = consume_driver(final_tokens)
    if final_tokens and final_tokens[-1] in {"mrr", "ndrpdr", "soak"}:
        final_tokens.pop()
    test = "-".join(final_tokens)
    topology = parse_job_dimensions(job).get("testbed")
    hosts = hosts_value(row.get("hosts"))
    testbed = text_value(hosts[0]) if hosts else None
    if not test or not topology or not testbed:
        return None
    infra = f"{topology}-{nic}-{driver}"
    return {
        "dut": dut,
        "area": area,
        "area_label": area_label(area),
        "test": test,
        "infra": infra,
        "testbed": testbed,
        "framesize": framesize,
        "cores": cores,
        "nic": nic,
        "driver": driver,
    }


def semantic_metrics(row: dict[str, Any], logical_type: str) -> dict[str, Any]:
    """Return normalized semantic metric values and units for one row."""

    metrics: dict[str, Any] = {}
    for metric in ("throughput", "bandwidth", "latency"):
        columns = METRIC_COLUMNS[logical_type].get(metric)
        metrics[f"{metric}_value"] = (
            numeric_value(row.get(columns[0])) if columns else None
        )
        metrics[f"{metric}_unit"] = (
            text_value(row.get(columns[1])) if columns else None
        )
    return metrics


def consume_driver(tokens: list[str]) -> tuple[str, list[str]]:
    remaining = list(tokens)
    for driver in sorted(Constants.DRIVERS, key=len, reverse=True):
        driver_tokens = driver.split("-")
        if remaining[:len(driver_tokens)] == driver_tokens:
            return driver, remaining[len(driver_tokens):]
    return "dpdk", remaining


def natural_key(value: str) -> tuple[Any, ...]:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in _NATURAL_PART.split(value)
    )


def area_label(area: str) -> str:
    label = Constants.LABELS.get(area)
    if label:
        return label
    return area.replace("_", " ").replace("ip4", "IPv4").replace(
        "ip6", "IPv6"
    ).title().replace("Ipv4", "IPv4").replace("Ipv6", "IPv6")


def text_value(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    normalized = str(value).strip().lower()
    return normalized or None


def is_passed(value: Any) -> bool:
    if value is None:
        return False
    try:
        if pd.isna(value):
            return False
    except (TypeError, ValueError):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def numeric_value(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if pd.notna(parsed) else None


def integer_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def hosts_value(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        normalized = value.strip()
        return [normalized] if normalized else None
    if not isinstance(value, (list, tuple, set)) and hasattr(value, "tolist"):
        try:
            value = value.tolist()
        except (TypeError, ValueError):
            return None
    if isinstance(value, (list, tuple, set)):
        hosts = [str(item).strip() for item in value if str(item).strip()]
        return list(dict.fromkeys(hosts)) or None
    normalized = str(value).strip()
    return [normalized] if normalized else None
