"""Rendering helpers for the CSIT Trending dashboard."""

import hashlib
import html
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlencode

from trending_export import default_trending_export_filename


FILTER_FIELDS = (
    ("dut", "DUT", False),
    ("area", "Area", False),
    ("test", "Test", False),
    ("infra", "Infra", False),
    ("testbed", "Testbeds", True),
    ("framesize", "Framesize", True),
    ("cores", "Number of cores", True),
    ("test_type", "Test type", True),
)
METRICS = (
    ("throughput", "Throughput"),
    ("bandwidth", "Bandwidth"),
    ("latency", "Average Latency at 50% PDR"),
)
SERIES_COLORS = (
    "#0057b8",
    "#c62828",
    "#008a45",
    "#7b1fa2",
    "#c45a00",
    "#007c91",
    "#6d4c41",
    "#ad1457",
    "#455a64",
    "#827717",
    "#283593",
    "#00695c",
    "#9e2a2b",
    "#5e35b1",
    "#2e7d32",
    "#8e24aa",
    "#1565c0",
    "#d84315",
    "#00838f",
    "#558b2f",
)
BASE_DIR = Path(__file__).resolve().parent
_TRENDING_TEMPLATE = Template(
    (BASE_DIR / "templates" / "trending.html").read_text(encoding="utf-8")
)


def render_trending_content(
        catalog_payload: dict[str, Any],
        series_payload: dict[str, Any] | None,
        selected_ids: list[str],
        *,
        now: datetime | None = None,
    ) -> str:
    """Render filters, selected series, and semantic scatter charts."""

    catalog_warning = _payload_warning(catalog_payload, "Trending catalog")
    filters = catalog_payload.get("filters") or {}
    options = catalog_payload.get("filter_options") or {}
    labels = catalog_payload.get("option_labels") or {}
    series_payload = series_payload or _empty_series_payload()
    series_warning = _payload_warning(series_payload, "Trending series")
    analysis_warning = _analysis_warning(series_payload)
    series = series_payload.get("series") or []
    records = series_payload.get("records") or []
    known_series = [item for item in series if isinstance(item, dict)]
    series_colors = _series_color_map(known_series)
    selected_inputs = _hidden_inputs("series", selected_ids)
    filter_inputs = "".join(
        _hidden_inputs(field, [filters.get(field)])
        for field, _label, _all in FILTER_FIELDS
        if filters.get(field) is not None
    )
    controls = "".join(
        _filter_control(
            field,
            label,
            bool(supports_all),
            options.get(field) or [],
            filters.get(field),
            (labels.get(field) or {}),
        )
        for field, label, supports_all in FILTER_FIELDS
    )
    selected_tests = _selected_tests(known_series, series_colors)
    charts = "".join(
        _scatter_chart(
            records,
            metric=metric,
            title=title,
            colors=series_colors,
            now=now,
        )
        for metric, title in METRICS
    )
    disabled = " disabled" if not known_series else ""
    add_disabled = " disabled" if catalog_payload.get("error") else ""
    return _TRENDING_TEMPLATE.substitute(
        catalog_warning=catalog_warning,
        series_warning=series_warning,
        analysis_warning=analysis_warning,
        selected_inputs=selected_inputs,
        filter_inputs=filter_inputs,
        filter_controls=controls,
        selected_tests=selected_tests,
        charts=charts,
        add_disabled=add_disabled,
        remove_disabled=disabled,
        trending_actions=_trending_actions(selected_ids, records, now=now),
        details_dialog=_trending_details_dialog(),
        download_dialog=_trending_download_dialog(),
        show_url_dialog=_trending_show_url_dialog(),
    )


def _filter_control(
        field: str,
        label: str,
        supports_all: bool,
        options: list[Any],
        selected: Any,
        labels: dict[str, Any],
    ) -> str:
    values = [str(value) for value in options]
    if supports_all:
        values.insert(0, "all")
    disabled = " disabled" if not values else ""
    option_markup = []
    if not values:
        option_markup.append('<option value="">Unavailable</option>')
    for value in values:
        selected_attr = " selected" if str(selected) == value else ""
        display = "All" if value == "all" else labels.get(value, value)
        option_markup.append(
            f'<option value="{_escape(value)}"{selected_attr}>'
            f"{_escape(display)}</option>"
        )
    control_id = f"trending-{field.replace('_', '-')}"
    return (
        '<div class="filter-control trending-filter-control">'
        f'<label for="{control_id}">{_escape(label)}</label>'
        f'<select id="{control_id}" name="{_escape(field)}" '
        f'data-trending-filter{disabled}>'
        f"{''.join(option_markup)}"
        "</select></div>"
    )


def _selected_tests(
        series: list[dict[str, Any]],
        colors: dict[str, str],
    ) -> str:
    if not series:
        return '<p class="selected-tests-empty">No tests selected.</p>'
    rows = []
    for item in sorted(
            series,
            key=lambda value: (
                str(value.get("name") or "").lower(),
                str(value.get("series_id") or ""),
            ),
        ):
        series_id = str(item.get("series_id") or "")
        name = str(item.get("name") or series_id)
        color = colors.get(series_id, SERIES_COLORS[0])
        rows.append(
            '<label class="selected-test">'
            f'<input type="checkbox" name="remove" value="{_escape(series_id)}">'
            f'<span class="series-swatch" style="--series-color: {color}"></span>'
            f'<span class="selected-test-name">{_escape(name)}</span>'
            "</label>"
        )
    return "".join(rows)


def _scatter_chart(
        records: list[Any],
        *,
        metric: str,
        title: str,
        colors: dict[str, str],
        now: datetime | None,
    ) -> str:
    now = _utc_now(now)
    points = []
    for record in records:
        if not isinstance(record, dict):
            continue
        value = _number(record.get(f"{metric}_value"))
        timestamp = _timestamp(record.get("start_time"))
        if value is None or timestamp is None:
            continue
        analysis = _metric_analysis(record, metric)
        points.append({
            "record": record,
            "value": value,
            "time": min(timestamp, now),
            "unit": _text(record.get(f"{metric}_unit")),
            "analysis": analysis,
        })
    if not points:
        return ""

    width = 1000.0
    height = 350.0
    left = 100.0
    right = 28.0
    top = 24.0
    bottom = 62.0
    plot_width = width - left - right
    plot_height = height - top - bottom
    earliest = min(point["time"] for point in points)
    if earliest >= now:
        earliest = now - timedelta(days=1)
    span = max((now - earliest).total_seconds(), 1.0)
    maximum = max(
        value
        for point in points
        for value in (
            point["value"],
            point["analysis"]["trend"] if point["analysis"] else None,
        )
        if value is not None
    )
    y_max = max(maximum * 1.1, 1.0)
    y_ticks = [y_max * index / 4 for index in range(5)]
    units = sorted({point["unit"] for point in points if point["unit"]})
    axis_title = title + (f" [{'|'.join(units)}]" if units else "")

    grid = []
    for value in y_ticks:
        y = top + plot_height - plot_height * (value / y_max)
        grid.append(
            f'<line class="chart-grid" x1="{left:.1f}" y1="{y:.1f}" '
            f'x2="{width - right:.1f}" y2="{y:.1f}" />'
            f'<text class="axis-label axis-label-y" x="{left - 12:.1f}" '
            f'y="{y + 4:.1f}">{_escape(_format_si(value))}</text>'
        )

    x_ticks = []
    for index in range(5):
        ratio = index / 4
        tick_time = earliest + timedelta(seconds=span * ratio)
        x = left + plot_width * ratio
        label = now.strftime("%Y-%m-%d") if index == 4 else _date_tick(tick_time, span)
        end_class = " axis-label-x-end" if index == 4 else ""
        x_ticks.append(
            f'<line class="axis-tick" x1="{x:.1f}" y1="{top + plot_height:.1f}" '
            f'x2="{x:.1f}" y2="{top + plot_height + 6:.1f}" />'
            f'<text class="axis-label axis-label-x{end_class}" x="{x:.1f}" '
            f'y="{top + plot_height + 24:.1f}">{_escape(label)}</text>'
        )

    def coordinates(point: dict[str, Any], value: float) -> tuple[float, float]:
        x = left + plot_width * (
            (point["time"] - earliest).total_seconds() / span
        )
        y = top + plot_height - plot_height * (value / y_max)
        return x, y

    analyzed_by_series: dict[tuple[str, str | None], list[dict[str, Any]]] = {}
    for point in points:
        if point["analysis"] is None:
            continue
        key = (str(point["record"].get("series_id")), point["unit"])
        analyzed_by_series.setdefault(key, []).append(point)

    trend_lines = []
    trend_hit_targets = []
    trend_targets = []
    anomalies = []
    for (series_id, _unit), series_points in analyzed_by_series.items():
        series_points.sort(key=lambda point: (
            point["time"],
            _sortable_build(point["record"].get("build")),
        ))
        color = colors.get(series_id, SERIES_COLORS[0])
        coordinates_list = [
            coordinates(point, point["analysis"]["trend"])
            for point in series_points
        ]
        if len(coordinates_list) == 1:
            x, y = coordinates_list[0]
            trend_lines.append(
                f'<line class="trending-trend-line" x1="{x - 4:.1f}" '
                f'y1="{y:.1f}" x2="{x + 4:.1f}" y2="{y:.1f}" '
                f'stroke="{color}" />'
            )
        else:
            trend_lines.append(
                f'<polyline class="trending-trend-line" fill="none" '
                f'stroke="{color}" points="'
                + " ".join(
                    f"{x:.1f},{y:.1f}" for x, y in coordinates_list
                )
                + '" />'
            )

        for index, (point, (x, y)) in enumerate(
                zip(series_points, coordinates_list, strict=True)
            ):
            trend_tooltip = _trend_tooltip(point["record"], metric)
            hit_points = _trend_hit_region(coordinates_list, index)
            hit_coordinates = " ".join(
                f"{px:.1f},{py:.1f}" for px, py in hit_points
            )
            trend_hit_targets.append(
                '<polyline class="trending-trend-hit-target '
                'chart-tooltip-target trending-details-target" fill="none" '
                f'points="{hit_coordinates}" '
                f'style="--series-color: {color}" tabindex="0" role="button" '
                f'data-tooltip="{_escape(trend_tooltip)}" '
                f'aria-label="{_escape(trend_tooltip)}" />'
            )
            trend_targets.append(
                f'<circle class="trending-trend-target chart-tooltip-target '
                f'trending-details-target" cx="{x:.1f}" cy="{y:.1f}" '
                f'r="5" tabindex="0" role="button" '
                f'data-tooltip="{_escape(trend_tooltip)}" '
                f'aria-label="{_escape(trend_tooltip)}" />'
            )
            classification = point["analysis"]["classification"]
            if classification not in {"progression", "regression"}:
                continue
            anomaly_tooltip = _anomaly_tooltip(point["record"], metric)
            anomalies.append(
                f'<circle class="trending-anomaly trending-{classification} '
                f'chart-tooltip-target trending-details-target" '
                f'cx="{x:.1f}" cy="{y:.1f}" r="7" tabindex="0" '
                f'role="button" data-tooltip="{_escape(anomaly_tooltip)}" '
                f'aria-label="{_escape(anomaly_tooltip)}" />'
            )

    circles = []
    for point in points:
        record = point["record"]
        x, y = coordinates(point, point["value"])
        tooltip = _point_tooltip(record)
        color = colors.get(str(record.get("series_id")), SERIES_COLORS[0])
        circles.append(
            f'<circle class="trending-point chart-tooltip-target '
            f'trending-details-target" '
            f'cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{color}" '
            f'tabindex="0" role="button" data-tooltip="{_escape(tooltip)}" '
            f'aria-label="{_escape(tooltip)}" />'
        )

    chart_id = f"trending-{metric}-chart"
    return f"""
<section class="chart-section trending-chart" aria-labelledby="{chart_id}-heading">
  <div class="chart-heading">
    <h2 id="{chart_id}-heading">{_escape(title)}</h2>
    {_chart_legend(bool(analyzed_by_series))}
  </div>
  <div class="chart-scroll">
    <svg class="scatter-chart" viewBox="0 0 {width:.0f} {height:.0f}"
         role="img" aria-labelledby="{chart_id}-title {chart_id}-description">
      <title id="{chart_id}-title">{_escape(title)}</title>
      <desc id="{chart_id}-description">Selected CSIT trending samples over UTC time.</desc>
      {''.join(grid)}
      <line class="chart-axis" x1="{left:.1f}" y1="{top:.1f}"
            x2="{left:.1f}" y2="{top + plot_height:.1f}" />
      <line class="chart-axis" x1="{left:.1f}" y1="{top + plot_height:.1f}"
            x2="{width - right:.1f}" y2="{top + plot_height:.1f}" />
      {''.join(x_ticks)}
      <text class="axis-title" x="{-height / 2:.1f}" y="22"
            transform="rotate(-90)">{_escape(axis_title)}</text>
      {''.join(trend_lines)}
      {''.join(trend_hit_targets)}
      {''.join(trend_targets)}
      {''.join(circles)}
      {''.join(anomalies)}
    </svg>
  </div>
</section>
"""


def _trend_hit_region(
        coordinates: list[tuple[float, float]],
        index: int,
    ) -> list[tuple[float, float]]:
    """Return the nearest-point portion of a rendered trend path."""

    current = coordinates[index]
    if len(coordinates) == 1:
        return [(current[0] - 5.0, current[1]), (current[0] + 5.0, current[1])]
    region = []
    if index:
        region.append(_midpoint(coordinates[index - 1], current))
    else:
        region.append(current)
    if 0 < index < len(coordinates) - 1:
        region.append(current)
    if index < len(coordinates) - 1:
        region.append(_midpoint(current, coordinates[index + 1]))
    else:
        region.append(current)
    return region


def _midpoint(
        first: tuple[float, float],
        second: tuple[float, float],
    ) -> tuple[float, float]:
    return ((first[0] + second[0]) / 2, (first[1] + second[1]) / 2)


def _trending_details_dialog() -> str:
    return """
<dialog id="trending-details-dialog" class="details-dialog trending-details-dialog"
        aria-labelledby="trending-details-title">
  <div class="details-dialog-frame">
    <header class="details-dialog-header">
      <h2 id="trending-details-title">Detailed Information</h2>
      <div class="details-dialog-actions">
        <button class="icon-button copy-button" type="button"
                data-copy-trending-details
                aria-label="Copy detailed information"
                title="Copy detailed information">
          <span class="copy-icon" aria-hidden="true"></span>
        </button>
        <button class="icon-button details-close" type="button"
                data-trending-dialog-close
                aria-label="Close detailed information"
                title="Close detailed information">&times;</button>
      </div>
    </header>
    <div class="details-dialog-body">
      <section class="details-section">
        <pre class="details-statistics" data-trending-details-content></pre>
      </section>
    </div>
    <p class="visually-hidden" data-trending-copy-status
       aria-live="polite"></p>
  </div>
</dialog>
"""


def _trending_actions(
        selected_ids: list[str],
        records: list[Any],
        *,
        now: datetime | None,
    ) -> str:
    export_params = urlencode([
        ("series", series_id)
        for series_id in selected_ids
        if str(series_id).strip()
    ])
    disabled = " disabled" if not any(
        isinstance(record, dict) for record in records
    ) else ""
    filename = default_trending_export_filename(_utc_now(now))
    return f"""
<div class="dashboard-actions trending-actions" aria-label="Trending actions">
  <button class="command-button command-button-secondary" type="button"
          data-open-url-dialog data-url-dialog-target="#trending-url-dialog"
          data-url-mode="current">Show URL</button>
  <button class="command-button command-button-primary" type="button"
          data-open-download-dialog
          data-download-dialog-target="#trending-download-dialog"
          data-export-endpoint="/api/trending/export"
          data-export-params="{_escape(export_params)}"
          data-default-filename="{_escape(filename)}"{disabled}>Download</button>
</div>
"""


def _trending_download_dialog() -> str:
    return """
<dialog id="trending-download-dialog" class="action-dialog"
        aria-labelledby="trending-download-dialog-title">
  <form class="action-dialog-frame" method="dialog" data-download-form>
    <header class="action-dialog-header">
      <h2 id="trending-download-dialog-title">Download Trending</h2>
      <button class="icon-button" type="button" data-download-close
              aria-label="Close Trending download dialog"
              title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <label class="dialog-field" for="trending-download-filename">
        <span>Filename</span>
        <input id="trending-download-filename" type="text"
               data-download-filename autocomplete="off" spellcheck="false">
      </label>
      <fieldset class="format-control">
        <legend>Format</legend>
        <label><input type="radio" name="export-format" value="xlsx" checked>
          <span>XLSX</span></label>
        <label><input type="radio" name="export-format" value="csv">
          <span>CSV</span></label>
      </fieldset>
      <p class="dialog-status" data-download-status role="status"
         aria-live="polite"></p>
    </div>
    <footer class="action-dialog-footer">
      <button class="command-button command-button-secondary" type="button"
              data-download-cancel>Cancel</button>
      <button class="command-button command-button-primary" type="submit"
              data-download-submit>Download</button>
    </footer>
  </form>
</dialog>
"""


def _trending_show_url_dialog() -> str:
    return """
<dialog id="trending-url-dialog" class="action-dialog"
        aria-labelledby="trending-url-dialog-title">
  <div class="action-dialog-frame">
    <header class="action-dialog-header">
      <h2 id="trending-url-dialog-title">Current Page URL</h2>
      <button class="icon-button" type="button" data-url-close
              aria-label="Close Trending URL dialog"
              title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <div class="dialog-field">
        <label for="trending-page-url">Share this Trending view</label>
        <span class="url-copy-row">
          <input id="trending-page-url" type="url" data-current-page-url
                 readonly spellcheck="false">
          <button class="icon-button copy-button" type="button" data-copy-url
                  aria-label="Copy current Trending URL" title="Copy URL">
            <span class="copy-icon" aria-hidden="true"></span>
          </button>
        </span>
      </div>
      <p class="dialog-status" data-url-status role="status"
         aria-live="polite"></p>
    </div>
  </div>
</dialog>
"""


def _point_tooltip(record: dict[str, Any]) -> str:
    lines = []
    _append_line(lines, "dut", record.get("dut"))
    _append_line(lines, "infra", record.get("infra"))
    _append_line(lines, "test", record.get("test"))
    timestamp = _timestamp(record.get("start_time"))
    if timestamp is not None:
        lines.append(f"date: {timestamp.strftime('%Y-%m-%d %H:%M')}")
    for metric in ("throughput", "bandwidth", "latency"):
        value = _number(record.get(f"{metric}_value"))
        if value is None:
            continue
        unit = _text(record.get(f"{metric}_unit"))
        label = f"{metric} [{unit}]" if unit else metric
        lines.append(f"{label}: {_format_si(value)}")
    dut = _text(record.get("dut"))
    version = _text(record.get("dut_version"))
    if dut and version:
        lines.append(f"{dut}-ver: {version}")
    job = _text(record.get("job"))
    build = record.get("build")
    if job and build is not None:
        lines.append(f"csit-ref: {job}/{build}")
    hosts = record.get("hosts")
    if isinstance(hosts, list) and hosts:
        lines.append("hosts: " + ", ".join(str(value) for value in hosts))
    elif _text(hosts):
        lines.append(f"hosts: {_text(hosts)}")
    return "\n".join(lines)


def _trend_tooltip(record: dict[str, Any], metric: str) -> str:
    lines = _analysis_identity_lines(record)
    analysis = _metric_analysis(record, metric) or {}
    unit = _text(record.get(f"{metric}_unit"))
    trend_label = f"trend [{unit}]" if unit else "trend"
    stdev_label = f"stdev [{unit}]" if unit else "stdev"
    trend = _number(analysis.get("trend"))
    stdev = _number(analysis.get("stdev"))
    if trend is not None:
        lines.append(f"{trend_label}: {_format_si(trend)}")
    if stdev is not None:
        lines.append(f"{stdev_label}: {_format_si(stdev)}")
    _append_run_details(lines, record)
    return "\n".join(lines)


def _anomaly_tooltip(record: dict[str, Any], metric: str) -> str:
    lines = _analysis_identity_lines(record)
    analysis = _metric_analysis(record, metric) or {}
    unit = _text(record.get(f"{metric}_unit"))
    trend_label = f"trend [{unit}]" if unit else "trend"
    trend = _number(analysis.get("trend"))
    if trend is not None:
        lines.append(f"{trend_label}: {_format_si(trend)}")
    classification = _text(analysis.get("classification"))
    if classification:
        lines.append(f"classification: {classification}")
    _append_run_details(lines, record)
    return "\n".join(lines)


def _analysis_identity_lines(record: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    _append_line(lines, "dut", record.get("dut"))
    _append_line(lines, "infra", record.get("infra"))
    _append_line(lines, "test", record.get("test"))
    timestamp = _timestamp(record.get("start_time"))
    if timestamp is not None:
        lines.append(f"date: {timestamp.strftime('%Y-%m-%d %H:%M')}")
    return lines


def _append_run_details(lines: list[str], record: dict[str, Any]) -> None:
    dut = _text(record.get("dut"))
    version = _text(record.get("dut_version"))
    if dut and version:
        lines.append(f"{dut}-ver: {version}")
    job = _text(record.get("job"))
    build = record.get("build")
    if job and build is not None:
        lines.append(f"csit-ref: {job}/{build}")
    hosts = record.get("hosts")
    if isinstance(hosts, list) and hosts:
        lines.append("hosts: " + ", ".join(str(value) for value in hosts))
    elif _text(hosts):
        lines.append(f"hosts: {_text(hosts)}")


def _metric_analysis(record: dict[str, Any], metric: str) -> dict[str, Any] | None:
    analysis = record.get(f"{metric}_analysis")
    if not isinstance(analysis, dict):
        return None
    trend = _number(analysis.get("trend"))
    stdev = _number(analysis.get("stdev"))
    classification = _text(analysis.get("classification"))
    if trend is None or stdev is None or classification not in {
            "normal", "progression", "regression",
        }:
        return None
    return {
        "trend": trend,
        "stdev": stdev,
        "classification": classification,
    }


def _sortable_build(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 2 ** 63 - 1


def _chart_legend(has_analysis: bool) -> str:
    items = [
        '<span><i class="trend-legend-sample"></i>Samples</span>',
    ]
    if has_analysis:
        items.extend((
            '<span><i class="trend-legend-line"></i>Trend</span>',
            '<span><i class="trend-legend-ring trend-legend-progression"></i>'
            'Progression</span>',
            '<span><i class="trend-legend-ring trend-legend-regression"></i>'
            'Regression</span>',
        ))
    return (
        '<div class="chart-legend trending-chart-legend" '
        'aria-label="Trending graph legend">'
        + "".join(items)
        + "</div>"
    )


def _append_line(lines: list[str], label: str, value: Any) -> None:
    normalized = _text(value)
    if normalized:
        lines.append(f"{label}: {normalized}")


def _payload_warning(payload: dict[str, Any], label: str) -> str:
    if not payload.get("error"):
        unknown = payload.get("unknown_series") or []
        if not unknown:
            return ""
        return (
            '<section class="inline-warning" role="status">'
            f"<strong>{_escape(label)} changed</strong>"
            f"<p>{len(unknown)} saved selection(s) are no longer available.</p>"
            "</section>"
        )
    message = payload.get("message") or f"{label} is unavailable."
    return (
        '<section class="inline-warning" role="status">'
        f"<strong>{_escape(label)} unavailable</strong>"
        f"<p>{_escape(message)}</p>"
        "</section>"
    )


def _analysis_warning(payload: dict[str, Any]) -> str:
    analysis = payload.get("trend_analysis")
    if not isinstance(analysis, dict):
        return ""
    errors = analysis.get("errors")
    if not isinstance(errors, list) or not errors:
        return ""
    return (
        '<section class="inline-warning" role="status">'
        '<strong>Trend analysis partially unavailable</strong>'
        f"<p>{len(errors)} selected series metric(s) could not be classified. "
        "Their measured samples remain visible.</p>"
        "</section>"
    )


def _empty_series_payload() -> dict[str, Any]:
    return {"series": [], "records": [], "unknown_series": []}


def _hidden_inputs(name: str, values: list[Any]) -> str:
    return "".join(
        f'<input type="hidden" name="{_escape(name)}" value="{_escape(value)}">'
        for value in values
        if value is not None and str(value) != ""
    )


def _series_color_map(series: list[dict[str, Any]]) -> dict[str, str]:
    """Assign deterministic, collision-free colors for the first 20 series."""

    series_ids = sorted({
        str(item.get("series_id"))
        for item in series
        if item.get("series_id") is not None
    })
    available = set(range(len(SERIES_COLORS)))
    assigned: dict[str, str] = {}
    for series_id in series_ids:
        digest = hashlib.sha256(series_id.encode()).digest()
        preferred = int.from_bytes(digest[:2], "big") % len(SERIES_COLORS)
        if available:
            color_index = next(
                index
                for offset in range(len(SERIES_COLORS))
                if (index := (preferred + offset) % len(SERIES_COLORS))
                in available
            )
            available.remove(color_index)
        else:
            color_index = preferred
        assigned[series_id] = SERIES_COLORS[color_index]
    return assigned


def _utc_now(value: datetime | None) -> datetime:
    value = value or datetime.now(tz=UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return _utc_now(parsed)


def _date_tick(value: datetime, span: float) -> str:
    if span <= timedelta(days=2).total_seconds():
        return value.strftime("%m-%d %H:%M")
    return value.strftime("%Y-%m-%d")


def _format_si(value: float) -> str:
    if value == 0:
        return "0"
    for threshold, suffix in (
            (1_000_000_000, "G"),
            (1_000_000, "M"),
            (1_000, "k"),
        ):
        if abs(value) >= threshold:
            return f"{value / threshold:.1f}{suffix}"
    return f"{value:.1f}"


def _number(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _escape(value: Any) -> str:
    return html.escape(str(value), quote=True)
