"""Rendering helpers for the CSIT Iterative dashboard."""

import hashlib
import html
import math
from datetime import UTC, datetime
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlencode

from iterative_export import default_iterative_export_filename
from trending_dashboard import SERIES_COLORS


FILTER_FIELDS = (
    ("release", "Release", False),
    ("dut", "DUT", False),
    ("dut_version", "DUT Version", False),
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
BASE_DIR = Path(__file__).resolve().parent
_ITERATIVE_TEMPLATE = Template(
    (BASE_DIR / "templates" / "iterative.html").read_text(encoding="utf-8")
)


def render_iterative_content(
        catalog_payload: dict[str, Any],
        series_payload: dict[str, Any] | None,
        selected_ids: list[str],
        *,
        now: datetime | None = None,
    ) -> str:
    """Render Iterative filters, selected tests, box plots, and actions."""

    catalog_warning = _payload_warning(catalog_payload, "Iterative catalog")
    filters = catalog_payload.get("filters") or {}
    options = catalog_payload.get("filter_options") or {}
    labels = catalog_payload.get("option_labels") or {}
    series_payload = series_payload or _empty_series_payload()
    series_warning = _payload_warning(series_payload, "Iterative series")
    known_series = [
        item for item in series_payload.get("series") or []
        if isinstance(item, dict)
    ]
    records = [
        item for item in series_payload.get("records") or []
        if isinstance(item, dict)
    ]
    ordered_series = sorted(
        known_series,
        key=lambda item: (
            str(item.get("name") or "").lower(),
            str(item.get("series_id") or ""),
        ),
    )
    colors = _series_color_map(ordered_series)
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
            supports_all,
            options.get(field) or [],
            filters.get(field),
            labels.get(field) or {},
        )
        for field, label, supports_all in FILTER_FIELDS
    )
    charts = "".join(
        _box_chart(
            records,
            ordered_series,
            metric=metric,
            title=title,
            colors=colors,
        )
        for metric, title in METRICS
    )
    disabled = " disabled" if not ordered_series else ""
    add_disabled = " disabled" if catalog_payload.get("error") else ""
    return _ITERATIVE_TEMPLATE.substitute(
        catalog_warning=catalog_warning,
        series_warning=series_warning,
        selected_inputs=selected_inputs,
        filter_inputs=filter_inputs,
        filter_controls=controls,
        selected_tests=_selected_tests(ordered_series, colors),
        charts=charts,
        add_disabled=add_disabled,
        remove_disabled=disabled,
        iterative_actions=_iterative_actions(selected_ids, records, now=now),
        details_dialog=_details_dialog(),
        download_dialog=_download_dialog(),
        show_url_dialog=_show_url_dialog(),
    )


def box_statistics(values: list[float]) -> dict[str, Any] | None:
    """Return Tukey box statistics for finite, non-negative samples."""

    ordered = sorted(value for value in values if math.isfinite(value) and value >= 0)
    if not ordered:
        return None
    q1 = _quantile(ordered, 0.25)
    median = _quantile(ordered, 0.5)
    q3 = _quantile(ordered, 0.75)
    iqr = q3 - q1
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    non_outliers = [
        value for value in ordered
        if lower_fence <= value <= upper_fence
    ]
    return {
        "min": ordered[0],
        "lower_fence": lower_fence,
        "lower_whisker": non_outliers[0],
        "q1": q1,
        "median": median,
        "q3": q3,
        "upper_whisker": non_outliers[-1],
        "upper_fence": upper_fence,
        "max": ordered[-1],
        "outliers": [
            value for value in ordered
            if value < lower_fence or value > upper_fence
        ],
    }


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
    control_id = f"iterative-{field.replace('_', '-')}"
    return (
        '<div class="filter-control iterative-filter-control">'
        f'<label for="{control_id}">{_escape(label)}</label>'
        f'<select id="{control_id}" name="{_escape(field)}" '
        f'data-iterative-filter{disabled}>'
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
    for index, item in enumerate(series, start=1):
        series_id = str(item.get("series_id") or "")
        name = str(item.get("name") or series_id)
        color = colors.get(series_id, SERIES_COLORS[0])
        rows.append(
            '<label class="selected-test">'
            f'<input type="checkbox" name="remove" value="{_escape(series_id)}">'
            f'<span class="series-index">{index}</span>'
            f'<span class="series-swatch" style="--series-color: {color}"></span>'
            f'<span class="selected-test-name">{_escape(name)}</span>'
            "</label>"
        )
    return "".join(rows)


def _box_chart(
        records: list[dict[str, Any]],
        series: list[dict[str, Any]],
        *,
        metric: str,
        title: str,
        colors: dict[str, str],
    ) -> str:
    series_ids = [str(item.get("series_id") or "") for item in series]
    grouped: dict[str, list[tuple[dict[str, Any], float]]] = {
        series_id: [] for series_id in series_ids
    }
    units = set()
    for record in records:
        series_id = str(record.get("series_id") or "")
        value = _number(record.get(f"{metric}_value"))
        if series_id not in grouped or value is None or value < 0:
            continue
        grouped[series_id].append((record, value))
        unit = _text(record.get(f"{metric}_unit"))
        if unit:
            units.add(unit)
    grouped = {key: value for key, value in grouped.items() if value}
    if not grouped:
        return ""

    width = max(520.0, 150.0 + len(series) * 110.0)
    height = 430.0
    left = 100.0
    right = 28.0
    top = 28.0
    bottom = 62.0
    plot_width = width - left - right
    plot_height = height - top - bottom
    stats = {
        series_id: box_statistics([value for _record, value in samples])
        for series_id, samples in grouped.items()
    }
    maximum = max(
        item["max"] for item in stats.values() if item is not None
    )
    y_max = max(maximum * 1.1, 1.0)
    y_ticks = [y_max * index / 5 for index in range(6)]
    grid = []
    for value in y_ticks:
        y = top + plot_height - plot_height * value / y_max
        grid.append(
            f'<line class="chart-grid" x1="{left:.1f}" y1="{y:.1f}" '
            f'x2="{width - right:.1f}" y2="{y:.1f}" />'
            f'<text class="axis-label axis-label-y" x="{left - 12:.1f}" '
            f'y="{y + 4:.1f}">{_escape(_format_si(value))}</text>'
        )

    def x_coordinate(index: int) -> float:
        return left + plot_width * (index + 0.5) / max(len(series), 1)

    def y_coordinate(value: float) -> float:
        return top + plot_height - plot_height * value / y_max

    x_ticks = []
    shapes = []
    points = []
    series_names = {
        str(item.get("series_id") or ""): str(item.get("name") or "")
        for item in series
    }
    for index, item in enumerate(series):
        series_id = str(item.get("series_id") or "")
        x = x_coordinate(index)
        x_ticks.append(
            f'<line class="axis-tick" x1="{x:.1f}" y1="{top + plot_height:.1f}" '
            f'x2="{x:.1f}" y2="{top + plot_height + 6:.1f}" />'
            f'<text class="axis-label axis-label-x" x="{x:.1f}" '
            f'y="{top + plot_height + 24:.1f}">{index + 1}</text>'
        )
        summary = stats.get(series_id)
        if summary is None:
            continue
        color = colors.get(series_id, SERIES_COLORS[0])
        q1_y = y_coordinate(summary["q1"])
        q3_y = y_coordinate(summary["q3"])
        median_y = y_coordinate(summary["median"])
        lower_y = y_coordinate(summary["lower_whisker"])
        upper_y = y_coordinate(summary["upper_whisker"])
        tooltip = _box_tooltip(
            series_names.get(series_id) or series_id,
            summary,
            _first_unit(grouped[series_id], metric),
        )
        target_y = min(upper_y, q3_y)
        target_height = max(lower_y - target_y, 14.0)
        shapes.append(
            f'<g class="iterative-box-group iterative-details-target '
            f'chart-tooltip-target" tabindex="0" role="button" '
            f'data-tooltip="{_escape(tooltip)}" aria-label="{_escape(tooltip)}">'
            f'<line class="box-whisker" x1="{x:.1f}" y1="{upper_y:.1f}" '
            f'x2="{x:.1f}" y2="{lower_y:.1f}" />'
            f'<line class="box-whisker" x1="{x - 18:.1f}" y1="{upper_y:.1f}" '
            f'x2="{x + 18:.1f}" y2="{upper_y:.1f}" />'
            f'<line class="box-whisker" x1="{x - 18:.1f}" y1="{lower_y:.1f}" '
            f'x2="{x + 18:.1f}" y2="{lower_y:.1f}" />'
            f'<rect class="box-body" x="{x - 25:.1f}" y="{q3_y:.1f}" '
            f'width="50" height="{max(q1_y - q3_y, 1.0):.1f}" '
            f'style="--series-color: {color}" />'
            f'<line class="box-median" x1="{x - 25:.1f}" y1="{median_y:.1f}" '
            f'x2="{x + 25:.1f}" y2="{median_y:.1f}" />'
            f'<rect class="box-hit-target" x="{x - 32:.1f}" y="{target_y:.1f}" '
            f'width="64" height="{target_height:.1f}" />'
            "</g>"
        )
        outliers = summary["outliers"]
        for sample_index, (record, value) in enumerate(grouped[series_id]):
            jitter = _jitter(record, metric, sample_index)
            point_tooltip = _point_tooltip(record)
            outlier_class = " iterative-outlier" if value in outliers else ""
            points.append(
                f'<circle class="iterative-point{outlier_class} '
                f'iterative-details-target chart-tooltip-target" '
                f'cx="{x + jitter:.1f}" cy="{y_coordinate(value):.1f}" r="3" '
                f'fill="{color}" tabindex="0" role="button" '
                f'data-tooltip="{_escape(point_tooltip)}" '
                f'aria-label="{_escape(point_tooltip)}" />'
            )

    units_text = "|".join(sorted(units))
    axis_title = title + (f" [{units_text}]" if units_text else "")
    chart_id = f"iterative-{metric}-chart"
    return f"""
<section class="chart-section iterative-chart" aria-labelledby="{chart_id}-heading">
  <div class="chart-heading">
    <h2 id="{chart_id}-heading">{_escape(title)}</h2>
    <div class="chart-legend iterative-chart-legend" aria-label="Box graph legend">
      <span><i class="box-legend-sample"></i>Samples</span>
      <span><i class="box-legend-box"></i>Distribution</span>
      <span><i class="box-legend-outlier"></i>Outlier</span>
    </div>
  </div>
  <div class="chart-scroll">
    <svg class="box-chart" style="min-width: {width:.0f}px"
         viewBox="0 0 {width:.0f} {height:.0f}" role="img"
         aria-labelledby="{chart_id}-title {chart_id}-description">
      <title id="{chart_id}-title">{_escape(title)}</title>
      <desc id="{chart_id}-description">Tukey box plots and Iterative CSIT samples.</desc>
      {''.join(grid)}
      <line class="chart-axis" x1="{left:.1f}" y1="{top:.1f}"
            x2="{left:.1f}" y2="{top + plot_height:.1f}" />
      <line class="chart-axis" x1="{left:.1f}" y1="{top + plot_height:.1f}"
            x2="{width - right:.1f}" y2="{top + plot_height:.1f}" />
      {''.join(x_ticks)}
      <text class="axis-title" x="{-height / 2:.1f}" y="22"
            transform="rotate(-90)">{_escape(axis_title)}</text>
      {''.join(shapes)}
      {''.join(points)}
    </svg>
  </div>
</section>
"""


def _quantile(values: list[float], fraction: float) -> float:
    position = (len(values) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _jitter(record: dict[str, Any], metric: str, index: int) -> float:
    identity = "|".join((
        metric,
        str(record.get("job") or ""),
        str(record.get("build") or ""),
        str(record.get("test_id") or ""),
        str(index),
    ))
    value = int.from_bytes(hashlib.sha256(identity.encode()).digest()[:2], "big")
    return (value / 65535.0 - 0.5) * 36.0


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


def _box_tooltip(name: str, stats: dict[str, Any], unit: str | None) -> str:
    lines = [f"test: {name}"]
    suffix = f" [{unit}]" if unit else ""
    for key, label in (
            ("max", "max"),
            ("upper_fence", "upper fence"),
            ("q3", "q3"),
            ("median", "median"),
            ("q1", "q1"),
            ("lower_fence", "lower fence"),
            ("min", "min"),
        ):
        lines.append(f"{label}{suffix}: {_format_si(stats[key])}")
    return "\n".join(lines)


def _first_unit(samples: list[tuple[dict[str, Any], float]], metric: str) -> str | None:
    return next(
        (
            unit for record, _value in samples
            if (unit := _text(record.get(f"{metric}_unit")))
        ),
        None,
    )


def _details_dialog() -> str:
    return """
<dialog id="iterative-details-dialog" class="details-dialog iterative-details-dialog"
        aria-labelledby="iterative-details-title">
  <div class="details-dialog-frame">
    <header class="details-dialog-header">
      <h2 id="iterative-details-title">Detailed Information</h2>
      <div class="details-dialog-actions">
        <button class="icon-button copy-button" type="button"
                data-copy-iterative-details aria-label="Copy detailed information"
                title="Copy detailed information">
          <span class="copy-icon" aria-hidden="true"></span>
        </button>
        <button class="icon-button details-close" type="button"
                data-iterative-dialog-close aria-label="Close detailed information"
                title="Close detailed information">&times;</button>
      </div>
    </header>
    <div class="details-dialog-body">
      <section class="details-section">
        <pre class="details-statistics" data-iterative-details-content></pre>
      </section>
    </div>
    <p class="visually-hidden" data-iterative-copy-status aria-live="polite"></p>
  </div>
</dialog>
"""


def _iterative_actions(
        selected_ids: list[str],
        records: list[dict[str, Any]],
        *,
        now: datetime | None,
    ) -> str:
    export_params = urlencode([
        ("series", series_id)
        for series_id in selected_ids
        if str(series_id).strip()
    ])
    disabled = " disabled" if not records else ""
    filename = default_iterative_export_filename(_utc_now(now))
    return f"""
<div class="dashboard-actions iterative-actions" aria-label="Iterative actions">
  <button class="command-button command-button-secondary" type="button"
          data-open-url-dialog data-url-dialog-target="#iterative-url-dialog"
          data-url-mode="current">Show URL</button>
  <button class="command-button command-button-primary" type="button"
          data-open-download-dialog
          data-download-dialog-target="#iterative-download-dialog"
          data-export-endpoint="/api/iterative/export"
          data-export-params="{_escape(export_params)}"
          data-default-filename="{_escape(filename)}"{disabled}>Download</button>
</div>
"""


def _download_dialog() -> str:
    return """
<dialog id="iterative-download-dialog" class="action-dialog"
        aria-labelledby="iterative-download-dialog-title">
  <form class="action-dialog-frame" method="dialog" data-download-form>
    <header class="action-dialog-header">
      <h2 id="iterative-download-dialog-title">Download Iterative</h2>
      <button class="icon-button" type="button" data-download-close
              aria-label="Close Iterative download dialog" title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <label class="dialog-field" for="iterative-download-filename">
        <span>Filename</span>
        <input id="iterative-download-filename" type="text"
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


def _show_url_dialog() -> str:
    return """
<dialog id="iterative-url-dialog" class="action-dialog"
        aria-labelledby="iterative-url-dialog-title">
  <div class="action-dialog-frame">
    <header class="action-dialog-header">
      <h2 id="iterative-url-dialog-title">Current Page URL</h2>
      <button class="icon-button" type="button" data-url-close
              aria-label="Close Iterative URL dialog" title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <div class="dialog-field">
        <label for="iterative-page-url">Share this Iterative view</label>
        <span class="url-copy-row">
          <input id="iterative-page-url" type="url" data-current-page-url
                 readonly spellcheck="false">
          <button class="icon-button copy-button" type="button" data-copy-url
                  aria-label="Copy current Iterative URL" title="Copy URL">
            <span class="copy-icon" aria-hidden="true"></span>
          </button>
        </span>
      </div>
      <p class="dialog-status" data-url-status role="status" aria-live="polite"></p>
    </div>
  </div>
</dialog>
"""


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


def _empty_series_payload() -> dict[str, Any]:
    return {"series": [], "records": [], "unknown_series": []}


def _hidden_inputs(name: str, values: list[Any]) -> str:
    return "".join(
        f'<input type="hidden" name="{_escape(name)}" value="{_escape(value)}">'
        for value in values
        if value is not None and str(value) != ""
    )


def _series_color_map(series: list[dict[str, Any]]) -> dict[str, str]:
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
                if (index := (preferred + offset) % len(SERIES_COLORS)) in available
            )
            available.remove(color_index)
        else:
            color_index = preferred
        assigned[series_id] = SERIES_COLORS[color_index]
    return assigned


def _append_line(lines: list[str], label: str, value: Any) -> None:
    normalized = _text(value)
    if normalized:
        lines.append(f"{label}: {normalized}")


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
