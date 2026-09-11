"""HTML and SVG rendering for the CSIT dashboard client."""

import html
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path
from string import Template
from typing import Any

from statistics_export import default_export_filename
from comparison_dashboard import render_comparison_content
from coverage_dashboard import render_coverage_content
from iterative_dashboard import render_iterative_content
from trending_dashboard import render_trending_content


DATASETS = ("statistics", "trending", "iterative", "coverage", "comparison")
DATASET_LABELS = {
    "statistics": "Statistics",
    "trending": "Trending",
    "iterative": "Iterative",
    "coverage": "Coverage",
    "comparison": "Comparison",
}
FILTER_FIELDS = (
    ("dut", "DUT"),
    ("test_type", "Test Type"),
    ("cadence", "Cadence"),
    ("testbed", "Testbed"),
)
BLUE = "#2563a6"
RED = "#c43c4b"
BASE_CHART_WIDTH = 1000.0
MIN_CHART_WIDTH = 720.0
MIN_SAMPLE_SLOT_WIDTH = 12.0
MIN_BAR_GAP = 3.0
BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
_DASHBOARD_TEMPLATE = Template(
    (TEMPLATE_DIR / "dashboard.html").read_text(encoding="utf-8")
)
_STATUS_TEMPLATE = Template(
    (TEMPLATE_DIR / "status.html").read_text(encoding="utf-8")
)


def render_dashboard_page(
        selected_dataset: str,
        datasets_payload: dict[str, Any],
        mcp_status: dict[str, Any],
        statistics_payload: dict[str, Any] | None = None,
        trending_catalog_payload: dict[str, Any] | None = None,
        trending_series_payload: dict[str, Any] | None = None,
        selected_trending_series: list[str] | None = None,
        iterative_catalog_payload: dict[str, Any] | None = None,
        iterative_series_payload: dict[str, Any] | None = None,
        selected_iterative_series: list[str] | None = None,
        coverage_catalog_payload: dict[str, Any] | None = None,
        coverage_tables_payload: dict[str, Any] | None = None,
        comparison_catalog_payload: dict[str, Any] | None = None,
        comparison_table_payload: dict[str, Any] | None = None,
        *,
        now: datetime | None = None,
    ) -> str:
    """Render the dashboard shell and selected dataset content."""

    connected = bool(mcp_status.get("connected"))
    payload_error = datasets_payload.get("error")
    data_status = datasets_payload.get("data_status")
    if not data_status:
        data_status = "unknown" if not payload_error else "warning"
    accent_class = (
        "status-ready"
        if connected and data_status in {"ready", "degraded"}
        else "status-warning"
    )
    if selected_dataset == "statistics":
        content = _statistics_content(statistics_payload or {}, now=now)
    elif selected_dataset == "trending":
        content = render_trending_content(
            trending_catalog_payload or {},
            trending_series_payload,
            selected_trending_series or [],
            now=now,
        )
    elif selected_dataset == "iterative":
        content = render_iterative_content(
            iterative_catalog_payload or {},
            iterative_series_payload,
            selected_iterative_series or [],
            now=now,
        )
    elif selected_dataset == "coverage":
        content = render_coverage_content(
            coverage_catalog_payload or {},
            coverage_tables_payload,
            now=now,
        )
    elif selected_dataset == "comparison":
        content = render_comparison_content(
            comparison_catalog_payload or {},
            comparison_table_payload,
            now=now,
        )
    else:
        content = _dataset_placeholder(selected_dataset)
    return _DASHBOARD_TEMPLATE.substitute(
        status_class=accent_class,
        connection_status="connected" if connected else "disconnected",
        data_status=_escape(data_status),
        freshness=_escape(_display_freshness(datasets_payload.get("freshness"))),
        mcp_url=_escape(mcp_status.get("url") or "unknown"),
        dataset_tabs=_dataset_tabs(selected_dataset),
        dashboard_content=content,
    )


def render_status_page(status: dict[str, Any]) -> str:
    """Render the browser status page used for required MCP failures."""

    server = status.get("server") or {}
    return _STATUS_TEMPLATE.substitute(
        mcp_url=_escape(status.get("url")),
        connected=_escape(status.get("connected")),
        server=_escape(server.get("name") or "unknown"),
        last_connected=_escape(status.get("last_connected_at") or "never"),
        last_error=_escape(status.get("last_error") or "No error detail available."),
        last_error_at=_escape(status.get("last_error_at") or "unknown"),
        reconnect_attempts=_escape(status.get("reconnect_attempts")),
        tools=_escape(", ".join(status.get("tools") or []) or "unknown"),
        resources=_escape(", ".join(status.get("resources") or []) or "unknown"),
        prompts=_escape(", ".join(status.get("prompts") or []) or "unknown"),
    )


def _statistics_content(payload: dict[str, Any], *, now: datetime | None) -> str:
    if payload.get("error"):
        message = payload.get("message") or "Statistics data is unavailable."
        return (
            '<section class="inline-warning" role="status">'
            "<strong>Statistics unavailable</strong>"
            f"<p>{_escape(message)}</p>"
            "</section>"
        )

    filters = payload.get("filters") or {}
    options = payload.get("filter_options") or {}
    records = payload.get("records") or []
    filter_form = _filter_form(filters, options)
    count_chart = _bar_chart(
        records,
        kind="counts",
        title="Passed / Failed Tests",
        chart_id="test-counts-chart",
        now=now,
    )
    duration_chart = _bar_chart(
        records,
        kind="duration",
        title="Duration",
        chart_id="duration-chart",
        now=now,
    )
    return f"""
<form class="statistics-filters" method="get" action="/" data-statistics-filters>
  <input type="hidden" name="dataset" value="statistics">
  {filter_form}
  <noscript><button class="apply-button" type="submit">Apply filters</button></noscript>
</form>
{count_chart}
{duration_chart}
{_statistics_actions(filters, records)}
{_run_details_dialog()}
{_download_dialog()}
{_show_url_dialog()}
"""


def _filter_form(
        filters: dict[str, Any],
        options: dict[str, Any],
    ) -> str:
    controls = []
    for field, label in FILTER_FIELDS:
        values = options.get(field) or []
        selected = filters.get(field)
        disabled = " disabled" if not values else ""
        option_markup = []
        if not values:
            option_markup.append('<option value="">Unavailable</option>')
        for value in values:
            selected_attr = " selected" if str(value) == str(selected) else ""
            option_markup.append(
                f'<option value="{_escape(value)}"{selected_attr}>'
                f"{_escape(value)}</option>"
            )
        control_id = f"statistics-{field.replace('_', '-')}"
        controls.append(
            '<div class="filter-control">'
            f'<label for="{control_id}">{_escape(label)}</label>'
            f'<select id="{control_id}" name="{field}" data-auto-submit{disabled}>'
            f"{''.join(option_markup)}"
            "</select>"
            "</div>"
        )
    return "".join(controls)


def _bar_chart(
        records: list[dict[str, Any]],
        *,
        kind: str,
        title: str,
        chart_id: str,
        now: datetime | None,
    ) -> str:
    now = _utc_now(now)
    points = _chart_points(records, kind=kind, now=now)
    legend = _chart_legend(kind)
    if not points:
        return f"""
<section class="chart-section" aria-labelledby="{chart_id}-heading">
  <div class="chart-heading">
    <h2 id="{chart_id}-heading">{_escape(title)}</h2>
    {legend}
  </div>
  <div class="chart-empty" role="status">No runs are available for this selection.</div>
</section>
"""

    dense_width = 100.0 + len(points) * MIN_SAMPLE_SLOT_WIDTH
    width = max(BASE_CHART_WIDTH, dense_width)
    minimum_display_width = max(MIN_CHART_WIDTH, dense_width)
    height = 320.0
    left = 74.0
    right = 26.0
    top = 24.0
    bottom = 62.0
    plot_width = width - left - right
    plot_height = height - top - bottom
    earliest = min(point["plot_time"] for point in points)
    if earliest >= now:
        earliest = now - timedelta(days=1)
    span = max((now - earliest).total_seconds(), 1.0)
    maximum = max(point["maximum"] for point in points)
    y_max, y_ticks = _axis_scale(maximum, kind=kind)
    sample_slot_width = plot_width / max(len(points), 1)
    bar_width = min(34.0, max(4.0, sample_slot_width * 0.6))
    x_centers = _bar_centers(
        points,
        earliest=earliest,
        span=span,
        left=left,
        right=right,
        width=width,
        bar_width=bar_width,
    )

    grid = []
    for value in y_ticks:
        ratio = value / y_max
        y = top + plot_height - (plot_height * ratio)
        label = (
            _format_duration(value)
            if kind == "duration"
            else _format_number(value)
        )
        grid.append(
            f'<line class="chart-grid" x1="{left:.1f}" y1="{y:.1f}" '
            f'x2="{width - right:.1f}" y2="{y:.1f}" />'
            f'<text class="axis-label axis-label-y" x="{left - 12:.1f}" '
            f'y="{y + 4:.1f}" font-size="10">{_escape(label)}</text>'
        )

    bars = []
    for point, x_center in zip(points, x_centers):
        if kind == "counts":
            bars.append(
                _count_bar(point, x_center, bar_width, top, plot_height, y_max)
            )
        else:
            bars.append(
                _duration_bar(point, x_center, bar_width, top, plot_height, y_max)
            )

    x_ticks = []
    for index in range(5):
        ratio = index / 4
        tick_time = earliest + timedelta(seconds=span * ratio)
        x = left + plot_width * ratio
        if index == 4:
            label = now.strftime("%Y-%m-%d")
        elif span <= timedelta(days=2).total_seconds():
            label = tick_time.strftime("%m-%d %H:%M")
        else:
            label = tick_time.strftime("%Y-%m-%d")
        anchor_class = " axis-label-x-end" if index == 4 else ""
        x_ticks.append(
            f'<line class="axis-tick" x1="{x:.1f}" y1="{top + plot_height:.1f}" '
            f'x2="{x:.1f}" y2="{top + plot_height + 6:.1f}" />'
            f'<text class="axis-label axis-label-x{anchor_class}" x="{x:.1f}" '
            f'y="{height - 27:.1f}" font-size="10">{_escape(label)}</text>'
        )

    description = (
        "Stacked passed and failed test counts by run."
        if kind == "counts"
        else "Run duration in seconds by start time."
    )
    return f"""
<section class="chart-section" aria-labelledby="{chart_id}-heading">
  <div class="chart-heading">
    <h2 id="{chart_id}-heading">{_escape(title)}</h2>
    {legend}
  </div>
  <div class="chart-scroll">
    <svg class="bar-chart" viewBox="0 0 {width:.1f} {height:.1f}" role="img"
         style="min-width: {minimum_display_width:.0f}px; aspect-ratio: {width:.1f} / {height:.1f};"
         aria-labelledby="{chart_id}-svg-title {chart_id}-svg-description">
      <title id="{chart_id}-svg-title">{_escape(title)}</title>
      <desc id="{chart_id}-svg-description">{_escape(description)}</desc>
      {''.join(grid)}
      <line class="chart-axis" x1="{left:.1f}" y1="{top:.1f}"
            x2="{left:.1f}" y2="{top + plot_height:.1f}" />
      <line class="chart-axis" x1="{left:.1f}" y1="{top + plot_height:.1f}"
            x2="{width - right:.1f}" y2="{top + plot_height:.1f}" />
      {''.join(bars)}
      {''.join(x_ticks)}
    </svg>
  </div>
</section>
"""


def _bar_centers(
        points: list[dict[str, Any]],
        *,
        earliest: datetime,
        span: float,
        left: float,
        right: float,
        width: float,
        bar_width: float,
) -> list[float]:
    """Return chronological x positions with a visible gap between samples."""

    minimum = left + bar_width / 2
    maximum = width - right - bar_width / 2
    plot_width = width - left - right
    spacing = bar_width + MIN_BAR_GAP
    centers = []
    for point in points:
        seconds = (point["plot_time"] - earliest).total_seconds()
        nominal = left + (seconds / span) * plot_width
        center = min(max(nominal, minimum), maximum)
        if centers:
            center = max(center, centers[-1] + spacing)
        centers.append(center)

    overflow = centers[-1] - maximum
    if overflow > 0:
        centers = [center - overflow for center in centers]
    if centers[0] < minimum:
        available_spacing = (
            (maximum - minimum) / max(len(centers) - 1, 1)
        )
        centers = [
            minimum + index * available_spacing
            for index in range(len(centers))
        ]
    return centers


def _chart_points(
        records: list[dict[str, Any]],
        *,
        kind: str,
        now: datetime,
    ) -> list[dict[str, Any]]:
    points = []
    for record in records:
        start_time = _parse_datetime(record.get("start_time"))
        if start_time is None:
            continue
        point = {
            "record": record,
            "start_time": start_time,
            "plot_time": min(start_time, now),
        }
        if kind == "counts":
            if not record.get("counts_available"):
                point.update({"passed": 0.0, "failed": 0.0, "maximum": 0.0})
            else:
                passed = _non_negative_number(record.get("passed_count"))
                failed = _non_negative_number(record.get("failed_count"))
                point.update({
                    "passed": passed,
                    "failed": failed,
                    "maximum": passed + failed,
                })
        else:
            duration = _non_negative_number(record.get("duration"))
            point.update({"duration": duration, "maximum": duration})
        points.append(point)
    return sorted(points, key=lambda point: point["start_time"])


def _count_bar(
        point: dict[str, Any],
        x_center: float,
        bar_width: float,
        top: float,
        plot_height: float,
        y_max: float,
    ) -> str:
    record = point["record"]
    x = x_center - bar_width / 2
    baseline = top + plot_height
    tooltip = _run_tooltip(record)
    tooltip_attributes = _run_attributes(tooltip, record)
    if not record.get("counts_available"):
        return (
            f'<g class="run-bar count-unavailable" {tooltip_attributes}>'
            f'<circle cx="{x_center:.1f}" cy="{baseline - 4:.1f}" r="4" /></g>'
        )
    passed_height = (point["passed"] / y_max) * plot_height
    failed_height = (point["failed"] / y_max) * plot_height
    passed_y = baseline - passed_height
    failed_y = passed_y - failed_height
    return f"""
<g class="run-bar" {tooltip_attributes}>
  <rect class="bar-passed" x="{x:.1f}" y="{passed_y:.1f}"
        width="{bar_width:.1f}" height="{passed_height:.1f}" />
  <rect class="bar-failed" x="{x:.1f}" y="{failed_y:.1f}"
        width="{bar_width:.1f}" height="{failed_height:.1f}" />
</g>
"""


def _duration_bar(
        point: dict[str, Any],
        x_center: float,
        bar_width: float,
        top: float,
        plot_height: float,
        y_max: float,
    ) -> str:
    duration = point["duration"]
    bar_height = (duration / y_max) * plot_height
    y = top + plot_height - bar_height
    x = x_center - bar_width / 2
    record = point["record"]
    tooltip = _run_tooltip(record)
    tooltip_attributes = _run_attributes(tooltip, record)
    return f"""
<g class="run-bar" {tooltip_attributes}>
  <rect class="bar-duration" x="{x:.1f}" y="{y:.1f}"
        width="{bar_width:.1f}" height="{bar_height:.1f}" />
</g>
"""


def _chart_legend(kind: str) -> str:
    if kind == "counts":
        return (
            '<div class="chart-legend" aria-label="Legend">'
            '<span><i class="legend-swatch legend-passed"></i>Passed</span>'
            '<span><i class="legend-swatch legend-failed"></i>Failed</span>'
            "</div>"
        )
    return (
        '<div class="chart-legend" aria-label="Legend">'
        '<span><i class="legend-swatch legend-duration"></i>Seconds</span>'
        "</div>"
    )


def _dataset_tabs(selected_dataset: str) -> str:
    tabs = []
    for dataset in DATASETS:
        active = dataset == selected_dataset
        active_class = " dataset-tab-active" if active else ""
        current = ' aria-current="page"' if active else ""
        tabs.append(
            f'<a class="dataset-tab{active_class}" '
            f'href="/?dataset={dataset}"{current}>'
            f'{_escape(DATASET_LABELS[dataset])}</a>'
        )
    return "".join(tabs)


def _dataset_placeholder(selected_dataset: str) -> str:
    return (
        '<section class="dataset-placeholder" aria-live="polite">'
        f"<h2>{_escape(DATASET_LABELS[selected_dataset])}</h2>"
        "</section>"
    )


def _run_details_dialog() -> str:
    return """
<dialog id="run-details-dialog" class="details-dialog"
        aria-labelledby="run-details-title">
  <div class="details-dialog-frame">
    <header class="details-dialog-header">
      <h2 id="run-details-title">Detailed Information</h2>
      <button class="icon-button details-close" type="button"
              data-dialog-close aria-label="Close detailed information"
              title="Close detailed information">&times;</button>
    </header>
    <div class="details-dialog-body">
      <section class="details-section" aria-labelledby="run-statistics-title">
        <div class="details-section-heading">
          <h3 id="run-statistics-title">Run Statistics</h3>
          <button class="icon-button copy-button" type="button"
                  data-copy-run-statistics
                  aria-label="Copy run statistics" title="Copy run statistics">
            <span class="copy-icon" aria-hidden="true"></span>
          </button>
        </div>
        <pre class="details-statistics" data-run-statistics></pre>
      </section>
      <section class="details-section" aria-labelledby="failed-tests-title">
        <div class="details-section-heading">
          <h3 id="failed-tests-title">List of Failed Tests (<span
              data-failed-count>0</span>)</h3>
          <button class="icon-button copy-button" type="button"
                  data-copy-failed-tests disabled
                  aria-label="Copy failed tests" title="Copy failed tests">
            <span class="copy-icon" aria-hidden="true"></span>
          </button>
        </div>
        <p class="details-loading" data-failed-status role="status"></p>
        <ul class="failed-tests-list" data-failed-tests></ul>
      </section>
    </div>
    <p class="visually-hidden" data-copy-status aria-live="polite"></p>
  </div>
</dialog>
"""


def _statistics_actions(
        filters: dict[str, Any],
        records: list[dict[str, Any]],
) -> str:
    attributes = " ".join(
        f'data-filter-{field.replace("_", "-")}="{_escape(filters.get(field) or "")}"'
        for field in ("dut", "test_type", "cadence", "testbed")
    )
    disabled = " disabled" if not records else ""
    filename = _escape(default_export_filename(filters))
    return f"""
<div class="statistics-actions" aria-label="Statistics actions">
  <button class="command-button command-button-secondary" type="button"
          data-open-url-dialog data-url-dialog-target="#show-url-dialog"
          data-url-mode="statistics" {attributes}>Show URL</button>
  <button class="command-button command-button-primary" type="button"
          data-open-download-dialog data-download-dialog-target="#download-dialog"
          data-export-endpoint="/api/statistics/export"
          data-default-filename="{filename}"
          {attributes}{disabled}>Download</button>
</div>
"""


def _download_dialog() -> str:
    return """
<dialog id="download-dialog" class="action-dialog"
        aria-labelledby="download-dialog-title">
  <form class="action-dialog-frame" method="dialog" data-download-form>
    <header class="action-dialog-header">
      <h2 id="download-dialog-title">Download Statistics</h2>
      <button class="icon-button" type="button" data-download-close
              aria-label="Close download dialog" title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <label class="dialog-field" for="download-filename">
        <span>Filename</span>
        <input id="download-filename" type="text" data-download-filename
               autocomplete="off" spellcheck="false">
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


def _show_url_dialog() -> str:
    return """
<dialog id="show-url-dialog" class="action-dialog"
        aria-labelledby="show-url-dialog-title">
  <div class="action-dialog-frame">
    <header class="action-dialog-header">
      <h2 id="show-url-dialog-title">Current Page URL</h2>
      <button class="icon-button" type="button" data-url-close
              aria-label="Close URL dialog" title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <div class="dialog-field">
        <label for="current-page-url">Share this Statistics view</label>
        <span class="url-copy-row">
          <input id="current-page-url" type="url" data-current-page-url
                 readonly spellcheck="false">
          <button class="icon-button copy-button" type="button" data-copy-url
                  aria-label="Copy current page URL" title="Copy URL">
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


def _display_freshness(value: Any) -> str:
    if not value:
        return "unknown"
    parsed = _parse_datetime(value)
    if parsed is None:
        return str(value)
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _utc_now(value: datetime | None) -> datetime:
    value = value or datetime.now(tz=UTC)
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _axis_scale(value: float, *, kind: str) -> tuple[float, list[float]]:
    if kind == "counts":
        return _integer_axis_scale(value)

    maximum = max(value * 1.1, 1.0)
    return maximum, [maximum * index / 4 for index in range(5)]


def _integer_axis_scale(value: float) -> tuple[float, list[float]]:
    target = max(value * 1.1, 1.0)
    rough_step = target / 4.0
    magnitude = 10 ** math.floor(math.log10(rough_step))
    normalized = rough_step / magnitude
    step = next(
        factor * magnitude
        for factor in (1.0, 2.0, 5.0, 10.0)
        if normalized <= factor
    )
    step = max(1, int(math.ceil(step)))
    maximum = float(step * math.ceil(target / step))
    ticks = [float(value) for value in range(0, int(maximum) + 1, step)]
    return maximum, ticks


def _non_negative_number(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return max(number, 0.0)


def _format_number(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")


def _run_tooltip(record: dict[str, Any]) -> str:
    lines = []
    start_time = _parse_datetime(record.get("start_time"))
    if start_time is not None:
        lines.append(f'date: {start_time.strftime("%Y-%m-%d %H:%M")}')

    duration = _optional_non_negative_number(record.get("duration"))
    if duration is not None:
        lines.append(f"duration: {_format_duration(duration)}")

    if record.get("counts_available"):
        passed = _optional_non_negative_number(record.get("passed_count"))
        failed = _optional_non_negative_number(record.get("failed_count"))
        if passed is not None:
            lines.append(f"passed: {int(passed)}")
        if failed is not None:
            lines.append(f"failed: {int(failed)}")

    dut = _normalized_text(record.get("dut"))
    dut_version = _normalized_text(record.get("dut_version"))
    if dut and dut_version:
        lines.append(f"{dut}-ver: {dut_version}")

    job = _normalized_text(record.get("job"))
    build = _normalized_text(record.get("build"))
    if job and build:
        lines.append(f"csit-ref: {job}/{build}")

    hosts = _display_hosts(record.get("hosts"))
    if hosts:
        lines.append(f"hosts: {hosts}")

    return "\n".join(_escape(line) for line in lines)


def _run_attributes(tooltip: str, record: dict[str, Any]) -> str:
    job = _normalized_text(record.get("job")) or ""
    build = _normalized_text(record.get("build")) or ""
    failed = ""
    if record.get("counts_available"):
        failed_count = _optional_non_negative_number(record.get("failed_count"))
        if failed_count is not None:
            failed = str(int(failed_count))
    return (
        'tabindex="0" role="button" '
        f'data-tooltip="{tooltip}" aria-label="{tooltip}" '
        f'data-run-job="{_escape(job)}" data-run-build="{_escape(build)}" '
        f'data-failed-count="{_escape(failed)}"'
    )


def _format_duration(seconds: float) -> str:
    total_minutes = int(math.floor((seconds / 60.0) + 0.5))
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def _optional_non_negative_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number < 0:
        return None
    return number


def _normalized_text(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _display_hosts(value: Any) -> str:
    values = value if isinstance(value, (list, tuple, set)) else [value]
    hosts = []
    for item in values:
        normalized = _normalized_text(item)
        if normalized and normalized not in hosts:
            hosts.append(normalized)
    return ", ".join(hosts)


def _escape(value: Any) -> str:
    return html.escape(str(value))
