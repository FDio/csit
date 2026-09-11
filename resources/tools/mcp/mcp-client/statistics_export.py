"""Statistics export formatting and serialization helpers."""

import csv
import io
import math
import re
from datetime import UTC, datetime
from typing import Any, Mapping, Sequence

import xlsxwriter


MISSING_TEST_ID = "[test_id unavailable]"
TEST_ID_TEST_TYPES = {"hoststack", "mrr", "ndrpdr", "soak"}
TEST_ID_DRIVERS = (
    ("af", "xdp"),
    ("vfio", "pci"),
    ("avf",),
    ("rdma",),
    ("dpdk",),
    ("mlx5",),
    ("octeon",),
)
TEST_ID_NIC_PATTERN = re.compile(r"\d+(?:ge|gbe)[a-z0-9_]*", re.IGNORECASE)
TEST_ID_CORE_PATTERN = re.compile(r"\d+c", re.IGNORECASE)
TEST_ID_FRAME_PATTERN = re.compile(r"(?:\d+b|imix|jumbo)", re.IGNORECASE)
_FILENAME_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def canonical_failed_test_name(test_id: str) -> str:
    """Return a CSIT test name as NIC-[driver]-frame-core-area-type."""

    original = test_id.strip()
    segments = [segment for segment in original.lower().split(".") if segment]
    if not segments:
        return original

    nic = None
    nic_segment_index = None
    nic_token_index = None
    nic_segment_tokens: list[str] = []
    for segment_index, segment in enumerate(segments):
        segment_tokens = [token for token in segment.split("-") if token]
        for token_index, token in enumerate(segment_tokens):
            match = TEST_ID_NIC_PATTERN.search(token)
            if match:
                nic = match.group(0).lower()
                nic_segment_index = segment_index
                nic_token_index = token_index
                nic_segment_tokens = segment_tokens
                break
        if nic is not None:
            break
    if nic is None or nic_segment_index is None or nic_token_index is None:
        return original

    driver_start = nic_token_index + 1
    driver_tokens = next(
        (
            list(candidate)
            for candidate in TEST_ID_DRIVERS
            if nic_segment_tokens[driver_start:driver_start + len(candidate)]
            == list(candidate)
        ),
        [],
    )

    uses_dotted_case = nic_segment_index < len(segments) - 1
    case_tokens = (
        [token for token in segments[-1].split("-") if token]
        if uses_dotted_case
        else nic_segment_tokens
    )
    test_type_index = next(
        (
            index
            for index in range(len(case_tokens) - 1, -1, -1)
            if case_tokens[index] in TEST_ID_TEST_TYPES
        ),
        None,
    )
    if test_type_index is None:
        test_type = next(
            (
                segment
                for segment in reversed(segments[:nic_segment_index])
                if segment in TEST_ID_TEST_TYPES
            ),
            None,
        )
        if test_type is None:
            return original
        test_type_index = len(case_tokens)
    else:
        test_type = case_tokens[test_type_index]

    core_index = next(
        (
            index
            for index in range(test_type_index)
            if TEST_ID_CORE_PATTERN.fullmatch(case_tokens[index])
        ),
        None,
    )
    frame_index = next(
        (
            index
            for index in range(test_type_index)
            if TEST_ID_FRAME_PATTERN.fullmatch(case_tokens[index])
        ),
        None,
    )
    if core_index is None or frame_index is None:
        return original

    area_start = 0 if uses_dotted_case else driver_start + len(driver_tokens)
    area = [
        token
        for index, token in enumerate(case_tokens[:test_type_index])
        if index >= area_start and index not in {core_index, frame_index}
    ]
    if not area:
        return original

    components = [nic]
    if driver_tokens:
        components.append("-".join(driver_tokens))
    components.extend(
        [
            case_tokens[frame_index],
            case_tokens[core_index],
            *area,
            test_type,
        ]
    )
    return "-".join(components)


def default_export_filename(filters: Mapping[str, Any]) -> str:
    """Return the default filename stem for selected statistics filters."""

    components = ["stats"]
    for field in ("dut", "test_type", "cadence", "testbed"):
        components.append(_filename_component(filters.get(field)) or "unknown")
    return "-".join(components)


def sanitized_export_filename(value: Any, default: str, extension: str) -> str:
    """Return a safe ASCII attachment filename with the requested extension."""

    raw = str(value or "").strip().replace("\\", "/").rsplit("/", 1)[-1]
    raw = re.sub(r"\.(?:csv|xlsx)$", "", raw, flags=re.IGNORECASE)
    stem = _filename_component(raw) or _filename_component(default) or "statistics"
    return f"{stem[:120]}.{extension}"


def statistics_export_table(
        records: Sequence[Mapping[str, Any]],
        *,
        dut: str,
        failed_tests: Mapping[tuple[str, int], Sequence[str]],
    ) -> tuple[list[str], list[list[Any]]]:
    """Return export headers and normalized rows sorted oldest first."""

    headers = [
        "build",
        "date",
        "duration",
        "passed",
        "failed",
        f"{dut or 'dut'}-ver",
        "csit-ref",
        "hosts",
        "Failed tests",
    ]
    indexed_records = list(enumerate(records))
    indexed_records.sort(key=lambda item: _record_sort_key(item[1], item[0]))
    rows = [
        _statistics_export_row(record, failed_tests=failed_tests)
        for _, record in indexed_records
    ]
    return headers, rows


def csv_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    """Serialize one statistics table as Excel-friendly UTF-8 CSV."""

    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")


def xlsx_export_bytes(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> bytes:
    """Serialize one statistics table as a sortable XLSX workbook."""

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(
        output,
        {
            "in_memory": True,
            "strings_to_formulas": False,
            "strings_to_urls": False,
        },
    )
    worksheet = workbook.add_worksheet("Statistics")
    columns = [{"header": str(header)} for header in headers]
    if rows:
        worksheet.add_table(
            0,
            0,
            len(rows),
            len(headers) - 1,
            {
                "name": "StatisticsTable",
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


def _statistics_export_row(
        record: Mapping[str, Any],
        *,
        failed_tests: Mapping[tuple[str, int], Sequence[str]],
    ) -> list[Any]:
    build = _optional_integer(record.get("build"))
    job = _normalized_text(record.get("job"))
    run_key = (job, build) if job is not None and build is not None else None
    counts_available = bool(record.get("counts_available"))
    return [
        build if build is not None else "",
        _formatted_date(record.get("start_time")),
        _formatted_duration(record.get("duration")),
        _optional_count(record.get("passed_count")) if counts_available else "",
        _optional_count(record.get("failed_count")) if counts_available else "",
        _normalized_text(record.get("dut_version")) or "",
        f"{job}/{build}" if job is not None and build is not None else "",
        _formatted_hosts(record.get("hosts")),
        ", ".join(failed_tests.get(run_key, ())) if run_key is not None else "",
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


def _formatted_duration(value: Any) -> str:
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(seconds) or seconds < 0:
        return ""
    total_minutes = int(math.floor((seconds / 60.0) + 0.5))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def _optional_count(value: Any) -> int | str:
    number = _optional_integer(value)
    return number if number is not None else ""


def _optional_integer(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or not number.is_integer():
        return None
    return int(number)


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
    normalized = _FILENAME_UNSAFE.sub("-", normalized).strip("._-")
    return normalized
