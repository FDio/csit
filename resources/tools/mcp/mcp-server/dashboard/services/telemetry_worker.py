"""Isolated OpenMetrics decoding for authoritative telemetry queries."""

from __future__ import annotations

import multiprocessing
import sys
from time import perf_counter
from typing import Any, Iterable

from .telemetry import decode_telemetry_cell, parse_openmetrics


def decode_telemetry_rows(
        rows: Iterable[tuple[int, Any]],
        *,
        metric_names: tuple[str, ...],
        max_decoded_bytes: int,
        max_samples: int,
    ) -> dict[str, Any]:
    """Decode selected source rows into bounded, JSON-ready sample records."""

    decoded_bytes = 0
    sample_count = 0
    results: list[dict[str, Any]] = []
    for source_row, telemetry in rows:
        remaining_bytes = max_decoded_bytes - decoded_bytes
        if remaining_bytes < 1:
            return _limit_result(
                results,
                resource="decoded_bytes",
                observed=decoded_bytes + 1,
                maximum=max_decoded_bytes,
            )
        decoded = decode_telemetry_cell(
            telemetry,
            max_decoded_bytes=remaining_bytes,
        )
        decoded_bytes += decoded.decoded_bytes
        if decoded.limit_exceeded:
            return _limit_result(
                results,
                resource="decoded_bytes",
                observed=decoded_bytes + 1,
                maximum=max_decoded_bytes,
            )

        samples: tuple[dict[str, Any], ...] = ()
        parse_errors: tuple[str, ...] = ()
        truncated = False
        if decoded.text:
            remaining_samples = max_samples - sample_count
            if remaining_samples < 1:
                return _limit_result(
                    results,
                    resource="samples",
                    observed=sample_count + 1,
                    maximum=max_samples,
                )
            parsed = parse_openmetrics(
                decoded.text,
                max_samples=remaining_samples + 1,
                metric_names=set(metric_names),
            )
            samples = parsed.samples
            parse_errors = parsed.errors
            truncated = parsed.truncated
            sample_count += len(samples)
        results.append({
            "source_row": int(source_row),
            "samples": list(samples),
            "decode_errors": list(decoded.errors),
            "parse_errors": list(parse_errors),
            "truncated": truncated,
            "decoded_bytes": decoded.decoded_bytes,
            "decoded_limit_exceeded": decoded.limit_exceeded,
        })
        if truncated or sample_count > max_samples:
            return _limit_result(
                results,
                resource="samples",
                observed=max(sample_count, max_samples + 1),
                maximum=max_samples,
            )

    return {
        "status": "ok",
        "rows": results,
        "decoded_bytes": decoded_bytes,
        "sample_count": sample_count,
    }


def run_telemetry_decode_worker(
        rows: list[tuple[int, Any]],
        *,
        metric_names: tuple[str, ...],
        max_decoded_bytes: int,
        max_samples: int,
        timeout_seconds: float,
        memory_limit_bytes: int,
    ) -> dict[str, Any]:
    """Run decoding in a disposable process and return its bounded result."""

    context = multiprocessing.get_context("spawn")
    parent_connection, child_connection = context.Pipe(duplex=False)
    process = context.Process(
        target=_worker_entry,
        args=(
            child_connection,
            rows,
            metric_names,
            max_decoded_bytes,
            max_samples,
            memory_limit_bytes,
        ),
        name="csit-telemetry-decode",
        daemon=True,
    )
    started = perf_counter()
    process.start()
    child_connection.close()
    result: dict[str, Any]
    try:
        if not parent_connection.poll(max(timeout_seconds, 0.001)):
            _stop_process(process)
            return {
                "status": "timeout",
                "message": "Telemetry decode worker exceeded its deadline.",
                "worker_pid": process.pid,
                "duration_seconds": round(perf_counter() - started, 3),
            }
        try:
            result = parent_connection.recv()
        except (EOFError, OSError) as err:
            result = {
                "status": "failed",
                "message": "Telemetry decode worker exited without a result.",
                "error": repr(err),
            }
        process.join(timeout=1)
        if process.is_alive():
            _stop_process(process)
        result["worker_pid"] = process.pid
        result["worker_exit_code"] = process.exitcode
        result["duration_seconds"] = round(perf_counter() - started, 3)
        return result
    finally:
        parent_connection.close()
        if process.is_alive():
            _stop_process(process)


def _worker_entry(
        connection,
        rows: list[tuple[int, Any]],
        metric_names: tuple[str, ...],
        max_decoded_bytes: int,
        max_samples: int,
        memory_limit_bytes: int,
    ) -> None:
    """Apply process limits, decode rows, and send one terminal result."""

    try:
        _apply_memory_limit(memory_limit_bytes)
        result = decode_telemetry_rows(
            rows,
            metric_names=metric_names,
            max_decoded_bytes=max_decoded_bytes,
            max_samples=max_samples,
        )
    except MemoryError:
        result = {
            "status": "memory_limit",
            "message": "Telemetry decode worker exhausted its memory budget.",
        }
    except BaseException as err:  # The parent must receive a bounded failure.
        result = {
            "status": "failed",
            "message": "Telemetry decode worker failed.",
            "error": repr(err),
        }
    try:
        connection.send(result)
    finally:
        connection.close()


def _apply_memory_limit(memory_limit_bytes: int) -> None:
    """Apply an address-space limit in the Linux container when available."""

    if memory_limit_bytes <= 0 or not sys.platform.startswith("linux"):
        return
    try:
        import resource

        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        limit = memory_limit_bytes
        if hard not in (-1, resource.RLIM_INFINITY):
            limit = min(limit, hard)
        resource.setrlimit(resource.RLIMIT_AS, (limit, hard))
    except (ImportError, OSError, ValueError):
        # Admission control and byte budgets still protect platforms which do
        # not permit changing RLIMIT_AS.
        return


def _stop_process(process: multiprocessing.Process) -> None:
    process.terminate()
    process.join(timeout=1)
    if process.is_alive() and hasattr(process, "kill"):
        process.kill()
        process.join(timeout=1)


def _limit_result(
        rows: list[dict[str, Any]],
        *,
        resource: str,
        observed: int,
        maximum: int,
    ) -> dict[str, Any]:
    return {
        "status": "limit_exceeded",
        "resource": resource,
        "observed": observed,
        "maximum": maximum,
        "rows": rows,
    }
