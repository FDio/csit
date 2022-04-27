# Copyright (c) 2022 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Plotly Dash HTML layout override.
"""

from asyncio.log import logger
import logging
import pandas as pd
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html
from dash import callback_context, no_update
from dash import Input, Output
from dash.exceptions import PreventUpdate
from pyparsing import PrecededBy
from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta

from ..data.data import Data
from .graphs import graph_statistics


class Layout:
    """
    """

    def __init__(self, app, html_layout_file, spec_file, graph_layout_file,
        data_spec_file):
        """
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._spec_file = spec_file
        self._graph_layout_file = graph_layout_file
        self._data_spec_file = data_spec_file

        # Read the data:
        data_stats, data_mrr, data_ndrpdr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_stats(days=7)

        df_tst_info = pd.concat([data_mrr, data_ndrpdr], ignore_index=True)

        # Pre-process the data:
        data_stats = data_stats[~data_stats.job.str.contains("-verify-")]
        data_stats = data_stats[~data_stats.job.str.contains("-coverage-")]
        data_stats = data_stats[~data_stats.job.str.contains("-iterative-")]
        data_stats = data_stats[["job", "build", "start_time", "duration"]]

        self._jobs = sorted(list(data_stats["job"].unique()))

        tst_info = {
            "job": list(),
            "build": list(),
            "dut_type": list(),
            "dut_version": list(),
            "hosts": list(),
            "passed": list(),
            "failed": list()
        }
        for job in self._jobs:
            df_job = df_tst_info.loc[(df_tst_info["job"] == job)]
            builds = df_job["build"].unique()
            for build in builds:
                df_build = df_job.loc[(df_job["build"] == build)]
                tst_info["job"].append(job)
                tst_info["build"].append(build)
                tst_info["dut_type"].append(df_build["dut_type"].iloc[-1])
                tst_info["dut_version"].append(df_build["dut_version"].iloc[-1])
                tst_info["hosts"].append(df_build["hosts"].iloc[-1])
                try:
                    passed = df_build.value_counts(subset='passed')[True]
                except KeyError:
                    passed = 0
                try:
                    failed = df_build.value_counts(subset='passed')[False]
                except KeyError:
                    failed = 0
                tst_info["passed"].append(passed)
                tst_info["failed"].append(failed)

        self._data = data_stats.merge(pd.DataFrame.from_dict(tst_info))

        # Read from files:
        self._html_layout = ""
        self._graph_layout = None

        try:
            with open(self._html_layout_file, "r") as file_read:
                self._html_layout = file_read.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._html_layout_file}\n{err}"
            )

        try:
            with open(self._graph_layout_file, "r") as file_read:
                self._graph_layout = load(file_read, Loader=FullLoader)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._graph_layout_file}\n"
                f"{err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the specification file "
                f"{self._graph_layout_file}\n"
                f"{err}"
            )

        self._default_fig_passed, self._default_fig_duration = graph_statistics(
            self.data, self.jobs[0], self.layout
        )

        # Callbacks:
        if self._app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self._app)

    @property
    def html_layout(self) -> dict:
        return self._html_layout

    @property
    def data(self) -> pd.DataFrame:
        return self._data

    @property
    def layout(self) -> dict:
        return self._graph_layout

    @property
    def jobs(self) -> list:
        return self._jobs

    def add_content(self):
        """
        """
        if self.html_layout:
            return html.Div(
                id="div-main",
                children=[
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[
                            self._add_navbar(),
                        ]
                    ),
                    dcc.Loading(
                        dbc.Offcanvas(
                            class_name="w-50",
                            id="offcanvas-metadata",
                            title="Detailed Information",
                            placement="end",
                            is_open=False,
                            children=[
                                dbc.Row(id="row-metadata")
                            ]
                        )
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            self._add_ctrl_col(),
                            self._add_plotting_col(),
                        ]
                    )
                ]
            )
        else:
            return html.Div(
                id="div-main-error",
                children=[
                    dbc.Alert(
                        [
                            "An Error Occured",
                        ],
                        color="danger",
                    ),
                ]
            )

    def _add_navbar(self):
        """Add nav element with navigation panel. It is placed on the top.
        """
        return dbc.NavbarSimple(
            id="navbarsimple-main",
            children=[
                dbc.NavItem(
                    dbc.NavLink(
                        "Continuous Performance Statistics",
                        disabled=True,
                        external_link=True,
                        href="#"
                    )
                )
            ],
            brand="Dashboard",
            brand_href="/",
            brand_external_link=True,
            class_name="p-2",
            fluid=True,
        )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with controls. It is placed on the left side.
        """
        return dbc.Col(
            id="col-controls",
            children=[
                self._add_ctrl_panel(),
            ],
        )

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with plots and tables. It is placed on the right side.
        """
        return dbc.Col(
            id="col-plotting-area",
            children=[
                dbc.Row(  # Passed / failed tests
                    id="row-graph-passed",
                    class_name="g-0 p-2",
                    children=[
                        dcc.Loading(children=[
                            dcc.Graph(
                                id="graph-passed",
                                figure=self._default_fig_passed
                            )
                        ])
                    ]
                ),
                dbc.Row(  # Duration
                    id="row-graph-duration",
                    class_name="g-0 p-2",
                    children=[
                        dcc.Loading(children=[
                            dcc.Graph(
                                id="graph-duration",
                                figure=self._default_fig_duration
                            )
                        ])
                    ]
                ),
                dbc.Row(  # Download
                    id="row-btn-download",
                    class_name="g-0 p-2",
                    children=[
                        dcc.Loading(children=[
                            dbc.Button(
                                id="btn-download-data",
                                children=["Download Data"]
                            ),
                            dcc.Download(id="download-data")
                        ])
                    ]
                )
            ],
            width=9,
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """
        """
        return dbc.Row(
            id="row-ctrl-panel",
            class_name="g-0 p-2",
            children=[
                dbc.Label("Choose the Trending Job"),
                dbc.RadioItems(
                    id="ri_job",
                    value=self.jobs[0],
                    options=[{"label": i, "value": i} for i in self.jobs]
                ),
                dbc.Label("Choose the Time Period"),
                dcc.DatePickerRange(
                    id="dpr-period",
                    className="d-flex justify-content-center",
                    min_date_allowed=\
                        datetime.utcnow()-timedelta(days=180),
                    max_date_allowed=datetime.utcnow(),
                    initial_visible_month=datetime.utcnow(),
                    start_date=datetime.utcnow() - timedelta(days=180),
                    end_date=datetime.utcnow(),
                    display_format="D MMMM YY"
                )
            ]
        )

    def callbacks(self, app):

        @app.callback(
            Output("graph-passed", "figure"),
            Output("graph-duration", "figure"),
            Input("ri_job", "value"),
            Input("dpr-period", "start_date"),
            Input("dpr-period", "end_date"),
            prevent_initial_call=True
        )
        def _update_ctrl_panel(job:str, d_start: str, d_end: str) -> tuple:
            """
            """

            d_start = datetime(int(d_start[0:4]), int(d_start[5:7]),
                int(d_start[8:10]))
            d_end = datetime(int(d_end[0:4]), int(d_end[5:7]), int(d_end[8:10]))

            fig_passed, fig_duration = graph_statistics(
                self.data, job, self.layout, d_start, d_end
            )

            return fig_passed, fig_duration

        @app.callback(
            Output("download-data", "data"),
            Input("btn-download-data", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(n_clicks):
            """
            """
            if not n_clicks:
                raise PreventUpdate

            return dcc.send_data_frame(self.data.to_csv, "statistics.csv")

        @app.callback(
            Output("row-metadata", "children"),
            Output("offcanvas-metadata", "is_open"),
            Input("graph-passed", "clickData"),
            Input("graph-duration", "clickData"),
            prevent_initial_call=True
        )
        def _show_metadata_from_graphs(
                passed_data: dict, duration_data: dict) -> tuple:
            """
            """

            if not (passed_data or duration_data):
                raise PreventUpdate

            metadata = no_update
            open_canvas = False
            title = "Job Statistics"
            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "graph-passed":
                graph_data = passed_data["points"][0].get("hovertext", "")
            elif trigger_id == "graph-duration":
                graph_data = duration_data["points"][0].get("text", "")
            if graph_data:
                metadata = [
                    dbc.Card(
                        class_name="gy-2 p-0",
                        children=[
                            dbc.CardHeader(children=[
                                dcc.Clipboard(
                                    target_id="metadata",
                                    title="Copy",
                                    style={"display": "inline-block"}
                                ),
                                title
                            ]),
                            dbc.CardBody(
                                id="metadata",
                                class_name="p-0",
                                children=[dbc.ListGroup(
                                    children=[
                                        dbc.ListGroupItem(
                                            [
                                                dbc.Badge(
                                                    x.split(":")[0]
                                                ),
                                                x.split(": ")[1]
                                            ]
                                        ) for x in graph_data.split("<br>")
                                    ],
                                    flush=True),
                                ]
                            )
                        ]
                    )
                ]
                open_canvas = True

            return metadata, open_canvas
