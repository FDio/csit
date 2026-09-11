"""Rendering helpers for the CSIT Comparison dashboard."""

import html
import math
from datetime import UTC, datetime
from pathlib import Path
from string import Template
from typing import Any
from urllib.parse import urlencode

from comparison_export import default_comparison_export_filename


REFERENCE_FIELDS = (
    ("release", "Release"), ("dut", "DUT"),
    ("dut_version", "DUT Version"), ("infra", "Infra"),
    ("framesize", "Framesize"), ("cores", "Number of Cores"),
    ("test_type", "Test Type"),
)
BASE_DIR = Path(__file__).resolve().parent
_TEMPLATE = Template(
    (BASE_DIR / "templates" / "comparison.html").read_text(encoding="utf-8")
)


def render_comparison_content(
        catalog: dict[str, Any], table: dict[str, Any] | None,
        *, now: datetime | None = None,
    ) -> str:
    filters = catalog.get("filters") or {}
    options = catalog.get("filter_options") or {}
    complete = bool(catalog.get("complete"))
    records = [
        record for record in (table or {}).get("records") or []
        if isinstance(record, dict)
    ]
    return _TEMPLATE.substitute(
        catalog_warning=_warning(catalog, "Comparison catalog"),
        reference_controls="".join(
            _control(field, label, options.get(field) or [], filters.get(field), index)
            for index, (field, label) in enumerate(REFERENCE_FIELDS)
        ),
        compared_controls="".join((
            _control("parameter", "Parameter", options.get("parameter") or [], filters.get("parameter"), 7),
            _control("value", "Value", options.get("value") or [], filters.get("value"), 8),
        )),
        outliers_checked=" checked" if filters.get("remove_extreme_outliers") else "",
        table_warning=_warning(table or {}, "Comparison table"),
        comparison_table=_table(table or {}, records) if complete else _empty_state(),
        comparison_actions=_actions(filters, records, now=now) if complete else "",
        table_download_dialog=_download_dialog("table", "Download Comparison Table"),
        data_download_dialog=_download_dialog("data", "Download Raw Comparison Data"),
        show_url_dialog=_url_dialog(),
    )


def _control(field, label, options, selected, index):
    normalized = []
    for option in options:
        if isinstance(option, dict):
            value = str(option.get("value") or "")
            display = str(option.get("label") or value)
        else:
            value = display = str(option)
        if value:
            normalized.append((value, display))
    disabled = " disabled" if not normalized else ""
    markup = ['<option value="">Select...</option>']
    markup.extend(
        f'<option value="{_escape(value)}"'
        f'{" selected" if str(selected) == value else ""}>{_escape(display)}</option>'
        for value, display in normalized
    )
    control_id = f"comparison-{field.replace('_', '-')}"
    return (
        '<div class="filter-control comparison-filter-control">'
        f'<label for="{control_id}">{_escape(label)}</label>'
        f'<select id="{control_id}" name="{_escape(field)}" '
        f'data-comparison-filter data-comparison-index="{index}"{disabled}>'
        f'{"".join(markup)}</select></div>'
    )


def _table(payload, records):
    if not records:
        return '<div class="comparison-empty" role="status">No paired tests match this comparison.</div>'
    reference = str(payload.get("reference_label") or "Reference")
    compared = str(payload.get("compared_label") or "Compared")
    unit = str(payload.get("unit") or "")
    unit_suffix = f" [{unit}]" if unit else ""
    dimensions = payload.get("title_dimensions") or []
    title = ", ".join(
        f'{str(item.get("name") or "").replace("_", " ").title()}: {item.get("value")}'
        for item in dimensions if isinstance(item, dict)
    )
    leaf = [
        ("Test Name", "text"), ("Mean", "number"), ("Stdev", "number"),
        ("Mean", "number"), ("Stdev", "number"),
        ("Mean", "number"), ("Stdev", "number"),
    ]
    filter_row = ''.join(
        '<th><label class="visually-hidden" for="comparison-filter-'
        f'{index}">Filter {_escape(label)}</label><input id="comparison-filter-{index}" '
        f'class="comparison-column-filter" data-table-filter="{index}" '
        f'data-filter-type="{kind}" placeholder="Filter" autocomplete="off"></th>'
        for index, (label, kind) in enumerate(leaf)
    )
    header = (
        '<thead><tr><th rowspan="2" scope="col"><button type="button" '
        'class="comparison-sort" data-sort-column="0" data-sort-type="text" '
        'aria-label="Sort by Test Name">Test Name<span aria-hidden="true">'
        '&#8597;</span></button></th>'
        f'<th colspan="2" scope="colgroup">{_escape(reference + unit_suffix)}</th>'
        f'<th colspan="2" scope="colgroup">{_escape(compared + unit_suffix)}</th>'
        '<th colspan="2" scope="colgroup">Relative Change [%]</th></tr><tr>'
        + ''.join(_sort_button(label, index, kind) for index, (label, kind) in enumerate(leaf[1:], 1))
        + '</tr><tr class="comparison-filter-row">' + filter_row + '</tr></thead>'
    )
    body = ''.join(_row(record) for record in records)
    return (
        '<div class="comparison-table-panel">'
        f'<h2>Comparison for: {_escape(title)}</h2>'
        '<div class="comparison-table-scroll"><table class="comparison-table" '
        'data-comparison-table>' + header + f'<tbody>{body}</tbody></table></div></div>'
    )


def _sort_button(label, index, kind):
    return (
        f'<th scope="col"><button type="button" class="comparison-sort" '
        f'data-sort-column="{index}" data-sort-type="{kind}" '
        f'aria-label="Sort by {_escape(label)}">{_escape(label)}'
        '<span aria-hidden="true">&#8597;</span></button></th>'
    )


def _row(record):
    values = [
        record.get("test_name"), record.get("reference_mean"),
        record.get("reference_stdev"), record.get("compared_mean"),
        record.get("compared_stdev"), record.get("relative_change_mean"),
        record.get("relative_change_stdev"),
    ]
    cells = [
        f'<td data-filter-value="{_escape(values[0] or "")}" data-sort-value="{_escape(values[0] or "")}">{_escape(values[0] or "")}</td>'
    ]
    for value in values[1:]:
        try:
            number = float(value)
        except (TypeError, ValueError):
            cells.append('<td data-filter-value="" data-sort-value=""></td>')
            continue
        if not math.isfinite(number):
            cells.append('<td data-filter-value="" data-sort-value=""></td>')
        else:
            cells.append(
                f'<td data-filter-value="{number}" data-sort-value="{number}">{number:.2f}</td>'
            )
    return '<tr>' + ''.join(cells) + '</tr>'


def _actions(filters, records, *, now):
    export_params = urlencode([
        (field, str(filters.get(field)))
        for field, _label in REFERENCE_FIELDS
        if filters.get(field) is not None
    ] + [
        ("parameter", str(filters.get("parameter") or "")),
        ("value", str(filters.get("value") or "")),
        ("remove_extreme_outliers", "true" if filters.get("remove_extreme_outliers") else "false"),
    ])
    disabled = " disabled" if not records else ""
    current = _utc_now(now)
    table_name = default_comparison_export_filename("table", current)
    data_name = default_comparison_export_filename("data", current)
    return f'''
<div class="dashboard-actions comparison-actions" aria-label="Comparison actions">
  <button class="command-button command-button-secondary" type="button"
          data-open-url-dialog data-url-dialog-target="#comparison-url-dialog"
          data-url-mode="current">Show URL</button>
  <button class="command-button command-button-secondary" type="button"
          data-open-download-dialog data-download-dialog-target="#comparison-table-download-dialog"
          data-export-endpoint="/api/comparison/export" data-export-view="table"
          data-export-params="{_escape(export_params)}"
          data-default-filename="{_escape(table_name)}"{disabled}>Download Table</button>
  <button class="command-button command-button-primary" type="button"
          data-open-download-dialog data-download-dialog-target="#comparison-data-download-dialog"
          data-export-endpoint="/api/comparison/export" data-export-view="data"
          data-export-params="{_escape(export_params)}"
          data-default-filename="{_escape(data_name)}"{disabled}>Download Raw Data</button>
</div>'''


def _download_dialog(view, title):
    return f'''
<dialog id="comparison-{view}-download-dialog" class="action-dialog" aria-labelledby="comparison-{view}-download-title">
  <form class="action-dialog-frame" method="dialog" data-download-form>
    <header class="action-dialog-header"><h2 id="comparison-{view}-download-title">{_escape(title)}</h2>
      <button class="icon-button" type="button" data-download-close aria-label="Close download dialog" title="Close">&times;</button></header>
    <div class="action-dialog-body"><label class="dialog-field"><span>Filename</span>
      <input type="text" data-download-filename autocomplete="off" spellcheck="false"></label>
      <fieldset class="format-control"><legend>Format</legend>
        <label><input type="radio" name="export-format" value="xlsx" checked><span>XLSX</span></label>
        <label><input type="radio" name="export-format" value="csv"><span>CSV</span></label>
      </fieldset><p class="dialog-status" data-download-status role="status" aria-live="polite"></p></div>
    <footer class="action-dialog-footer"><button class="command-button command-button-secondary" type="button" data-download-cancel>Cancel</button>
      <button class="command-button command-button-primary" type="submit" data-download-submit>Download</button></footer>
  </form>
</dialog>'''


def _url_dialog():
    return '''
<dialog id="comparison-url-dialog" class="action-dialog" aria-labelledby="comparison-url-title">
  <div class="action-dialog-frame"><header class="action-dialog-header"><h2 id="comparison-url-title">Current Page URL</h2>
    <button class="icon-button" type="button" data-url-close aria-label="Close Comparison URL dialog" title="Close">&times;</button></header>
    <div class="action-dialog-body"><div class="dialog-field"><label>Share this Comparison view</label><span class="url-copy-row">
      <input type="url" data-current-page-url readonly spellcheck="false"><button class="icon-button copy-button" type="button" data-copy-url aria-label="Copy current Comparison URL" title="Copy URL"><span class="copy-icon" aria-hidden="true"></span></button>
    </span></div><p class="dialog-status" data-url-status role="status" aria-live="polite"></p></div></div>
</dialog>'''


def _empty_state():
    return '<div class="comparison-empty" role="status">Complete the reference and compared selections to view results.</div>'


def _warning(payload, label):
    if not payload.get("error"):
        return ""
    message = payload.get("message") or f"{label} is unavailable."
    return f'<section class="inline-warning" role="status"><strong>{_escape(label)} unavailable</strong><p>{_escape(message)}</p></section>'


def _utc_now(value):
    current = value or datetime.now(tz=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(UTC)


def _escape(value):
    return html.escape(str(value if value is not None else ""), quote=True)
