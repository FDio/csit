"""Coverage export formatting and serialization helpers."""

import csv
import io
import math
import re
from datetime import UTC, datetime
from typing import Any, Mapping, Sequence

import xlsxwriter


COVERAGE_EXPORT_HEADERS = [
    "Suite",
    "Test Name",
    "Throughput_Unit",
    "Throughput_NDR",
    "Throughput_NDR_Gbps",
    "Throughput_PDR",
    "Throughput_PDR_Gbps",
    *[
        f"Latency {direction.title()} [us]_{pdr}% PDR_P{percentile}"
        for direction in ("forward", "reverse")
        for pdr in (10, 50, 90)
        for percentile in (50, 90, 99)
    ],
]
_LATENCY_KEYS = [
    f"latency_{direction}_pdr_{pdr}_p{percentile}"
    for direction in ("forward", "reverse")
    for pdr in (10, 50, 90)
    for percentile in (50, 90, 99)
]
_FILENAME_UNSAFE = re.compile(r"[^A-Za-z0-9 ._:-]+")
_NATURAL_PART = re.compile(r"(\d+)")


def default_coverage_export_filename(now: datetime | None = None) -> str:
    current = now or datetime.now(tz=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return f"coverage-{current.astimezone(UTC).strftime('%Y-%m-%d %H:%M:%S')}"


def sanitized_coverage_export_filename(
        value: Any,
        default: str,
        extension: str,
    ) -> str:
    raw = str(value or "").strip().replace("\\", "/").rsplit("/", 1)[-1]
    raw = raw.replace("\r", "").replace("\n", "").replace('"', "")
    raw = re.sub(r"\.(?:csv|xlsx)$", "", raw, flags=re.IGNORECASE)
    stem = _filename_component(raw) or _filename_component(default) or "coverage"
    return f"{stem[:120]}.{extension}"


def coverage_export_table(
        records: Sequence[Mapping[str, Any]],
    ) -> tuple[list[str], list[list[Any]]]:
    ordered = sorted(
        enumerate(records),
        key=lambda item: (
            _natural_key(item[1].get("suite")),
            _natural_key(item[1].get("test_name")),
            str(item[1].get("job") or ""),
            _optional_integer(item[1].get("build")),
            item[0],
        ),
    )
    rows = [_export_row(record) for _, record in ordered]
    return list(COVERAGE_EXPORT_HEADERS), rows


def csv_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def xlsx_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output,
        {
            "in_memory": True,
            "strings_to_formulas": False,
            "strings_to_urls": False,
        },
    )
    worksheet = workbook.add_worksheet("Coverage")
    columns = [{"header": str(header)} for header in headers]
    if rows:
        worksheet.add_table(
            0,
            0,
            len(rows),
            len(headers) - 1,
            {
                "name": "CoverageTable",
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
        worksheet.set_column(index, index, min(max(width + 2, 10), 44))
    workbook.close()
    return output.getvalue()


def _export_row(record: Mapping[str, Any]) -> list[Any]:
    return [
        _text(record.get("suite")),
        _text(record.get("test_name")),
        _text(record.get("throughput_unit")),
        _optional_number(record.get("throughput_ndr")),
        _optional_number(record.get("throughput_ndr_gbps")),
        _optional_number(record.get("throughput_pdr")),
        _optional_number(record.get("throughput_pdr_gbps")),
        *[_optional_integer(record.get(key)) for key in _LATENCY_KEYS],
    ]


def _optional_integer(value: Any) -> int | str:
    number = _number(value)
    if number is None or not number.is_integer():
        return ""
    return int(number)


def _optional_number(value: Any) -> float | int | str:
    number = _number(value)
    if number is None:
        return ""
    return int(number) if number.is_integer() else number


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _natural_key(value: Any) -> tuple[Any, ...]:
    return tuple(
        int(part) if part.isdigit() else part.lower()
        for part in _NATURAL_PART.split(_text(value))
    )


def _filename_component(value: Any) -> str:
    normalized = str(value or "").strip()
    normalized = _FILENAME_UNSAFE.sub("-", normalized)
    return normalized.strip(" ._:-")
