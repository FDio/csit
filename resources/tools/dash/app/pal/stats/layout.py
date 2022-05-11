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

import logging
import pandas as pd
import dash_bootstrap_components as dbc

from flask import Flask
from dash import dcc
from dash import html
from dash import callback_context, no_update
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta
from copy import deepcopy

from ..data.data import Data
from ..data.url_processing import url_decode, url_encode
from .graphs import graph_statistics, select_data


class Layout:
    """
    """

    DEFAULT_JOB = "csit-vpp-perf-mrr-daily-master-2n-icx"

    def __init__(self, app: Flask, html_layout_file: str, spec_file: str,
        graph_layout_file: str, data_spec_file: str, tooltip_file: str,
        time_period: int=None) -> None:
        """
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._spec_file = spec_file
        self._graph_layout_file = graph_layout_file
        self._data_spec_file = data_spec_file
        self._tooltip_file = tooltip_file
        self._time_period = time_period

        # Read the data:
        data_stats, data_mrr, data_ndrpdr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_stats(days=self._time_period)

        df_tst_info = pd.concat([data_mrr, data_ndrpdr], ignore_index=True)

        # Pre-process the data:
        data_stats = data_stats[~data_stats.job.str.contains("-verify-")]
        data_stats = data_stats[~data_stats.job.str.contains("-coverage-")]
        data_stats = data_stats[~data_stats.job.str.contains("-iterative-")]
        data_stats = data_stats[["job", "build", "start_time", "duration"]]

        data_time_period = \
            (datetime.utcnow() - data_stats["start_time"].min()).days
        if self._time_period > data_time_period:
            self._time_period = data_time_period

        jobs = sorted(list(data_stats["job"].unique()))
        job_info = {
            "job": list(),
            "dut": list(),
            "ttype": list(),
            "cadence": list(),
            "tbed": list()
        }
        for job in jobs:
            lst_job = job.split("-")
            job_info["job"].append(job)
            job_info["dut"].append(lst_job[1])
            job_info["ttype"].append(lst_job[3])
            job_info["cadence"].append(lst_job[4])
            job_info["tbed"].append("-".join(lst_job[-2:]))
        self.df_job_info = pd.DataFrame.from_dict(job_info)

        self._default = self._set_job_params(self.DEFAULT_JOB)

        tst_info = {
            "job": list(),
            "build": list(),
            "dut_type": list(),
            "dut_version": list(),
            "hosts": list(),
            "passed": list(),
            "failed": list()
        }
        for job in jobs:
            # TODO: Add list of failed tests for each build
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
        self._tooltips = dict()

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
                f"{self._graph_layout_file}\n{err}"
            )

        try:
            with open(self._tooltip_file, "r") as file_read:
                self._tooltips = load(file_read, Loader=FullLoader)
        except IOError as err:
            logging.warning(
                f"Not possible to open the file {self._tooltip_file}\n{err}"
            )
        except YAMLError as err:
            logging.warning(
                f"An error occurred while parsing the specification file "
                f"{self._tooltip_file}\n{err}"
            )


        self._default_fig_passed, self._default_fig_duration = graph_statistics(
            self.data, self._default["job"], self.layout
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
    def time_period(self) -> int:
        return self._time_period

    @property
    def default(self) -> any:
        return self._default

    def _get_duts(self) -> list:
        """
        """
        return sorted(list(self.df_job_info["dut"].unique()))

    def _get_ttypes(self, dut: str) -> list:
        """
        """
        return sorted(list(self.df_job_info.loc[(
            self.df_job_info["dut"] == dut
        )]["ttype"].unique()))

    def _get_cadences(self, dut: str, ttype: str) -> list:
        """
        """
        return sorted(list(self.df_job_info.loc[(
            (self.df_job_info["dut"] == dut) &
            (self.df_job_info["ttype"] == ttype)
        )]["cadence"].unique()))

    def _get_test_beds(self, dut: str, ttype: str, cadence: str) -> list:
        """
        """
        return sorted(list(self.df_job_info.loc[(
            (self.df_job_info["dut"] == dut) &
            (self.df_job_info["ttype"] == ttype) &
            (self.df_job_info["cadence"] == cadence)
        )]["tbed"].unique()))

    def _get_job(self, dut, ttype, cadence, testbed):
        """Get the name of a job defined by dut, ttype, cadence, testbed.

        Input information comes from control panel.
        """
        return self.df_job_info.loc[(
            (self.df_job_info["dut"] == dut) &
            (self.df_job_info["ttype"] == ttype) &
            (self.df_job_info["cadence"] == cadence) &
            (self.df_job_info["tbed"] == testbed)
        )]["job"].item()

    def _set_job_params(self, job: str) -> dict:
        """
        """
        lst_job = job.split("-")
        return {
            "job": job,
            "dut": lst_job[1],
            "ttype": lst_job[3],
            "cadence": lst_job[4],
            "tbed": "-".join(lst_job[-2:]),
            "duts": self._generate_options(self._get_duts()),
            "ttypes": self._generate_options(self._get_ttypes(lst_job[1])),
            "cadences": self._generate_options(self._get_cadences(
                lst_job[1], lst_job[3])),
            "tbeds": self._generate_options(self._get_test_beds(
                lst_job[1], lst_job[3], lst_job[4]))
        }

    def _show_tooltip(self, id: str, title: str) -> list:
        """
        """
        return [
            f"{title} ",
            dbc.Badge(
                id=id,
                children="?",
                pill=True,
                color="white",
                text_color="info",
                class_name="border ms-1",
            ),
            dbc.Tooltip(
                children=self._tooltips.get(id, str()),
                target=id,
                placement="auto"
            )
        ]

    def add_content(self):
        """
        """
        if self.html_layout:
            return html.Div(
                id="div-main",
                children=[
                    dcc.Store(id="control-panel"),
                    dcc.Location(id="url", refresh=False),
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[
                            self._add_navbar(),
                        ]
                    ),
                    dcc.Loading(
                        dbc.Offcanvas(
                            class_name="w-25",
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
                dbc.Row(
                    class_name="g-0 p-2",
                    align="center",
                    justify="start",
                    children=[
                        dbc.Col(  # Download
                            width=2,
                            children=[
                                dcc.Loading(children=[
                                    dbc.Button(
                                        id="btn-download-data",
                                        children=self._show_tooltip(
                                            "help-download", "Download Data"),
                                        class_name="me-1",
                                        color="info"
                                    ),
                                    dcc.Download(id="download-data")
                                ]),
                            ]
                        ),
                        dbc.Col(  # Show URL
                            width=10,
                            children=[
                                dbc.Card(
                                    id="card-url",
                                    body=True,
                                    class_name="gy-2 p-0",
                                    children=[]
                                ),
                            ]
                        )
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
            class_name="g-0",
            children=[
                dbc.Row(
                    class_name="g-0 p-2",
                    children=[
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=self._show_tooltip(
                                        "help-dut", "Device under Test")
                                ),
                                dbc.Row(
                                    dbc.RadioItems(
                                        id="ri-duts",
                                        inline=True,
                                        value=self.default["dut"],
                                        options=self.default["duts"]
                                    )
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=self._show_tooltip(
                                        "help-ttype", "Test Type"),
                                ),
                                dbc.RadioItems(
                                    id="ri-ttypes",
                                    inline=True,
                                    value=self.default["ttype"],
                                    options=self.default["ttypes"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=self._show_tooltip(
                                        "help-cadence", "Cadence"),
                                ),
                                dbc.RadioItems(
                                    id="ri-cadences",
                                    inline=True,
                                    value=self.default["cadence"],
                                    options=self.default["cadences"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Label(
                                    class_name="p-0",
                                    children=self._show_tooltip(
                                        "help-tbed", "Test Bed"),
                                ),
                                dbc.Select(
                                    id="dd-tbeds",
                                    placeholder="Select a test bed...",
                                    value=self.default["tbed"],
                                    options=self.default["tbeds"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="gy-1",
                            children=[
                                dbc.Alert(
                                    id="al-job",
                                    color="info",
                                    children=self.default["job"]
                                )
                            ]
                        ),
                        dbc.Row(
                            class_name="g-0 p-2",
                            children=[
                                dbc.Label(
                                    class_name="gy-1",
                                    children=self._show_tooltip(
                                        "help-time-period", "Time Period"),
                                ),
                                dcc.DatePickerRange(
                                    id="dpr-period",
                                    className="d-flex justify-content-center",
                                    min_date_allowed=\
                                        datetime.utcnow() - timedelta(
                                            days=self.time_period),
                                    max_date_allowed=datetime.utcnow(),
                                    initial_visible_month=datetime.utcnow(),
                                    start_date=\
                                        datetime.utcnow() - timedelta(
                                            days=self.time_period),
                                    end_date=datetime.utcnow(),
                                    display_format="D MMM YY"
                                )
                            ]
                        )
                    ]
                ),
            ]
        )

    class ControlPanel:
        def __init__(self, panel: dict, default: dict) -> None:
            self._defaults = {
                "ri-ttypes-options": default["ttypes"],
                "ri-cadences-options": default["cadences"],
                "dd-tbeds-options": default["tbeds"],
                "ri-duts-value": default["dut"],
                "ri-ttypes-value": default["ttype"],
                "ri-cadences-value": default["cadence"],
                "dd-tbeds-value": default["tbed"],
                "al-job-children": default["job"]
            }
            self._panel = deepcopy(self._defaults)
            if panel:
                for key in self._defaults:
                    self._panel[key] = panel[key]

        def set(self, kwargs: dict) -> None:
            for key, val in kwargs.items():
                if key in self._panel:
                    self._panel[key] = val
                else:
                    raise KeyError(f"The key {key} is not defined.")

        @property
        def defaults(self) -> dict:
            return self._defaults

        @property
        def panel(self) -> dict:
            return self._panel

        def get(self, key: str) -> any:
            return self._panel[key]

        def values(self) -> list:
            return list(self._panel.values())

    @staticmethod
    def _generate_options(opts: list) -> list:
        return [{"label": i, "value": i} for i in opts]

    @staticmethod
    def _get_date(s_date: str) -> datetime:
        return datetime(int(s_date[0:4]), int(s_date[5:7]), int(s_date[8:10]))

    def callbacks(self, app):

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("graph-passed", "figure"),
            Output("graph-duration", "figure"),
            Output("card-url", "children"),
            Output("ri-ttypes", "options"),
            Output("ri-cadences", "options"),
            Output("dd-tbeds", "options"),
            Output("ri-duts", "value"),
            Output("ri-ttypes", "value"),
            Output("ri-cadences", "value"),
            Output("dd-tbeds", "value"),
            Output("al-job", "children"),
            State("control-panel", "data"),  # Store
            Input("ri-duts", "value"),
            Input("ri-ttypes", "value"),
            Input("ri-cadences", "value"),
            Input("dd-tbeds", "value"),
            Input("dpr-period", "start_date"),
            Input("dpr-period", "end_date"),
            Input("url", "href")
            # prevent_initial_call=True
        )
        def _update_ctrl_panel(cp_data: dict, dut:str, ttype: str, cadence:str,
                tbed: str, start: str, end: str, href: str) -> tuple:
            """
            """

            ctrl_panel = self.ControlPanel(cp_data, self.default)

            start = self._get_date(start)
            end = self._get_date(end)

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "ri-duts":
                ttype_opts = self._generate_options(self._get_ttypes(dut))
                ttype_val = ttype_opts[0]["value"]
                cad_opts = self._generate_options(
                    self._get_cadences(dut, ttype_val))
                cad_val = cad_opts[0]["value"]
                tbed_opts = self._generate_options(
                    self._get_test_beds(dut, ttype_val, cad_val))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-duts-value": dut,
                    "ri-ttypes-options": ttype_opts,
                    "ri-ttypes-value": ttype_val,
                    "ri-cadences-options": cad_opts,
                    "ri-cadences-value": cad_val,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "ri-ttypes":
                cad_opts = self._generate_options(
                    self._get_cadences(ctrl_panel.get("ri-duts-value"), ttype))
                cad_val = cad_opts[0]["value"]
                tbed_opts = self._generate_options(
                    self._get_test_beds(ctrl_panel.get("ri-duts-value"),
                    ttype, cad_val))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-ttypes-value": ttype,
                    "ri-cadences-options": cad_opts,
                    "ri-cadences-value": cad_val,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "ri-cadences":
                tbed_opts = self._generate_options(
                    self._get_test_beds(ctrl_panel.get("ri-duts-value"),
                    ctrl_panel.get("ri-ttypes-value"), cadence))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-cadences-value": cadence,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "dd-tbeds":
                ctrl_panel.set({
                    "dd-tbeds-value": tbed
                })
            elif trigger_id == "dpr-period":
                pass
            elif trigger_id == "url":
                # TODO: Add verification
                if url_params:
                    new_job = url_params.get("job", list())[0]
                    new_start = url_params.get("start", list())[0]
                    new_end = url_params.get("end", list())[0]
                    if new_job and new_start and new_end:
                        start = self._get_date(new_start)
                        end = self._get_date(new_end)
                        job_params = self._set_job_params(new_job)
                        ctrl_panel = self.ControlPanel(None, job_params)
                else:
                    ctrl_panel = self.ControlPanel(cp_data, self.default)
                    job = self._get_job(
                        ctrl_panel.get("ri-duts-value"),
                        ctrl_panel.get("ri-ttypes-value"),
                        ctrl_panel.get("ri-cadences-value"),
                        ctrl_panel.get("dd-tbeds-value")
                    )

            job = self._get_job(
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )

            ctrl_panel.set({"al-job-children": job})
            fig_passed, fig_duration = graph_statistics(self.data, job,
                self.layout, start, end)

            if parsed_url:
                new_url = url_encode({
                    "scheme": parsed_url["scheme"],
                    "netloc": parsed_url["netloc"],
                    "path": parsed_url["path"],
                    "params": {
                        "job": job,
                        "start": start,
                        "end": end
                    }
                })
            else:
                new_url = str()

            ret_val = [
                ctrl_panel.panel,
                fig_passed,
                fig_duration,
                [  # URL
                    dcc.Clipboard(
                        target_id="card-url",
                        title="Copy URL",
                        style={"display": "inline-block"}
                    ),
                    new_url
                ]
            ]
            ret_val.extend(ctrl_panel.values())
            return ret_val

        @app.callback(
            Output("download-data", "data"),
            State("control-panel", "data"),  # Store
            State("dpr-period", "start_date"),
            State("dpr-period", "end_date"),
            Input("btn-download-data", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(cp_data: dict, start: str, end: str, n_clicks: int):
            """
            """
            if not (n_clicks):
                raise PreventUpdate

            ctrl_panel = self.ControlPanel(cp_data, self.default)

            job = self._get_job(
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )

            start = datetime(int(start[0:4]), int(start[5:7]), int(start[8:10]))
            end = datetime(int(end[0:4]), int(end[5:7]), int(end[8:10]))
            data = select_data(self.data, job, start, end)
            data = data.drop(columns=["job", ])

            return dcc.send_data_frame(data.T.to_csv, f"{job}-stats.csv")

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
