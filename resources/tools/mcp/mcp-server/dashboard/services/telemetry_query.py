"""Bounded authoritative telemetry time-series queries."""

from __future__ import annotations

from collections import OrderedDict, defaultdict
import json
import math
import threading
from time import monotonic, perf_counter
from typing import Any, Mapping
from uuid import uuid4

import pandas as pd

from .observability import log_event, process_rss_bytes
from .memory import estimated_python_heap_bytes
from .serialization import MAX_SERIALIZED_RESPONSE_BYTES, validation_error_payload
from .telemetry import TELEMETRY_PARSER_VERSION, canonical_telemetry_label
from .telemetry_locator import (
    build_telemetry_locator,
    raw_telemetry_frame,
    resolve_telemetry_rows,
)
from .telemetry_worker import run_telemetry_decode_worker


DEFAULT_TIMESERIES_LIMIT = 1000
MAX_TIMESERIES_LIMIT = 5000
MAX_SELECTED_SERIES = 20
MAX_SELECTED_NODES = 100
MAX_RESPONSE_CACHE_BYTES = 8_000_000
MAX_SAMPLE_CACHE_BYTES = 32_000_000
VALID_AGGREGATIONS = {"per_run", "daily_mean"}

SEMANTIC_METRICS: dict[str, dict[str, Any]] = {
    "cycles_per_packet": {
        "source_metrics": (
            "vpp.inst_and_clock.clocks_per_packets",
            "vpp.runtime.clocks",
        ),
        "unit": "cycles/packet",
        "preferred_direction": "lower",
        "source_label_policies": {
            "vpp.inst_and_clock.clocks_per_packets": {},
            "vpp.runtime.clocks": {
                "required_if_present": {"state": ("active",)},
            },
        },
        "description": (
            "VPP cycles per packet. Prefer the direct inst_and_clock metric; "
            "fall back to the per-node runtime clocks metric."
        ),
    },
}


class TelemetryQueryService:
    """Decode only source rows selected for one bounded telemetry query."""

    def __init__(self, *, settings, trending_service=None) -> None:
        self._settings = settings
        self._trending = trending_service
        self._semaphore = threading.BoundedSemaphore(
            settings.telemetry_query_max_concurrent
        )
        self._lock = threading.Lock()
        self._active_queries = 0
        self._sample_cache: OrderedDict[
            tuple[Any, ...], dict[str, Any]
        ] = OrderedDict()
        self._response_cache: OrderedDict[tuple[Any, ...], dict[str, Any]] = (
            OrderedDict()
        )
        self._response_cache_sizes: dict[tuple[Any, ...], int] = {}
        self._response_cache_bytes = 0
        self._sample_cache_sizes: dict[tuple[Any, ...], int] = {}
        self._sample_cache_bytes = 0

    def timeseries_payload(
            self,
            data: pd.DataFrame,
            status: Mapping[str, Any],
            *,
            telemetry_source: pd.DataFrame | None = None,
            telemetry_locator: pd.DataFrame | None = None,
            dataset: Any,
            series: Any,
            metric: Any,
            node_names: Any = None,
            testbed: Any = None,
            days: Any = 30,
            start_time: Any = None,
            end_time: Any = None,
            passed: Any = True,
            aggregation: Any = "per_run",
            offset: Any = 0,
            limit: Any = DEFAULT_TIMESERIES_LIMIT,
        ) -> dict[str, Any]:
        """Return complete targeted telemetry points or a structured error."""

        normalized, errors = self._validate(
            dataset=dataset,
            series=series,
            metric=metric,
            node_names=node_names,
            testbed=testbed,
            days=days,
            start_time=start_time,
            end_time=end_time,
            passed=passed,
            aggregation=aggregation,
            offset=offset,
            limit=limit,
        )
        if errors:
            return validation_error_payload(errors, normalized)
        query_id = uuid4().hex

        if telemetry_source is None:
            fallback_data = data.copy(deep=False)
            telemetry_source = raw_telemetry_frame(fallback_data)
        if telemetry_locator is None:
            telemetry_locator = build_telemetry_locator(
                data,
                telemetry_source,
            )
        generation = (
            id(data), status.get("last_success_at"), len(data),
            TELEMETRY_PARSER_VERSION,
        )
        cache_key = (
            generation,
            tuple(normalized["series"]),
            normalized["metric"],
            tuple(normalized["node_names"]),
            normalized["testbed"],
            normalized["start_time"],
            normalized["end_time"],
            normalized["aggregation"],
            normalized["offset"],
            normalized["limit"],
        )
        cached = self._cache_get(self._response_cache, cache_key)
        if cached is not None:
            cached["query_cache_hit"] = True
            log_event(
                "telemetry_query_cache_hit",
                query_id=query_id,
                query=self._query_context(normalized),
                cache_generation=status.get("last_success_at"),
                returned_count=cached.get("returned_count"),
                rss_bytes=process_rss_bytes(),
            )
            return cached

        acquired = self._semaphore.acquire(
            timeout=self._settings.telemetry_query_queue_timeout_seconds
        )
        if not acquired:
            payload = {
                "error": "server_busy",
                "message": (
                    "Telemetry query capacity is currently in use. Retry the "
                    "same bounded request after the suggested delay."
                ),
                "retry_after_seconds": 2,
                "filters": normalized,
            }
            log_event(
                "telemetry_query_rejected",
                query_id=query_id,
                reason="concurrency_limit",
                query=self._query_context(normalized),
                active_queries=self._active_query_count(),
                rss_bytes=process_rss_bytes(),
            )
            return payload

        started = perf_counter()
        deadline = monotonic() + self._settings.telemetry_query_timeout_seconds
        with self._lock:
            self._active_queries += 1
            active_queries = self._active_queries
        log_event(
            "telemetry_query_started",
            query_id=query_id,
            query=self._query_context(normalized),
            cache_generation=status.get("last_success_at"),
            active_queries=active_queries,
            rss_bytes=process_rss_bytes(),
        )
        outcome = "exception"
        result_context: dict[str, Any] = {}
        try:
            cached = self._cache_get(self._response_cache, cache_key)
            if cached is not None:
                cached["query_cache_hit"] = True
                outcome = "success"
                result_context = self._result_context(cached)
                return cached
            payload = self._execute(
                data,
                telemetry_source,
                telemetry_locator,
                status,
                generation=generation,
                filters=normalized,
                deadline=deadline,
                query_id=query_id,
            )
            if "error" not in payload:
                self._cache_put(self._response_cache, cache_key, payload)
            outcome = str(payload.get("error") or "success")
            result_context = self._result_context(payload)
            return payload
        finally:
            duration = round(perf_counter() - started, 3)
            with self._lock:
                self._active_queries -= 1
                active_queries = self._active_queries
            self._semaphore.release()
            log_event(
                "telemetry_query_completed",
                query_id=query_id,
                query=self._query_context(normalized),
                cache_generation=status.get("last_success_at"),
                duration_seconds=duration,
                outcome=outcome,
                active_queries=active_queries,
                rss_bytes=process_rss_bytes(),
                **result_context,
            )

    def run_guarded_diagnostic(
            self,
            tool_name: str,
            dataset: str,
            callback,
        ):
        """Bound legacy sampled telemetry work with the shared query gate."""

        acquired = self._semaphore.acquire(
            timeout=self._settings.telemetry_query_queue_timeout_seconds
        )
        if not acquired:
            log_event(
                "telemetry_query_rejected",
                reason="concurrency_limit",
                query={"tool": tool_name, "dataset": dataset},
                active_queries=self._active_query_count(),
                rss_bytes=process_rss_bytes(),
            )
            return {
                "error": "server_busy",
                "message": (
                    "Telemetry query capacity is currently in use. Retry the "
                    "request after the suggested delay."
                ),
                "retry_after_seconds": 2,
                "dataset": dataset,
            }
        started = perf_counter()
        with self._lock:
            self._active_queries += 1
            active_queries = self._active_queries
        log_event(
            "telemetry_query_started",
            query={"tool": tool_name, "dataset": dataset},
            active_queries=active_queries,
            rss_bytes=process_rss_bytes(),
        )
        outcome = "exception"
        try:
            response = callback()
            outcome = "success"
            return response
        finally:
            with self._lock:
                self._active_queries -= 1
                active_queries = self._active_queries
            self._semaphore.release()
            log_event(
                "telemetry_query_completed",
                query={"tool": tool_name, "dataset": dataset},
                duration_seconds=round(perf_counter() - started, 3),
                outcome=outcome,
                active_queries=active_queries,
                rss_bytes=process_rss_bytes(),
            )

    def status_snapshot(self) -> dict[str, Any]:
        """Return additive operational metadata for telemetry query limits."""

        return {
            "active_queries": self._active_query_count(),
            "max_concurrent_queries": (
                self._settings.telemetry_query_max_concurrent
            ),
            "queue_timeout_seconds": (
                self._settings.telemetry_query_queue_timeout_seconds
            ),
            "query_timeout_seconds": (
                self._settings.telemetry_query_timeout_seconds
            ),
            "max_source_rows": self._settings.telemetry_query_max_source_rows,
            "max_samples": self._settings.telemetry_query_max_samples,
            "cache_entries": self._settings.telemetry_query_cache_entries,
            "response_cache_max_bytes": MAX_RESPONSE_CACHE_BYTES,
            "sample_cache_max_bytes": MAX_SAMPLE_CACHE_BYTES,
            "max_encoded_bytes": (
                self._settings.telemetry_query_max_encoded_bytes
            ),
            "max_decoded_bytes": (
                self._settings.telemetry_query_max_decoded_bytes
            ),
            "worker_memory_limit_bytes": (
                self._settings.telemetry_worker_memory_limit_bytes
            ),
            "worker_process_isolation": True,
        }

    def memory_snapshot(self) -> dict[str, Any]:
        """Return retained query-cache estimates without copying cache values."""

        with self._lock:
            return {
                "estimated_bytes": (
                    self._response_cache_bytes + self._sample_cache_bytes
                ),
                "response_cache_bytes": self._response_cache_bytes,
                "sample_cache_bytes": self._sample_cache_bytes,
                "response_cache_entries": len(self._response_cache),
                "sample_cache_entries": len(self._sample_cache),
            }

    def clear(self) -> None:
        """Release values associated with superseded dataframe generations."""

        with self._lock:
            self._sample_cache.clear()
            self._response_cache.clear()
            self._response_cache_sizes.clear()
            self._sample_cache_sizes.clear()
            self._response_cache_bytes = 0
            self._sample_cache_bytes = 0

    def _execute(
            self,
            data: pd.DataFrame,
            telemetry_source: pd.DataFrame,
            telemetry_locator: pd.DataFrame,
            status: Mapping[str, Any],
            *,
            generation: tuple[Any, ...],
            filters: dict[str, Any],
            deadline: float,
            query_id: str,
        ) -> dict[str, Any]:
        requested_start = pd.Timestamp(filters["start_time"])
        requested_end = pd.Timestamp(filters["end_time"])
        resolution = resolve_telemetry_rows(
            telemetry_locator,
            series=filters["series"],
            testbed=filters["testbed"],
            start_time=requested_start,
            end_time=requested_end,
        )
        matches = resolution["matches"]
        source_rows = list(dict.fromkeys(matches["_source_row"].tolist()))
        if len(source_rows) > self._settings.telemetry_query_max_source_rows:
            return self._limit_error(
                "source_rows",
                len(source_rows),
                self._settings.telemetry_query_max_source_rows,
                filters,
            )

        metric_definition = SEMANTIC_METRICS.get(filters["metric"])
        source_metrics = tuple(
            metric_definition["source_metrics"]
            if metric_definition else (filters["metric"],)
        )
        by_source: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for match in matches.to_dict(orient="records"):
            by_source[match["_source_row"]].append(match)

        if telemetry_source.empty:
            raw_by_source = pd.Series(dtype=object)
        elif telemetry_source.index.name == "_source_row":
            raw_by_source = telemetry_source["telemetry"]
        else:
            raw_by_source = telemetry_source.set_index("_source_row")[
                "telemetry"
            ]
        encoded_bytes = sum(
            _encoded_telemetry_size(raw_by_source.get(source_row))
            for source_row in source_rows
        )
        if encoded_bytes > self._settings.telemetry_query_max_encoded_bytes:
            return self._limit_error(
                "encoded_bytes",
                encoded_bytes,
                self._settings.telemetry_query_max_encoded_bytes,
                filters,
            )

        worker_result = self._samples_for_rows(
            generation,
            source_rows,
            raw_by_source,
            source_metrics,
            deadline=deadline,
            query_id=query_id,
        )
        worker_status = worker_result.get("status")
        if worker_status == "limit_exceeded":
            return self._limit_error(
                str(worker_result.get("resource") or "worker_budget"),
                int(worker_result.get("observed") or 0),
                int(worker_result.get("maximum") or 0),
                filters,
            )
        if worker_status == "timeout":
            return {
                "error": "query_timeout",
                "message": "Telemetry decode worker exceeded its deadline.",
                "timeout_seconds": self._settings.telemetry_query_timeout_seconds,
                "filters": filters,
            }
        if worker_status != "ok":
            return {
                "error": "telemetry_worker_failed",
                "message": str(worker_result.get("message") or (
                    "The isolated telemetry worker failed."
                )),
                "reason": worker_status,
                "filters": filters,
            }

        row_results = {
            int(item["source_row"]): item
            for item in worker_result.get("rows", [])
        }
        records: list[dict[str, Any]] = []
        decode_errors: list[dict[str, Any]] = []
        parse_errors: list[dict[str, Any]] = []
        decoded_rows = 0
        decoded_bytes = int(worker_result.get("decoded_bytes") or 0)
        parsed_metric_sample_count = 0
        node_matched_sample_count = 0
        semantic_policy_matched_sample_count = 0
        available_node_names: set[str] = set()
        parsed_by_source_metric: dict[str, int] = defaultdict(int)
        for source_row in source_rows:
            if monotonic() > deadline:
                return {
                    "error": "query_timeout",
                    "message": "Telemetry query exceeded its execution deadline.",
                    "timeout_seconds": (
                        self._settings.telemetry_query_timeout_seconds
                    ),
                    "filters": filters,
                }
            source = data.iloc[source_row]
            row_result = row_results.get(int(source_row), {})
            samples = row_result.get("samples", [])
            row_decode_errors = row_result.get("decode_errors", [])
            row_parse_errors = row_result.get("parse_errors", [])
            truncated = bool(row_result.get("truncated"))
            decoded_rows += 1
            if row_decode_errors:
                decode_errors.append({
                    "source_row": _safe_value(source_row),
                    "errors": list(row_decode_errors[:3]),
                })
            if row_parse_errors:
                parse_errors.append({
                    "source_row": _safe_value(source_row),
                    "errors": list(row_parse_errors[:3]),
                })
            if truncated:
                return self._limit_error(
                    "samples",
                    self._settings.telemetry_query_max_samples + 1,
                    self._settings.telemetry_query_max_samples,
                    filters,
                )
            for sample in samples:
                labels = sample.get("labels") or {}
                parsed_metric_sample_count += 1
                source_metric = str(sample.get("metric_name") or "")
                parsed_by_source_metric[source_metric] += 1
                node_name = canonical_telemetry_label(
                    labels.get("node_name")
                )
                if node_name:
                    available_node_names.add(node_name)
                if not self._node_matches(
                        labels, node_names=filters["node_names"]
                    ):
                    continue
                node_matched_sample_count += 1
                if not self._semantic_policy_matches(
                        sample, labels, metric_definition=metric_definition
                    ):
                    continue
                semantic_policy_matched_sample_count += 1
                for match in by_source[source_row]:
                    records.append(self._point(
                        source,
                        match,
                        sample,
                        metric=filters["metric"],
                        metric_definition=metric_definition,
                    ))
                    if len(records) > self._settings.telemetry_query_max_samples:
                        return self._limit_error(
                            "samples",
                            len(records),
                            self._settings.telemetry_query_max_samples,
                            filters,
                        )

        records = self._deduplicate_semantic_records(
            records,
            metric_definition=metric_definition,
            source_metrics=source_metrics,
        )
        records_by_source_metric: dict[str, int] = defaultdict(int)
        for record in records:
            records_by_source_metric[str(record.get("source_metric") or "")] += 1
        if filters["aggregation"] == "daily_mean":
            records = self._daily_mean(records)
        records.sort(key=lambda item: (
            str(item.get("start_time") or ""),
            str(item.get("series_id") or ""),
            str(item.get("node_name") or ""),
            str(item.get("hostname") or ""),
            str(item.get("thread_id") or ""),
            str(item.get("thread_name") or ""),
        ))

        offset = filters["offset"]
        page = records[offset:offset + filters["limit"]]
        estimated_page_bytes = len(json.dumps(page).encode("utf-8"))
        if estimated_page_bytes > int(MAX_SERIALIZED_RESPONSE_BYTES * 0.85):
            return self._limit_error(
                "response_bytes",
                estimated_page_bytes,
                int(MAX_SERIALIZED_RESPONSE_BYTES * 0.85),
                filters,
            )
        returned_count = len(page)
        has_more = offset + returned_count < len(records)
        reasons: list[str] = []
        cache_reference = pd.to_datetime(
            status.get("last_success_at"), errors="coerce", utc=True
        )
        configured_horizon = (
            cache_reference - pd.Timedelta(
                days=self._settings.effective_time_period()
            )
            if not pd.isna(cache_reference) else None
        )
        if (
            configured_horizon is not None and
            requested_start < configured_horizon
        ):
            reasons.append("requested_window_exceeds_loaded_cache_horizon")
        if resolution["unknown_series"]:
            reasons.append("unknown_series")
        if decode_errors:
            reasons.append("source_rows_with_decode_errors")
        if parse_errors:
            reasons.append("source_rows_with_parse_errors")
        if not source_rows:
            reasons.append("no_source_rows_in_window")
        elif parsed_metric_sample_count == 0:
            reasons.append("source_metric_not_found")
        elif filters["node_names"] and node_matched_sample_count == 0:
            reasons.append("requested_nodes_not_found")
        elif semantic_policy_matched_sample_count == 0:
            reasons.append("semantic_label_policy_no_match")
        elif not records:
            reasons.append("no_records_after_selection")

        bounded_node_names = sorted(available_node_names)[:50]

        completeness = {
            "complete": not reasons,
            "reasons": reasons,
            "authoritative_source_filter": True,
            "representative_index_used": False,
            "requested_start_time": filters["start_time"],
            "requested_end_time": filters["end_time"],
            "available_start_time": resolution["available_start_time"],
            "available_end_time": resolution["available_end_time"],
            "configured_cache_days": self._settings.effective_time_period(),
            "matched_source_row_count": len(source_rows),
            "decoded_source_row_count": decoded_rows,
            "encoded_source_bytes": encoded_bytes,
            "decoded_source_bytes": decoded_bytes,
            "decode_error_count": len(decode_errors),
            "parse_error_count": len(parse_errors),
            "truncated": False,
            "selection": {
                "parsed_source_metric_sample_count": (
                    parsed_metric_sample_count
                ),
                "node_matched_sample_count": node_matched_sample_count,
                "semantic_policy_matched_sample_count": (
                    semantic_policy_matched_sample_count
                ),
                "parsed_samples_by_source_metric": dict(
                    sorted(parsed_by_source_metric.items())
                ),
                "records_by_source_metric": dict(
                    sorted(records_by_source_metric.items())
                ),
                "available_node_names": bounded_node_names,
                "available_node_names_truncated": (
                    len(available_node_names) > len(bounded_node_names)
                ),
            },
        }
        return {
            "schema_version": 1,
            "dataset": "telemetry_timeseries",
            "source_dataset": filters["dataset"],
            "telemetry": True,
            "metric": filters["metric"],
            "metric_definition": (
                {
                    key: value
                    for key, value in metric_definition.items()
                    if key != "source_label_policies"
                }
                if metric_definition else None
            ),
            "total_row_count": len(data),
            "row_count": len(records),
            "returned_count": returned_count,
            "limit": filters["limit"],
            "offset": offset,
            "has_more": has_more,
            "next_offset": offset + returned_count if has_more else None,
            "freshness": status.get("last_success_at"),
            "data_status": status.get("status"),
            "filters": filters,
            "series": resolution["series"],
            "unknown_series": resolution["unknown_series"],
            "completeness": completeness,
            "errors": {
                "decode": decode_errors[:20],
                "parse": parse_errors[:20],
            },
            "columns": list(page[0]) if page else [],
            "records": page,
            "query_cache_hit": False,
        }

    def _samples_for_rows(
            self,
            generation: tuple[Any, ...],
            source_rows: list[Any],
            raw_by_source: pd.Series,
            metric_names: tuple[str, ...],
            *,
            deadline: float,
            query_id: str,
        ) -> dict[str, Any]:
        """Resolve cached rows and decode all misses in one isolated worker."""

        results: list[dict[str, Any]] = []
        missing: list[tuple[int, Any]] = []
        decoded_bytes = 0
        sample_count = 0
        for source_row in source_rows:
            normalized_row = int(source_row)
            cache_key = (generation, normalized_row, metric_names)
            cached = self._cache_get(self._sample_cache, cache_key)
            if cached is None:
                missing.append((
                    normalized_row,
                    _portable_telemetry(raw_by_source.get(source_row)),
                ))
                continue
            results.append(cached)
            decoded_bytes += int(cached.get("decoded_bytes") or 0)
            sample_count += len(cached.get("samples") or [])

        if decoded_bytes > self._settings.telemetry_query_max_decoded_bytes:
            return {
                "status": "limit_exceeded",
                "resource": "decoded_bytes",
                "observed": decoded_bytes,
                "maximum": self._settings.telemetry_query_max_decoded_bytes,
            }
        if sample_count > self._settings.telemetry_query_max_samples:
            return {
                "status": "limit_exceeded",
                "resource": "samples",
                "observed": sample_count,
                "maximum": self._settings.telemetry_query_max_samples,
            }

        if missing:
            timeout_seconds = deadline - monotonic()
            if timeout_seconds <= 0:
                return {
                    "status": "timeout",
                    "message": "Telemetry query exceeded its execution deadline.",
                }
            log_event(
                "telemetry_worker_started",
                query_id=query_id,
                source_row_count=len(missing),
                cached_source_row_count=len(results),
                decoded_bytes_remaining=(
                    self._settings.telemetry_query_max_decoded_bytes -
                    decoded_bytes
                ),
                samples_remaining=(
                    self._settings.telemetry_query_max_samples - sample_count
                ),
                memory_limit_bytes=(
                    self._settings.telemetry_worker_memory_limit_bytes
                ),
            )
            worker_result = run_telemetry_decode_worker(
                missing,
                metric_names=metric_names,
                max_decoded_bytes=(
                    self._settings.telemetry_query_max_decoded_bytes -
                    decoded_bytes
                ),
                max_samples=(
                    self._settings.telemetry_query_max_samples - sample_count
                ),
                timeout_seconds=timeout_seconds,
                memory_limit_bytes=(
                    self._settings.telemetry_worker_memory_limit_bytes
                ),
            )
            log_event(
                "telemetry_worker_completed",
                query_id=query_id,
                status=worker_result.get("status"),
                worker_pid=worker_result.get("worker_pid"),
                worker_exit_code=worker_result.get("worker_exit_code"),
                duration_seconds=worker_result.get("duration_seconds"),
                decoded_bytes=worker_result.get("decoded_bytes"),
                sample_count=worker_result.get("sample_count"),
                resource=worker_result.get("resource"),
            )
            if worker_result.get("status") != "ok":
                return worker_result
            for item in worker_result.get("rows", []):
                cache_key = (
                    generation,
                    int(item["source_row"]),
                    metric_names,
                )
                self._cache_put(self._sample_cache, cache_key, item)
                results.append(item)
            decoded_bytes += int(worker_result.get("decoded_bytes") or 0)
            sample_count += int(worker_result.get("sample_count") or 0)

        order = {int(source_row): index for index, source_row in enumerate(source_rows)}
        results.sort(key=lambda item: order.get(int(item["source_row"]), len(order)))
        return {
            "status": "ok",
            "rows": results,
            "decoded_bytes": decoded_bytes,
            "sample_count": sample_count,
        }

    @staticmethod
    def _node_matches(
            labels: Mapping[str, Any],
            *,
            node_names: list[str],
        ) -> bool:
        if not node_names:
            return True
        node_name = canonical_telemetry_label(labels.get("node_name"))
        return node_name in node_names

    @staticmethod
    def _semantic_policy_matches(
            sample: Mapping[str, Any],
            labels: Mapping[str, Any],
            *,
            metric_definition: Mapping[str, Any] | None,
        ) -> bool:
        if metric_definition is None:
            return True
        policies = metric_definition.get("source_label_policies", {})
        policy = policies.get(str(sample.get("metric_name") or ""), {})
        for key, expected_values in policy.get(
                "required_if_present", {}
            ).items():
            if key in labels:
                actual = canonical_telemetry_label(labels[key])
                if actual not in expected_values:
                    return False
        return True

    @staticmethod
    def _point(
            source: pd.Series,
            match: Mapping[str, Any],
            sample: Mapping[str, Any],
            *,
            metric: str,
            metric_definition: Mapping[str, Any] | None,
        ) -> dict[str, Any]:
        labels = sample.get("labels") or {}
        value = _finite_number(sample.get("value"))
        return {
            "series_id": str(match["series_id"]),
            "series_name": str(match["name"]),
            "test_type": str(match["test_type"]),
            "metric": metric,
            "source_metric": str(sample.get("metric_name") or ""),
            "node_name": _optional_text(canonical_telemetry_label(
                labels.get("node_name")
            )),
            "hostname": _optional_text(canonical_telemetry_label(
                labels.get("hostname")
            )),
            "thread_id": _optional_text(canonical_telemetry_label(
                labels.get("thread_id")
            )),
            "thread_name": _optional_text(canonical_telemetry_label(
                labels.get("thread_name")
            )),
            "thread_lcore": _optional_text(canonical_telemetry_label(
                labels.get("thread_lcore")
            )),
            "value": value,
            "unit": (
                metric_definition.get("unit")
                if metric_definition else _optional_text(sample.get("unit"))
            ),
            "start_time": _optional_text(source.get("start_time")),
            "telemetry_timestamp": _optional_text(sample.get("timestamp")),
            "job": _optional_text(source.get("job")),
            "build": _integer(source.get("build")),
            "test_id": _optional_text(source.get("test_id")),
            "dut_type": _optional_text(source.get("dut_type")),
            "dut_version": _optional_text(source.get("dut_version")),
            "hosts": _hosts(source.get("hosts")),
            "label_key": _optional_text(sample.get("label_key")),
        }

    @staticmethod
    def _deduplicate_semantic_records(
            records: list[dict[str, Any]],
            *,
            metric_definition: Mapping[str, Any] | None,
            source_metrics: tuple[str, ...],
        ) -> list[dict[str, Any]]:
        if metric_definition is None:
            return records
        priority = {name: index for index, name in enumerate(source_metrics)}
        selected: dict[tuple[Any, ...], dict[str, Any]] = {}
        for record in records:
            key = (
                record.get("series_id"), record.get("start_time"),
                record.get("job"), record.get("build"),
                record.get("node_name"), record.get("hostname"),
                record.get("thread_id") or record.get("thread_name") or
                record.get("thread_lcore"),
            )
            current = selected.get(key)
            if current is None or priority.get(
                    record["source_metric"], len(priority)
                ) < priority.get(current["source_metric"], len(priority)):
                selected[key] = record
        return list(selected.values())

    @staticmethod
    def _daily_mean(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            timestamp = pd.to_datetime(
                record.get("start_time"), errors="coerce", utc=True
            )
            if pd.isna(timestamp):
                continue
            key = (
                timestamp.strftime("%Y-%m-%d"), record.get("series_id"),
                record.get("series_name"), record.get("test_type"),
                record.get("metric"), record.get("source_metric"),
                record.get("node_name"), record.get("hostname"),
                record.get("thread_id"), record.get("thread_name"),
                record.get("unit"),
            )
            grouped[key].append(record)
        output = []
        for key, group in grouped.items():
            values = [item["value"] for item in group if item["value"] is not None]
            if not values:
                continue
            first = group[0]
            output.append({
                **first,
                "start_time": f"{key[0]}T00:00:00+00:00",
                "value": sum(values) / len(values),
                "sample_count": len(values),
                "job": None,
                "build": None,
                "test_id": None,
                "telemetry_timestamp": None,
            })
        return output

    def _validate(self, **values: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        errors: list[dict[str, Any]] = []
        dataset = str(values["dataset"] or "").strip().lower()
        if dataset != "trending":
            errors.append(_field_error(
                "dataset", values["dataset"],
                "dataset must be 'trending' for series-based telemetry queries.",
            ))
        series = _string_list(values["series"])
        if not series or len(series) > MAX_SELECTED_SERIES:
            errors.append(_field_error(
                "series", values["series"],
                f"series must contain between 1 and {MAX_SELECTED_SERIES} IDs.",
            ))
        metric = str(values["metric"] or "").strip()
        if not metric:
            errors.append(_field_error(
                "metric", values["metric"], "metric must not be empty."
            ))
        nodes = list(dict.fromkeys(
            canonical_telemetry_label(node)
            for node in _string_list(values["node_names"])
            if canonical_telemetry_label(node)
        ))
        if len(nodes) > MAX_SELECTED_NODES:
            errors.append(_field_error(
                "node_names", values["node_names"],
                f"node_names may contain at most {MAX_SELECTED_NODES} values.",
            ))
        days = _integer(values["days"])
        if days is None or days < 1 or days > self._settings.max_time_period:
            errors.append(_field_error(
                "days", values["days"],
                f"days must be between 1 and {self._settings.max_time_period}.",
            ))
            days = 30
        aggregation = str(values["aggregation"] or "").strip().lower()
        if aggregation not in VALID_AGGREGATIONS:
            errors.append(_field_error(
                "aggregation", values["aggregation"],
                "aggregation must be 'per_run' or 'daily_mean'.",
            ))
        passed = _boolean(values["passed"])
        if passed is not True:
            errors.append(_field_error(
                "passed", values["passed"],
                "telemetry_timeseries currently supports passed=true only.",
            ))
        offset = _integer(values["offset"])
        if offset is None or offset < 0:
            errors.append(_field_error(
                "offset", values["offset"], "offset must be an integer >= 0."
            ))
            offset = 0
        limit = _integer(values["limit"])
        if limit is None or not 1 <= limit <= MAX_TIMESERIES_LIMIT:
            errors.append(_field_error(
                "limit", values["limit"],
                f"limit must be between 1 and {MAX_TIMESERIES_LIMIT}.",
            ))
            limit = DEFAULT_TIMESERIES_LIMIT
        parsed_end = _timestamp(values["end_time"])
        parsed_start = _timestamp(values["start_time"])
        if values["end_time"] not in (None, "") and parsed_end is None:
            errors.append(_field_error(
                "end_time", values["end_time"],
                "end_time must be an ISO-8601 timestamp.",
            ))
        if values["start_time"] not in (None, "") and parsed_start is None:
            errors.append(_field_error(
                "start_time", values["start_time"],
                "start_time must be an ISO-8601 timestamp.",
            ))
        end = parsed_end or pd.Timestamp.now(tz="UTC")
        start = parsed_start or end - pd.Timedelta(days=days)
        if start > end:
            errors.append(_field_error(
                "start_time", values["start_time"],
                "start_time must not be later than end_time.",
            ))
        return {
            "dataset": dataset,
            "series": series,
            "metric": metric,
            "node_names": nodes,
            "testbed": _optional_text(values["testbed"]),
            "days": days,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "passed": True,
            "aggregation": aggregation,
            "offset": offset,
            "limit": limit,
        }, errors

    @staticmethod
    def _limit_error(
            resource: str,
            requested: int,
            maximum: int,
            filters: Mapping[str, Any],
        ) -> dict[str, Any]:
        return {
            "error": "query_too_large",
            "message": (
                "The authoritative telemetry query exceeds its processing "
                "budget; no partial analysis was returned."
            ),
            "resource": resource,
            "requested": requested,
            "maximum": maximum,
            "filters": dict(filters),
            "suggestions": [
                "Reduce the time window or number of selected series.",
                "Select only the VPP node names required for the analysis.",
                "Use daily_mean aggregation for a smaller response.",
            ],
        }

    def _active_query_count(self) -> int:
        with self._lock:
            return self._active_queries

    def _cache_get(self, cache: OrderedDict, key: tuple[Any, ...]):
        with self._lock:
            value = cache.get(key)
            if value is None:
                return None
            cache.move_to_end(key)
            return dict(value)

    def _cache_put(self, cache: OrderedDict, key: tuple[Any, ...], value: Any) -> None:
        with self._lock:
            if cache is self._response_cache:
                previous_size = self._response_cache_sizes.pop(key, 0)
                self._response_cache_bytes -= previous_size
                value_size = max(
                    len(json.dumps(value).encode("utf-8")),
                    estimated_python_heap_bytes(value),
                )
                self._response_cache_sizes[key] = value_size
                self._response_cache_bytes += value_size
            elif cache is self._sample_cache:
                previous_size = self._sample_cache_sizes.pop(key, 0)
                self._sample_cache_bytes -= previous_size
                value_size = max(
                    len(json.dumps(value).encode("utf-8")),
                    estimated_python_heap_bytes(value),
                )
                self._sample_cache_sizes[key] = value_size
                self._sample_cache_bytes += value_size
            cache[key] = dict(value)
            cache.move_to_end(key)
            while (
                len(cache) > self._settings.telemetry_query_cache_entries or
                (
                    cache is self._response_cache and
                    self._response_cache_bytes > MAX_RESPONSE_CACHE_BYTES
                ) or (
                    cache is self._sample_cache and
                    self._sample_cache_bytes > MAX_SAMPLE_CACHE_BYTES
                )
            ):
                evicted_key, _ = cache.popitem(last=False)
                if cache is self._response_cache:
                    self._response_cache_bytes -= (
                        self._response_cache_sizes.pop(evicted_key, 0)
                    )
                elif cache is self._sample_cache:
                    self._sample_cache_bytes -= (
                        self._sample_cache_sizes.pop(evicted_key, 0)
                    )

    @staticmethod
    def _query_context(filters: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "dataset": filters.get("dataset"),
            "metric": filters.get("metric"),
            "series_count": len(filters.get("series") or []),
            "node_count": len(filters.get("node_names") or []),
            "testbed": filters.get("testbed"),
            "start_time": filters.get("start_time"),
            "end_time": filters.get("end_time"),
            "aggregation": filters.get("aggregation"),
            "offset": filters.get("offset"),
            "limit": filters.get("limit"),
        }

    @staticmethod
    def _result_context(payload: Mapping[str, Any]) -> dict[str, Any]:
        completeness = payload.get("completeness")
        if not isinstance(completeness, Mapping):
            completeness = {}
        selection = completeness.get("selection")
        if not isinstance(selection, Mapping):
            selection = {}
        return {
            "matched_source_row_count": completeness.get(
                "matched_source_row_count"
            ),
            "decoded_source_row_count": completeness.get(
                "decoded_source_row_count"
            ),
            "encoded_source_bytes": completeness.get("encoded_source_bytes"),
            "decoded_source_bytes": completeness.get("decoded_source_bytes"),
            "parsed_source_metric_sample_count": selection.get(
                "parsed_source_metric_sample_count"
            ),
            "node_matched_sample_count": selection.get(
                "node_matched_sample_count"
            ),
            "semantic_policy_matched_sample_count": selection.get(
                "semantic_policy_matched_sample_count"
            ),
            "row_count": payload.get("row_count"),
            "returned_count": payload.get("returned_count"),
            "complete": completeness.get("complete"),
        }


def _field_error(field: str, value: Any, message: str) -> dict[str, Any]:
    return {"field": field, "value": _safe_value(value), "message": message}


def _encoded_telemetry_size(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        return len(value.encode("utf-8"))
    if not isinstance(value, (list, tuple, set)) and hasattr(value, "tolist"):
        try:
            value = value.tolist()
        except (TypeError, ValueError):
            return len(str(value).encode("utf-8"))
    if isinstance(value, (list, tuple, set)):
        return sum(_encoded_telemetry_size(item) for item in value)
    if isinstance(value, bytes):
        return len(value)
    return len(str(value).encode("utf-8"))


def _portable_telemetry(value: Any) -> Any:
    """Return a spawn-safe raw telemetry value without dataframe references."""

    if value is None or isinstance(value, (str, bytes, list, tuple)):
        return value
    if hasattr(value, "as_py"):
        try:
            return value.as_py()
        except (TypeError, ValueError):
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except (TypeError, ValueError):
            pass
    return value


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    items = value if isinstance(value, (list, tuple, set)) else [value]
    return list(dict.fromkeys(
        text for item in items if (text := str(item).strip())
    ))


def _integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    if isinstance(value, float) and not value.is_integer():
        return None
    if isinstance(value, str) and str(parsed) != value.strip():
        return None
    return parsed


def _boolean(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    return None


def _timestamp(value: Any) -> pd.Timestamp | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        timestamp = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _finite_number(value: Any) -> float | int | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return int(number) if number.is_integer() else number


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    text = str(value).strip()
    return text or None


def _hosts(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return [value] if value else None
    if not isinstance(value, (list, tuple, set)) and hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, (list, tuple, set)):
        return [str(item) for item in value]
    return [str(value)]


def _safe_value(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple, set)):
        return [_safe_value(item) for item in value]
    return str(value)
