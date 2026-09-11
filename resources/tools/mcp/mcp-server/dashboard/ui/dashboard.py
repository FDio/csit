"""Prefab UI dashboard builders."""

import json
from html import escape

import pandas as pd
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Dashboard,
    DashboardItem,
    DataTable,
    DataTableColumn,
)
from prefab_ui.themes import Presentation


def build_dashboard(statistics: pd.DataFrame) -> str:
    """Build and render the CSIT statistics dashboard."""

    with Dashboard(columns=4, row_height="auto", gap=4, css_class="w-full") as view:
        with DashboardItem(col=1, row=1, col_span=4):
            DataTable(
                columns=[
                    DataTableColumn(key="job", header="Job", sortable=True),
                    DataTableColumn(key="build", header="Build", sortable=True),
                    DataTableColumn(key="start_time", header="Start Time", sortable=True),
                    DataTableColumn(key="duration", header="Duration", sortable=True),
                ],
                rows=statistics,
                search=True
            )

    return PrefabApp(
        title="CSIT dashboard",
        theme=Presentation(mode="dark"),
        view=view
    ).html()


def build_status_page(status: dict) -> str:
    """Build simple HTML for cases where dashboard data is not ready."""

    status_json = escape(json.dumps(status, indent=2))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CSIT dashboard</title>
</head>
<body>
  <h1>CSIT data is not ready</h1>
  <pre>{status_json}</pre>
</body>
</html>"""
