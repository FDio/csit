"""Rendering helpers for the CSIT Coverage dashboard."""

import html
import math
from datetime import UTC, datetime
from itertools import groupby
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlencode

from coverage_export import default_coverage_export_filename


FILTER_FIELDS = (
    ("release", "Release"),
    ("dut", "DUT"),
    ("dut_version", "DUT Version"),
    ("area", "Area"),
    ("infra", "Infra"),
)
PDR_LEVELS = (10, 50, 90)
PERCENTILES = (50, 90, 99)
BASE_DIR = Path(__file__).resolve().parent
_COVERAGE_TEMPLATE = Template(
    (BASE_DIR / "templates" / "coverage.html").read_text(encoding="utf-8")
)


def render_coverage_content(
        catalog_payload: dict[str, Any],
        tables_payload: dict[str, Any] | None,
        *,
        now: datetime | None = None,
    ) -> str:
    """Render Coverage cascading filters, accordion tables, and actions."""

    filters = catalog_payload.get("filters") or {}
    options = catalog_payload.get("filter_options") or {}
    records = [
        record for record in (tables_payload or {}).get("records") or []
        if isinstance(record, dict)
    ]
    complete = bool(catalog_payload.get("complete"))
    catalog_warning = _payload_warning(catalog_payload, "Coverage catalog")
    table_warning = _payload_warning(tables_payload or {}, "Coverage tables")
    controls = "".join(
        _filter_control(field, label, options.get(field) or [], filters.get(field))
        for field, label in FILTER_FIELDS
    )
    tables = _accordion_tables(records, tables_payload or {}) if complete else ""
    actions = _coverage_actions(filters, records, now=now) if complete else ""
    return _COVERAGE_TEMPLATE.substitute(
        catalog_warning=catalog_warning,
        complete="true" if complete else "false",
        filter_controls=controls,
        table_warning=table_warning,
        tables=tables,
        coverage_actions=actions,
        download_dialog=_download_dialog(),
        show_url_dialog=_show_url_dialog(),
    )


def _filter_control(
        field: str,
        label: str,
        options: list[Any],
        selected: Any,
    ) -> str:
    normalized = []
    for option in options:
        if isinstance(option, dict):
            value = str(option.get("value") or "")
            display = str(option.get("label") or value)
        else:
            value = str(option)
            display = value
        if value:
            normalized.append((value, display))
    disabled = " disabled" if not normalized else ""
    option_markup = ['<option value="">Select...</option>']
    option_markup.extend(
        f'<option value="{_escape(value)}"'
        f'{" selected" if str(selected) == value else ""}>'
        f'{_escape(display)}</option>'
        for value, display in normalized
    )
    control_id = f"coverage-{field.replace('_', '-')}"
    return (
        '<div class="filter-control coverage-filter-control">'
        f'<label for="{control_id}">{_escape(label)}</label>'
        f'<select id="{control_id}" name="{_escape(field)}" '
        f'data-coverage-filter{disabled}>'
        f'{"".join(option_markup)}</select></div>'
    )


def _accordion_tables(
        records: list[dict[str, Any]],
        payload: dict[str, Any],
    ) -> str:
    if not records:
        return (
            '<div class="coverage-empty" role="status">'
            'No passed Coverage tests match this selection.</div>'
        )
    forward = bool(payload.get("has_forward_latency"))
    reverse = bool(payload.get("has_reverse_latency"))
    groups = []
    key = lambda record: str(record.get("accordion_title") or "Coverage")
    for title, grouped in groupby(records, key=key):
        rows = list(grouped)
        groups.append(
            '<details class="coverage-accordion">'
            f'<summary>{_escape(title)}<span>{len(rows)} test(s)</span></summary>'
            '<div class="coverage-table-scroll">'
            '<table class="coverage-table" data-sortable-table>'
            f'{_table_header(forward, reverse)}'
            f'<tbody>{"".join(_table_row(row, forward, reverse) for row in rows)}</tbody>'
            '</table></div></details>'
        )
    return '<div class="coverage-accordions">' + "".join(groups) + "</div>"


def _table_header(forward: bool, reverse: bool) -> str:
    directions = [
        direction for direction, enabled in (("Forward", forward), ("Reverse", reverse))
        if enabled
    ]
    top = [
        '<tr><th rowspan="3" scope="col" class="coverage-test-column">'
        f'{_sort_button("Test Name", 0, "text")}</th>',
        '<th colspan="4" scope="colgroup">Throughput</th>',
    ]
    top.extend(
        f'<th colspan="9" scope="colgroup">Latency {direction} [us]</th>'
        for direction in directions
    )
    top.append('</tr>')
    second = [
        '<tr><th colspan="2" scope="colgroup">NDR</th>'
        '<th colspan="2" scope="colgroup">PDR</th>'
    ]
    second.extend(
        ''.join(f'<th colspan="3" scope="colgroup">{pdr}% PDR</th>' for pdr in PDR_LEVELS)
        for _direction in directions
    )
    second.append('</tr>')
    third = ['<tr>']
    column = 1
    for label in ("MPPS", "GBPS", "MPPS", "GBPS"):
        third.append(f'<th scope="col">{_sort_button(label, column, "number")}</th>')
        column += 1
    for _direction in directions:
        for _pdr in PDR_LEVELS:
            for percentile in PERCENTILES:
                third.append(
                    f'<th scope="col">{_sort_button(f"P{percentile}", column, "number")}</th>'
                )
                column += 1
    third.append('</tr>')
    return '<thead>' + "".join(top + second + third) + '</thead>'


def _sort_button(label: str, column: int, value_type: str) -> str:
    return (
        f'<button class="coverage-sort" type="button" data-sort-column="{column}" '
        f'data-sort-type="{value_type}" aria-label="Sort by {_escape(label)}">'
        f'{_escape(label)}<span aria-hidden="true">&#8597;</span></button>'
    )


def _table_row(record: dict[str, Any], forward: bool, reverse: bool) -> str:
    name = str(record.get("test_name") or "")
    url = str(record.get("source_url") or "")
    cells = [
        '<td class="coverage-test-column" data-sort-value="'
        f'{_escape(name)}"><a href="{_escape(url)}" target="_blank" '
        f'rel="noopener noreferrer">{_escape(name)}</a></td>',
    ]
    for key in (
        "throughput_ndr",
        "throughput_ndr_gbps",
        "throughput_pdr",
        "throughput_pdr_gbps",
    ):
        cells.append(_number_cell(record.get(key), decimals=2))
    for direction, enabled in (("forward", forward), ("reverse", reverse)):
        if not enabled:
            continue
        for pdr in PDR_LEVELS:
            for percentile in PERCENTILES:
                cells.append(_number_cell(
                    record.get(f"latency_{direction}_pdr_{pdr}_p{percentile}"),
                    decimals=0,
                ))
    return '<tr>' + "".join(cells) + '</tr>'


def _number_cell(value: Any, *, decimals: int) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return '<td data-sort-value=""></td>'
    if not math.isfinite(number):
        return '<td data-sort-value=""></td>'
    display = f"{number:.{decimals}f}" if decimals else str(int(round(number)))
    return f'<td data-sort-value="{number}">{_escape(display)}</td>'


def _coverage_actions(
        filters: dict[str, Any],
        records: list[dict[str, Any]],
        *,
        now: datetime | None,
    ) -> str:
    export_params = urlencode([
        (field, str(filters.get(field)))
        for field, _label in FILTER_FIELDS
        if filters.get(field) is not None
    ])
    disabled = " disabled" if not records else ""
    filename = default_coverage_export_filename(_utc_now(now))
    return f"""
<div class="dashboard-actions coverage-actions" aria-label="Coverage actions"
     data-coverage-actions>
  <button class="command-button command-button-secondary" type="button"
          data-open-url-dialog data-url-dialog-target="#coverage-url-dialog"
          data-url-mode="current">Show URL</button>
  <button class="command-button command-button-primary" type="button"
          data-open-download-dialog
          data-download-dialog-target="#coverage-download-dialog"
          data-export-endpoint="/api/coverage/export"
          data-export-params="{_escape(export_params)}"
          data-default-filename="{_escape(filename)}"{disabled}>Download</button>
</div>
"""


def _download_dialog() -> str:
    return """
<dialog id="coverage-download-dialog" class="action-dialog"
        aria-labelledby="coverage-download-dialog-title">
  <form class="action-dialog-frame" method="dialog" data-download-form>
    <header class="action-dialog-header">
      <h2 id="coverage-download-dialog-title">Download Coverage</h2>
      <button class="icon-button" type="button" data-download-close
              aria-label="Close Coverage download dialog" title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <label class="dialog-field" for="coverage-download-filename">
        <span>Filename</span>
        <input id="coverage-download-filename" type="text"
               data-download-filename autocomplete="off" spellcheck="false">
      </label>
      <fieldset class="format-control">
        <legend>Format</legend>
        <label><input type="radio" name="export-format" value="xlsx" checked>
          <span>XLSX</span></label>
        <label><input type="radio" name="export-format" value="csv">
          <span>CSV</span></label>
      </fieldset>
      <p class="dialog-status" data-download-status role="status" aria-live="polite"></p>
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
<dialog id="coverage-url-dialog" class="action-dialog"
        aria-labelledby="coverage-url-dialog-title">
  <div class="action-dialog-frame">
    <header class="action-dialog-header">
      <h2 id="coverage-url-dialog-title">Current Page URL</h2>
      <button class="icon-button" type="button" data-url-close
              aria-label="Close Coverage URL dialog" title="Close">&times;</button>
    </header>
    <div class="action-dialog-body">
      <div class="dialog-field">
        <label for="coverage-page-url">Share this Coverage view</label>
        <span class="url-copy-row">
          <input id="coverage-page-url" type="url" data-current-page-url
                 readonly spellcheck="false">
          <button class="icon-button copy-button" type="button" data-copy-url
                  aria-label="Copy current Coverage URL" title="Copy URL">
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
        return ""
    message = payload.get("message") or f"{label} is unavailable."
    return (
        '<section class="inline-warning" role="status">'
        f'<strong>{_escape(label)} unavailable</strong>'
        f'<p>{_escape(message)}</p></section>'
    )


def _utc_now(value: datetime | None) -> datetime:
    current = value or datetime.now(tz=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC)


def _escape(value: Any) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)
