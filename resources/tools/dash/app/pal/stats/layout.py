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

from ..utils.constants import Constants as C
from ..utils.utils import show_tooltip, gen_new_url, get_date, get_ttypes, \
    get_cadences, get_test_beds, get_job, generate_options, set_job_params
from ..utils.url_processing import url_decode
from ..data.data import Data
from .graphs import graph_statistics, select_data


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(self, app: Flask, html_layout_file: str,
        graph_layout_file: str, data_spec_file: str, tooltip_file: str,
        time_period: int=None) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param graph_layout_file: Path and name of the file with layout of
            plot.ly graphs.
        :param data_spec_file: Path and name of the file specifying the data to
            be read from parquets for this application.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :param time_period: It defines the time period for data read from the
            parquets in days from now back to the past.
        :type app: Flask
        :type html_layout_file: str
        :type graph_layout_file: str
        :type data_spec_file: str
        :type tooltip_file: str
        :type time_period: int
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
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
        d_job_info = {
            "job": list(),
            "dut": list(),
            "ttype": list(),
            "cadence": list(),
            "tbed": list()
        }
        for job in jobs:
            lst_job = job.split("-")
            d_job_info["job"].append(job)
            d_job_info["dut"].append(lst_job[1])
            d_job_info["ttype"].append(lst_job[3])
            d_job_info["cadence"].append(lst_job[4])
            d_job_info["tbed"].append("-".join(lst_job[-2:]))
        self.job_info = pd.DataFrame.from_dict(d_job_info)

        self._default = set_job_params(self.job_info, C.STATS_DEFAULT_JOB)

        tst_info = {
            "job": list(),
            "build": list(),
            "dut_type": list(),
            "dut_version": list(),
            "hosts": list(),
            "passed": list(),
            "failed": list(),
            "lst_failed": list()
        }
        for job in jobs:
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
                    passed = df_build.value_counts(subset="passed")[True]
                except KeyError:
                    passed = 0
                try:
                    failed = df_build.value_counts(subset="passed")[False]
                    failed_tests = df_build.loc[(df_build["passed"] == False)]\
                        ["test_id"].to_list()
                    l_failed = list()
                    for tst in failed_tests:
                        lst_tst = tst.split(".")
                        suite = lst_tst[-2].replace("2n1l-", "").\
                            replace("1n1l-", "").replace("2n-", "")
                        l_failed.append(f"{suite.split('-')[0]}-{lst_tst[-1]}")
                except KeyError:
                    failed = 0
                    l_failed = list()
                tst_info["passed"].append(passed)
                tst_info["failed"].append(failed)
                tst_info["lst_failed"].append(sorted(l_failed))

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

    def add_content(self):
        """Top level method which generated the web page.

        It generates:
        - Store for user input data,
        - Navigation bar,
        - Main area with control panel and ploting area.

        If no HTML layout is provided, an error message is displayed instead.

        :returns: The HTML div with the whole page.
        :rtype: html.Div
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

        :returns: Navigation bar.
        :rtype: dbc.NavbarSimple
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

        :returns: Column with the control panel.
        :rtype: dbc.Col
        """
        return dbc.Col(
            id="col-controls",
            children=[
                self._add_ctrl_panel(),
            ],
        )

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with plots and tables. It is placed on the right side.

        :returns: Column with tables.
        :rtype: dbc.Col
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
                                        children=show_tooltip(self._tooltips,
                                            "help-download", "Download Data"),
                                        class_name="me-1",
                                        color="info"
                                    ),
                                    dcc.Download(id="download-data")
                                ])
                            ]
                        ),
                        dbc.Col(  # Show URL
                            width=10,
                            children=[
                                dbc.InputGroup(
                                    class_name="me-1",
                                    children=[
                                        dbc.InputGroupText(
                                            style=C.URL_STYLE,
                                            children=show_tooltip(
                                                self._tooltips,
                                                "help-url", "URL",
                                                "input-url"
                                            )
                                        ),
                                        dbc.Input(
                                            id="input-url",
                                            readonly=True,
                                            type="url",
                                            style=C.URL_STYLE,
                                            value=""
                                        )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ],
            width=9,
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """Add control panel.

        :returns: Control panel.
        :rtype: dbc.Row
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
                                    children=show_tooltip(self._tooltips,
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
                                    children=show_tooltip(self._tooltips,
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
                                    children=show_tooltip(self._tooltips,
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
                                    children=show_tooltip(self._tooltips,
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
                                    children=show_tooltip(self._tooltips,
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
        """A class representing the control panel.
        """

        def __init__(self, panel: dict, default: dict) -> None:
            """Initialisation of the control pannel by default values. If
            particular values are provided (parameter "panel") they are set
            afterwards.

            :param panel: Custom values to be set to the control panel.
            :param default: Default values to be set to the control panel.
            :type panel: dict
            :type defaults: dict
            """

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
            """Set the values of the Control panel.

            :param kwargs: key - value pairs to be set.
            :type kwargs: dict
            :raises KeyError: If the key in kwargs is not present in the Control
                panel.
            """
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
            """Returns the value of a key from the Control panel.

            :param key: The key which value should be returned.
            :type key: str
            :returns: The value of the key.
            :rtype: any
            :raises KeyError: If the key in kwargs is not present in the Control
                panel.
            """
            return self._panel[key]

        def values(self) -> list:
            """Returns the values from the Control panel as a list.

            :returns: The values from the Control panel.
            :rtype: list
            """
            return list(self._panel.values())


    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("graph-passed", "figure"),
            Output("graph-duration", "figure"),
            Output("input-url", "value"),
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
        )
        def _update_ctrl_panel(cp_data: dict, dut: str, ttype: str, cadence:str,
                tbed: str, start: str, end: str, href: str) -> tuple:
            """Update the application when the event is detected.

            :param cp_data: Current status of the control panel stored in
                browser.
            :param dut: Input - DUT name.
            :param ttype: Input - Test type.
            :param cadence: Input - The cadence of the job.
            :param tbed: Input - The test bed.
            :param start: Date and time where the data processing starts.
            :param end: Date and time where the data processing ends.
            :param href: Input - The URL provided by the browser.
            :type cp_data: dict
            :type dut: str
            :type ttype: str
            :type cadence: str
            :type tbed: str
            :type start: str
            :type end: str
            :type href: str
            :returns: New values for web page elements.
            :rtype: tuple
            """

            ctrl_panel = self.ControlPanel(cp_data, self.default)

            start = get_date(start)
            end = get_date(end)

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "ri-duts":
                ttype_opts = generate_options(get_ttypes(self.job_info, dut))
                ttype_val = ttype_opts[0]["value"]
                cad_opts = generate_options(get_cadences(
                    self.job_info, dut, ttype_val))
                cad_val = cad_opts[0]["value"]
                tbed_opts = generate_options(get_test_beds(
                    self.job_info, dut, ttype_val, cad_val))
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
                cad_opts = generate_options(get_cadences(
                    self.job_info, ctrl_panel.get("ri-duts-value"), ttype))
                cad_val = cad_opts[0]["value"]
                tbed_opts = generate_options(get_test_beds(
                    self.job_info, ctrl_panel.get("ri-duts-value"), ttype,
                    cad_val))
                tbed_val = tbed_opts[0]["value"]
                ctrl_panel.set({
                    "ri-ttypes-value": ttype,
                    "ri-cadences-options": cad_opts,
                    "ri-cadences-value": cad_val,
                    "dd-tbeds-options": tbed_opts,
                    "dd-tbeds-value": tbed_val
                })
            elif trigger_id == "ri-cadences":
                tbed_opts = generate_options(get_test_beds(
                    self.job_info, ctrl_panel.get("ri-duts-value"),
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
                        start = get_date(new_start)
                        end = get_date(new_end)
                        job_params = set_job_params(self.job_info, new_job)
                        ctrl_panel = self.ControlPanel(None, job_params)
                else:
                    ctrl_panel = self.ControlPanel(cp_data, self.default)

            job = get_job(
                self.job_info,
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )

            ctrl_panel.set({"al-job-children": job})
            fig_passed, fig_duration = graph_statistics(self.data, job,
                self.layout, start, end)

            ret_val = [
                ctrl_panel.panel,
                fig_passed,
                fig_duration,
                gen_new_url(
                    parsed_url,
                    {
                        "job": job,
                        "start": start,
                        "end": end
                    }
                )
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
            """Download the data

            :param cp_data: Current status of the control panel stored in
                browser.
            :param start: Date and time where the data processing starts.
            :param end: Date and time where the data processing ends.
            :param n_clicks: Number of clicks on the button "Download".
            :type cp_data: dict
            :type start: str
            :type end: str
            :type n_clicks: int
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """
            if not (n_clicks):
                raise PreventUpdate

            ctrl_panel = self.ControlPanel(cp_data, self.default)

            job = get_job(
                self.job_info,
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )

            data = select_data(self.data, job, get_date(start), get_date(end))
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
            """Generates the data for the offcanvas displayed when a particular
            point in a graph is clicked on.

            :param passed_data: The data from the clicked point in the graph
                displaying the pass/fail data.
            :param duration_data: The data from the clicked point in the graph
                displaying the duration data.
            :type passed_data: dict
            :type duration data: dict
            :returns: The data to be displayed on the offcanvas (job statistics
                and the list of failed tests) and the information to show the
                offcanvas.
            :rtype: tuple(list, bool)
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
                lst_graph_data = graph_data.split("<br>")

                # Prepare list of failed tests:
                job = str()
                build = str()
                for itm in lst_graph_data:
                    if "csit-ref:" in itm:
                        job, build = itm.split(" ")[-1].split("/")
                        break
                if job and build:
                    fail_tests = self.data.loc[
                        (self.data["job"] == job) &
                        (self.data["build"] == build)
                    ]["lst_failed"].values[0]
                    if not fail_tests:
                        fail_tests = None
                else:
                    fail_tests = None

                # Create the content of the offcanvas:
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
                                        ) for x in lst_graph_data
                                    ],
                                    flush=True),
                                ]
                            )
                        ]
                    )
                ]

                if fail_tests is not None:
                    metadata.append(
                        dbc.Card(
                            class_name="gy-2 p-0",
                            children=[
                                dbc.CardHeader(
                                    f"List of Failed Tests ({len(fail_tests)})"
                                ),
                                dbc.CardBody(
                                    id="failed-tests",
                                    class_name="p-0",
                                    children=[dbc.ListGroup(
                                        children=[
                                            dbc.ListGroupItem(x) \
                                                for x in fail_tests
                                        ],
                                        flush=True),
                                    ]
                                )
                            ]
                        )
                    )

                open_canvas = True

            return metadata, open_canvas
