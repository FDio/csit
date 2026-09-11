"""OpenMetrics telemetry decoding and compact telemetry payload helpers."""

from __future__ import annotations

import base64
import math
import re
import zlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

import pandas as pd


TELEMETRY_DATASETS = ("trending", "iterative", "coverage")
TELEMETRY_CONTEXT_COLUMNS = (
    "job",
    "build",
    "start_time",
    "test_type",
    "dut_type",
    "dut_version",
    "tg_type",
    "hosts",
    "test_id",
    "release",
    "passed",
)
TELEMETRY_COLUMNS = (
    "source_dataset",
    "source_row",
    *TELEMETRY_CONTEXT_COLUMNS,
    "metric_name",
    "labels",
    "label_key",
    "value",
    "timestamp",
    "type",
    "unit",
    "help",
)
DEFAULT_TELEMETRY_LIMIT = 100
DEFAULT_ANALYSIS_LIMIT = 20
MAX_TELEMETRY_LIMIT = 10_000
DEFAULT_MAX_TELEMETRY_SOURCE_ROWS = 500
DEFAULT_MAX_TELEMETRY_SAMPLES = 100_000
TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}


@dataclass(frozen=True)
class DecodedTelemetry:
    """Decoded telemetry text and decode errors for one source row."""

    text: str
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ParsedOpenMetrics:
    """Parsed OpenMetrics samples and parse errors for one source row."""

    samples: tuple[dict[str, Any], ...]
    errors: tuple[str, ...]
    truncated: bool = False


def empty_telemetry_data(dataset_keys: Iterable[str]) -> dict[str, pd.DataFrame]:
    """Return empty telemetry dataframes keyed by source dataset."""

    return {
        dataset: pd.DataFrame(columns=list(TELEMETRY_COLUMNS))
        for dataset in dataset_keys
    }


def empty_telemetry_status(dataset_keys: Iterable[str]) -> dict[str, dict[str, Any]]:
    """Return empty telemetry status entries keyed by source dataset."""

    return {
        dataset: _telemetry_status_entry(
            available=False,
            sample_count=0,
            rows_with_telemetry=0,
            rows_with_errors=0,
            metric_names=[],
            source_row_count=0,
            indexed_row_count=0,
            truncated=False,
            status="not_available",
        )
        for dataset in dataset_keys
    }


def indexing_telemetry_status(
        data: Mapping[str, pd.DataFrame]
    ) -> dict[str, dict[str, Any]]:
    """Return status metadata while telemetry indexing is in progress."""

    status = empty_telemetry_status(data)
    for dataset, frame in data.items():
        if frame.empty or "telemetry" not in frame.columns:
            continue
        source_row_count = sum(
            1 for value in frame["telemetry"] if _telemetry_values(value)
        )
        status[dataset] = _telemetry_status_entry(
            available=source_row_count > 0,
            sample_count=0,
            rows_with_telemetry=0,
            rows_with_errors=0,
            metric_names=[],
            source_row_count=source_row_count,
            indexed_row_count=0,
            truncated=False,
            status="indexing" if source_row_count > 0 else "empty",
        )
    return status


def failed_telemetry_status(
        data: pd.DataFrame,
        error: Exception,
        *,
        max_source_rows: int,
        max_samples: int
    ) -> dict[str, Any]:
    """Return non-fatal telemetry indexing failure metadata."""

    source_row_count = (
        sum(1 for value in data["telemetry"] if _telemetry_values(value))
        if "telemetry" in data.columns
        else 0
    )
    return _telemetry_status_entry(
        available=source_row_count > 0,
        sample_count=0,
        rows_with_telemetry=0,
        rows_with_errors=source_row_count,
        metric_names=[],
        source_row_count=source_row_count,
        indexed_row_count=0,
        truncated=False,
        max_source_rows=max_source_rows,
        max_samples=max_samples,
        status="failed",
        error=repr(error),
    )


def normalize_dataset_telemetry(
        dataset: str,
        data: pd.DataFrame,
        *,
        max_source_rows: int = DEFAULT_MAX_TELEMETRY_SOURCE_ROWS,
        max_samples: int = DEFAULT_MAX_TELEMETRY_SAMPLES
    ) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Decode a bounded, representative telemetry index for one dataset."""

    if data.empty or "telemetry" not in data.columns:
        return (
            data,
            pd.DataFrame(columns=list(TELEMETRY_COLUMNS)),
            _telemetry_status_entry(
                available=False,
                sample_count=0,
                rows_with_telemetry=0,
                rows_with_errors=0,
                metric_names=[],
                source_row_count=0,
                indexed_row_count=0,
                truncated=False,
                max_source_rows=max_source_rows,
                max_samples=max_samples,
            ),
        )

    working_data = data.copy(deep=False)
    telemetry_records: list[dict[str, Any]] = []
    metric_names: set[str] = set()
    metric_counts: list[Any] = [pd.NA] * len(working_data)
    decode_errors_by_row: list[str | None] = [None] * len(working_data)
    parse_errors: list[str | None] = [None] * len(working_data)
    rows_with_telemetry = 0
    rows_with_errors = 0
    rows_with_decode_errors = 0
    rows_with_parse_errors = 0
    decode_error_count = 0
    parse_error_count = 0
    truncated = False

    candidate_positions = [
        position
        for position, value in enumerate(working_data["telemetry"])
        if _telemetry_values(value)
    ]
    selected_positions = _representative_positions(
        candidate_positions,
        max_source_rows=max_source_rows,
    )
    if len(selected_positions) < len(candidate_positions):
        truncated = True

    sample_budget_per_row = max(
        1,
        max_samples // max(1, len(selected_positions)),
    )
    for source_position in selected_positions:
        source_row = working_data.index[source_position]
        row = working_data.iloc[source_position]
        decoded = decode_telemetry_cell(row.get("telemetry"))
        row_decode_errors = list(decoded.errors)
        row_parse_errors: list[str] = []
        row_samples: tuple[dict[str, Any], ...] = ()
        if decoded.text:
            rows_with_telemetry += 1
            parsed = parse_openmetrics(
                decoded.text,
                max_samples=sample_budget_per_row,
            )
            row_parse_errors.extend(parsed.errors)
            row_samples = parsed.samples
            truncated = truncated or parsed.truncated

        context = _source_context(row)
        for sample in row_samples:
            metric_name = str(sample.get("metric_name") or "")
            if metric_name:
                metric_names.add(metric_name)
            telemetry_records.append({
                "source_dataset": dataset,
                "source_row": int(source_row)
                if isinstance(source_row, int)
                else str(source_row),
                **context,
                **sample,
            })

        metric_counts[source_position] = len(row_samples)
        if row_decode_errors:
            rows_with_decode_errors += 1
            decode_error_count += len(row_decode_errors)
            decode_errors_by_row[source_position] = "; ".join(
                row_decode_errors[:3]
            )
        if row_parse_errors:
            rows_with_parse_errors += 1
            parse_error_count += len(row_parse_errors)
            parse_errors[source_position] = "; ".join(row_parse_errors[:3])
        if row_decode_errors or row_parse_errors:
            rows_with_errors += 1

    working_data["telemetry_metric_count"] = pd.Series(
        metric_counts,
        index=working_data.index,
        dtype="Int64",
    )
    working_data["telemetry_decode_error"] = pd.Series(
        decode_errors_by_row,
        index=working_data.index,
        dtype=object,
    )
    working_data["telemetry_parse_error"] = pd.Series(
        parse_errors,
        index=working_data.index,
        dtype=object,
    )
    telemetry_data = pd.DataFrame.from_records(
        telemetry_records,
        columns=list(TELEMETRY_COLUMNS),
    )
    return (
        working_data,
        telemetry_data,
        _telemetry_status_entry(
            available=bool(candidate_positions),
            sample_count=len(telemetry_records),
            rows_with_telemetry=rows_with_telemetry,
            rows_with_errors=rows_with_errors,
            metric_names=sorted(metric_names),
            source_row_count=len(candidate_positions),
            indexed_row_count=len(selected_positions),
            truncated=truncated,
            rows_with_decode_errors=rows_with_decode_errors,
            rows_with_parse_errors=rows_with_parse_errors,
            decode_error_count=decode_error_count,
            parse_error_count=parse_error_count,
            max_source_rows=max_source_rows,
            max_samples=max_samples,
        ),
    )


def decode_telemetry_cell(value: Any) -> DecodedTelemetry:
    """Decode one raw telemetry cell into OpenMetrics text."""

    values = _telemetry_values(value)
    if not values:
        return DecodedTelemetry(text="", errors=())

    decoded_parts: list[str] = []
    errors: list[str] = []
    for index, item in enumerate(values):
        try:
            encoded = _encoded_bytes(item)
            compressed = base64.b64decode(encoded)
            decoded_parts.append(
                zlib.decompress(compressed).decode("utf-8", errors="replace")
            )
        except Exception as err:  # noqa: BLE001 - telemetry must not fail loads.
            errors.append(f"decode[{index}]: {type(err).__name__}: {err}")

    return DecodedTelemetry(
        text="\n".join(part for part in decoded_parts if part),
        errors=tuple(errors),
    )


def parse_openmetrics(
        text: str,
        *,
        max_samples: int | None = None
    ) -> ParsedOpenMetrics:
    """Parse OpenMetrics text into sample dictionaries."""

    help_by_metric: dict[str, str] = {}
    type_by_metric: dict[str, str] = {}
    unit_by_metric: dict[str, str] = {}
    samples: list[dict[str, Any]] = []
    errors: list[str] = []
    truncated = False

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            _parse_comment(
                line,
                help_by_metric=help_by_metric,
                type_by_metric=type_by_metric,
                unit_by_metric=unit_by_metric,
            )
            continue

        try:
            sample = _parse_sample_line(line)
        except ValueError as err:
            errors.append(f"line {line_number}: {err}")
            continue

        metric_name = sample["metric_name"]
        sample["type"] = _metric_metadata(metric_name, type_by_metric)
        sample["unit"] = _metric_metadata(metric_name, unit_by_metric)
        sample["help"] = _metric_metadata(metric_name, help_by_metric)
        samples.append(sample)
        if max_samples is not None and len(samples) >= max_samples:
            truncated = True
            break

    return ParsedOpenMetrics(
        samples=tuple(samples),
        errors=tuple(errors),
        truncated=truncated,
    )


def telemetry_metrics_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        status: Mapping[str, Any],
        metric_name: str | None = None,
        label_key: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        test_id: str | None = None,
        build: int | None = None,
        passed: bool | None = None,
        offset: int = 0,
        limit: int = DEFAULT_TELEMETRY_LIMIT
    ) -> dict[str, Any]:
    """Build a paginated telemetry metric sample payload."""

    filtered_data, filters, errors = _filtered_telemetry_data(
        data,
        metric_name=metric_name,
        label_key=label_key,
        test_type=test_type,
        dut_type=dut_type,
        job=job,
        release=release,
        hosts=hosts,
        test_id=test_id,
        build=build,
        passed=passed,
    )
    parsed_offset, offset_error = _parse_int(
        "offset",
        offset,
        default=0,
        minimum=0,
    )
    parsed_limit, limit_error = _parse_int(
        "limit",
        limit,
        default=DEFAULT_TELEMETRY_LIMIT,
        minimum=1,
        maximum=MAX_TELEMETRY_LIMIT,
    )
    filters["offset"] = parsed_offset
    filters["limit"] = parsed_limit
    errors.extend(err for err in (offset_error, limit_error) if err is not None)
    if errors:
        return _validation_error(errors, filters)

    returned_data = filtered_data.iloc[
        parsed_offset:parsed_offset + parsed_limit
    ]
    returned_count = len(returned_data)
    has_more = parsed_offset + returned_count < len(filtered_data)
    return {
        "schema_version": 1,
        "dataset": dataset,
        "telemetry": True,
        "total_row_count": len(data),
        "row_count": len(filtered_data),
        "returned_count": returned_count,
        "limit": parsed_limit,
        "offset": parsed_offset,
        "has_more": has_more,
        "next_offset": parsed_offset + returned_count if has_more else None,
        "freshness": status.get("last_success_at"),
        "data_status": status.get("status"),
        "filters": _json_safe_value(filters),
        "columns": list(returned_data.columns),
        "records": _records_from_dataframe(returned_data),
    }


def telemetry_metric_values_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        status: Mapping[str, Any],
        metric_name: str,
        group_by: str = "metric_name",
        label_key: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        test_id: str | None = None,
        build: int | None = None,
        passed: bool | None = None,
        limit: int = DEFAULT_ANALYSIS_LIMIT
    ) -> dict[str, Any]:
    """Build grouped telemetry metric value summaries."""

    filtered_data, filters, errors = _filtered_telemetry_data(
        data,
        metric_name=metric_name,
        label_key=label_key,
        test_type=test_type,
        dut_type=dut_type,
        job=job,
        release=release,
        hosts=hosts,
        test_id=test_id,
        build=build,
        passed=passed,
    )
    records, summary, group_errors = _grouped_value_summary(
        filtered_data,
        group_by=group_by,
        limit=limit,
    )
    filters.update({"group_by": group_by, "limit": limit})
    errors.extend(group_errors)
    if errors:
        return _validation_error(errors, filters)

    return _analysis_payload(
        analysis="telemetry_metric_values",
        dataset=dataset,
        data=filtered_data,
        status=status,
        filters=filters,
        group_by=group_by,
        metric_name=metric_name,
        summary=summary,
        records=records,
        explanation=(
            f"Summarizes OpenMetrics samples for metric '{metric_name}' by "
            f"{group_by}."
        ),
    )


def telemetry_trend_summary_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        status: Mapping[str, Any],
        metric_name: str,
        group_by: str = "metric_name",
        label_key: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        test_id: str | None = None,
        passed: bool | None = None,
        order_by: str = "build",
        recent_count: int = 3,
        baseline_count: int = 3,
        limit: int = DEFAULT_ANALYSIS_LIMIT
    ) -> dict[str, Any]:
    """Build recent-vs-baseline telemetry metric trend summaries."""

    filtered_data, filters, errors = _filtered_telemetry_data(
        data,
        metric_name=metric_name,
        label_key=label_key,
        test_type=test_type,
        dut_type=dut_type,
        job=job,
        release=release,
        hosts=hosts,
        test_id=test_id,
        passed=passed,
    )
    records, summary, trend_errors = _trend_records(
        filtered_data,
        group_by=group_by,
        order_by=order_by,
        recent_count=recent_count,
        baseline_count=baseline_count,
        limit=limit,
    )
    filters.update({
        "group_by": group_by,
        "order_by": order_by,
        "recent_count": recent_count,
        "baseline_count": baseline_count,
        "limit": limit,
    })
    errors.extend(trend_errors)
    if errors:
        return _validation_error(errors, filters)

    return _analysis_payload(
        analysis="telemetry_trend_summary",
        dataset=dataset,
        data=filtered_data,
        status=status,
        filters=filters,
        group_by=group_by,
        metric_name=metric_name,
        summary=summary,
        records=records,
        explanation=(
            f"Compares recent telemetry samples for '{metric_name}' against "
            "the preceding baseline window."
        ),
    )


def telemetry_anomalies_payload(
        *,
        dataset: str,
        data: pd.DataFrame,
        status: Mapping[str, Any],
        metric_name: str,
        group_by: str = "metric_name",
        label_key: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        test_id: str | None = None,
        passed: bool | None = None,
        threshold: float = 2.0,
        limit: int = DEFAULT_ANALYSIS_LIMIT
    ) -> dict[str, Any]:
    """Build deterministic z-score telemetry anomaly records."""

    filtered_data, filters, errors = _filtered_telemetry_data(
        data,
        metric_name=metric_name,
        label_key=label_key,
        test_type=test_type,
        dut_type=dut_type,
        job=job,
        release=release,
        hosts=hosts,
        test_id=test_id,
        passed=passed,
    )
    records, summary, anomaly_errors = _anomaly_records(
        filtered_data,
        group_by=group_by,
        threshold=threshold,
        limit=limit,
    )
    filters.update({
        "group_by": group_by,
        "threshold": threshold,
        "limit": limit,
    })
    errors.extend(anomaly_errors)
    if errors:
        return _validation_error(errors, filters)

    return _analysis_payload(
        analysis="telemetry_anomalies",
        dataset=dataset,
        data=filtered_data,
        status=status,
        filters=filters,
        group_by=group_by,
        metric_name=metric_name,
        summary=summary,
        records=records,
        explanation=(
            f"Flags '{metric_name}' telemetry samples whose z-score is above "
            "the configured threshold."
        ),
    )


def _telemetry_values(value: Any) -> list[Any]:
    value = _python_value(value)
    if _is_missing_scalar(value):
        return []
    if isinstance(value, (list, tuple, set)):
        return [
            item for item in value
            if not _is_missing_scalar(item)
        ]
    return [value]


def _representative_positions(
        positions: list[int],
        *,
        max_source_rows: int
    ) -> list[int]:
    """Select evenly spaced source rows so the index spans the loaded window."""

    if len(positions) <= max_source_rows:
        return positions
    if max_source_rows == 1:
        return [positions[-1]]

    last_position = len(positions) - 1
    selected_indexes = {
        round(index * last_position / (max_source_rows - 1))
        for index in range(max_source_rows)
    }
    return [positions[index] for index in sorted(selected_indexes)]


def _encoded_bytes(value: Any) -> bytes:
    value = _python_value(value)
    if isinstance(value, bytes):
        return value
    return str(value).encode("utf-8")


def _parse_comment(
        line: str,
        *,
        help_by_metric: dict[str, str],
        type_by_metric: dict[str, str],
        unit_by_metric: dict[str, str]
    ) -> None:
    if line == "# EOF":
        return
    match = re.match(r"^#\s+(HELP|TYPE|UNIT)\s+(\S+)\s*(.*)$", line)
    if not match:
        return

    kind, metric_name, value = match.groups()
    if kind == "HELP":
        help_by_metric[metric_name] = value
    elif kind == "TYPE":
        type_by_metric[metric_name] = value
    elif kind == "UNIT":
        unit_by_metric[metric_name] = value


def _parse_sample_line(line: str) -> dict[str, Any]:
    token, rest = _split_metric_token(line)
    metric_name, labels = _parse_metric_token(token)
    values = rest.split()
    if not values:
        raise ValueError("missing metric value")

    value = _parse_openmetrics_float(values[0])
    timestamp = values[1] if len(values) > 1 else None
    return {
        "metric_name": metric_name,
        "labels": labels,
        "label_key": _label_key(labels),
        "value": value,
        "timestamp": timestamp,
    }


def _split_metric_token(line: str) -> tuple[str, str]:
    in_quotes = False
    escaped = False
    brace_depth = 0
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_quotes:
            escaped = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            continue
        if not in_quotes:
            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth = max(0, brace_depth - 1)
            elif char.isspace() and brace_depth == 0:
                return line[:index], line[index:].strip()
    raise ValueError("missing whitespace after metric name")


def _parse_metric_token(token: str) -> tuple[str, dict[str, str]]:
    if "{" not in token:
        return token, {}
    if not token.endswith("}"):
        raise ValueError("invalid metric label block")
    metric_name, label_text = token.split("{", 1)
    return metric_name, _parse_labels(label_text[:-1])


def _parse_labels(label_text: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    if not label_text:
        return labels
    for item in _split_label_items(label_text):
        if "=" not in item:
            raise ValueError("invalid label assignment")
        key, raw_value = item.split("=", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not key:
            raise ValueError("label name must not be empty")
        if not raw_value:
            raise ValueError("label value must not be empty")

        starts_quoted = raw_value.startswith('"')
        ends_quoted = raw_value.endswith('"')
        if starts_quoted != ends_quoted:
            raise ValueError("label value has mismatched quotes")
        if starts_quoted:
            labels[key] = _unescape_label_value(raw_value[1:-1])
        else:
            # CSIT telemetry uses an OpenMetrics-compatible text dialect with
            # unquoted label values. Preserve those values as strings.
            labels[key] = _unescape_label_value(raw_value)
    return labels


def _split_label_items(label_text: str) -> list[str]:
    items: list[str] = []
    start = 0
    in_quotes = False
    escaped = False
    for index, char in enumerate(label_text):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_quotes:
            escaped = True
            continue
        if char == '"':
            in_quotes = not in_quotes
            continue
        if char == "," and not in_quotes:
            items.append(label_text[start:index].strip())
            start = index + 1
    items.append(label_text[start:].strip())
    return [item for item in items if item]


def _unescape_label_value(value: str) -> str:
    return (
        value
        .replace(r"\n", "\n")
        .replace(r"\"", '"')
        .replace(r"\\", "\\")
    )


def _parse_openmetrics_float(value: str) -> float | None:
    normalized = value.strip()
    if normalized in {"NaN", "nan"}:
        return None
    if normalized in {"+Inf", "Inf", "+inf", "inf"}:
        return None
    if normalized in {"-Inf", "-inf"}:
        return None
    try:
        parsed = float(normalized)
    except ValueError as exc:
        raise ValueError(f"invalid metric value {value!r}") from exc
    if not math.isfinite(parsed):
        return None
    return parsed


def _metric_metadata(metric_name: str, metadata: Mapping[str, str]) -> str | None:
    if metric_name in metadata:
        return metadata[metric_name]
    for suffix in ("_total", "_bucket", "_sum", "_count", "_created"):
        if metric_name.endswith(suffix):
            family = metric_name.removesuffix(suffix)
            if family in metadata:
                return metadata[family]
    return None


def _source_context(row: pd.Series) -> dict[str, Any]:
    return {
        column: _json_safe_value(row.get(column))
        for column in TELEMETRY_CONTEXT_COLUMNS
    }


def _label_key(labels: Mapping[str, str]) -> str:
    if not labels:
        return ""
    return ",".join(
        f"{key}={labels[key]}"
        for key in sorted(labels)
    )


def _telemetry_status_entry(
        *,
        available: bool,
        sample_count: int,
        rows_with_telemetry: int,
        rows_with_errors: int,
        metric_names: list[str],
        source_row_count: int,
        indexed_row_count: int,
        truncated: bool,
        rows_with_decode_errors: int = 0,
        rows_with_parse_errors: int = 0,
        decode_error_count: int = 0,
        parse_error_count: int = 0,
        max_source_rows: int | None = None,
        max_samples: int | None = None,
        status: str | None = None,
        error: str | None = None
    ) -> dict[str, Any]:
    resolved_status = status
    if resolved_status is None:
        if not available:
            resolved_status = "not_available"
        elif truncated:
            resolved_status = "partial"
        else:
            resolved_status = "ready"

    return {
        "status": resolved_status,
        "available": available,
        "sample_count": sample_count,
        "source_row_count": source_row_count,
        "indexed_row_count": indexed_row_count,
        "rows_with_telemetry": rows_with_telemetry,
        "rows_with_errors": rows_with_errors,
        "rows_with_decode_errors": rows_with_decode_errors,
        "rows_with_parse_errors": rows_with_parse_errors,
        "decode_error_count": decode_error_count,
        "parse_error_count": parse_error_count,
        "metric_names": metric_names,
        "metric_name_count": len(metric_names),
        "truncated": truncated,
        "limits": {
            "max_source_rows": max_source_rows,
            "max_samples": max_samples,
        },
        "error": error,
    }


def _filtered_telemetry_data(
        data: pd.DataFrame,
        *,
        metric_name: str | None = None,
        label_key: str | None = None,
        test_type: str | None = None,
        dut_type: str | None = None,
        job: str | None = None,
        release: str | None = None,
        hosts: str | list[str] | None = None,
        test_id: str | None = None,
        build: int | None = None,
        passed: bool | None = None
    ) -> tuple[pd.DataFrame, dict[str, Any], list[dict[str, Any]]]:
    filters = {
        "metric_name": metric_name,
        "label_key": label_key,
        "test_type": test_type,
        "dut_type": dut_type,
        "job": job,
        "release": release,
        "hosts": hosts,
        "test_id": test_id,
        "build": build,
        "passed": passed,
    }
    errors: list[dict[str, Any]] = []
    filtered_data = data
    for column, value in (
            ("metric_name", metric_name),
            ("label_key", label_key),
            ("test_type", test_type),
            ("dut_type", dut_type),
            ("job", job),
            ("release", release),
            ("hosts", hosts),
            ("test_id", test_id),
        ):
        filtered_data = _filter_by_text(
            filtered_data,
            column=column,
            value=value,
            errors=errors,
        )
    parsed_build, build_error = _parse_int("build", build, default=None, minimum=0)
    if build_error is not None:
        errors.append(build_error)
    filters["build"] = parsed_build
    filtered_data = _filter_by_int(
        filtered_data,
        column="build",
        value=parsed_build,
        errors=errors,
    )
    parsed_passed, passed_error = _parse_bool(passed)
    if passed_error is not None:
        errors.append(passed_error)
    filters["passed"] = parsed_passed
    filtered_data = _filter_by_bool(
        filtered_data,
        column="passed",
        value=parsed_passed,
        errors=errors,
    )
    return filtered_data, filters, errors


def _filter_by_text(
        data: pd.DataFrame,
        *,
        column: str,
        value: Any,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if value is None:
        return data
    if column not in data.columns:
        errors.append(_missing_column_error(column))
        return data
    return data.loc[
        data[column].map(lambda item: _text_filter_matches(item, value))
    ]


def _text_filter_matches(actual: Any, expected: Any) -> bool:
    actual_value = _json_safe_value(actual)
    expected_value = _json_safe_value(expected)
    if isinstance(expected_value, list):
        return _normalized_text_key(actual_value) == _normalized_text_key(
            expected_value
        )
    if isinstance(actual_value, list):
        expected_text = str(expected_value)
        return (
            expected_text in {str(item) for item in actual_value} or
            _normalized_text_key(actual_value) == expected_text
        )
    return _normalized_text_key(actual_value) == _normalized_text_key(expected_value)


def _filter_by_int(
        data: pd.DataFrame,
        *,
        column: str,
        value: int | None,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if value is None:
        return data
    if column not in data.columns:
        errors.append(_missing_column_error(column))
        return data
    return data.loc[pd.to_numeric(data[column], errors="coerce") == value]


def _filter_by_bool(
        data: pd.DataFrame,
        *,
        column: str,
        value: bool | None,
        errors: list[dict[str, Any]]
    ) -> pd.DataFrame:
    if value is None:
        return data
    if column not in data.columns:
        errors.append(_missing_column_error(column))
        return data
    normalized = data[column].astype(str).str.strip().str.lower()
    expected_values = TRUE_VALUES if value else FALSE_VALUES
    return data.loc[normalized.isin(expected_values)]


def _grouped_value_summary(
        data: pd.DataFrame,
        *,
        group_by: str,
        limit: int
    ) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    errors = _validate_group_limit(data, group_by=group_by, limit=limit)
    if errors:
        return [], {}, errors

    records = []
    working_data = data.copy()
    working_data["_telemetry_group_key"] = working_data[group_by].map(
        _normalized_text_key
    )
    for group_key, group in working_data.groupby(
            "_telemetry_group_key",
            dropna=False,
        ):
        records.append({
            group_by: _json_safe_value(group_key),
            "group_key": _json_safe_value(group_key),
            "sample_count": len(group),
            "value": _numeric_summary(group["value"]),
            "metric_names": sorted(
                {
                    str(value) for value in group["metric_name"].dropna().unique()
                }
            ),
        })

    records = sorted(
        records,
        key=lambda item: (item["sample_count"], str(item["group_key"])),
        reverse=True,
    )[:limit]
    return records, {
        "group_count": len(records),
        "sample_count": len(data),
        "method": "grouped_numeric_summary",
    }, []


def _trend_records(
        data: pd.DataFrame,
        *,
        group_by: str,
        order_by: str,
        recent_count: int,
        baseline_count: int,
        limit: int
    ) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    errors = _validate_group_limit(data, group_by=group_by, limit=limit)
    for field, value in (
            ("recent_count", recent_count),
            ("baseline_count", baseline_count),
        ):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            errors.append({
                "field": field,
                "message": f"{field} must be a positive integer.",
                "value": value,
            })
    if order_by not in data.columns:
        errors.append(_missing_column_error(order_by, field="order_by"))
    if errors:
        return [], {}, errors

    required_count = recent_count + baseline_count
    records = []
    skipped_count = 0
    working_data = _ordered_data(data, order_by=order_by)
    working_data["_telemetry_group_key"] = working_data[group_by].map(
        _normalized_text_key
    )
    for group_key, group in working_data.groupby(
            "_telemetry_group_key",
            dropna=False,
        ):
        values = pd.to_numeric(group["value"], errors="coerce").dropna()
        if len(values) < required_count:
            skipped_count += 1
            continue
        recent = values.tail(recent_count)
        baseline = values.iloc[-required_count:-recent_count]
        baseline_summary = _numeric_summary(baseline)
        recent_summary = _numeric_summary(recent)
        baseline_mean = baseline_summary["mean"]
        recent_mean = recent_summary["mean"]
        if baseline_mean is None or recent_mean is None:
            skipped_count += 1
            continue
        delta = recent_mean - baseline_mean
        relative_delta = (
            (delta / abs(baseline_mean)) * 100
            if baseline_mean not in (None, 0)
            else None
        )
        records.append({
            group_by: _json_safe_value(group_key),
            "group_key": _json_safe_value(group_key),
            "baseline": baseline_summary,
            "recent": recent_summary,
            "mean_delta": _safe_number(delta),
            "relative_delta_percent": _safe_number(relative_delta),
            "direction": _trend_direction(delta),
        })

    records = sorted(
        records,
        key=lambda item: (
            abs(item["relative_delta_percent"] or 0),
            str(item["group_key"]),
        ),
        reverse=True,
    )[:limit]
    return records, {
        "group_count": len(records),
        "skipped_group_count": skipped_count,
        "recent_count": recent_count,
        "baseline_count": baseline_count,
        "order_by": order_by,
        "method": "recent_vs_baseline",
    }, []


def _anomaly_records(
        data: pd.DataFrame,
        *,
        group_by: str,
        threshold: float,
        limit: int
    ) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    errors = _validate_group_limit(data, group_by=group_by, limit=limit)
    if isinstance(threshold, bool):
        errors.append(_positive_float_error("threshold", threshold))
    else:
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            errors.append(_positive_float_error("threshold", threshold))
        else:
            if threshold <= 0:
                errors.append(_positive_float_error("threshold", threshold))
    if errors:
        return [], {}, errors

    records: list[dict[str, Any]] = []
    working_data = data.copy()
    working_data["_telemetry_value"] = pd.to_numeric(
        working_data["value"],
        errors="coerce",
    )
    working_data["_telemetry_group_key"] = working_data[group_by].map(
        _normalized_text_key
    )
    for group_key, group in working_data.groupby(
            "_telemetry_group_key",
            dropna=False,
        ):
        numeric_values = group["_telemetry_value"].dropna()
        if len(numeric_values) < 3:
            continue
        expected = numeric_values.mean()
        std = numeric_values.std()
        if pd.isna(std) or std == 0:
            continue
        for index, value in numeric_values.items():
            score = abs((value - expected) / std)
            if score < threshold:
                continue
            source_row = data.loc[index]
            records.append({
                group_by: _json_safe_value(group_key),
                "group_key": _json_safe_value(group_key),
                "metric_name": _json_safe_value(source_row.get("metric_name")),
                "label_key": _json_safe_value(source_row.get("label_key")),
                "actual": _safe_number(value),
                "expected": _safe_number(expected),
                "score": _safe_number(score),
                "threshold": threshold,
                "direction": "above" if value > expected else "below",
                "build": _json_safe_value(source_row.get("build")),
                "test_id": _json_safe_value(source_row.get("test_id")),
                "start_time": _json_safe_value(source_row.get("start_time")),
                "explanation": (
                    f"Telemetry value is {score:.2f} standard deviations "
                    "from the group mean."
                ),
            })

    records = sorted(
        records,
        key=lambda item: (item["score"], str(item["group_key"])),
        reverse=True,
    )
    return records[:limit], {
        "anomaly_count": len(records),
        "returned_count": min(len(records), limit),
        "threshold": threshold,
        "method": "z_score",
    }, []


def _validate_group_limit(
        data: pd.DataFrame,
        *,
        group_by: str,
        limit: int
    ) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if group_by not in data.columns:
        errors.append(_missing_column_error(group_by, field="group_by"))
    if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
        errors.append({
            "field": "limit",
            "message": "limit must be a positive integer.",
            "value": limit,
        })
    return errors


def _ordered_data(data: pd.DataFrame, *, order_by: str) -> pd.DataFrame:
    working_data = data.copy()
    if order_by in {"start_time", "timestamp"}:
        working_data["_telemetry_order"] = pd.to_datetime(
            working_data[order_by],
            errors="coerce",
            utc=True,
        )
    else:
        numeric_values = pd.to_numeric(working_data[order_by], errors="coerce")
        working_data["_telemetry_order"] = numeric_values
        if numeric_values.dropna().empty:
            working_data["_telemetry_order"] = working_data[order_by].map(
                _normalized_text_key
            )
    return (
        working_data
        .dropna(subset=["value", "_telemetry_order"])
        .sort_values(
            by="_telemetry_order",
            ascending=True,
            kind="mergesort",
        )
        .drop(columns=["_telemetry_order"])
    )


def _numeric_summary(values: pd.Series) -> dict[str, Any]:
    numeric_values = pd.to_numeric(values, errors="coerce").dropna()
    if numeric_values.empty:
        return {
            "count": 0,
            "min": None,
            "mean": None,
            "max": None,
            "median": None,
            "std": None,
            "p10": None,
            "p90": None,
        }
    return {
        "count": int(numeric_values.count()),
        "min": _safe_number(numeric_values.min()),
        "mean": _safe_number(numeric_values.mean()),
        "max": _safe_number(numeric_values.max()),
        "median": _safe_number(numeric_values.median()),
        "std": _safe_number(numeric_values.std()),
        "p10": _safe_number(numeric_values.quantile(0.10)),
        "p90": _safe_number(numeric_values.quantile(0.90)),
    }


def _analysis_payload(
        *,
        analysis: str,
        dataset: str,
        data: pd.DataFrame,
        status: Mapping[str, Any],
        filters: Mapping[str, Any],
        group_by: str,
        metric_name: str,
        summary: Mapping[str, Any],
        records: list[dict[str, Any]],
        explanation: str
    ) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "analysis": analysis,
        "dataset": dataset,
        "telemetry": True,
        "filters": _json_safe_value(dict(filters)),
        "metric_name": metric_name,
        "group_by": group_by,
        "row_count": len(data),
        "freshness": status.get("last_success_at"),
        "data_status": status.get("status"),
        "summary": _json_safe_value(dict(summary)),
        "records": _json_safe_value(records),
        "explanation": explanation,
    }


def _parse_int(
        field: str,
        value: Any,
        *,
        default: int | None,
        minimum: int,
        maximum: int | None = None
    ) -> tuple[int | None, dict[str, Any] | None]:
    if value is None:
        return default, None
    if isinstance(value, bool):
        return default, _int_error(field, value, minimum, maximum)
    if isinstance(value, float) and not value.is_integer():
        return default, _int_error(field, value, minimum, maximum)
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default, _int_error(field, value, minimum, maximum)
    if parsed < minimum or (maximum is not None and parsed > maximum):
        return default, _int_error(field, value, minimum, maximum)
    return parsed, None


def _parse_bool(value: Any) -> tuple[bool | None, dict[str, Any] | None]:
    if value is None:
        return None, None
    if isinstance(value, bool):
        return value, None
    normalized = str(value).strip().lower()
    if normalized in TRUE_VALUES:
        return True, None
    if normalized in FALSE_VALUES:
        return False, None
    return None, {
        "field": "passed",
        "message": "passed must be a boolean value.",
        "value": value,
    }


def _int_error(
        field: str,
        value: Any,
        minimum: int,
        maximum: int | None
    ) -> dict[str, Any]:
    expected = f"integer >= {minimum}"
    if maximum is not None:
        expected = f"integer between {minimum} and {maximum}"
    return {
        "field": field,
        "message": f"{field} must be an {expected}.",
        "value": value,
    }


def _positive_float_error(field: str, value: Any) -> dict[str, Any]:
    return {
        "field": field,
        "message": f"{field} must be greater than 0.",
        "value": value,
    }


def _missing_column_error(column: str, field: str | None = None) -> dict[str, Any]:
    field = field or column
    return {
        "field": field,
        "message": (
            f"{field} filter is unsupported because column '{column}' "
            "is not available in the telemetry dataset."
        ),
    }


def _validation_error(
        errors: list[dict[str, Any]],
        filters: Mapping[str, Any]
    ) -> dict[str, Any]:
    return {
        "error": "validation_error",
        "message": "Invalid MCP tool arguments.",
        "details": {
            "errors": errors,
        },
        "filters": _json_safe_value(dict(filters)),
    }


def _records_from_dataframe(data: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            str(column): _json_safe_value(value)
            for column, value in record.items()
        }
        for record in data.to_dict(orient="records")
    ]


def _normalized_text_key(value: Any) -> str | None:
    safe_value = _json_safe_value(value)
    if safe_value is None:
        return None
    if isinstance(safe_value, list):
        return ",".join(sorted(str(item) for item in safe_value))
    return str(safe_value)


def _trend_direction(delta: float) -> str:
    if delta > 0:
        return "up"
    if delta < 0:
        return "down"
    return "flat"


def _safe_number(value: Any) -> float | int | None:
    if value is None:
        return None
    try:
        if pd.isna(value) or not math.isfinite(float(value)):
            return None
    except (TypeError, ValueError):
        return None
    parsed = float(value)
    if parsed.is_integer():
        return int(parsed)
    return parsed


def _python_value(value: Any) -> Any:
    if hasattr(value, "as_py"):
        try:
            value = value.as_py()
        except (TypeError, ValueError):
            pass

    if not isinstance(value, (str, bytes)) and hasattr(value, "tolist"):
        try:
            listed = value.tolist()
        except (TypeError, ValueError):
            listed = value
        if listed is not value:
            return _python_value(listed)

    return value


def _is_missing_scalar(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, tuple, set, dict)):
        return False
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


def _json_safe_value(value: Any) -> Any:
    value = _python_value(value)
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, dict):
        return {
            str(key): _json_safe_value(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set)):
        return [_json_safe_value(item) for item in value]
    if not isinstance(value, (str, bytes)) and hasattr(value, "item"):
        try:
            item = value.item()
        except (TypeError, ValueError):
            item = value
        if item is not value:
            return _json_safe_value(item)
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value
