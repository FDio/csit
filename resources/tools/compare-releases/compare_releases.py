#!/usr/bin/env python3
"""Compare test data from two release workbooks.

The script reads two YYMM.xlsx inputs, downloads/caches Robot Framework
report.html.gz files listed in their Log columns, aggregates test metrics by
test identity, and writes a filterable Excel comparison workbook.
"""

from __future__ import annotations

import argparse
import ast
import base64
import gzip
import hashlib
import json
import math
import re
import sys
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ImportError as exc:  # pragma: no cover - exercised only without dependency.
    raise SystemExit("compare_releases.py requires openpyxl. Install it and retry.") from exc


CACHE_DIR_DEFAULT = ".cache/failed-test-logs"
DEFAULT_TIMEOUT = 60
DEFAULT_RETRIES = 2
STATUSES = ["Fail", "Pass", "Skip", "Not Run"]

OUTPUT_COLUMNS = [
    "DUT",
    "Node",
    "Job type",
    "Test type",
    "Status",
    "NIC",
    "Driver",
    "Framesize",
    "Number of cores",
    "Test area",
    "Mean current",
    "Stdev current",
    "Mean NDR current",
    "Stdev NDR current",
    "Mean PDR current",
    "Stdev PDR current",
    "Mean previous",
    "Stdev previous",
    "Mean NDR previous",
    "Stdev NDR previous",
    "Mean PDR previous",
    "Stdev PDR previous",
    "Diff",
    "Rel Diff",
    "Diff NDR",
    "Rel Diff NDR",
    "Diff PDR",
    "Rel Diff PDR",
]

IDENTITY_FIELDS = (
    "dut",
    "node",
    "job_type",
    "test_type",
    "nic",
    "driver",
    "framesize",
    "cores",
    "test_area",
)

ProgressLogger = Optional[Callable[[str], None]]


class CompareReleasesError(Exception):
    """Base error for predictable command-line failures."""


class InputError(CompareReleasesError):
    """Raised for invalid workbook input."""


class ReportParseError(CompareReleasesError):
    """Raised when a Robot Framework report cannot be decoded."""


class LogFetchError(CompareReleasesError):
    """Raised when a log cannot be downloaded or read from cache."""


@dataclass(frozen=True)
class ReleaseInfo:
    label: str
    path: Path
    year: int
    month: int


@dataclass(frozen=True)
class WorkbookRow:
    dut: str
    node: str
    job_type: str
    test_type: str
    testbed: str
    log_url: str
    source_row: int


@dataclass(frozen=True)
class RobotTest:
    name: str
    tags: Tuple[str, ...]
    status: str
    message: str


@dataclass(frozen=True)
class TagFields:
    nic: str = ""
    driver: str = ""
    framesize: str = ""
    cores: str = ""
    test_area: str = ""


@dataclass(frozen=True)
class TestIdentity:
    dut: str
    node: str
    job_type: str
    test_type: str
    nic: str
    driver: str
    framesize: str
    cores: str
    test_area: str

    def sort_key(self) -> Tuple[str, ...]:
        return tuple(getattr(self, field_name) for field_name in IDENTITY_FIELDS)


@dataclass(frozen=True)
class MetricValues:
    standard: Optional[float] = None
    ndr: Optional[float] = None
    pdr: Optional[float] = None


@dataclass(frozen=True)
class MetricSummary:
    mean: Optional[float] = None
    stdev: Optional[float] = None


@dataclass
class TestAggregate:
    identity: TestIdentity
    testbed: str = ""
    log_urls: List[str] = field(default_factory=list)
    standard_values: List[float] = field(default_factory=list)
    ndr_values: List[float] = field(default_factory=list)
    pdr_values: List[float] = field(default_factory=list)
    pass_count: int = 0
    fail_count: int = 0

    def add(self, row: WorkbookRow, status: str, metrics: MetricValues) -> None:
        if row.testbed and not self.testbed:
            self.testbed = row.testbed
        if row.log_url and row.log_url not in self.log_urls:
            self.log_urls.append(row.log_url)
        if status == "Pass":
            self.pass_count += 1
            if metrics.standard is not None:
                self.standard_values.append(metrics.standard)
            if metrics.ndr is not None:
                self.ndr_values.append(metrics.ndr)
            if metrics.pdr is not None:
                self.pdr_values.append(metrics.pdr)
        elif status:
            self.fail_count += 1

    @property
    def status(self) -> str:
        if self.fail_count:
            return "Fail"
        if self.pass_count:
            return "Pass"
        return ""


def parse_release_path(path: Path) -> ReleaseInfo:
    match = re.fullmatch(r"(\d{2})(\d{2})\.xlsx", path.name)
    if not match:
        raise InputError(f"Workbook name must use YYMM.xlsx format: {path}")
    year = 2000 + int(match.group(1))
    month = int(match.group(2))
    if month < 1 or month > 12:
        raise InputError(f"Workbook month must be between 01 and 12: {path}")
    return ReleaseInfo(path.stem, path, year, month)


def determine_releases(paths: Sequence[Path]) -> Tuple[ReleaseInfo, ReleaseInfo]:
    if len(paths) != 2:
        raise InputError("Exactly two input workbooks are required.")
    releases = sorted((parse_release_path(path) for path in paths), key=lambda item: (item.year, item.month))
    if releases[0].label == releases[1].label:
        raise InputError("The two input workbooks must describe different releases.")
    return releases[0], releases[1]


def clean_cell(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_headers(header: Sequence[object]) -> Dict[str, List[int]]:
    mapping: Dict[str, List[int]] = {}
    for index, value in enumerate(header):
        name = clean_cell(value)
        if name:
            mapping.setdefault(name, []).append(index)
    return mapping


def first_cell(row: Sequence[object], header_map: Mapping[str, Sequence[int]], name: str) -> str:
    for index in header_map.get(name, []):
        if index < len(row):
            value = clean_cell(row[index])
            if value:
                return value
    return ""


def read_workbook_rows(path: Path) -> List[WorkbookRow]:
    if not path.exists():
        raise InputError(f"Input workbook does not exist: {path}")
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook.worksheets[0]
        iterator = worksheet.iter_rows(values_only=True)
        header = next(iterator, None)
        if header is None:
            raise InputError(f"Input workbook is empty: {path}")
        header_map = normalize_headers(header)
        required = ["DUT", "Node", "Job type", "Test type", "Log"]
        missing = [name for name in required if name not in header_map]
        if missing:
            raise InputError(f"{path} is missing required column(s): {', '.join(missing)}")

        rows: List[WorkbookRow] = []
        for excel_row_number, row in enumerate(iterator, start=2):
            if not any(cell is not None for cell in row):
                continue
            rows.append(
                WorkbookRow(
                    dut=first_cell(row, header_map, "DUT"),
                    node=first_cell(row, header_map, "Node"),
                    job_type=first_cell(row, header_map, "Job type").lower(),
                    test_type=first_cell(row, header_map, "Test type").lower(),
                    testbed=first_cell(row, header_map, "Testbed"),
                    log_url=first_cell(row, header_map, "Log"),
                    source_row=excel_row_number,
                )
            )
        return rows
    finally:
        workbook.close()


def report_url(log_url: str) -> str:
    stripped = log_url.strip()
    if stripped.endswith("/report.html.gz"):
        return stripped
    return stripped.rstrip("/") + "/report.html.gz"


def cache_file_for_url(cache_dir: Path, url: str) -> Path:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    readable_parts = parts[-3:] if len(parts) >= 3 else parts
    readable = "_".join(readable_parts).replace("report.html.gz", "report")
    readable = re.sub(r"[^A-Za-z0-9_.-]+", "_", readable).strip("._") or "log"
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    return cache_dir / f"{readable}-{digest}.html.gz"


def download_report(
    log_url: str,
    cache_dir: Path,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    offline: bool = False,
) -> bytes:
    url = report_url(log_url)
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_file_for_url(cache_dir, url)
    if cache_path.exists():
        return cache_path.read_bytes()
    if offline:
        raise LogFetchError(f"Missing cached log for offline mode: {url}")

    last_error: Optional[BaseException] = None
    for attempt in range(retries + 1):
        try:
            request = Request(url, headers={"User-Agent": "compare-releases/1.0"})
            with urlopen(request, timeout=timeout) as response:
                data = response.read()
            cache_path.write_bytes(data)
            return data
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(min(2**attempt, 5))
    raise LogFetchError(f"Could not download {url}: {last_error}")


def decode_report_bytes(data: bytes) -> str:
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    return data.decode("utf-8", errors="replace")


def emit_progress(logger: ProgressLogger, message: str) -> None:
    if logger is not None:
        logger(message)


def extract_array_literal(text: str, start: int) -> Tuple[str, int]:
    index = text.find("[", start)
    if index == -1:
        raise ReportParseError("Could not find JavaScript array literal.")
    depth = 0
    quote_char = ""
    escape = False
    for position in range(index, len(text)):
        char = text[position]
        if quote_char:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote_char:
                quote_char = ""
            continue
        if char in {"'", '"'}:
            quote_char = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[index : position + 1], position + 1
    raise ReportParseError("Unterminated JavaScript array literal.")


def replace_js_references(literal: str, replacements: Mapping[str, str]) -> str:
    if not replacements:
        return literal
    result: List[str] = []
    position = 0
    quote_char = ""
    escape = False
    keys = sorted(replacements, key=len, reverse=True)
    while position < len(literal):
        char = literal[position]
        if quote_char:
            result.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote_char:
                quote_char = ""
            position += 1
            continue
        if char in {"'", '"'}:
            quote_char = char
            result.append(char)
            position += 1
            continue
        matched_key = next((key for key in keys if literal.startswith(key, position)), None)
        if matched_key:
            result.append(replacements[matched_key])
            position += len(matched_key)
            continue
        result.append(char)
        position += 1
    return "".join(result)


def parse_js_array_literal(literal: str, label: str) -> list:
    try:
        return json.loads(literal)
    except json.JSONDecodeError as json_error:
        python_literal = re.sub(r"\bnull\b", "None", literal)
        python_literal = re.sub(r"\btrue\b", "True", python_literal)
        python_literal = re.sub(r"\bfalse\b", "False", python_literal)
        python_literal = re.sub(r"\bundefined\b", "None", python_literal)
        python_literal = re.sub(r"\bNaN\b", "None", python_literal)
        try:
            parsed = ast.literal_eval(python_literal)
        except (SyntaxError, ValueError) as ast_error:
            start = max(json_error.pos - 50, 0)
            end = min(json_error.pos + 50, len(literal))
            snippet = literal[start:end].replace("\n", "\\n")
            raise ReportParseError(
                f"Could not parse Robot {label} JavaScript array near character "
                f"{json_error.pos}: {snippet}"
            ) from ast_error
        if not isinstance(parsed, list):
            raise ReportParseError(f"Robot {label} payload is not an array.")
        return parsed


def extract_window_array_assignments(report_html: str, variable_pattern: str) -> Dict[str, list]:
    assignments: Dict[str, list] = {}
    pattern = re.compile(rf"({variable_pattern})\s*=")
    for match in pattern.finditer(report_html):
        variable_name = match.group(1)
        literal, _ = extract_array_literal(report_html, match.end())
        replacements = {name: json.dumps(value) for name, value in assignments.items()}
        resolved_literal = replace_js_references(literal, replacements)
        assignments[variable_name] = parse_js_array_literal(resolved_literal, variable_name)
    return assignments


def extract_robot_payload(report_html: str) -> Tuple[list, List[str]]:
    split_parts = extract_window_array_assignments(report_html, r"window\.sPart\d+")
    split_replacements = {name: json.dumps(value) for name, value in split_parts.items()}

    suite_match = re.search(r'window\.output\["suite"\]\s*=', report_html)
    if not suite_match:
        raise ReportParseError('Robot report is missing window.output["suite"].')
    suite_literal, _ = extract_array_literal(report_html, suite_match.end())
    suite_literal = replace_js_references(suite_literal, split_replacements)
    suite = parse_js_array_literal(suite_literal, "suite")

    strings: List[str] = []
    for match in re.finditer(r'window\.output\["strings"\]\.concat\s*\(', report_html):
        strings_literal, _ = extract_array_literal(report_html, match.end())
        strings.extend(parse_js_array_literal(strings_literal, "strings"))
    if not strings:
        raise ReportParseError('Robot report is missing window.output["strings"].')
    return suite, strings


def robot_string(strings: Sequence[str], index: Optional[int]) -> str:
    if index is None:
        return ""
    if not isinstance(index, int) or index < 0 or index >= len(strings):
        return ""
    text = strings[index]
    if not text:
        return ""
    if text.startswith("*"):
        return text[1:]
    # Robot may store long strings compressed. Most fields used here are plain
    # "*"-prefixed strings, but this fallback keeps diagnostics readable.
    try:
        return zlib.decompress(base64.b64decode(text)).decode("utf-8", errors="replace")
    except Exception:
        return text


def decode_status(status: Sequence[object], strings: Sequence[str]) -> Tuple[str, str]:
    if not status:
        return "", ""
    status_index = int(status[0])
    status_text = STATUSES[status_index] if 0 <= status_index < len(STATUSES) else ""
    message = robot_string(strings, int(status[3])) if len(status) >= 4 else ""
    return status_text, message


def collect_robot_tests(report_html: str) -> List[RobotTest]:
    suite, strings = extract_robot_payload(report_html)
    tests: List[RobotTest] = []

    def visit_suite(element: Sequence[object]) -> None:
        for child_suite in element[6]:
            visit_suite(child_suite)
        for test in element[7]:
            status, message = decode_status(test[4], strings)
            tags = tuple(robot_string(strings, int(tag_index)) for tag_index in test[3])
            tests.append(
                RobotTest(
                    name=robot_string(strings, int(test[0])),
                    tags=tags,
                    status=status,
                    message=message,
                )
            )

    visit_suite(suite)
    return tests


def quartile_inc(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ValueError("quartile_inc requires at least one value")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def exclude_outliers(values: Iterable[float]) -> List[float]:
    numbers = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if len(numbers) <= 1:
        return numbers
    q1 = quartile_inc(numbers, 0.25)
    q3 = quartile_inc(numbers, 0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return [value for value in numbers if lower <= value <= upper]


def mean(values: Sequence[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def population_stdev(values: Sequence[float]) -> Optional[float]:
    if len(values) <= 1:
        return None
    average = mean(values)
    if average is None:
        return None
    return math.sqrt(sum((value - average) ** 2 for value in values) / len(values))


def summarize(values: Iterable[float]) -> MetricSummary:
    cleaned = exclude_outliers(values)
    return MetricSummary(mean(cleaned), population_stdev(cleaned))


def parse_number_list(literal: str) -> List[float]:
    parsed = ast.literal_eval(literal)
    if not isinstance(parsed, (list, tuple)):
        raise ValueError("result literal is not a list")
    return [float(value) for value in parsed]


def list_mean_from_message(message: str, pattern: re.Pattern[str]) -> Optional[float]:
    match = pattern.search(message)
    if not match:
        return None
    values = exclude_outliers(parse_number_list(match.group(1)))
    return mean(values)


MRR_PATTERN = re.compile(r"Maximum Receive Rate trial results .*?:\s*(\[[^\]]+\])", re.IGNORECASE | re.DOTALL)
GSO_PATTERN = re.compile(r"iPerf3 trial results .*?:\s*(\[[^\]]+\])", re.IGNORECASE | re.DOTALL)
NDR_PATTERN = re.compile(r"\bNDR:\s*([0-9.+\-eE]+)\s*pps", re.IGNORECASE)
PDR_PATTERN = re.compile(r"\bPDR:\s*([0-9.+\-eE]+)\s*pps", re.IGNORECASE)
TRANSFER_PATTERN = re.compile(r"Transfer Rate:\s*([0-9.+\-eE]+)\s*\[Kbytes/sec\]", re.IGNORECASE)
SOAK_PATTERN = re.compile(r"PLRsearch lower bound:\s*([0-9.+\-eE]+)\s*(?:pps|cps)\b", re.IGNORECASE)


def parse_test_result(test_type: str, message: str) -> MetricValues:
    if test_type == "mrr":
        return MetricValues(standard=list_mean_from_message(message, MRR_PATTERN))
    if test_type == "gso":
        return MetricValues(standard=list_mean_from_message(message, GSO_PATTERN))
    if test_type == "ndrpdr":
        ndr = NDR_PATTERN.search(message)
        pdr = PDR_PATTERN.search(message)
        return MetricValues(
            ndr=float(ndr.group(1)) if ndr else None,
            pdr=float(pdr.group(1)) if pdr else None,
        )
    if test_type == "hoststack":
        transfer = TRANSFER_PATTERN.search(message)
        return MetricValues(standard=float(transfer.group(1)) if transfer else None)
    if test_type == "soak":
        soak = SOAK_PATTERN.search(message)
        return MetricValues(standard=float(soak.group(1)) if soak else None)
    return MetricValues()


def is_framesize_tag(tag: str) -> bool:
    return bool(re.fullmatch(r"(?:\d+B|IMIX)", tag, re.IGNORECASE))


def is_core_tag(tag: str) -> bool:
    return bool(re.fullmatch(r"\d+C", tag, re.IGNORECASE))


def canonical_framesize(tag: str) -> str:
    return tag.upper()


def canonical_core_count(tag: str) -> str:
    return tag.lower()


def fallback_area_from_name(name: str, framesize: str, cores: str, test_type: str) -> str:
    lower_name = name.lower()
    if framesize and cores:
        prefix = f"{framesize.lower()}-{cores.lower()}-"
        suffix = f"-{test_type.lower()}"
        start = lower_name.find(prefix)
        if start != -1 and lower_name.endswith(suffix):
            return lower_name[start + len(prefix) : -len(suffix)]
    match = re.search(r"(?:\d+b|imix)-\d+c-(?P<area>.+?)-" + re.escape(test_type.lower()) + r"$", lower_name)
    return match.group("area") if match else ""


def looks_like_test_area(tag: str, test_name: str) -> bool:
    if tag.startswith(("NIC_", "DRV_")) or is_framesize_tag(tag) or is_core_tag(tag):
        return False
    if re.fullmatch(r"\d+T\d+C", tag, re.IGNORECASE):
        return False
    upper = tag.upper()
    excluded_prefixes = ("RXQ_", "TXQ_", "FIB_")
    excluded_exact = {
        "BASE",
        "ETH",
        "GSO",
        "HOSTSTACK",
        "HW_ENV",
        "IP4BASE",
        "IP4FWD",
        "IP4_RND",
        "IP6BASE",
        "IP6FWD",
        "IP6_RND",
        "MRR",
        "MTHREAD",
        "NDRPDR",
        "PERFTEST",
        "SCALE",
        "SOAK",
        "2_NODE_SINGLE_LINK_TOPO",
    }
    if upper in excluded_exact or upper.startswith(excluded_prefixes):
        return False
    lower = tag.lower()
    return ("-" in lower or any(char.islower() for char in tag)) and lower in test_name.lower()


def extract_tag_fields(test_name: str, tags: Sequence[str], test_type: str) -> TagFields:
    nic = ""
    driver = ""
    framesize = ""
    cores = ""
    area = ""
    for tag in tags:
        if tag.startswith("NIC_") and not nic:
            nic = tag[4:]
        elif tag.startswith("DRV_") and not driver:
            driver = tag[4:]
        elif is_framesize_tag(tag) and not framesize:
            framesize = canonical_framesize(tag)
        elif is_core_tag(tag) and not cores:
            cores = canonical_core_count(tag)

    for tag in tags:
        if looks_like_test_area(tag, test_name):
            area = tag.lower()
            break

    if not framesize:
        match = re.search(r"(?:^|-)(\d+B|IMIX)(?:-|$)", test_name, re.IGNORECASE)
        framesize = canonical_framesize(match.group(1)) if match else ""
    if not cores:
        match = re.search(r"(?:^|-)(\d+C)(?:-|$)", test_name, re.IGNORECASE)
        cores = canonical_core_count(match.group(1)) if match else ""
    if not area:
        area = fallback_area_from_name(test_name, framesize, cores, test_type)

    return TagFields(nic=nic, driver=driver, framesize=framesize, cores=cores, test_area=area)


def identity_for(row: WorkbookRow, robot_test: RobotTest) -> TestIdentity:
    tags = extract_tag_fields(robot_test.name, robot_test.tags, row.test_type)
    return TestIdentity(
        dut=row.dut,
        node=row.node,
        job_type=row.job_type,
        test_type=row.test_type,
        nic=tags.nic,
        driver=tags.driver,
        framesize=tags.framesize,
        cores=tags.cores,
        test_area=tags.test_area,
    )


def process_release(
    rows: Sequence[WorkbookRow],
    cache_dir: Path,
    timeout: int,
    retries: int,
    offline: bool,
    max_logs: Optional[int] = None,
    fetcher: Callable[[str, Path, int, int, bool], bytes] = download_report,
    release_label: str = "",
    logger: ProgressLogger = None,
) -> Dict[TestIdentity, TestAggregate]:
    aggregates: Dict[TestIdentity, TestAggregate] = {}
    parsed_reports: Dict[str, List[RobotTest]] = {}
    processed_logs = 0
    total_logs = sum(1 for row in rows if row.log_url)
    limit = min(total_logs, max_logs) if max_logs is not None else total_logs
    prefix = f"[{release_label}] " if release_label else ""

    for row in rows:
        if not row.log_url:
            continue
        if max_logs is not None and processed_logs >= max_logs:
            break
        processed_logs += 1
        report = report_url(row.log_url)
        cache_path = cache_file_for_url(cache_dir, report)

        if row.log_url not in parsed_reports:
            if cache_path.exists():
                emit_progress(logger, f"{prefix}log {processed_logs}/{limit}: using cached {report}")
            elif offline:
                emit_progress(logger, f"{prefix}log {processed_logs}/{limit}: checking cache for {report}")
            else:
                emit_progress(logger, f"{prefix}log {processed_logs}/{limit}: downloading {report}")
            try:
                data = fetcher(row.log_url, cache_dir, timeout, retries, offline)
                parsed_reports[row.log_url] = collect_robot_tests(decode_report_bytes(data))
            except LogFetchError:
                raise
            except (OSError, EOFError, UnicodeDecodeError, ReportParseError) as exc:
                parsed_reports[row.log_url] = []
                emit_progress(logger, f"{prefix}WARNING: skipped {report}: {exc}")
                continue
            emit_progress(logger, f"{prefix}log {processed_logs}/{limit}: parsed {len(parsed_reports[row.log_url])} tests")

        for robot_test in parsed_reports[row.log_url]:
            identity = identity_for(row, robot_test)
            aggregate = aggregates.setdefault(identity, TestAggregate(identity=identity, testbed=row.testbed))
            metrics = parse_test_result(row.test_type, robot_test.message) if robot_test.status == "Pass" else MetricValues()
            aggregate.add(row, robot_test.status, metrics)

    emit_progress(logger, f"{prefix}built {len(aggregates)} aggregate test identities")
    return aggregates


def aggregate_summaries(aggregate: Optional[TestAggregate]) -> Dict[str, MetricSummary]:
    if aggregate is None or aggregate.pass_count == 0:
        return {"standard": MetricSummary(), "ndr": MetricSummary(), "pdr": MetricSummary()}
    return {
        "standard": summarize(aggregate.standard_values),
        "ndr": summarize(aggregate.ndr_values),
        "pdr": summarize(aggregate.pdr_values),
    }


def combined_status(current: Optional[TestAggregate], previous: Optional[TestAggregate]) -> str:
    current_status = current.status if current else ""
    previous_status = previous.status if previous else ""
    if current_status and previous_status:
        return "Pass" if current_status == "Pass" and previous_status == "Pass" else "Fail"
    if current_status == "Fail" or previous_status == "Fail":
        return "Fail"
    return ""


def diff_pair(current: MetricSummary, previous: MetricSummary) -> Tuple[Optional[float], Optional[float]]:
    if current.mean is None or previous.mean is None:
        return None, None
    diff = current.mean - previous.mean
    rel = diff / previous.mean if previous.mean else None
    return diff, rel


def output_rows(
    current: Mapping[TestIdentity, TestAggregate],
    previous: Mapping[TestIdentity, TestAggregate],
) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    for identity in sorted(set(current) | set(previous), key=lambda item: item.sort_key()):
        current_aggregate = current.get(identity)
        previous_aggregate = previous.get(identity)
        current_summary = aggregate_summaries(current_aggregate)
        previous_summary = aggregate_summaries(previous_aggregate)
        standard_diff, standard_rel = diff_pair(current_summary["standard"], previous_summary["standard"])
        ndr_diff, ndr_rel = diff_pair(current_summary["ndr"], previous_summary["ndr"])
        pdr_diff, pdr_rel = diff_pair(current_summary["pdr"], previous_summary["pdr"])

        row: Dict[str, object] = {
            "DUT": identity.dut,
            "Node": identity.node,
            "Job type": identity.job_type,
            "Test type": identity.test_type,
            "Status": combined_status(current_aggregate, previous_aggregate),
            "NIC": identity.nic,
            "Driver": identity.driver,
            "Framesize": identity.framesize,
            "Number of cores": identity.cores,
            "Test area": identity.test_area,
            "Mean current": current_summary["standard"].mean,
            "Stdev current": current_summary["standard"].stdev,
            "Mean NDR current": current_summary["ndr"].mean,
            "Stdev NDR current": current_summary["ndr"].stdev,
            "Mean PDR current": current_summary["pdr"].mean,
            "Stdev PDR current": current_summary["pdr"].stdev,
            "Mean previous": previous_summary["standard"].mean,
            "Stdev previous": previous_summary["standard"].stdev,
            "Mean NDR previous": previous_summary["ndr"].mean,
            "Stdev NDR previous": previous_summary["ndr"].stdev,
            "Mean PDR previous": previous_summary["pdr"].mean,
            "Stdev PDR previous": previous_summary["pdr"].stdev,
            "Diff": standard_diff,
            "Rel Diff": standard_rel,
            "Diff NDR": ndr_diff,
            "Rel Diff NDR": ndr_rel,
            "Diff PDR": pdr_diff,
            "Rel Diff PDR": pdr_rel,
        }
        rows.append(row)
    return rows


def write_output_workbook(rows: Sequence[Mapping[str, object]], output_path: Path) -> None:
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Comparison"
    worksheet.append(OUTPUT_COLUMNS)
    for row in rows:
        worksheet.append([row.get(column) for column in OUTPUT_COLUMNS])

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(style="thin", color="D9E2F3")
    border = Border(bottom=thin)
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    worksheet.freeze_panes = "A2"
    max_row = max(worksheet.max_row, 1)
    max_col = worksheet.max_column
    worksheet.auto_filter.ref = f"A1:{get_column_letter(max_col)}{max_row}"

    percent_columns = {"Rel Diff", "Rel Diff NDR", "Rel Diff PDR"}
    numeric_columns = {
        "Mean current",
        "Stdev current",
        "Mean NDR current",
        "Stdev NDR current",
        "Mean PDR current",
        "Stdev PDR current",
        "Mean previous",
        "Stdev previous",
        "Mean NDR previous",
        "Stdev NDR previous",
        "Mean PDR previous",
        "Stdev PDR previous",
        "Diff",
        "Diff NDR",
        "Diff PDR",
    }
    for column_index, column_name in enumerate(OUTPUT_COLUMNS, start=1):
        letter = get_column_letter(column_index)
        width = min(max(len(column_name) + 2, 12), 60)
        if column_name in {"Test area"}:
            width = 30
        elif column_name in numeric_columns or column_name in percent_columns:
            width = 16
        worksheet.column_dimensions[letter].width = width
        for cell in worksheet.iter_cols(min_col=column_index, max_col=column_index, min_row=2, max_row=max_row):
            for value_cell in cell:
                if column_name in percent_columns and value_cell.value is not None:
                    value_cell.number_format = "0.00%"
                elif column_name in numeric_columns and value_cell.value is not None:
                    value_cell.number_format = "#,##0.00"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)


def compare_workbooks(
    workbook_a: Path,
    workbook_b: Path,
    output_path: Optional[Path],
    cache_dir: Path,
    timeout: int,
    retries: int,
    offline: bool,
    max_logs: Optional[int],
    fetcher: Callable[[str, Path, int, int, bool], bytes] = download_report,
    logger: ProgressLogger = None,
) -> Path:
    emit_progress(logger, "Detecting current and previous releases.")
    previous_release, current_release = determine_releases([workbook_a, workbook_b])
    if output_path is None:
        output_path = Path(f"comparison_{previous_release.label}_to_{current_release.label}.xlsx")
    emit_progress(
        logger,
        f"Previous release: {previous_release.label} ({previous_release.path}); "
        f"current release: {current_release.label} ({current_release.path}).",
    )

    emit_progress(logger, f"Reading previous workbook: {previous_release.path}")
    previous_rows = read_workbook_rows(previous_release.path)
    emit_progress(logger, f"Loaded {len(previous_rows)} previous workbook rows.")
    emit_progress(logger, f"Reading current workbook: {current_release.path}")
    current_rows = read_workbook_rows(current_release.path)
    emit_progress(logger, f"Loaded {len(current_rows)} current workbook rows.")

    emit_progress(logger, f"Processing previous release logs with cache: {cache_dir}")
    previous_aggregates = process_release(
        previous_rows,
        cache_dir,
        timeout,
        retries,
        offline,
        max_logs,
        fetcher,
        previous_release.label,
        logger,
    )
    emit_progress(logger, f"Processing current release logs with cache: {cache_dir}")
    current_aggregates = process_release(
        current_rows,
        cache_dir,
        timeout,
        retries,
        offline,
        max_logs,
        fetcher,
        current_release.label,
        logger,
    )
    emit_progress(logger, "Merging current and previous aggregate rows.")
    rows = output_rows(current_aggregates, previous_aggregates)
    emit_progress(logger, f"Writing {len(rows)} comparison rows to {output_path}")
    write_output_workbook(rows, output_path)
    emit_progress(logger, f"Done: {output_path}")
    return output_path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare test results from two YYMM release workbooks.")
    parser.add_argument("workbooks", nargs=2, type=Path, metavar="WORKBOOK", help="Input workbook named YYMM.xlsx")
    parser.add_argument("-o", "--output", type=Path, help="Output comparison workbook path")
    parser.add_argument("--cache-dir", type=Path, default=Path(CACHE_DIR_DEFAULT), help=f"Log cache directory (default: {CACHE_DIR_DEFAULT})")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Download timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--retries", type=int, default=DEFAULT_RETRIES, help=f"Download retry count (default: {DEFAULT_RETRIES})")
    parser.add_argument("--offline", action="store_true", help="Use only cached logs and fail if a log is missing")
    parser.add_argument("--max-logs", type=int, help="Process at most this many log rows per workbook")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        output_path = compare_workbooks(
            args.workbooks[0],
            args.workbooks[1],
            args.output,
            args.cache_dir,
            args.timeout,
            args.retries,
            args.offline,
            args.max_logs,
            logger=lambda message: print(message, flush=True),
        )
    except CompareReleasesError as exc:
        parser.exit(2, f"error: {exc}\n")
    print(output_path, flush=True)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
