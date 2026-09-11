"""Application settings for the CSIT MCP server."""

from dataclasses import dataclass
import os
from typing import Any, FrozenSet, Mapping

from .utils.constants import Constants as C
from .services.telemetry import (
    DEFAULT_MAX_TELEMETRY_SAMPLES,
    DEFAULT_MAX_TELEMETRY_SOURCE_ROWS,
)


TRUE_VALUES = {"1", "true", "yes", "y"}
FALSE_VALUES = {"0", "false", "no", "n"}
VALID_DATA_MODES = {"s3", "fixture"}


@dataclass(frozen=True)
class AppSettings:
    """Resolved application settings backed by existing CSIT constants."""

    server_name: str
    server_version: str
    server_description: str
    public_tags: FrozenSet[str]
    mcp_path: str
    data_mode: str
    refresh_interval_seconds: int
    cors_allow_origins: tuple[str, ...]
    data_spec_file: str
    max_time_period: int
    time_period: int | None
    log_format: str
    log_date_format: str
    log_level: int
    start_failures: bool
    start_statistics: bool
    start_trending: bool
    start_report: bool
    start_coverage: bool
    news_title: str
    stats_title: str
    trend_title: str
    report_title: str
    coverage_title: str
    max_pool_size: int = 30
    telemetry_max_source_rows: int = DEFAULT_MAX_TELEMETRY_SOURCE_ROWS
    telemetry_max_samples: int = DEFAULT_MAX_TELEMETRY_SAMPLES
    telemetry_query_max_concurrent: int = 1
    telemetry_query_queue_timeout_seconds: int = 5
    telemetry_query_timeout_seconds: int = 30
    telemetry_query_max_source_rows: int = 2000
    telemetry_query_max_samples: int = 20_000
    telemetry_query_cache_entries: int = 256
    telemetry_query_max_encoded_bytes: int = 134_217_728
    telemetry_query_max_decoded_bytes: int = 536_870_912
    telemetry_worker_memory_limit_bytes: int = 2_147_483_648
    query_max_concurrent: int = 1
    query_queue_timeout_seconds: int = 5
    query_heavy_row_threshold: int = 100_000
    query_memory_soft_limit_percent: int = 75
    cache_snapshot_path: str = ""
    s3_read_max_attempts: int = 3
    s3_read_retry_base_seconds: int = 2
    refresh_memory_limit_percent: int = 85
    snapshot_refresh_max_age_seconds: int = 0
    refresh_worker_timeout_seconds: int = 1800
    validation_errors: tuple[dict[str, Any], ...] = ()

    def effective_time_period(self) -> int:
        """Return the configured time period capped at the maximum."""

        if self.time_period is None or self.time_period > self.max_time_period:
            return self.max_time_period
        return self.time_period

    def configuration_status(self) -> dict[str, Any]:
        """Return JSON-ready configuration validation status."""

        return {
            "valid": not self.validation_errors,
            "errors": [dict(error) for error in self.validation_errors],
            "values": {
                "CSIT_DATA_MODE": self.data_mode,
                "CSIT_TIME_PERIOD": self.time_period,
                "CSIT_MAX_TIME_PERIOD": self.max_time_period,
                "effective_time_period": self.effective_time_period(),
                "CSIT_REFRESH_INTERVAL_SECONDS": self.refresh_interval_seconds,
                "CSIT_CORS_ALLOW_ORIGINS": list(self.cors_allow_origins),
                "CSIT_MAX_POOL_SIZE": self.max_pool_size,
                "CSIT_TELEMETRY_MAX_SOURCE_ROWS": (
                    self.telemetry_max_source_rows
                ),
                "CSIT_TELEMETRY_MAX_SAMPLES": self.telemetry_max_samples,
                "CSIT_TELEMETRY_QUERY_MAX_CONCURRENT": (
                    self.telemetry_query_max_concurrent
                ),
                "CSIT_TELEMETRY_QUERY_QUEUE_TIMEOUT_SECONDS": (
                    self.telemetry_query_queue_timeout_seconds
                ),
                "CSIT_TELEMETRY_QUERY_TIMEOUT_SECONDS": (
                    self.telemetry_query_timeout_seconds
                ),
                "CSIT_TELEMETRY_QUERY_MAX_SOURCE_ROWS": (
                    self.telemetry_query_max_source_rows
                ),
                "CSIT_TELEMETRY_QUERY_MAX_SAMPLES": (
                    self.telemetry_query_max_samples
                ),
                "CSIT_TELEMETRY_QUERY_CACHE_ENTRIES": (
                    self.telemetry_query_cache_entries
                ),
                "CSIT_TELEMETRY_QUERY_MAX_ENCODED_BYTES": (
                    self.telemetry_query_max_encoded_bytes
                ),
                "CSIT_TELEMETRY_QUERY_MAX_DECODED_BYTES": (
                    self.telemetry_query_max_decoded_bytes
                ),
                "CSIT_TELEMETRY_WORKER_MEMORY_LIMIT_BYTES": (
                    self.telemetry_worker_memory_limit_bytes
                ),
                "CSIT_QUERY_MAX_CONCURRENT": self.query_max_concurrent,
                "CSIT_QUERY_QUEUE_TIMEOUT_SECONDS": (
                    self.query_queue_timeout_seconds
                ),
                "CSIT_QUERY_HEAVY_ROW_THRESHOLD": (
                    self.query_heavy_row_threshold
                ),
                "CSIT_QUERY_MEMORY_SOFT_LIMIT_PERCENT": (
                    self.query_memory_soft_limit_percent
                ),
                "CSIT_CACHE_SNAPSHOT_PATH": self.cache_snapshot_path,
                "CSIT_S3_READ_MAX_ATTEMPTS": self.s3_read_max_attempts,
                "CSIT_S3_READ_RETRY_BASE_SECONDS": (
                    self.s3_read_retry_base_seconds
                ),
                "CSIT_REFRESH_MEMORY_LIMIT_PERCENT": (
                    self.refresh_memory_limit_percent
                ),
                "CSIT_SNAPSHOT_REFRESH_MAX_AGE_SECONDS": (
                    self.snapshot_refresh_max_age_seconds
                ),
                "CSIT_REFRESH_WORKER_TIMEOUT_SECONDS": (
                    self.refresh_worker_timeout_seconds
                ),
                "CSIT_START_TRENDING": self.start_trending,
                "CSIT_START_REPORT": self.start_report,
                "CSIT_START_COVERAGE": self.start_coverage,
                "CSIT_START_STATISTICS": self.start_statistics,
                "CSIT_START_FAILURES": self.start_failures,
            },
        }


def _env_key(name: str) -> str:
    return f"CSIT_{name}"


def _raw_env(
        environ: Mapping[str, str],
        name: str,
        default_value: str
    ) -> str:
    return environ.get(_env_key(name), default_value)


def _add_error(
        errors: list[dict[str, Any]],
        *,
        name: str,
        value: str,
        message: str
    ) -> None:
    errors.append(
        {
            "field": _env_key(name),
            "value": value,
            "message": message,
        }
    )


def _parse_int(
        environ: Mapping[str, str],
        name: str,
        default_value: int,
        errors: list[dict[str, Any]],
        *,
        positive: bool = False
    ) -> int:
    raw_value = _raw_env(environ, name, str(default_value))
    try:
        value = int(raw_value.strip())
    except ValueError:
        _add_error(
            errors,
            name=name,
            value=raw_value,
            message="expected an integer",
        )
        return default_value

    if positive and value < 1:
        _add_error(
            errors,
            name=name,
            value=raw_value,
            message="expected a positive integer",
        )
        return default_value

    return value


def _parse_bool(
        environ: Mapping[str, str],
        name: str,
        default_value: bool,
        errors: list[dict[str, Any]]
    ) -> bool:
    raw_value = _raw_env(environ, name, str(default_value))
    normalized = raw_value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False

    _add_error(
        errors,
        name=name,
        value=raw_value,
        message="expected one of true, yes, y, 1, false, no, n, 0",
    )
    return default_value


def _parse_cors_allow_origins(
        environ: Mapping[str, str],
        errors: list[dict[str, Any]]
    ) -> tuple[str, ...]:
    raw_value = _raw_env(environ, "CORS_ALLOW_ORIGINS", C.CORS_ALLOW_ORIGINS)
    origins = tuple(item.strip() for item in raw_value.split(","))
    non_empty_origins = tuple(origin for origin in origins if origin)

    if not non_empty_origins or len(non_empty_origins) != len(origins):
        _add_error(
            errors,
            name="CORS_ALLOW_ORIGINS",
            value=raw_value,
            message="expected '*' or comma-separated http(s) origins",
        )
        return ("*",)

    if "*" in non_empty_origins:
        if non_empty_origins == ("*",):
            return non_empty_origins
        _add_error(
            errors,
            name="CORS_ALLOW_ORIGINS",
            value=raw_value,
            message="wildcard '*' must be the only configured origin",
        )
        return ("*",)

    invalid_origins = [
        origin for origin in non_empty_origins
        if not origin.startswith(("http://", "https://"))
    ]
    if invalid_origins:
        _add_error(
            errors,
            name="CORS_ALLOW_ORIGINS",
            value=raw_value,
            message="origins must start with http:// or https://",
        )
        return ("*",)

    return non_empty_origins


def get_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    """Return settings using the current ``Constants`` values."""

    env = os.environ if environ is None else environ
    validation_errors: list[dict[str, Any]] = []

    data_mode = _raw_env(env, "DATA_MODE", C.DATA_MODE).strip().lower()
    if data_mode not in VALID_DATA_MODES:
        _add_error(
            validation_errors,
            name="DATA_MODE",
            value=_raw_env(env, "DATA_MODE", C.DATA_MODE),
            message="expected 's3' or 'fixture'",
        )

    time_period = _parse_int(
        env,
        "TIME_PERIOD",
        C.MAX_TIME_PERIOD,
        validation_errors,
        positive=True,
    )
    refresh_interval_seconds = _parse_int(
        env,
        "REFRESH_INTERVAL_SECONDS",
        0,
        validation_errors,
    )
    max_pool_size = _parse_int(
        env,
        "MAX_POOL_SIZE",
        C.MAX_POOL_SIZE,
        validation_errors,
        positive=True,
    )
    telemetry_max_source_rows = _parse_int(
        env,
        "TELEMETRY_MAX_SOURCE_ROWS",
        DEFAULT_MAX_TELEMETRY_SOURCE_ROWS,
        validation_errors,
        positive=True,
    )
    telemetry_max_samples = _parse_int(
        env,
        "TELEMETRY_MAX_SAMPLES",
        DEFAULT_MAX_TELEMETRY_SAMPLES,
        validation_errors,
        positive=True,
    )
    telemetry_query_max_concurrent = _parse_int(
        env,
        "TELEMETRY_QUERY_MAX_CONCURRENT",
        1,
        validation_errors,
        positive=True,
    )
    telemetry_query_queue_timeout_seconds = _parse_int(
        env,
        "TELEMETRY_QUERY_QUEUE_TIMEOUT_SECONDS",
        5,
        validation_errors,
        positive=True,
    )
    telemetry_query_timeout_seconds = _parse_int(
        env,
        "TELEMETRY_QUERY_TIMEOUT_SECONDS",
        30,
        validation_errors,
        positive=True,
    )
    telemetry_query_max_source_rows = _parse_int(
        env,
        "TELEMETRY_QUERY_MAX_SOURCE_ROWS",
        2000,
        validation_errors,
        positive=True,
    )
    telemetry_query_max_samples = _parse_int(
        env,
        "TELEMETRY_QUERY_MAX_SAMPLES",
        20_000,
        validation_errors,
        positive=True,
    )
    telemetry_query_cache_entries = _parse_int(
        env,
        "TELEMETRY_QUERY_CACHE_ENTRIES",
        256,
        validation_errors,
        positive=True,
    )
    telemetry_query_max_encoded_bytes = _parse_int(
        env,
        "TELEMETRY_QUERY_MAX_ENCODED_BYTES",
        134_217_728,
        validation_errors,
        positive=True,
    )
    telemetry_query_max_decoded_bytes = _parse_int(
        env,
        "TELEMETRY_QUERY_MAX_DECODED_BYTES",
        536_870_912,
        validation_errors,
        positive=True,
    )
    telemetry_worker_memory_limit_bytes = _parse_int(
        env,
        "TELEMETRY_WORKER_MEMORY_LIMIT_BYTES",
        2_147_483_648,
        validation_errors,
        positive=True,
    )
    query_max_concurrent = _parse_int(
        env,
        "QUERY_MAX_CONCURRENT",
        1,
        validation_errors,
        positive=True,
    )
    query_queue_timeout_seconds = _parse_int(
        env,
        "QUERY_QUEUE_TIMEOUT_SECONDS",
        5,
        validation_errors,
        positive=True,
    )
    query_heavy_row_threshold = _parse_int(
        env,
        "QUERY_HEAVY_ROW_THRESHOLD",
        100_000,
        validation_errors,
        positive=True,
    )
    query_memory_soft_limit_percent = _parse_int(
        env,
        "QUERY_MEMORY_SOFT_LIMIT_PERCENT",
        75,
        validation_errors,
        positive=True,
    )
    if not 1 <= query_memory_soft_limit_percent <= 99:
        _add_error(
            validation_errors,
            name="QUERY_MEMORY_SOFT_LIMIT_PERCENT",
            value=str(query_memory_soft_limit_percent),
            message="expected an integer between 1 and 99",
        )
        query_memory_soft_limit_percent = 75
    refresh_memory_limit_percent = _parse_int(
        env,
        "REFRESH_MEMORY_LIMIT_PERCENT",
        85,
        validation_errors,
        positive=True,
    )
    if not 1 <= refresh_memory_limit_percent <= 99:
        _add_error(
            validation_errors,
            name="REFRESH_MEMORY_LIMIT_PERCENT",
            value=str(refresh_memory_limit_percent),
            message="expected an integer between 1 and 99",
        )
        refresh_memory_limit_percent = 85
    snapshot_refresh_max_age_seconds = _parse_int(
        env,
        "SNAPSHOT_REFRESH_MAX_AGE_SECONDS",
        0,
        validation_errors,
    )
    refresh_worker_timeout_seconds = _parse_int(
        env,
        "REFRESH_WORKER_TIMEOUT_SECONDS",
        1800,
        validation_errors,
        positive=True,
    )
    s3_read_max_attempts = _parse_int(
        env,
        "S3_READ_MAX_ATTEMPTS",
        C.S3_READ_MAX_ATTEMPTS,
        validation_errors,
        positive=True,
    )
    s3_read_retry_base_seconds = _parse_int(
        env,
        "S3_READ_RETRY_BASE_SECONDS",
        C.S3_READ_RETRY_BASE_SECONDS,
        validation_errors,
        positive=True,
    )
    cors_allow_origins = _parse_cors_allow_origins(env, validation_errors)

    return AppSettings(
        server_name="csit_mcp",
        server_version="1.0.0",
        server_description="A FastMCP server providing FD.io CSIT data.",
        public_tags=frozenset({"fd.io", "public"}),
        mcp_path=C.MCP_PATH,
        data_mode=data_mode,
        refresh_interval_seconds=refresh_interval_seconds,
        cors_allow_origins=cors_allow_origins,
        data_spec_file=C.DATA_SPEC_FILE,
        max_time_period=C.MAX_TIME_PERIOD,
        time_period=time_period,
        log_format=C.LOG_FORMAT,
        log_date_format=C.LOG_DATE_FORMAT,
        log_level=C.LOG_LEVEL,
        start_failures=_parse_bool(
            env, "START_FAILURES", C.START_FAILURES, validation_errors
        ),
        start_statistics=_parse_bool(
            env, "START_STATISTICS", C.START_STATISTICS, validation_errors
        ),
        start_trending=_parse_bool(
            env, "START_TRENDING", C.START_TRENDING, validation_errors
        ),
        start_report=_parse_bool(
            env, "START_REPORT", C.START_REPORT, validation_errors
        ),
        start_coverage=_parse_bool(
            env, "START_COVERAGE", C.START_COVERAGE, validation_errors
        ),
        news_title=C.NEWS_TITLE,
        stats_title=C.STATS_TITLE,
        trend_title=C.TREND_TITLE,
        report_title=C.REPORT_TITLE,
        coverage_title=C.COVERAGE_TITLE,
        max_pool_size=max_pool_size,
        telemetry_max_source_rows=telemetry_max_source_rows,
        telemetry_max_samples=telemetry_max_samples,
        telemetry_query_max_concurrent=telemetry_query_max_concurrent,
        telemetry_query_queue_timeout_seconds=(
            telemetry_query_queue_timeout_seconds
        ),
        telemetry_query_timeout_seconds=telemetry_query_timeout_seconds,
        telemetry_query_max_source_rows=telemetry_query_max_source_rows,
        telemetry_query_max_samples=telemetry_query_max_samples,
        telemetry_query_cache_entries=telemetry_query_cache_entries,
        telemetry_query_max_encoded_bytes=telemetry_query_max_encoded_bytes,
        telemetry_query_max_decoded_bytes=telemetry_query_max_decoded_bytes,
        telemetry_worker_memory_limit_bytes=(
            telemetry_worker_memory_limit_bytes
        ),
        query_max_concurrent=query_max_concurrent,
        query_queue_timeout_seconds=query_queue_timeout_seconds,
        query_heavy_row_threshold=query_heavy_row_threshold,
        query_memory_soft_limit_percent=query_memory_soft_limit_percent,
        cache_snapshot_path=_raw_env(env, "CACHE_SNAPSHOT_PATH", "").strip(),
        s3_read_max_attempts=s3_read_max_attempts,
        s3_read_retry_base_seconds=s3_read_retry_base_seconds,
        refresh_memory_limit_percent=refresh_memory_limit_percent,
        snapshot_refresh_max_age_seconds=snapshot_refresh_max_age_seconds,
        refresh_worker_timeout_seconds=refresh_worker_timeout_seconds,
        validation_errors=tuple(validation_errors),
    )
