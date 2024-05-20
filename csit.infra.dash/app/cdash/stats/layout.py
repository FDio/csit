# Copyright (c) 2024 Cisco and/or its affiliates.
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

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.utils import show_tooltip, gen_new_url, get_ttypes, get_cadences, \
    get_test_beds, get_job, generate_options, set_job_params, navbar_trending
from ..utils.url_processing import url_decode
from .graphs import graph_statistics, select_data


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(
            self,
            app: Flask,
            data_stats: pd.DataFrame,
            data_trending: pd.DataFrame,
            html_layout_file: str,
            graph_layout_file: str,
            tooltip_file: str
        ) -> None:
        """Initialization:
        - save the input parameters,
        - read and pre-process the data,
        - prepare data for the control panel,
        - read HTML layout file,
        - read tooltips from the tooltip file.

        :param app: Flask application running the dash application.
        :param data_stats: Pandas dataframe with staistical data.
        :param data_trending: Pandas dataframe with trending data.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param graph_layout_file: Path and name of the file with layout of
            plot.ly graphs.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type data_stats: pandas.DataFrame
        :type data_trending: pandas.DataFrame
        :type html_layout_file: str
        :type graph_layout_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._graph_layout_file = graph_layout_file
        self._tooltip_file = tooltip_file

        # Pre-process the data:
        data_stats = data_stats[~data_stats.job.str.contains("-verify-")]
        data_stats = data_stats[~data_stats.job.str.contains("-coverage-")]
        data_stats = data_stats[~data_stats.job.str.contains("-iterative-")]
        data_stats = data_stats[["job", "build", "start_time", "duration"]]

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
        self._job_info = pd.DataFrame.from_dict(d_job_info)

        self._default = set_job_params(self._job_info, C.STATS_DEFAULT_JOB)

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
            df_job = data_trending.loc[(data_trending["job"] == job)]
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
        self._html_layout = str()
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

        # Control panel partameters and their default values.
        self._cp_default = {
            "ri-ttypes-options": self._default["ttypes"],
            "ri-cadences-options": self._default["cadences"],
            "dd-tbeds-options": self._default["tbeds"],
            "ri-duts-value": self._default["dut"],
            "ri-ttypes-value": self._default["ttype"],
            "ri-cadences-value": self._default["cadence"],
            "dd-tbeds-value": self._default["tbed"],
            "al-job-children": html.A(
                self._default["job"],
                href=f"{C.URL_CICD}{self._default['job']}",
                target="_blank"
            )
        }

        # Callbacks:
        if self._app is not None and hasattr(self, "callbacks"):
            self.callbacks(self._app)

    @property
    def html_layout(self) -> dict:
        return self._html_layout

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
                className="small",
                children=[
                    dcc.Store(id="control-panel"),
                    dcc.Location(id="url", refresh=False),
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_trending((False, False, True, False))]
                    ),
                    dbc.Spinner(
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
                            self._add_plotting_col()
                        ]
                    ),
                    dbc.Offcanvas(
                        class_name="w-75",
                        id="offcanvas-documentation",
                        title="Documentation",
                        placement="end",
                        is_open=False,
                        children=html.Iframe(
                            src=C.URL_DOC_TRENDING,
                            width="100%",
                            height="100%"
                        )
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
                        color="danger"
                    )
                ]
            )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with controls. It is placed on the left side.

        :returns: Column with the control panel.
        :rtype: dbc.Col
        """
        return dbc.Col([
            html.Div(
                children=self._add_ctrl_panel(),
                className="sticky-top"
            )
        ])

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with plots and tables. It is placed on the right side.

        :returns: Column with tables.
        :rtype: dbc.Col
        """
        return dbc.Col(
            id="col-plotting-area",
            children=[
                dbc.Spinner(
                    children=[
                        dbc.Row(
                            id="plotting-area",
                            class_name="g-0 p-0",
                            children=[
                                C.PLACEHOLDER
                            ]
                        )
                    ]
                )
            ],
            width=9
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """Add control panel.

        :returns: Control panel.
        :rtype: dbc.Row
        """
        return [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-dut",
                                "DUT"
                            )),
                            dbc.RadioItems(
                                id="ri-duts",
                                inline=True,
                                value=self._default["dut"],
                                options=self._default["duts"],
                                class_name="form-control"
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-ttype",
                                "Test Type"
                            )),
                            dbc.RadioItems(
                                id="ri-ttypes",
                                inline=True,
                                value=self._default["ttype"],
                                options=self._default["ttypes"],
                                class_name="form-control"
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-cadence",
                                "Cadence"
                            )),
                            dbc.RadioItems(
                                id="ri-cadences",
                                inline=True,
                                value=self._default["cadence"],
                                options=self._default["cadences"],
                                class_name="form-control"
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-tbed",
                                "Test Bed"
                            )),
                            dbc.Select(
                                id="dd-tbeds",
                                placeholder="Select a test bed...",
                                value=self._default["tbed"],
                                options=self._default["tbeds"]
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Alert(
                        id="al-job",
                        color="info",
                        children=self._default["job"]
                    )
                ]
            )
        ]

    def _get_plotting_area(
            self,
            job: str,
            url: str
        ) -> list:
        """Generate the plotting area with all its content.

        :param job: The job which data will be displayed.
        :param url: URL to be displayed in the modal window.
        :type job: str
        :type url: str
        :returns: List of rows with elements to be displayed in the plotting
            area.
        :rtype: list
        """

        figs = graph_statistics(self._data, job, self._graph_layout)

        if not figs[0]:
            return C.PLACEHOLDER

        return [
            dbc.Row(
                id="row-graph-passed",
                class_name="g-0 p-1",
                children=[
                    dcc.Graph(
                        id="graph-passed",
                        figure=figs[0]
                    )
                ]
            ),
            dbc.Row(
                id="row-graph-duration",
                class_name="g-0 p-1",
                children=[
                    dcc.Graph(
                        id="graph-duration",
                        figure=figs[1]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col([html.Div(
                        [
                            dbc.Button(
                                id="plot-btn-url",
                                children="Show URL",
                                class_name="me-1",
                                color="info",
                                style={
                                    "text-transform": "none",
                                    "padding": "0rem 1rem"
                                }
                            ),
                            dbc.Modal(
                                [
                                    dbc.ModalHeader(dbc.ModalTitle("URL")),
                                    dbc.ModalBody(url)
                                ],
                                id="plot-mod-url",
                                size="xl",
                                is_open=False,
                                scrollable=True
                            ),
                            dbc.Button(
                                id="plot-btn-download",
                                children="Download Data",
                                class_name="me-1",
                                color="info",
                                style={
                                    "text-transform": "none",
                                    "padding": "0rem 1rem"
                                }
                            ),
                            dcc.Download(id="download-stats-data")
                        ],
                        className=\
                            "d-grid gap-0 d-md-flex justify-content-md-end"
                    )])
                ],
                class_name="g-0 p-0"
            )
        ]

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("plotting-area", "children"),
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
            Input("url", "href")
        )
        def _update_ctrl_panel(cp_data: dict, dut: str, ttype: str,
                cadence: str, tbed: str, href: str) -> tuple:
            """Update the application when the event is detected.

            :param cp_data: Current status of the control panel stored in
                browser.
            :param dut: Input - DUT name.
            :param ttype: Input - Test type.
            :param cadence: Input - The cadence of the job.
            :param tbed: Input - The test bed.
            :param href: Input - The URL provided by the browser.
            :type cp_data: dict
            :type dut: str
            :type ttype: str
            :type cadence: str
            :type tbed: str
            :type href: str
            :returns: New values for web page elements.
            :rtype: tuple
            """

            ctrl_panel = ControlPanel(self._cp_default, cp_data)

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "ri-duts":
                ttype_opts = generate_options(get_ttypes(self._job_info, dut))
                ttype_val = ttype_opts[0]["value"]
                cad_opts = generate_options(get_cadences(
                    self._job_info, dut, ttype_val))
                cad_val = cad_opts[0]["value"]
                tbed_opts = generate_options(get_test_beds(
                    self._job_info, dut, ttype_val, cad_val))
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
                    self._job_info, ctrl_panel.get("ri-duts-value"), ttype))
                cad_val = cad_opts[0]["value"]
                tbed_opts = generate_options(get_test_beds(
                    self._job_info, ctrl_panel.get("ri-duts-value"), ttype,
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
                    self._job_info, ctrl_panel.get("ri-duts-value"),
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
            elif trigger_id == "url":
                if url_params:
                    new_job = url_params.get("job", list())[0]
                    if new_job:
                        job_params = set_job_params(self._job_info, new_job)
                        ctrl_panel = ControlPanel(
                            {
                                "ri-ttypes-options": job_params["ttypes"],
                                "ri-cadences-options": job_params["cadences"],
                                "dd-tbeds-options": job_params["tbeds"],
                                "ri-duts-value": job_params["dut"],
                                "ri-ttypes-value": job_params["ttype"],
                                "ri-cadences-value": job_params["cadence"],
                                "dd-tbeds-value": job_params["tbed"],
                                "al-job-children": html.A(
                                    self._default["job"],
                                    href=(
                                        f"{C.URL_CICD}"
                                        f"{self._default['job']}"
                                    ),
                                    target="_blank"
                                )
                            },
                            None
                        )
                else:
                    ctrl_panel = ControlPanel(self._cp_default, cp_data)

            job = get_job(
                self._job_info,
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )

            ctrl_panel.set(
                {
                    "al-job-children": html.A(
                        job,
                        href=f"{C.URL_CICD}{job}",
                        target="_blank"
                    )
                }
            )
            plotting_area = self._get_plotting_area(
                job,
                gen_new_url(parsed_url, {"job": job})
            )

            ret_val = [
                ctrl_panel.panel,
                plotting_area
            ]
            ret_val.extend(ctrl_panel.values)
            return ret_val

        @app.callback(
            Output("plot-mod-url", "is_open"),
            [Input("plot-btn-url", "n_clicks")],
            [State("plot-mod-url", "is_open")],
        )
        def toggle_plot_mod_url(n, is_open):
            """Toggle the modal window with url.
            """
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output("download-stats-data", "data"),
            State("control-panel", "data"),  # Store
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(cp_data: dict, n_clicks: int):
            """Download the data

            :param cp_data: Current status of the control panel stored in
                browser.
            :param n_clicks: Number of clicks on the button "Download".
            :type cp_data: dict
            :type n_clicks: int
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """
            if not n_clicks:
                raise PreventUpdate

            ctrl_panel = ControlPanel(self._cp_default, cp_data)

            job = get_job(
                self._job_info,
                ctrl_panel.get("ri-duts-value"),
                ctrl_panel.get("ri-ttypes-value"),
                ctrl_panel.get("ri-cadences-value"),
                ctrl_panel.get("dd-tbeds-value")
            )

            data = select_data(self._data, job)
            data = data.drop(columns=["job", ])

            return dcc.send_data_frame(
                data.T.to_csv, f"{job}-{C.STATS_DOWNLOAD_FILE_NAME}")

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
                    fail_tests = self._data.loc[
                        (self._data["job"] == job) &
                        (self._data["build"] == build)
                    ]["lst_failed"].values[0]
                    if not fail_tests:
                        fail_tests = None
                else:
                    fail_tests = None

                # Create the content of the offcanvas:
                list_group_items = list()
                for itm in lst_graph_data:
                    lst_itm = itm.split(": ")
                    if lst_itm[0] == "csit-ref":
                        list_group_item = dbc.ListGroupItem([
                            dbc.Badge(lst_itm[0]),
                            html.A(
                                lst_itm[1],
                                href=f"{C.URL_LOGS}{lst_itm[1]}",
                                target="_blank"
                            )
                        ])
                    else:
                        list_group_item = dbc.ListGroupItem([
                            dbc.Badge(lst_itm[0]),
                            lst_itm[1]
                        ])
                    list_group_items.append(list_group_item)
                metadata = [
                    dbc.Card(
                        class_name="gy-2 p-0",
                        children=[
                            dbc.CardHeader([
                                dcc.Clipboard(
                                    target_id="metadata",
                                    title="Copy",
                                    style={"display": "inline-block"}
                                ),
                                title
                            ]),
                            dbc.CardBody(
                                dbc.ListGroup(list_group_items, flush=True),
                                id="metadata",
                                class_name="p-0"
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

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
