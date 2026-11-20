#!/usr/bin/env python3
"""Find common and typical parameters of failed CSIT tests."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import re
import tarfile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


PARAMETERS = ("NIC", "Driver", "Framesize", "Number of cores", "Test area")
RUN_SUFFIXES = {"ndrpdr", "mrr", "soak", "cps", "rps", "reconf"}
KNOWN_DRIVER_TOKENS = {"avf", "mlx5", "rdma", "vfio"}
NIC_TOKEN_RE = re.compile(r"^\d+ge\d+p\d+[a-z0-9]*$")
DEFAULT_TIMEOUT = 30


@dataclass(frozen=True)
class TestExecution:
    """A single generated test execution from one run."""

    name: str
    nic: str
    driver: str
    framesize: str
    cores: str
    test_area: str
    failed: bool
    row_number: int
    run: str
    run_url: str
    log_url: str
    source_file: str

    @property
    def params(self) -> dict[str, str]:
        return {
            "NIC": self.nic,
            "Driver": self.driver,
            "Framesize": self.framesize,
            "Number of cores": self.cores,
            "Test area": self.test_area,
        }


@dataclass
class RunAnalysis:
    row: dict[str, str]
    row_number: int
    executions: list[TestExecution]
    unmatched_failures: list[str] = field(default_factory=list)


@dataclass
class GroupAnalysis:
    group_id: str
    meta: dict[str, str]
    runs: list[RunAnalysis] = field(default_factory=list)

    @property
    def executions(self) -> list[TestExecution]:
        return [execution for run in self.runs for execution in run.executions]


@dataclass(frozen=True)
class Candidate:
    params: tuple[tuple[str, str], ...]
    matching_total: int
    matching_failed: int
    total_executions: int
    total_failed: int
    matching_indices: frozenset[int]
    failed_indices: frozenset[int]
    failure_rate: float
    failed_share: float
    lift: float

    @property
    def param_count(self) -> int:
        return len(self.params)


def split_failed_tests(value: str) -> list[str]:
    """Split the CSV failed-tests field into exact generated test names."""

    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def normalize_robot_value(value: str) -> str:
    value = value.strip().strip("|").strip()
    if value.startswith("${") and value.endswith("}"):
        value = value[2:-1]
    if value.lower() in {"none", "${none}", ""}:
        return ""
    return value


def normalize_driver(value: str) -> str:
    value = normalize_robot_value(value)
    if not value:
        return ""
    value = value.strip()
    if value.upper().startswith("DRV_"):
        value = value[4:]
    value = value.lower().replace("_", "-")
    if value == "vfio-pci":
        return value
    if value == "mlx5-core":
        return "mlx5"
    return value


def normalize_framesize(value: str) -> str:
    value = normalize_robot_value(value)
    if not value:
        return ""
    upper = value.upper()
    if upper.startswith("IMIX"):
        return "IMIX"
    match = re.fullmatch(r"(\d+)(B|KB|MB|GB)", upper)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return ""


def normalize_core(value: str) -> str:
    value = normalize_robot_value(value)
    match = re.fullmatch(r"(\d+)[cC]", value)
    if match:
        return f"{match.group(1)}c"
    return ""


def parse_pipe_row(line: str) -> list[str]:
    """Parse a Robot Framework pipe row and remove structural empty cells."""

    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|") if cell.strip()]


def parse_driver_from_text(text: str) -> str:
    tag_driver = ""
    for line in text.splitlines():
        cells = parse_pipe_row(line)
        if not cells:
            continue
        key = cells[0].replace(" ", "").lower()
        if key in {"${nic_driver}=", "${nic_driver}"} and len(cells) > 1:
            return normalize_driver(cells[1])
        for cell in cells:
            if cell.upper().startswith("DRV_") and not tag_driver:
                tag_driver = normalize_driver(cell)
    return tag_driver


def is_nic_token(token: str) -> bool:
    return bool(NIC_TOKEN_RE.fullmatch(token.lower()))


def parse_nic_and_area_from_stem(stem: str, driver: str) -> tuple[str, str]:
    tokens = [token for token in stem.split("-") if token]
    if not tokens:
        return "", ""

    nic_index = next((index for index, token in enumerate(tokens) if is_nic_token(token)), None)
    if nic_index is None:
        nic = ""
        area_tokens = tokens[:]
    else:
        nic = tokens[nic_index].lower()
        area_tokens = tokens[nic_index + 1 :]

    driver_parts = driver.split("-") if driver else []
    if driver_parts and area_tokens[: len(driver_parts)] == driver_parts:
        area_tokens = area_tokens[len(driver_parts) :]
    elif area_tokens and area_tokens[0].lower() in KNOWN_DRIVER_TOKENS:
        if area_tokens[0].lower() == "vfio" and len(area_tokens) > 1 and area_tokens[1].lower() == "pci":
            area_tokens = area_tokens[2:]
        else:
            area_tokens = area_tokens[1:]

    if area_tokens and area_tokens[-1].lower() in RUN_SUFFIXES:
        area_tokens = area_tokens[:-1]

    return nic, "-".join(area_tokens)


def extract_framesize_and_core(test_name: str, tags: Iterable[str] = ()) -> tuple[str, str]:
    framesize = ""
    cores = ""
    for tag in tags:
        framesize = framesize or normalize_framesize(tag)
        cores = cores or normalize_core(tag)
        if framesize and cores:
            break

    tokens = test_name.split("-")
    if not framesize and tokens:
        framesize = normalize_framesize(tokens[0])
    if not cores and len(tokens) > 1:
        cores = normalize_core(tokens[1])
    return framesize, cores


def looks_like_test_name(value: str) -> bool:
    framesize, cores = extract_framesize_and_core(value)
    return bool(framesize and cores and "-" in value)


def parse_robot_file(member_name: str, text: str) -> list[dict[str, str]]:
    """Parse generated Robot test cases from one suite file."""

    stem = Path(member_name).name
    if stem.endswith(".robot"):
        stem = stem[:-6]

    driver = parse_driver_from_text(text)
    nic, test_area = parse_nic_and_area_from_stem(stem, driver)

    cases: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    in_test_cases = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("***") and stripped.endswith("***"):
            in_test_cases = stripped.lower() == "*** test cases ***"
            current = None
            continue
        if not in_test_cases:
            continue

        cells = parse_pipe_row(line)
        if not cells:
            continue

        first = cells[0]
        if first.lower() == "[tags]" and current is not None:
            current_tags = current.setdefault("tags", [])
            assert isinstance(current_tags, list)
            current_tags.extend(cells[1:])
            continue

        if len(cells) == 1 and looks_like_test_name(first):
            current = {"name": first, "tags": []}
            cases.append(current)

    parsed: list[dict[str, str]] = []
    for case in cases:
        name = str(case["name"])
        tags = [str(tag) for tag in case.get("tags", [])]
        framesize, cores = extract_framesize_and_core(name, tags)
        parsed.append(
            {
                "name": name,
                "NIC": nic,
                "Driver": driver,
                "Framesize": framesize,
                "Number of cores": cores,
                "Test area": test_area,
                "source_file": member_name,
            }
        )
    return parsed


def parse_generated_tests_archive(
    archive_path: Path,
    failed_tests: set[str],
    row: dict[str, str],
    row_number: int,
) -> RunAnalysis:
    parsed_tests: list[dict[str, str]] = []

    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            if not member.isfile() or not member.name.endswith(".robot"):
                continue
            if Path(member.name).name == "__init__.robot":
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                continue
            text = extracted.read().decode("utf-8", errors="replace")
            parsed_tests.extend(parse_robot_file(member.name, text))

    seen_names = {test["name"] for test in parsed_tests}
    executions = [
        TestExecution(
            name=test["name"],
            nic=test["NIC"],
            driver=test["Driver"],
            framesize=test["Framesize"],
            cores=test["Number of cores"],
            test_area=test["Test area"],
            failed=test["name"] in failed_tests,
            row_number=row_number,
            run=row.get("Run", ""),
            run_url=row.get("Run URL", ""),
            log_url=row.get("Log", ""),
            source_file=test["source_file"],
        )
        for test in parsed_tests
    ]
    unmatched = sorted(failed_tests - seen_names)
    return RunAnalysis(row=row, row_number=row_number, executions=executions, unmatched_failures=unmatched)


def archive_url_for_log(log_url: str) -> str:
    return f"{log_url.rstrip('/')}/generated_tests.tar.gz"


def cache_path_for_url(cache_dir: Path, url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    run_id = url.rstrip("/").split("/")[-2] if "/" in url.rstrip("/") else "run"
    safe_run_id = re.sub(r"[^A-Za-z0-9_.-]", "_", run_id)
    return cache_dir / f"{safe_run_id}-{digest}.tar.gz"


def fetch_archive(log_url: str, cache_dir: Path, timeout: int = DEFAULT_TIMEOUT) -> tuple[Path, bool]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    archive_url = archive_url_for_log(log_url)
    cache_path = cache_path_for_url(cache_dir, archive_url)
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return cache_path, True

    request = Request(
        archive_url,
        headers={"User-Agent": "failed-test-parameter-analysis/1.0"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} fetching {archive_url}") from exc
    except URLError as exc:
        raise RuntimeError(f"URL error fetching {archive_url}: {exc.reason}") from exc

    if not payload:
        raise RuntimeError(f"empty archive fetched from {archive_url}")

    with tempfile.NamedTemporaryFile(delete=False, dir=cache_dir, suffix=".tmp") as handle:
        temp_path = Path(handle.name)
        handle.write(payload)

    try:
        # Validate the downloaded gzip stream before caching it as source data.
        with gzip.open(temp_path, "rb") as handle:
            handle.peek(1)
        temp_path.replace(cache_path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return cache_path, False


def group_id_for_row(row: dict[str, str], row_number: int) -> str:
    job_type = row.get("Job type", "").strip().lower()
    if job_type == "coverage":
        return "|".join(
            [
                row.get("DUT", ""),
                row.get("Node", ""),
                row.get("Job type", ""),
                row.get("Test type", ""),
                f"row-{row_number}",
            ]
        )
    return "|".join(
        [
            row.get("DUT", ""),
            row.get("Node", ""),
            row.get("Job type", ""),
            row.get("Test type", ""),
        ]
    )


def group_meta_for_row(row: dict[str, str], row_number: int) -> dict[str, str]:
    job_type = row.get("Job type", "").strip().lower()
    meta = {
        "DUT": row.get("DUT", ""),
        "Node": row.get("Node", ""),
        "Job type": row.get("Job type", ""),
        "Test type": row.get("Test type", ""),
        "Group ID": group_id_for_row(row, row_number),
        "Coverage Run": "",
        "Coverage Run URL": "",
        "Coverage Log": "",
        "Coverage Testbed": "",
    }
    if job_type == "coverage":
        meta["Coverage Run"] = row.get("Run", "")
        meta["Coverage Run URL"] = row.get("Run URL", "")
        meta["Coverage Log"] = row.get("Log", "")
        meta["Coverage Testbed"] = row.get("Testbed", "")
    return meta


def read_input_csv(path: Path) -> list[tuple[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [(line_number, row) for line_number, row in enumerate(csv.DictReader(handle), start=2)]


def analyze_csv(
    input_csv: Path,
    cache_dir: Path,
    timeout: int = DEFAULT_TIMEOUT,
    progress: Callable[[str], None] | None = None,
) -> tuple[list[GroupAnalysis], list[dict[str, str]]]:
    groups: dict[str, GroupAnalysis] = {}
    skipped: list[dict[str, str]] = []
    rows = read_input_csv(input_csv)
    rows_with_logs = sum(1 for _, row in rows if row.get("Log", "").strip())
    cached_archives = 0
    downloaded_archives = 0
    parsed_runs = 0

    emit_progress(progress, f"Loaded {len(rows)} rows from {input_csv}.")
    emit_progress(
        progress,
        f"Rows with log URLs: {rows_with_logs}; rows without logs: {len(rows) - rows_with_logs}.",
    )

    for index, (row_number, row) in enumerate(rows, start=1):
        log_url = row.get("Log", "").strip()
        if not log_url:
            skipped.append(skipped_row(row, row_number, "No log URL; run has not finished"))
            continue

        try:
            archive_path, from_cache = fetch_archive(log_url, cache_dir, timeout=timeout)
            if from_cache:
                cached_archives += 1
            else:
                downloaded_archives += 1
                if downloaded_archives == 1 or downloaded_archives % 25 == 0:
                    emit_progress(
                        progress,
                        "Downloaded "
                        f"{downloaded_archives} generated-test archive(s); "
                        f"latest CSV row {row_number}: {row.get('Run', '')}.",
                    )
            failed_tests = set(split_failed_tests(row.get("Failed tests", "")))
            run = parse_generated_tests_archive(archive_path, failed_tests, row, row_number)
        except (OSError, RuntimeError, tarfile.TarError) as exc:
            skipped.append(skipped_row(row, row_number, str(exc)))
            emit_progress(progress, f"Skipped CSV row {row_number}: {exc}")
            continue

        if not run.executions:
            skipped.append(skipped_row(row, row_number, "No generated Robot tests found in archive"))
            emit_progress(progress, f"Skipped CSV row {row_number}: no generated Robot tests found.")
            continue

        group_id = group_id_for_row(row, row_number)
        if group_id not in groups:
            groups[group_id] = GroupAnalysis(group_id=group_id, meta=group_meta_for_row(row, row_number))
        groups[group_id].runs.append(run)
        parsed_runs += 1

        if index == len(rows) or parsed_runs % 25 == 0:
            emit_progress(
                progress,
                "Processed "
                f"{index}/{len(rows)} rows; parsed runs: {parsed_runs}; "
                f"groups: {len(groups)}; skipped: {len(skipped)}; "
                f"cache hits: {cached_archives}; downloads: {downloaded_archives}.",
            )

    return list(groups.values()), skipped


def emit_progress(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is not None:
        progress(message)


def skipped_row(row: dict[str, str], row_number: int, reason: str) -> dict[str, str]:
    return {
        "CSV row": row_number,
        "DUT": row.get("DUT", ""),
        "Node": row.get("Node", ""),
        "Job type": row.get("Job type", ""),
        "Test type": row.get("Test type", ""),
        "Run": row.get("Run", ""),
        "Run URL": row.get("Run URL", ""),
        "Log": row.get("Log", ""),
        "Reason": reason,
    }


def mine_candidates(
    executions: list[TestExecution],
    min_failed_share: float,
    min_lift: float,
) -> list[Candidate]:
    total = len(executions)
    total_failed = sum(1 for execution in executions if execution.failed)
    if not total or not total_failed:
        return []

    baseline = total_failed / total
    buckets: dict[tuple[tuple[str, str], ...], dict[str, set[int]]] = {}

    for index, execution in enumerate(executions):
        present_params = [(key, value) for key, value in execution.params.items() if value]
        for size in range(1, len(present_params) + 1):
            for combo in itertools.combinations(present_params, size):
                key = tuple(combo)
                bucket = buckets.setdefault(key, {"matching": set(), "failed": set()})
                bucket["matching"].add(index)
                if execution.failed:
                    bucket["failed"].add(index)

    candidates: list[Candidate] = []
    for params, indexes in buckets.items():
        matching_total = len(indexes["matching"])
        matching_failed = len(indexes["failed"])
        if not matching_failed:
            continue

        failure_rate = matching_failed / matching_total
        failed_share = matching_failed / total_failed
        lift = failure_rate / baseline if baseline else 0.0

        passes_rank_rule = failed_share >= min_failed_share and lift >= min_lift
        passes_high_rate_rule = failure_rate >= 0.80 and matching_failed >= 2
        passes_all_failed_rule = failure_rate == 1.0 and matching_total >= 2
        if not (passes_rank_rule or passes_high_rate_rule or passes_all_failed_rule):
            continue

        candidates.append(
            Candidate(
                params=params,
                matching_total=matching_total,
                matching_failed=matching_failed,
                total_executions=total,
                total_failed=total_failed,
                matching_indices=frozenset(indexes["matching"]),
                failed_indices=frozenset(indexes["failed"]),
                failure_rate=failure_rate,
                failed_share=failed_share,
                lift=lift,
            )
        )

    candidates.sort(key=candidate_sort_key, reverse=True)
    return dedupe_candidates(candidates)


def candidate_sort_key(candidate: Candidate) -> tuple[float, float, float, int, int, float]:
    return (
        candidate.failed_share,
        candidate.failure_rate,
        candidate.lift,
        candidate.matching_failed,
        -candidate.param_count,
        -candidate.matching_total,
    )


def dedupe_candidates(candidates: list[Candidate]) -> list[Candidate]:
    selected: list[Candidate] = []
    for candidate in candidates:
        candidate_params = set(candidate.params)
        duplicate = False
        for existing in selected:
            existing_params = set(existing.params)
            if candidate.failed_indices == existing.failed_indices:
                duplicate = True
                break
            if (
                candidate.failed_indices.issubset(existing.failed_indices)
                and candidate_params.issuperset(existing_params)
                and candidate.failure_rate <= existing.failure_rate
            ):
                duplicate = True
                break
        if not duplicate:
            selected.append(candidate)
    return selected


def one_failed_candidate(executions: list[TestExecution]) -> Candidate:
    total = len(executions)
    total_failed = 1
    failed_index = next(index for index, execution in enumerate(executions) if execution.failed)
    failed_execution = executions[failed_index]
    params = tuple((key, value) for key, value in failed_execution.params.items() if value)
    matching_indices = {
        index
        for index, execution in enumerate(executions)
        if all(execution.params.get(key) == value for key, value in params)
    }
    matching_failed = sum(1 for index in matching_indices if executions[index].failed)
    matching_total = len(matching_indices)
    failure_rate = matching_failed / matching_total if matching_total else 0.0
    baseline = total_failed / total if total else 0.0
    lift = failure_rate / baseline if baseline else 0.0
    return Candidate(
        params=params,
        matching_total=matching_total,
        matching_failed=matching_failed,
        total_executions=total,
        total_failed=total_failed,
        matching_indices=frozenset(matching_indices),
        failed_indices=frozenset({failed_index}),
        failure_rate=failure_rate,
        failed_share=1.0,
        lift=lift,
    )


def findings_for_group(
    group: GroupAnalysis,
    min_failed_share: float,
    min_lift: float,
    top_per_group: int,
) -> list[dict[str, object]]:
    executions = group.executions
    total = len(executions)
    failed = sum(1 for execution in executions if execution.failed)

    if not total:
        return []

    if not failed:
        return [finding_row(group, None, "There are no failed tests in this group of runs.")]

    if failed == 1:
        return [finding_row(group, one_failed_candidate(executions), "single failure")]

    candidates = mine_candidates(executions, min_failed_share, min_lift)
    if not candidates:
        message = "Failed tests were present, but no parameter pattern met the selected thresholds."
        return [finding_row(group, None, message)]

    return [finding_row(group, candidate, "") for candidate in candidates[:top_per_group]]


def finding_row(group: GroupAnalysis, candidate: Candidate | None, explicit_text: str) -> dict[str, object]:
    executions = group.executions
    total = len(executions)
    failed = sum(1 for execution in executions if execution.failed)
    row: dict[str, object] = {
        **group.meta,
        "Runs analyzed": len(group.runs),
        "Total executions": total,
        "Failed executions": failed,
        "Group failure rate": failed / total if total else 0.0,
        "Pattern NIC": "",
        "Pattern Driver": "",
        "Pattern Framesize": "",
        "Pattern Number of cores": "",
        "Pattern Test area": "",
        "Matching executions": "",
        "Matching failures": "",
        "Pattern failure rate": "",
        "Failed share": "",
        "Lift": "",
        "Finding": explicit_text,
    }
    if candidate is None:
        return row

    params = dict(candidate.params)
    row.update(
        {
            "Pattern NIC": params.get("NIC", ""),
            "Pattern Driver": params.get("Driver", ""),
            "Pattern Framesize": params.get("Framesize", ""),
            "Pattern Number of cores": params.get("Number of cores", ""),
            "Pattern Test area": params.get("Test area", ""),
            "Matching executions": candidate.matching_total,
            "Matching failures": candidate.matching_failed,
            "Pattern failure rate": candidate.failure_rate,
            "Failed share": candidate.failed_share,
            "Lift": candidate.lift,
            "Finding": describe_candidate(candidate, explicit_text),
        }
    )
    return row


def describe_candidate(candidate: Candidate, explicit_text: str = "") -> str:
    params_text = ", ".join(f"{key}={value}" for key, value in candidate.params)
    if explicit_text == "single failure":
        return (
            f"One failed test matched {params_text}; matching tests failed at "
            f"{candidate.failure_rate:.1%} in this group of runs."
        )
    if candidate.failure_rate == 1.0:
        return (
            f"All tests matching {params_text} failed; these account for "
            f"{candidate.failed_share:.1%} of failures in this group of runs."
        )
    return (
        f"{candidate.failure_rate:.1%} of tests matching {params_text} failed; "
        f"these account for {candidate.failed_share:.1%} of failures in this group of runs."
    )


def summary_row(group: GroupAnalysis, finding_count: int) -> dict[str, object]:
    executions = group.executions
    total = len(executions)
    failed = sum(1 for execution in executions if execution.failed)
    unmatched = sum(len(run.unmatched_failures) for run in group.runs)
    return {
        **group.meta,
        "Runs analyzed": len(group.runs),
        "Total executions": total,
        "Failed executions": failed,
        "Failure rate": failed / total if total else 0.0,
        "Findings": finding_count,
        "Unmatched failed tests": unmatched,
    }


def build_workbook(
    groups: list[GroupAnalysis],
    skipped: list[dict[str, str]],
    output_path: Path,
    min_failed_share: float,
    min_lift: float,
    top_per_group: int,
) -> None:
    findings: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []

    for group in groups:
        group_findings = findings_for_group(group, min_failed_share, min_lift, top_per_group)
        findings.extend(group_findings)
        summaries.append(summary_row(group, len(group_findings)))

    workbook = Workbook()
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    write_sheet(workbook, "Findings", findings, FINDINGS_COLUMNS, percent_columns={
        "Group failure rate",
        "Pattern failure rate",
        "Failed share",
    }, decimal_columns={"Lift"})
    write_sheet(workbook, "Group Summary", summaries, SUMMARY_COLUMNS, percent_columns={"Failure rate"})
    write_sheet(workbook, "Skipped Runs", skipped, SKIPPED_COLUMNS, percent_columns=set())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output_path)


FINDINGS_COLUMNS = [
    "DUT",
    "Node",
    "Job type",
    "Test type",
    "Group ID",
    "Runs analyzed",
    "Total executions",
    "Failed executions",
    "Group failure rate",
    "Pattern NIC",
    "Pattern Driver",
    "Pattern Framesize",
    "Pattern Number of cores",
    "Pattern Test area",
    "Matching executions",
    "Matching failures",
    "Pattern failure rate",
    "Failed share",
    "Lift",
    "Finding",
]

SUMMARY_COLUMNS = [
    "DUT",
    "Node",
    "Job type",
    "Test type",
    "Group ID",
    "Coverage Run",
    "Coverage Run URL",
    "Coverage Log",
    "Coverage Testbed",
    "Runs analyzed",
    "Total executions",
    "Failed executions",
    "Failure rate",
    "Findings",
    "Unmatched failed tests",
]

SKIPPED_COLUMNS = [
    "CSV row",
    "DUT",
    "Node",
    "Job type",
    "Test type",
    "Run",
    "Run URL",
    "Log",
    "Reason",
]


def write_sheet(
    workbook: Workbook,
    title: str,
    rows: list[dict[str, object]],
    columns: list[str],
    percent_columns: set[str],
    decimal_columns: set[str] | None = None,
) -> None:
    decimal_columns = decimal_columns or set()
    sheet = workbook.create_sheet(title=title)
    sheet.sheet_view.showGridLines = False
    sheet.freeze_panes = "A2"

    sheet.append(columns)
    for row in rows:
        sheet.append([row.get(column, "") for column in columns])

    style_header(sheet)
    style_body(sheet, columns, percent_columns, decimal_columns)
    add_table(sheet, title.replace(" ", "") + "Table", len(rows) + 1, len(columns))
    autosize_columns(sheet, columns)


def style_header(sheet) -> None:
    fill = PatternFill("solid", fgColor="1F4E78")
    font = Font(color="FFFFFF", bold=True)
    alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for cell in sheet[1]:
        cell.fill = fill
        cell.font = font
        cell.alignment = alignment
    sheet.row_dimensions[1].height = 28


def style_body(sheet, columns: list[str], percent_columns: set[str], decimal_columns: set[str]) -> None:
    thin = Side(style="thin", color="D9E2F3")
    border = Border(bottom=thin)
    numeric_columns = {
        "Runs analyzed",
        "Total executions",
        "Failed executions",
        "Matching executions",
        "Matching failures",
        "Findings",
        "Unmatched failed tests",
        "CSV row",
    }
    wrap_columns = {"Finding", "Reason", "Coverage Run URL", "Coverage Log", "Run URL", "Log"}

    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            header = columns[cell.column - 1]
            cell.border = border
            cell.alignment = Alignment(
                vertical="top",
                horizontal="right" if header in numeric_columns or header in percent_columns else "left",
                wrap_text=header in wrap_columns or len(str(cell.value or "")) > 60,
            )
            if header in percent_columns and isinstance(cell.value, (int, float)):
                cell.number_format = "0.0%"
            elif header in decimal_columns and isinstance(cell.value, (int, float)):
                cell.number_format = "0.00"
            elif header in numeric_columns and isinstance(cell.value, (int, float)):
                cell.number_format = "#,##0"


def add_table(sheet, table_name: str, row_count: int, column_count: int) -> None:
    if row_count < 1 or column_count < 1:
        return
    end_cell = f"{get_column_letter(column_count)}{max(row_count, 1)}"
    table = Table(displayName=table_name, ref=f"A1:{end_cell}")
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2",
        showFirstColumn=False,
        showLastColumn=False,
        showRowStripes=True,
        showColumnStripes=False,
    )
    sheet.add_table(table)


def autosize_columns(sheet, columns: list[str]) -> None:
    max_widths = {
        "Finding": 90,
        "Reason": 80,
        "Coverage Run URL": 55,
        "Coverage Log": 65,
        "Run URL": 55,
        "Log": 65,
        "Pattern Test area": 45,
        "Group ID": 45,
    }
    min_widths = {
        "Finding": 42,
        "Reason": 30,
        "Coverage Run URL": 25,
        "Coverage Log": 25,
        "Run URL": 25,
        "Log": 25,
    }

    for index, column in enumerate(columns, start=1):
        letter = get_column_letter(index)
        values = [str(cell.value) if cell.value is not None else "" for cell in sheet[letter]]
        width = min(max(len(value) for value in values) + 2, max_widths.get(column, 28))
        width = max(width, min_widths.get(column, 10))
        sheet.column_dimensions[letter].width = width


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Identify common and typical parameters of failed generated CSIT tests."
    )
    parser.add_argument("input_csv", nargs="?", default="data.csv", help="Input CSV file")
    parser.add_argument("-o", "--output", default="failed_test_parameter_patterns.xlsx", help="Output .xlsx path")
    parser.add_argument("--cache-dir", default=".cache/failed-test-logs", help="Archive cache directory")
    parser.add_argument("--min-failed-share", type=float, default=0.30, help="Minimum share of failures to report")
    parser.add_argument("--min-lift", type=float, default=1.5, help="Minimum lift over group baseline")
    parser.add_argument("--top-per-group", type=int, default=5, help="Maximum findings per group")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-archive fetch timeout in seconds")
    return parser.parse_args()


def print_progress(message: str) -> None:
    print(message, flush=True)


def main() -> int:
    args = parse_args()
    input_csv = Path(args.input_csv)
    output_path = Path(args.output)
    cache_dir = Path(args.cache_dir)

    print_progress(f"Starting failed-test parameter analysis for {input_csv}.")
    print_progress(f"Using generated-test archive cache: {cache_dir}.")
    groups, skipped = analyze_csv(input_csv, cache_dir, timeout=args.timeout, progress=print_progress)
    print_progress(f"Mining failed-test parameter patterns across {len(groups)} groups.")
    build_workbook(
        groups=groups,
        skipped=skipped,
        output_path=output_path,
        min_failed_share=args.min_failed_share,
        min_lift=args.min_lift,
        top_per_group=args.top_per_group,
    )
    print_progress(f"Saved workbook to {output_path}.")

    analyzed_runs = sum(len(group.runs) for group in groups)
    print_progress(f"Analyzed groups: {len(groups)}")
    print_progress(f"Analyzed runs: {analyzed_runs}")
    print_progress(f"Skipped runs: {len(skipped)}")
    print_progress(f"Workbook: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
