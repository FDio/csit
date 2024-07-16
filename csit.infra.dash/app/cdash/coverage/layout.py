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
from dash import callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from ast import literal_eval
from yaml import load, FullLoader, YAMLError

from ..utils.constants import Constants as C
from ..utils.control_panel import ControlPanel
from ..utils.trigger import Trigger
from ..utils.utils import label, gen_new_url, generate_options, navbar_report, \
    show_tooltip, get_topo_arch
from ..utils.url_processing import url_decode
from .tables import coverage_tables, select_coverage_data


# Control panel partameters and their default values.
CP_PARAMS = {
    "rls-val": str(),
    "dut-opt": list(),
    "dut-dis": True,
    "dut-val": str(),
    "dutver-opt": list(),
    "dutver-dis": True,
    "dutver-val": str(),
    "phy-opt": list(),
    "phy-dis": True,
    "phy-val": str(),
    "area-opt": list(),
    "area-dis": True,
    "area-val": str(),
    "show-latency": ["show_latency", ]
}


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(
            self,
            app: Flask,
            data_coverage: pd.DataFrame,
            html_layout_file: str,
            tooltip_file: str
        ) -> None:
        """Initialization:
        - save the input parameters,
        - prepare data for the control panel,
        - read HTML layout file,

        :param app: Flask application running the dash application.
        :param html_layout_file: Path and name of the file specifying the HTML
            layout of the dash application.
        :param tooltip_file: Path and name of the yaml file specifying the
            tooltips.
        :type app: Flask
        :type html_layout_file: str
        :type tooltip_file: str
        """

        # Inputs
        self._app = app
        self._data = data_coverage
        self._html_layout_file = html_layout_file
        self._tooltip_file = tooltip_file

        # Get structure of tests:
        tbs = dict()
        cols = ["job", "test_id", "dut_version", "release", ]
        for _, row in self._data[cols].drop_duplicates().iterrows():
            rls = row["release"]
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            d_ver = row["dut_version"]
            tbed = get_topo_arch(lst_job)
            lst_test_id = row["test_id"].split(".")
            if dut == "dpdk":
                area = "dpdk"
            else:
                area = ".".join(lst_test_id[3:-2])
            suite = lst_test_id[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "")
            test = lst_test_id[-1]
            nic = suite.split("-")[0]
            for drv in C.DRIVERS:
                if drv in test:
                    driver = drv.replace("-", "_")
                    test = test.replace(f"{drv}-", "")
                    break
            else:
                driver = "dpdk"
            infra = "-".join((tbed, nic, driver))

            if tbs.get(rls, None) is None:
                tbs[rls] = dict()
            if tbs[rls].get(dut, None) is None:
                tbs[rls][dut] = dict()
            if tbs[rls][dut].get(d_ver, None) is None:
                tbs[rls][dut][d_ver] = dict()
            if tbs[rls][dut][d_ver].get(area, None) is None:
                tbs[rls][dut][d_ver][area] = list()
            if infra not in tbs[rls][dut][d_ver][area]:
                tbs[rls][dut][d_ver][area].append(infra)

        self._spec_tbs = tbs

        # Read from files:
        self._html_layout = str()

        try:
            with open(self._html_layout_file, "r") as file_read:
                self._html_layout = file_read.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._html_layout_file}\n{err}"
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

        # Callbacks:
        if self._app is not None and hasattr(self, "callbacks"):
            self.callbacks(self._app)

    @property
    def html_layout(self):
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

        if self.html_layout and self._spec_tbs:
            return html.Div(
                id="div-main",
                className="small",
                children=[
                    dbc.Row(
                        id="row-navbar",
                        class_name="g-0",
                        children=[navbar_report((False, False, True, False)), ]
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="store-selected-tests"),
                            dcc.Store(id="store-control-panel"),
                            dcc.Location(id="url", refresh=False),
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
                            src=C.URL_DOC_REL_NOTES,
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
                            "An Error Occured"
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
        """Add column with plots. It is placed on the right side.

        :returns: Column with plots.
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

    def _add_ctrl_panel(self) -> list:
        """Add control panel.

        :returns: Control panel.
        :rtype: list
        """
        return [
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(show_tooltip(
                                self._tooltips,
                                "help-release",
                                "CSIT Release"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "rls"},
                                placeholder="Select a Release...",
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self._spec_tbs.keys()
                                    ],
                                    key=lambda d: d["label"]
                                )
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
                                "help-dut",
                                "DUT"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dut"},
                                placeholder="Select a Device under Test..."
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
                                "help-dut-ver",
                                "DUT Version"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "dutver"},
                                placeholder=\
                                    "Select a Version of Device under Test..."
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
                                "help-area",
                                "Area"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "area"},
                                placeholder="Select an Area..."
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
                                "help-infra",
                                "Infra"
                            )),
                            dbc.Select(
                                id={"type": "ctrl-dd", "index": "phy"},
                                placeholder=\
                                    "Select a Physical Test Bed Topology..."
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
                                "help-show-latency",
                                "Latency"
                            )),
                            dbc.Checklist(
                                id="show-latency",
                                options=[{
                                    "value": "show_latency",
                                    "label": "Show Latency"
                                }],
                                value=["show_latency"],
                                inline=True,
                                class_name="ms-2"
                            )
                        ],
                        style={"align-items": "center"},
                        size="sm"
                    )
                ]
            )
        ]

    def _get_plotting_area(
            self,
            selected: dict,
            url: str,
            show_latency: bool
        ) -> list:
        """Generate the plotting area with all its content.

        :param selected: Selected parameters of tests.
        :param url: URL to be displayed in the modal window.
        :param show_latency: If True, latency is displayed in the tables.
        :type selected: dict
        :type url: str
        :type show_latency: bool
        :returns: List of rows with elements to be displayed in the plotting
            area.
        :rtype: list
        """
        if not selected:
            return C.PLACEHOLDER

        return [
            dbc.Row(
                children=coverage_tables(self._data, selected, show_latency),
                class_name="g-0 p-0",
            ),
            dbc.Row(
                children=C.PLACEHOLDER,
                class_name="g-0 p-1"
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
                            dcc.Download(id="download-iterative-data")
                        ],
                        className=\
                            "d-grid gap-0 d-md-flex justify-content-md-end"
                    )])
                ],
                class_name="g-0 p-0"
            ),
            dbc.Row(
                children=C.PLACEHOLDER,
                class_name="g-0 p-1"
            )
        ]

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        @app.callback(
            [
                Output("store-control-panel", "data"),
                Output("store-selected-tests", "data"),
                Output("plotting-area", "children"),
                Output({"type": "ctrl-dd", "index": "rls"}, "value"),
                Output({"type": "ctrl-dd", "index": "dut"}, "options"),
                Output({"type": "ctrl-dd", "index": "dut"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "dut"}, "value"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "options"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "dutver"}, "value"),
                Output({"type": "ctrl-dd", "index": "phy"}, "options"),
                Output({"type": "ctrl-dd", "index": "phy"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "phy"}, "value"),
                Output({"type": "ctrl-dd", "index": "area"}, "options"),
                Output({"type": "ctrl-dd", "index": "area"}, "disabled"),
                Output({"type": "ctrl-dd", "index": "area"}, "value"),
                Output("show-latency", "value"),
            ],
            [
                State("store-control-panel", "data"),
                State("store-selected-tests", "data")
            ],
            [
                Input("url", "href"),
                Input("show-latency", "value"),
                Input({"type": "ctrl-dd", "index": ALL}, "value")
            ]
        )
        def _update_application(
                control_panel: dict,
                selected: dict,
                href: str,
                show_latency: list,
                *_
            ) -> tuple:
            """Update the application when the event is detected.
            """

            ctrl_panel = ControlPanel(CP_PARAMS, control_panel)
            plotting_area = no_update
            on_draw = False
            if selected is None:
                selected = dict()

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            trigger = Trigger(callback_context.triggered)

            if trigger.type == "url" and url_params:
                try:
                    show_latency = literal_eval(url_params["show_latency"][0])
                    selected = literal_eval(url_params["selection"][0])
                except (KeyError, IndexError, AttributeError):
                    pass
                if selected:
                    ctrl_panel.set({
                        "rls-val": selected["rls"],
                        "dut-val": selected["dut"],
                        "dut-opt": generate_options(
                            self._spec_tbs[selected["rls"]].keys()
                        ),
                        "dut-dis": False,
                        "dutver-val": selected["dutver"],
                        "dutver-opt": generate_options(
                            self._spec_tbs[selected["rls"]]\
                                [selected["dut"]].keys()
                        ),
                        "dutver-dis": False,
                        "area-val": selected["area"],
                        "area-opt": [
                            {"label": label(v), "value": v} \
                                for v in sorted(self._spec_tbs[selected["rls"]]\
                                    [selected["dut"]]\
                                        [selected["dutver"]].keys())
                        ],
                        "area-dis": False,
                        "phy-val": selected["phy"],
                        "phy-opt": generate_options(
                            self._spec_tbs[selected["rls"]][selected["dut"]]\
                                [selected["dutver"]][selected["area"]]
                        ),
                        "phy-dis": False,
                        "show-latency": show_latency
                    })
                    on_draw = True
            elif trigger.type == "show-latency":
                ctrl_panel.set({"show-latency": show_latency})
                on_draw = True
            elif trigger.type == "ctrl-dd":
                if trigger.idx == "rls":
                    try:
                        options = generate_options(
                            self._spec_tbs[trigger.value].keys()
                        )
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "rls-val": trigger.value,
                        "dut-val": str(),
                        "dut-opt": options,
                        "dut-dis": disabled,
                        "dutver-val": str(),
                        "dutver-opt": list(),
                        "dutver-dis": True,
                        "phy-val": str(),
                        "phy-opt": list(),
                        "phy-dis": True,
                        "area-val": str(),
                        "area-opt": list(),
                        "area-dis": True
                    })
                elif trigger.idx == "dut":
                    try:
                        rls = ctrl_panel.get("rls-val")
                        dut = self._spec_tbs[rls][trigger.value]
                        options = generate_options(dut.keys())
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dut-val": trigger.value,
                        "dutver-val": str(),
                        "dutver-opt": options,
                        "dutver-dis": disabled,
                        "phy-val": str(),
                        "phy-opt": list(),
                        "phy-dis": True,
                        "area-val": str(),
                        "area-opt": list(),
                        "area-dis": True
                    })
                elif trigger.idx == "dutver":
                    try:
                        rls = ctrl_panel.get("rls-val")
                        dut = ctrl_panel.get("dut-val")
                        ver = self._spec_tbs[rls][dut][trigger.value]
                        options = [
                            {"label": label(v), "value": v} for v in sorted(ver)
                        ]
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "dutver-val": trigger.value,
                        "area-val": str(),
                        "area-opt": options,
                        "area-dis": disabled,
                        "phy-val": str(),
                        "phy-opt": list(),
                        "phy-dis": True
                    })
                elif trigger.idx == "area":
                    try:
                        rls = ctrl_panel.get("rls-val")
                        dut = ctrl_panel.get("dut-val")
                        ver = ctrl_panel.get("dutver-val")
                        options = generate_options(
                            self._spec_tbs[rls][dut][ver][trigger.value])
                        disabled = False
                    except KeyError:
                        options = list()
                        disabled = True
                    ctrl_panel.set({
                        "area-val": trigger.value,
                        "phy-val": str(),
                        "phy-opt": options,
                        "phy-dis": disabled
                    })
                elif trigger.idx == "phy":
                    ctrl_panel.set({"phy-val": trigger.value})
                    selected = {
                        "rls": ctrl_panel.get("rls-val"),
                        "dut": ctrl_panel.get("dut-val"),
                        "dutver": ctrl_panel.get("dutver-val"),
                        "phy": ctrl_panel.get("phy-val"),
                        "area": ctrl_panel.get("area-val"),
                    }
                    on_draw = True

            if on_draw:
                if selected:
                    plotting_area = self._get_plotting_area(
                        selected,
                        gen_new_url(
                            parsed_url,
                            {
                                "selection": selected,
                                "show_latency": show_latency
                            }
                        ),
                        show_latency=bool(show_latency)
                    )
                else:
                    plotting_area = C.PLACEHOLDER
                    selected = dict()

            ret_val = [
                ctrl_panel.panel,
                selected,
                plotting_area,
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
            Output("download-iterative-data", "data"),
            State("store-selected-tests", "data"),
            State("show-latency", "value"),
            Input("plot-btn-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_coverage_data(selection, show_latency, _):
            """Download the data

            :param selection: List of tests selected by user stored in the
                browser.
            :param show_latency: If True, latency is displayed in the tables.
            :type selection: dict
            :type show_latency: bool
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not selection:
                raise PreventUpdate

            df = select_coverage_data(
                self._data,
                selection,
                csv=True,
                show_latency=bool(show_latency)
            )

            return dcc.send_data_frame(df.to_csv, C.COVERAGE_DOWNLOAD_FILE_NAME)

        @app.callback(
            Output("offcanvas-documentation", "is_open"),
            Input("btn-documentation", "n_clicks"),
            State("offcanvas-documentation", "is_open")
        )
        def toggle_offcanvas_documentation(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
