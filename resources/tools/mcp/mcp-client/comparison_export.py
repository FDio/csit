"""Comparison summary/raw export formatting and serialization."""

import csv
import io
import math
import re
from datetime import UTC, datetime
from typing import Any, Mapping, Sequence

import xlsxwriter


RAW_HEADERS = [
    "job", "build", "dut_type", "dut_version", "tg_type", "hosts",
    "start_time", "passed", "test_id", "test_type", "release",
    "result_pdr_lower_rate_unit", "result_pdr_lower_rate_value",
    "result_ndr_lower_rate_unit", "result_ndr_lower_rate_value",
    "result_pdr_lower_bandwidth_unit", "result_pdr_lower_bandwidth_value",
    "result_ndr_lower_bandwidth_unit", "result_ndr_lower_bandwidth_value",
    "ref/cmp",
]
_RAW_KEYS = [*RAW_HEADERS[:-1], "ref_cmp"]
_FILENAME_UNSAFE = re.compile(r"[^A-Za-z0-9 ._:-]+")


def default_comparison_export_filename(view: str, now: datetime | None = None) -> str:
    current = now or datetime.now(tz=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    stamp = current.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")
    return f"comparison-{view}-{stamp}"


def sanitized_comparison_export_filename(
        value: Any, default: str, extension: str,
    ) -> str:
    raw = str(value or "").strip().replace("\\", "/").rsplit("/", 1)[-1]
    raw = raw.replace("\r", "").replace("\n", "").replace('"', "")
    raw = re.sub(r"\.(?:csv|xlsx)$", "", raw, flags=re.IGNORECASE)
    stem = _filename_component(raw) or _filename_component(default) or "comparison"
    return f"{stem[:120]}.{extension}"


def comparison_table_export(
        records: Sequence[Mapping[str, Any]],
        reference_label: str,
        compared_label: str,
    ) -> tuple[list[str], list[list[Any]]]:
    units = {str(record.get("unit") or "") for record in records}
    unit = units.pop() if len(units) == 1 else "mixed"
    suffix = f" [{unit}]" if unit else ""
    headers = [
        "Test Name",
        f"{reference_label}{suffix} Mean",
        f"{reference_label}{suffix} Stdev",
        f"{compared_label}{suffix} Mean",
        f"{compared_label}{suffix} Stdev",
        "Relative Change [%] Mean",
        "Relative Change [%] Stdev",
    ]
    ordered = sorted(records, key=lambda record: str(record.get("test_name") or "").lower())
    rows = [[
        _text(record.get("test_name")),
        _optional_number(record.get("reference_mean")),
        _optional_number(record.get("reference_stdev")),
        _optional_number(record.get("compared_mean")),
        _optional_number(record.get("compared_stdev")),
        _optional_number(record.get("relative_change_mean")),
        _optional_number(record.get("relative_change_stdev")),
    ] for record in ordered]
    return headers, rows


def comparison_data_export(
        records: Sequence[Mapping[str, Any]],
    ) -> tuple[list[str], list[list[Any]]]:
    ordered = sorted(records, key=lambda record: (
        0 if record.get("ref_cmp") == "reference" else 1,
        str(record.get("start_time") or ""),
        str(record.get("job") or ""),
        _sort_integer(record.get("build")),
        str(record.get("test_id") or ""),
    ))
    rows = []
    for record in ordered:
        row = []
        for key in _RAW_KEYS:
            value = record.get(key)
            if key == "hosts" and isinstance(value, (list, tuple)):
                value = ", ".join(str(item) for item in value)
            row.append(_cell(value))
        rows.append(row)
    return list(RAW_HEADERS), rows


def csv_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def xlsx_export_bytes(
        headers: Sequence[str], rows: Sequence[Sequence[Any]], *, view: str,
    ) -> bytes:
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {
        "in_memory": True,
        "strings_to_formulas": False,
        "strings_to_urls": False,
    })
    worksheet = workbook.add_worksheet("Comparison")
    columns = [{"header": str(header)} for header in headers]
    if rows:
        worksheet.add_table(0, 0, len(rows), len(headers) - 1, {
            "name": "ComparisonTable" if view == "table" else "ComparisonData",
            "columns": columns,
            "data": [list(row) for row in rows],
            "style": "Table Style Medium 2",
        })
    else:
        header = workbook.add_format({
            "bold": True, "font_color": "#FFFFFF", "bg_color": "#2563A6",
        })
        worksheet.write_row(0, 0, headers, header)
        worksheet.autofilter(0, 0, 0, len(headers) - 1)
    worksheet.freeze_panes(1, 1 if view == "table" else 0)
    for index, heading in enumerate(headers):
        values = [str(row[index]) for row in rows if index < len(row)]
        width = max([len(str(heading)), *(len(value) for value in values)] or [12])
        worksheet.set_column(index, index, min(max(width + 2, 10), 52))
    workbook.close()
    return output.getvalue()


def _cell(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return value
    number = _number(value)
    if number is not None and not isinstance(value, str):
        return int(number) if number.is_integer() else number
    return _text(value)


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


def _sort_integer(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _filename_component(value: Any) -> str:
    normalized = _FILENAME_UNSAFE.sub("-", str(value or "").strip())
    return normalized.strip(" ._:-")
