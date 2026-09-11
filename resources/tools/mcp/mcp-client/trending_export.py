"""Trending export formatting and serialization helpers."""

import csv
import io
import math
import re
from datetime import UTC, datetime
from typing import Any, Mapping, Sequence

import xlsxwriter


TRENDING_EXPORT_HEADERS = [
    "date",
    "job",
    "build",
    "dut type",
    "dut version",
    "hosts",
    "tg_type",
    "test_id",
    "throughput",
    "throughput unit",
    "bandwidth",
    "bandwidth unit",
    "latency",
    "latency unit",
]
_FILENAME_UNSAFE = re.compile(r"[^A-Za-z0-9 ._:-]+")


def default_trending_export_filename(now: datetime | None = None) -> str:
    """Return the timestamped default filename stem required by the UI."""

    current = now or datetime.now(tz=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return f"trending-{current.astimezone(UTC).strftime('%Y-%m-%d %H:%M:%S')}"


def sanitized_trending_export_filename(
        value: Any,
        default: str,
        extension: str,
    ) -> str:
    """Return a safe attachment filename while retaining timestamp punctuation."""

    raw = str(value or "").strip().replace("\\", "/").rsplit("/", 1)[-1]
    raw = raw.replace("\r", "").replace("\n", "").replace('"', "")
    raw = re.sub(r"\.(?:csv|xlsx)$", "", raw, flags=re.IGNORECASE)
    stem = _filename_component(raw) or _filename_component(default) or "trending"
    return f"{stem[:120]}.{extension}"


def trending_export_table(
        records: Sequence[Mapping[str, Any]],
    ) -> tuple[list[str], list[list[Any]]]:
    """Return Trending export rows in chronological order."""

    indexed_records = list(enumerate(records))
    indexed_records.sort(key=lambda item: _record_sort_key(item[1], item[0]))
    rows = [_trending_export_row(record) for _, record in indexed_records]
    return list(TRENDING_EXPORT_HEADERS), rows


def csv_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    """Serialize a Trending table as Excel-friendly UTF-8 CSV."""

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def xlsx_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    """Serialize a Trending table as a sortable XLSX workbook."""

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output,
        {
            "in_memory": True,
            "strings_to_formulas": False,
            "strings_to_urls": False,
        },
    )
    worksheet = workbook.add_worksheet("Trending")
    columns = [{"header": str(header)} for header in headers]
    if rows:
        worksheet.add_table(
            0,
            0,
            len(rows),
            len(headers) - 1,
            {
                "name": "TrendingTable",
                "columns": columns,
                "data": [list(row) for row in rows],
                "style": "Table Style Medium 2",
            },
        )
    else:
        header_format = workbook.add_format({
            "bold": True,
            "font_color": "#FFFFFF",
            "bg_color": "#2563A6",
        })
        worksheet.write_row(0, 0, headers, header_format)
        worksheet.autofilter(0, 0, 0, len(headers) - 1)
    worksheet.freeze_panes(1, 0)
    for index, header in enumerate(headers):
        values = [str(row[index]) for row in rows if index < len(row)]
        width = max([len(str(header)), *(len(value) for value in values)] or [12])
        worksheet.set_column(index, index, min(max(width + 2, 10), 48))
    workbook.close()
    return output.getvalue()


def _trending_export_row(record: Mapping[str, Any]) -> list[Any]:
    return [
        _formatted_date(record.get("start_time")),
        _normalized_text(record.get("job")) or "",
        _optional_integer(record.get("build")),
        (
            _normalized_text(record.get("dut_type"))
            or _normalized_text(record.get("dut"))
            or ""
        ),
        _normalized_text(record.get("dut_version")) or "",
        _formatted_hosts(record.get("hosts")),
        _normalized_text(record.get("tg_type")) or "",
        _normalized_text(record.get("test_id")) or "",
        _optional_number(record.get("throughput_value")),
        _normalized_text(record.get("throughput_unit")) or "",
        _optional_number(record.get("bandwidth_value")),
        _normalized_text(record.get("bandwidth_unit")) or "",
        _optional_number(record.get("latency_value")),
        _normalized_text(record.get("latency_unit")) or "",
    ]


def _record_sort_key(record: Mapping[str, Any], index: int) -> tuple[Any, ...]:
    parsed = _parsed_datetime(record.get("start_time"))
    return (parsed is None, parsed or datetime.max.replace(tzinfo=UTC), index)


def _parsed_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _formatted_date(value: Any) -> str:
    parsed = _parsed_datetime(value)
    return parsed.strftime("%Y-%m-%d %H:%M") if parsed is not None else ""


def _optional_integer(value: Any) -> int | str:
    if isinstance(value, bool) or value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(number) or not number.is_integer():
        return ""
    return int(number)


def _optional_number(value: Any) -> float | int | str:
    if isinstance(value, bool) or value is None:
        return ""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(number):
        return ""
    return int(number) if number.is_integer() else number


def _formatted_hosts(value: Any) -> str:
    values = value if isinstance(value, (list, tuple, set)) else [value]
    result = []
    for item in values:
        normalized = _normalized_text(item)
        if normalized is not None and normalized not in result:
            result.append(normalized)
    return ", ".join(result)


def _normalized_text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _filename_component(value: Any) -> str:
    normalized = str(value or "").strip()
    normalized = _FILENAME_UNSAFE.sub("-", normalized)
    return normalized.strip(" ._:-")
