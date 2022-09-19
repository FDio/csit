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
from dash import callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from datetime import datetime
from copy import deepcopy
from json import loads, JSONDecodeError
from ast import literal_eval

from ..utils.constants import Constants as C
from ..utils.utils import get_color, show_tooltip, label, sync_checklists, \
    gen_new_url, generate_options
from ..utils.url_processing import url_decode
from ..data.data import Data
from .graphs import graph_trending, graph_hdrh_latency, \
    select_trending_data


class Layout:
    """The layout of the dash app and the callbacks.
    """

    def __init__(self, app: Flask, html_layout_file: str,
        graph_layout_file: str, data_spec_file: str, tooltip_file: str,
        time_period: str=None) -> None:
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
        data_mrr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_trending_mrr(days=self._time_period)

        data_ndrpdr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_trending_ndrpdr(days=self._time_period)

        self._data = pd.concat([data_mrr, data_ndrpdr], ignore_index=True)

        data_time_period = \
            (datetime.utcnow() - self._data["start_time"].min()).days
        if self._time_period > data_time_period:
            self._time_period = data_time_period


        # Get structure of tests:
        tbs = dict()
        for _, row in self._data[["job", "test_id"]].drop_duplicates().\
                iterrows():
            lst_job = row["job"].split("-")
            dut = lst_job[1]
            ttype = lst_job[3]
            tbed = "-".join(lst_job[-2:])
            lst_test = row["test_id"].split(".")
            if dut == "dpdk":
                area = "dpdk"
            else:
                area = "-".join(lst_test[3:-2])
            suite = lst_test[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "")
            test = lst_test[-1]
            nic = suite.split("-")[0]
            for drv in C.DRIVERS:
                if drv in test:
                    if drv == "af-xdp":
                        driver = "af_xdp"
                    else:
                        driver = drv
                    test = test.replace(f"{drv}-", "")
                    break
            else:
                driver = "dpdk"
            infra = "-".join((tbed, nic, driver))
            lst_test = test.split("-")
            framesize = lst_test[0]
            core = lst_test[1] if lst_test[1] else "8C"
            test = "-".join(lst_test[2: -1])

            if tbs.get(dut, None) is None:
                tbs[dut] = dict()
            if tbs[dut].get(infra, None) is None:
                tbs[dut][infra] = dict()
            if tbs[dut][infra].get(area, None) is None:
                tbs[dut][infra][area] = dict()
            if tbs[dut][infra][area].get(test, None) is None:
                tbs[dut][infra][area][test] = dict()
                tbs[dut][infra][area][test]["core"] = list()
                tbs[dut][infra][area][test]["frame-size"] = list()
                tbs[dut][infra][area][test]["test-type"] = list()
            if core.upper() not in tbs[dut][infra][area][test]["core"]:
                tbs[dut][infra][area][test]["core"].append(core.upper())
            if framesize.upper() not in \
                    tbs[dut][infra][area][test]["frame-size"]:
                tbs[dut][infra][area][test]["frame-size"].append(
                    framesize.upper())
            if ttype == "mrr":
                if "MRR" not in tbs[dut][infra][area][test]["test-type"]:
                    tbs[dut][infra][area][test]["test-type"].append("MRR")
            elif ttype == "ndrpdr":
                if "NDR" not in tbs[dut][infra][area][test]["test-type"]:
                    tbs[dut][infra][area][test]["test-type"].extend(
                        ("NDR", "PDR"))
        self._spec_tbs = tbs

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

        # Callbacks:
        if self._app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self._app)

    @property
    def html_layout(self):
        return self._html_layout

    @property
    def spec_tbs(self):
        return self._spec_tbs

    @property
    def data(self):
        return self._data

    @property
    def layout(self):
        return self._graph_layout

    @property
    def time_period(self):
        return self._time_period

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

        if self.html_layout and self.spec_tbs:
            return html.Div(
                id="div-main",
                className="small",
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
                            title="Throughput And Latency",
                            placement="end",
                            is_open=False,
                            children=[
                                dbc.Row(id="metadata-tput-lat"),
                                dbc.Row(id="metadata-hdrh-graph"),
                            ]
                        )
                    ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="selected-tests"),
                            dcc.Store(id="control-panel"),
                            dcc.Location(id="url", refresh=False),
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
                        C.TREND_TITLE,
                        disabled=True,
                        external_link=True,
                        href="#"
                    )
                )
            ],
            brand=C.BRAND,
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
                dcc.Loading(
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
            width=9,
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
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-dut", "DUT")
                            ),
                            dbc.Select(
                                id="dd-ctrl-dut",
                                placeholder=(
                                    "Select a Device under Test..."
                                ),
                                options=sorted(
                                    [
                                        {"label": k, "value": k} \
                                            for k in self.spec_tbs.keys()
                                    ],
                                    key=lambda d: d["label"]
                                )
                            )
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-infra", "Infra")
                            ),
                            dbc.Select(
                                id="dd-ctrl-phy",
                                placeholder=(
                                    "Select a Physical Test Bed "
                                    "Topology..."
                                )
                            )
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-area", "Area")
                            ),
                            dbc.Select(
                                id="dd-ctrl-area",
                                placeholder="Select an Area...",
                                disabled=True,
                            ),
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.InputGroup(
                        [
                            dbc.InputGroupText(
                                children=show_tooltip(self._tooltips,
                                    "help-test", "Test")
                            ),
                            dbc.Select(
                                id="dd-ctrl-test",
                                placeholder="Select a Test...",
                                disabled=True,
                            ),
                        ],
                        size="sm",
                    ),
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-framesize", "Frame Size"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-framesize-all",
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                switch=False
                            ),
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-framesize",
                                inline=True,
                                switch=False
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-cores", "Number of Cores"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-core-all",
                                options=C.CL_ALL_DISABLED,
                                inline=False,
                                switch=False
                            )
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-core",
                                inline=True,
                                switch=False
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-ttype", "Test Type"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-testtype-all",
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                switch=False
                            ),
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-testtype",
                                inline=True,
                                switch=False
                            )
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(self._tooltips,
                            "help-normalize", "Normalize"),
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                id="cl-ctrl-normalize",
                                options=[{
                                    "value": "normalize",
                                    "label": (
                                        "Normalize results to CPU "
                                        "frequency 2GHz"
                                    )
                                }],
                                value=[],
                                inline=True,
                                switch=False
                            ),
                        ]
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Button(
                        id="btn-ctrl-add",
                        children="Add Selected",
                        color="info"
                    )
                ]
            ),
            dbc.Row(
                id="row-card-sel-tests",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED,
                children=[
                    dbc.Label("Selected tests"),
                    dbc.ListGroup(
                        class_name="overflow-auto p-0",
                        id="lg-selected",
                        children=[],
                        style={"max-height": "14em"},
                        flush=True
                    )
                ],
            ),
            dbc.Row(
                id="row-btns-sel-tests",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED,
                children=[
                    dbc.ButtonGroup(
                        children=[
                            dbc.Button(
                                id="btn-sel-remove",
                                children="Remove Selected",
                                class_name="w-100",
                                color="info",
                                disabled=False
                            ),
                            dbc.Button(
                                id="btn-sel-remove-all",
                                children="Remove All",
                                class_name="w-100",
                                color="info",
                                disabled=False
                            ),
                        ]
                    )
                ]
            )
        ]

    class ControlPanel:
        """A class representing the control panel.
        """

        def __init__(self, panel: dict) -> None:
            """Initialisation of the control pannel by default values. If
            particular values are provided (parameter "panel") they are set
            afterwards.

            :param panel: Custom values to be set to the control panel.
            :param default: Default values to be set to the control panel.
            :type panel: dict
            :type defaults: dict
            """

            # Defines also the order of keys
            self._defaults = {
                "dd-ctrl-dut-value": str(),
                "dd-ctrl-phy-options": list(),
                "dd-ctrl-phy-disabled": True,
                "dd-ctrl-phy-value": str(),
                "dd-ctrl-area-options": list(),
                "dd-ctrl-area-disabled": True,
                "dd-ctrl-area-value": str(),
                "dd-ctrl-test-options": list(),
                "dd-ctrl-test-disabled": True,
                "dd-ctrl-test-value": str(),
                "cl-ctrl-core-options": list(),
                "cl-ctrl-core-value": list(),
                "cl-ctrl-core-all-value": list(),
                "cl-ctrl-core-all-options": C.CL_ALL_DISABLED,
                "cl-ctrl-framesize-options": list(),
                "cl-ctrl-framesize-value": list(),
                "cl-ctrl-framesize-all-value": list(),
                "cl-ctrl-framesize-all-options": C.CL_ALL_DISABLED,
                "cl-ctrl-testtype-options": list(),
                "cl-ctrl-testtype-value": list(),
                "cl-ctrl-testtype-all-value": list(),
                "cl-ctrl-testtype-all-options": C.CL_ALL_DISABLED,
                "btn-ctrl-add-disabled": True,
                "cl-normalize-value": list(),
                #"cl-selected-options": list()
            }

            self._panel = deepcopy(self._defaults)
            if panel:
                for key in self._defaults:
                    self._panel[key] = panel[key]

        @property
        def defaults(self) -> dict:
            return self._defaults

        @property
        def panel(self) -> dict:
            return self._panel

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

        def values(self) -> tuple:
            """Returns the values from the Control panel as a list.

            :returns: The values from the Control panel.
            :rtype: list
            """
            return tuple(self._panel.values())

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """

        def _generate_plotting_area(tests: list, normalize: bool,
            url: str) -> list:
            """Generate the plotting area with all its content.
            """

            if not tests:
                return C.PLACEHOLDER

            figs = graph_trending(self.data, tests, self.layout, normalize)
            tput = dcc.Graph(figure=figs[0])
            lat = dcc.Graph(figure=figs[1])

            trending = [
                dbc.Row(
                    children=dbc.Tabs(
                        [
                            dbc.Tab(
                                children=tput,
                                label="Throughput",
                                tab_id="tab-tput"
                            ),
                            dbc.Tab(
                                children=lat,
                                label="Latency",
                                tab_id="tab-lat"
                            )
                        ],
                        id="tabs",
                        active_tab="tab-tput",
                    )
                ),
                dbc.Row(
                    [
                        dbc.Col([html.Div(
                            [
                                dbc.Button(
                                    id="btn-collapse-0-url",
                                    children="URL",
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
                                    id="modal",
                                    size="xl",
                                    is_open=False,
                                    scrollable=True
                                ),
                                dbc.Button(
                                    id="btn-ctrl-download",
                                    children="Download Data",
                                    class_name="me-1",
                                    color="info",
                                    style={
                                        "text-transform": "none",
                                        "padding": "0rem 1rem"
                                    }
                                ),
                                dcc.Download(id="download-data")
                            ],
                            className="d-grid gap-0 d-md-flex justify-content-md-end"
                        )])
                    ],
                    class_name="g-0 p-0",
                )
            ]

            acc_items = [
                dbc.AccordionItem(
                    title="Trending",
                    children=trending
                )
            ]

            return dbc.Col(
                children=[
                    dbc.Row(
                        dbc.Accordion(
                            children=acc_items,
                            class_name="g-0 p-1",
                            start_collapsed=False,
                            always_open=True
                        ),
                        class_name="g-0 p-0",
                    ),
                    dbc.Row(
                        dbc.Col([html.Div(
                            [
                                dbc.Button(
                                    id="btn-add-telemetry",
                                    children="Add Panel with Telemetry",
                                    class_name="me-1",
                                    color="info",
                                    style={
                                        "text-transform": "none",
                                        "padding": "0rem 1rem"
                                    }
                                )
                            ],
                            className="d-grid gap-0 d-md-flex justify-content-md-end"
                        )]),
                        class_name="g-0 p-0"
                    )
                ]
            )

        @app.callback(
            Output("modal", "is_open"),
            [Input("btn-collapse-0-url", "n_clicks")],
            [State("modal", "is_open")],
        )
        def toggle_modal(n, is_open):
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output("collapse-0", "is_open"),
            [Input("btn-collapse-0", "n_clicks")],
            [State("collapse-0", "is_open")],
        )
        def toggle_collapse0(n, is_open):
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output("collapse-1", "is_open"),
            [Input("btn-collapse-1", "n_clicks")],
            [State("collapse-1", "is_open")],
        )
        def toggle_collapse1(n, is_open):
            if n:
                return not is_open
            return is_open
        
        @app.callback(
            Output("collapse-2", "is_open"),
            [Input("btn-collapse-2", "n_clicks")],
            [State("collapse-2", "is_open")],
        )
        def toggle_collapse2(n, is_open):
            if n:
                return not is_open
            return is_open

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("selected-tests", "data"),  # Store
            Output("plotting-area", "children"),
            Output("row-card-sel-tests", "style"),
            Output("row-btns-sel-tests", "style"),
            Output("lg-selected", "children"),
            Output("dd-ctrl-dut", "value"),
            Output("dd-ctrl-phy", "options"),
            Output("dd-ctrl-phy", "disabled"),
            Output("dd-ctrl-phy", "value"),
            Output("dd-ctrl-area", "options"),
            Output("dd-ctrl-area", "disabled"),
            Output("dd-ctrl-area", "value"),
            Output("dd-ctrl-test", "options"),
            Output("dd-ctrl-test", "disabled"),
            Output("dd-ctrl-test", "value"),
            Output("cl-ctrl-core", "options"),
            Output("cl-ctrl-core", "value"),
            Output("cl-ctrl-core-all", "value"),
            Output("cl-ctrl-core-all", "options"),
            Output("cl-ctrl-framesize", "options"),
            Output("cl-ctrl-framesize", "value"),
            Output("cl-ctrl-framesize-all", "value"),
            Output("cl-ctrl-framesize-all", "options"),
            Output("cl-ctrl-testtype", "options"),
            Output("cl-ctrl-testtype", "value"),
            Output("cl-ctrl-testtype-all", "value"),
            Output("cl-ctrl-testtype-all", "options"),
            Output("btn-ctrl-add", "disabled"),
            Output("cl-ctrl-normalize", "value"),
            #Output("cl-selected", "options"),  # User selection
            State("control-panel", "data"),  # Store
            State("selected-tests", "data"),  # Store
            #State("cl-selected", "value"),  # User selection
            Input("dd-ctrl-dut", "value"),
            Input("dd-ctrl-phy", "value"),
            Input("dd-ctrl-area", "value"),
            Input("dd-ctrl-test", "value"),
            Input("cl-ctrl-core", "value"),
            Input("cl-ctrl-core-all", "value"),
            Input("cl-ctrl-framesize", "value"),
            Input("cl-ctrl-framesize-all", "value"),
            Input("cl-ctrl-testtype", "value"),
            Input("cl-ctrl-testtype-all", "value"),
            Input("cl-ctrl-normalize", "value"),
            Input("btn-ctrl-add", "n_clicks"),
            Input("btn-sel-remove", "n_clicks"),
            Input("btn-sel-remove-all", "n_clicks"),
            Input("url", "href")
        )
        def _update_ctrl_panel(cp_data: dict, store_sel: list,# list_sel: list,
            dd_dut: str, dd_phy: str, dd_area: str, dd_test: str, cl_core: list,
            cl_core_all: list, cl_framesize: list, cl_framesize_all: list,
            cl_testtype: list, cl_testtype_all: list, cl_normalize: list,
            btn_add: int, btn_remove: int, btn_remove_all: int,
            href: str) -> tuple:
            """Update the application when the event is detected.

            :param cp_data: Current status of the control panel stored in
                browser.
            :param store_sel: List of tests selected by user stored in the
                browser.
            :param list_sel: List of tests selected by the user shown in the
                checklist.
            :param dd_dut: Input - DUTs.
            :param dd_phy: Input - topo- arch-nic-driver.
            :param dd_area: Input - Tested area.
            :param dd_test: Input - Test.
            :param cl_core: Input - Number of cores.
            :param cl_core_all: Input - All numbers of cores.
            :param cl_framesize: Input - Frame sizes.
            :param cl_framesize_all: Input - All frame sizes.
            :param cl_testtype: Input - Test type (NDR, PDR, MRR).
            :param cl_testtype_all: Input - All test types.
            :param cl_normalize: Input - Normalize the results.
            :param btn_add: Input - Button "Add Selected" tests.
            :param btn_remove: Input - Button "Remove selected" tests.
            :param btn_remove_all: Input - Button "Remove All" tests.
            :param href: Input - The URL provided by the browser.
            :type cp_data: dict
            :type store_sel: list
            :type list_sel: list
            :type dd_dut: str
            :type dd_phy: str
            :type dd_area: str
            :type dd_test: str
            :type cl_core: list
            :type cl_core_all: list
            :type cl_framesize: list
            :type cl_framesize_all: list
            :type cl_testtype: list
            :type cl_testtype_all: list
            :type cl_normalize: list
            :type btn_add: int
            :type btn_remove: int
            :type btn_remove_all: int
            :type href: str
            :returns: New values for web page elements.
            :rtype: tuple
            """

            _ = btn_add
            _ = btn_remove
            _ = btn_remove_all

            ctrl_panel = self.ControlPanel(cp_data)
            norm = cl_normalize

            # Parse the url:
            parsed_url = url_decode(href)
            if parsed_url:
                url_params = parsed_url["params"]
            else:
                url_params = None

            plotting_area = no_update
            row_card_sel_tests = no_update
            row_btns_sel_tests = no_update
            lg_selected = no_update

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if trigger_id == "dd-ctrl-dut":
                try:
                    options = \
                        generate_options(sorted(self.spec_tbs[dd_dut].keys()))
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-ctrl-dut-value": dd_dut,
                    "dd-ctrl-phy-value": str(),
                    "dd-ctrl-phy-options": options,
                    "dd-ctrl-phy-disabled": disabled,
                    "dd-ctrl-area-value": str(),
                    "dd-ctrl-area-options": list(),
                    "dd-ctrl-area-disabled": True,
                    "dd-ctrl-test-value": str(),
                    "dd-ctrl-test-options": list(),
                    "dd-ctrl-test-disabled": True,
                    "cl-ctrl-core-options": list(),
                    "cl-ctrl-core-value": list(),
                    "cl-ctrl-core-all-value": list(),
                    "cl-ctrl-core-all-options": C.CL_ALL_DISABLED,
                    "cl-ctrl-framesize-options": list(),
                    "cl-ctrl-framesize-value": list(),
                    "cl-ctrl-framesize-all-value": list(),
                    "cl-ctrl-framesize-all-options": C.CL_ALL_DISABLED,
                    "cl-ctrl-testtype-options": list(),
                    "cl-ctrl-testtype-value": list(),
                    "cl-ctrl-testtype-all-value": list(),
                    "cl-ctrl-testtype-all-options": C.CL_ALL_DISABLED,
                })
            elif trigger_id == "dd-ctrl-phy":
                try:
                    dut = ctrl_panel.get("dd-ctrl-dut-value")
                    phy = self.spec_tbs[dut][dd_phy]
                    options = [{"label": label(v), "value": v} \
                        for v in sorted(phy.keys())]
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-ctrl-phy-value": dd_phy,
                    "dd-ctrl-area-value": str(),
                    "dd-ctrl-area-options": options,
                    "dd-ctrl-area-disabled": disabled,
                    "dd-ctrl-test-value": str(),
                    "dd-ctrl-test-options": list(),
                    "dd-ctrl-test-disabled": True,
                    "cl-ctrl-core-options": list(),
                    "cl-ctrl-core-value": list(),
                    "cl-ctrl-core-all-value": list(),
                    "cl-ctrl-core-all-options": C.CL_ALL_DISABLED,
                    "cl-ctrl-framesize-options": list(),
                    "cl-ctrl-framesize-value": list(),
                    "cl-ctrl-framesize-all-value": list(),
                    "cl-ctrl-framesize-all-options": C.CL_ALL_DISABLED,
                    "cl-ctrl-testtype-options": list(),
                    "cl-ctrl-testtype-value": list(),
                    "cl-ctrl-testtype-all-value": list(),
                    "cl-ctrl-testtype-all-options": C.CL_ALL_DISABLED,
                })
            elif trigger_id == "dd-ctrl-area":
                try:
                    dut = ctrl_panel.get("dd-ctrl-dut-value")
                    phy = ctrl_panel.get("dd-ctrl-phy-value")
                    area = self.spec_tbs[dut][phy][dd_area]
                    options = generate_options(sorted(area.keys()))
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = True
                ctrl_panel.set({
                    "dd-ctrl-area-value": dd_area,
                    "dd-ctrl-test-value": str(),
                    "dd-ctrl-test-options": options,
                    "dd-ctrl-test-disabled": disabled,
                    "cl-ctrl-core-options": list(),
                    "cl-ctrl-core-value": list(),
                    "cl-ctrl-core-all-value": list(),
                    "cl-ctrl-core-all-options": C.CL_ALL_DISABLED,
                    "cl-ctrl-framesize-options": list(),
                    "cl-ctrl-framesize-value": list(),
                    "cl-ctrl-framesize-all-value": list(),
                    "cl-ctrl-framesize-all-options": C.CL_ALL_DISABLED,
                    "cl-ctrl-testtype-options": list(),
                    "cl-ctrl-testtype-value": list(),
                    "cl-ctrl-testtype-all-value": list(),
                    "cl-ctrl-testtype-all-options": C.CL_ALL_DISABLED,
                })
            elif trigger_id == "dd-ctrl-test":
                dut = ctrl_panel.get("dd-ctrl-dut-value")
                phy = ctrl_panel.get("dd-ctrl-phy-value")
                area = ctrl_panel.get("dd-ctrl-area-value")
                if all((dut, phy, area, dd_test, )):
                    test = self.spec_tbs[dut][phy][area][dd_test]
                    ctrl_panel.set({
                        "dd-ctrl-test-value": dd_test,
                        "cl-ctrl-core-options": \
                            generate_options(sorted(test["core"])),
                        "cl-ctrl-core-value": list(),
                        "cl-ctrl-core-all-value": list(),
                        "cl-ctrl-core-all-options": C.CL_ALL_ENABLED,
                        "cl-ctrl-framesize-options": \
                            generate_options(sorted(test["frame-size"])),
                        "cl-ctrl-framesize-value": list(),
                        "cl-ctrl-framesize-all-value": list(),
                        "cl-ctrl-framesize-all-options": C.CL_ALL_ENABLED,
                        "cl-ctrl-testtype-options": \
                            generate_options(sorted(test["test-type"])),
                        "cl-ctrl-testtype-value": list(),
                        "cl-ctrl-testtype-all-value": list(),
                        "cl-ctrl-testtype-all-options": C.CL_ALL_ENABLED,
                    })
            elif trigger_id == "cl-ctrl-core":
                val_sel, val_all = sync_checklists(
                    options=ctrl_panel.get("cl-ctrl-core-options"),
                    sel=cl_core,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-ctrl-core-value": val_sel,
                    "cl-ctrl-core-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-core-all":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-ctrl-core-options"),
                    sel=list(),
                    all=cl_core_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-ctrl-core-value": val_sel,
                    "cl-ctrl-core-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-ctrl-framesize-options"),
                    sel=cl_framesize,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-ctrl-framesize-value": val_sel,
                    "cl-ctrl-framesize-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize-all":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-ctrl-framesize-options"),
                    sel=list(),
                    all=cl_framesize_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-ctrl-framesize-value": val_sel,
                    "cl-ctrl-framesize-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-ctrl-testtype-options"),
                    sel=cl_testtype,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-ctrl-testtype-value": val_sel,
                    "cl-ctrl-testtype-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype-all":
                val_sel, val_all = sync_checklists(
                    options = ctrl_panel.get("cl-ctrl-testtype-options"),
                    sel=list(),
                    all=cl_testtype_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-ctrl-testtype-value": val_sel,
                    "cl-ctrl-testtype-all-value": val_all,
                })
            elif trigger_id == "btn-ctrl-add":
                dut = ctrl_panel.get("dd-ctrl-dut-value")
                phy = ctrl_panel.get("dd-ctrl-phy-value")
                area = ctrl_panel.get("dd-ctrl-area-value")
                test = ctrl_panel.get("dd-ctrl-test-value")
                cores = ctrl_panel.get("cl-ctrl-core-value")
                framesizes = ctrl_panel.get("cl-ctrl-framesize-value")
                testtypes = ctrl_panel.get("cl-ctrl-testtype-value")
                # Add selected test to the list of tests in store:
                if all((dut, phy, area, test, cores, framesizes, testtypes)):
                    if store_sel is None:
                        store_sel = list()
                    for core in cores:
                        for framesize in framesizes:
                            for ttype in testtypes:
                                if dut == "trex":
                                    core = str()
                                tid = "-".join((
                                    dut, phy.replace('af_xdp', 'af-xdp'), area,
                                    framesize.lower(), core.lower(), test,
                                    ttype.lower()
                                ))
                                if tid not in [itm["id"] for itm in store_sel]:
                                    store_sel.append({
                                        "id": tid,
                                        "dut": dut,
                                        "phy": phy,
                                        "area": area,
                                        "test": test,
                                        "framesize": framesize.lower(),
                                        "core": core.lower(),
                                        "testtype": ttype.lower()
                                    })
                    store_sel = sorted(store_sel, key=lambda d: d["id"])
                    row_card_sel_tests = C.STYLE_ENABLED
                    row_btns_sel_tests = C.STYLE_ENABLED
                    if C.CLEAR_ALL_INPUTS:
                        ctrl_panel.set(ctrl_panel.defaults)
            elif trigger_id == "btn-sel-remove-all":
                plotting_area = C.PLACEHOLDER
                row_card_sel_tests = C.STYLE_DISABLED
                row_btns_sel_tests = C.STYLE_DISABLED
                store_sel = list()
                # ctrl_panel.set({
                #     "cl-selected-options": list()
                # })
            elif trigger_id == "btn-sel-remove":
                pass
                # if list_sel:
                #     new_store_sel = list()
                #     for item in store_sel:
                #         if item["id"] not in list_sel:
                #             new_store_sel.append(item)
                #     store_sel = new_store_sel
            elif trigger_id == "url":
                if url_params:
                    try:
                        store_sel = literal_eval(url_params["store_sel"][0])
                        norm = literal_eval(url_params["norm"][0])
                    except (KeyError, IndexError):
                        pass
                    if store_sel:
                        row_card_sel_tests = C.STYLE_ENABLED
                        row_btns_sel_tests = C.STYLE_ENABLED
                        last_test = store_sel[-1]
                        test = self.spec_tbs[last_test["dut"]]\
                            [last_test["phy"]][last_test["area"]]\
                                [last_test["test"]]
                        ctrl_panel.set({
                            "dd-ctrl-dut-value": last_test["dut"],
                            "dd-ctrl-phy-value": last_test["phy"],
                            "dd-ctrl-phy-options": generate_options(sorted(
                                self.spec_tbs[last_test["dut"]].keys())),
                            "dd-ctrl-phy-disabled": False,
                            "dd-ctrl-area-value": last_test["area"],
                            "dd-ctrl-area-options": [
                                {"label": label(v), "value": v} \
                                    for v in sorted(
                                        self.spec_tbs[last_test["dut"]]\
                                            [last_test["phy"]].keys())
                            ],
                            "dd-ctrl-area-disabled": False,
                            "dd-ctrl-test-value": last_test["test"],
                            "dd-ctrl-test-options": generate_options(sorted(
                                self.spec_tbs[last_test["dut"]]\
                                    [last_test["phy"]]\
                                        [last_test["area"]].keys())),
                            "dd-ctrl-test-disabled": False,
                            "cl-ctrl-core-options": generate_options(sorted(
                                test["core"])),
                            "cl-ctrl-core-value": [last_test["core"].upper(), ],
                            "cl-ctrl-core-all-value": list(),
                            "cl-ctrl-core-all-options": C.CL_ALL_ENABLED,
                            "cl-ctrl-framesize-options": generate_options(
                                sorted(test["frame-size"])),
                            "cl-ctrl-framesize-value": \
                                [last_test["framesize"].upper(), ],
                            "cl-ctrl-framesize-all-value": list(),
                            "cl-ctrl-framesize-all-options": C.CL_ALL_ENABLED,
                            "cl-ctrl-testtype-options": generate_options(sorted(
                                test["test-type"])),
                            "cl-ctrl-testtype-value": \
                                [last_test["testtype"].upper(), ],
                            "cl-ctrl-testtype-all-value": list(),
                            "cl-ctrl-testtype-all-options": C.CL_ALL_ENABLED
                        })

            if trigger_id in ("btn-ctrl-add", "url", "cl-ctrl-normalize",
                    "btn-sel-remove"):
                if store_sel:
                    plotting_area = _generate_plotting_area(
                        store_sel,
                        bool(norm),
                        gen_new_url(
                            parsed_url,
                            {
                                "store_sel": store_sel,
                                "norm": norm
                            }
                        )
                    )
                    lg_selected = [
                        dbc.ListGroupItem(
                            children=[
                                dbc.Checkbox(
                                    label=l["id"],
                                    value=False,
                                    label_class_name="m-0 p-0",
                                    label_style={"color": get_color(i)}
                                )
                            ],
                            class_name="p-0"
                        ) for i, l in enumerate(store_sel)
                    ]
                    # ctrl_panel.set({
                    #     "cl-selected-options": list_tests(store_sel)
                    # })    
                else:
                    plotting_area = C.PLACEHOLDER
                    row_card_sel_tests = C.STYLE_DISABLED
                    row_btns_sel_tests = C.STYLE_DISABLED
                    store_sel = list()
                    # ctrl_panel.set({
                    #     "cl-selected-options": list()
                    # })

            if ctrl_panel.get("cl-ctrl-core-value") and \
                    ctrl_panel.get("cl-ctrl-framesize-value") and \
                    ctrl_panel.get("cl-ctrl-testtype-value"):
                disabled = False
            else:
                disabled = True
            ctrl_panel.set({
                "btn-ctrl-add-disabled": disabled,
                "cl-normalize-value": norm
            })

            ret_val = [
                ctrl_panel.panel,
                store_sel,
                plotting_area,
                row_card_sel_tests,
                row_btns_sel_tests,
                lg_selected
            ]
            ret_val.extend(ctrl_panel.values())
            return ret_val

        @app.callback(
            Output("metadata-tput-lat", "children"),
            Output("metadata-hdrh-graph", "children"),
            Output("offcanvas-metadata", "is_open"),
            Input({"type": "graph", "index": ALL}, "clickData"),
            prevent_initial_call=True
        )
        def _show_metadata_from_graphs(graph_data: dict) -> tuple:
            """Generates the data for the offcanvas displayed when a particular
            point in a graph is clicked on.

            :param graph_data: The data from the clicked point in the graph.
            :type graph_data: dict
            :returns: The data to be displayed on the offcanvas and the
                information to show the offcanvas.
            :rtype: tuple(list, list, bool)
            """
            try:
                trigger_id = loads(
                    callback_context.triggered[0]["prop_id"].split(".")[0]
                )["index"]
                idx = 0 if trigger_id == "tput" else 1
                graph_data = graph_data[idx]["points"][0]
            except (JSONDecodeError, IndexError, KeyError, ValueError,
                    TypeError):
                raise PreventUpdate

            metadata = no_update
            graph = list()

            children = [
                dbc.ListGroupItem(
                    [dbc.Badge(x.split(":")[0]), x.split(": ")[1]]
                ) for x in graph_data.get("text", "").split("<br>")
            ]
            if trigger_id == "tput":
                title = "Throughput"
            elif trigger_id == "lat":
                title = "Latency"
                hdrh_data = graph_data.get("customdata", None)
                if hdrh_data:
                    graph = [dbc.Card(
                        class_name="gy-2 p-0",
                        children=[
                            dbc.CardHeader(hdrh_data.pop("name")),
                            dbc.CardBody(children=[
                                dcc.Graph(
                                    id="hdrh-latency-graph",
                                    figure=graph_hdrh_latency(
                                        hdrh_data, self.layout
                                    )
                                )
                            ])
                        ])
                    ]
            metadata = [
                dbc.Card(
                    class_name="gy-2 p-0",
                    children=[
                        dbc.CardHeader(children=[
                            dcc.Clipboard(
                                target_id="tput-lat-metadata",
                                title="Copy",
                                style={"display": "inline-block"}
                            ),
                            title
                        ]),
                        dbc.CardBody(
                            id="tput-lat-metadata",
                            class_name="p-0",
                            children=[dbc.ListGroup(children, flush=True), ]
                        )
                    ]
                )
            ]

            return metadata, graph, True

        @app.callback(
            Output("download-data", "data"),
            State("selected-tests", "data"),
            Input("btn-ctrl-download", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(store_sel, n_clicks):
            """Download the data

            :param store_sel: List of tests selected by user stored in the
                browser.
            :param n_clicks: Number of clicks on the button "Download".
            :type store_sel: list
            :type n_clicks: int
            :returns: dict of data frame content (base64 encoded) and meta data
                used by the Download component.
            :rtype: dict
            """

            if not n_clicks:
                raise PreventUpdate

            if not store_sel:
                raise PreventUpdate

            df = pd.DataFrame()
            for itm in store_sel:
                sel_data = select_trending_data(self.data, itm)
                if sel_data is None:
                    continue
                df = pd.concat([df, sel_data], ignore_index=True)

            return dcc.send_data_frame(df.to_csv, C.TREND_DOWNLOAD_FILE_NAME)


# Dummy functions with dummy data:

        def _generate_table(tbl_data: dict) -> dbc.Table:
            """
            """
            return dbc.Table.from_dataframe(
                pd.DataFrame(tbl_data),
                bordered=True,
                striped=True,
                hover=True,
                size="sm",
                color="info"
            )

        def _table_runtime(graph_data: dict) -> list:
            """
            """
            table = {  # Dummy table
                "Name": ["avf-0/3b/2/0-output", "avf-0/3b/2/0-tx",
                    "avf-0/3b/a/0-output", "avf-0/3b/a/0-tx", "avf-input",
                    "ethernet-input", "ip4-input-no-checksum", "ip4-lookup",
                    "ip4-rewrite"],
                "State": ["active", "active", "active", "active", "polling",
                    "active", "active", "active", "active"],
                "Calls": [21080, 21080, 21080, 21080, 21080, 42160, 42160,
                    42160, 42160],
                "Vectors": [5396480, 5396480, 5396480, 5396480, 10792960,
                    10792960, 10792960, 10792960, 10792960],
                "Suspends": [1, 21, 1, 21, 1, 1, 1, 1, 1],
                "Clocks": [10.4, 27.2, 10.5, 26.7, 23.9, 25.6, 37.7, 45.3,43.2],
                "Vectors/Call": [256.00, 256.00, 256.00, 256.00, 512.00, 256.00,
                    256.00, 256.00, 256.00]
            }

            return [
                "Thread 1 vpp_wk_0",
                _generate_table(table),
                "Thread 2 vpp_wk_1",
                _generate_table(table),
            ]

        def _table_interface(graph_data: dict) -> list:
            """
            """
            table = {  # Dummy table
                "Name": ["avf-0/3b/2/0", "", "", "", "",
                    "avf-0/3b/a/0", "", "", "", ""],
                "Counter": ["rx packets", "rx bytes", "tx packets", "tx bytes",
                    "ip4", "rx packets", "rx bytes", "tx packets", "tx bytes",
                    "ip4"],
                "Count": [10803200, 648192000, 10802688, 648161280, 10803200,
                    10803200, 648192000, 10802688, 648161280, 10803200]
            }

            return [_generate_table(table), ]

        def _table_instructions(graph_data: dict) -> list:
            """
            """
            table = {  # Dummy table
                "Name": ["avf-input", "ip4-input-no-checksum", "ip4-rewrite",
                    "ip4-lookup", "ethernet-input", "avf-0/3b/2/0-tx",
                    "avf-0/3b/2/0-output", "avf-0/3b/a/0-tx",
                    "avf-0/3b/a/0-output"],
                "Calls": [20770, 41539, 41540, 41539, 41540, 20770, 20770,
                    20770, 20770],
                "Packets": [10634240, 10633984, 10634240, 10633984, 10634240,
                    5317120, 5317120, 5317120, 5317120],
                "Packets/Call": [512.00, 256.00, 256.00, 256.00, 256.00, 256.00,
                    256.00, 256.00, 256.00],
                "Clocks/Packet": [23.69, 37.14, 42.59, 44.89, 24.31, 25.83,
                    9.88, 26.51, 10.01],
                "Instructions/Packet": [33.28, 64.83, 67.44, 67.08, 26.04,
                    42.16, 14.10, 42.53, 14.10],
                "IPC": [1.40, 1.75, 1.58, 1.49, 1.07, 1.63, 1.43, 1.60, 1.41]
            }

            return [
                "Thread 1 vpp_wk_0",
                _generate_table(table),
                "Thread 2 vpp_wk_1",
                _generate_table(table),
            ]

        def _table_cache(graph_data: dict) -> list:
            """
            """
            table = {  # Dummy table
                "Name": ["avf-input", "ip4-input-no-checksum", "ip4-rewrite",
                    "ip4-lookup", "ethernet-input", "avf-0/3b/2/0-tx",
                    "avf-0/3b/2/0-output", "avf-0/3b/a/0-tx",
                    "avf-0/3b/a/0-output"],
                "L1 hit/pkt": [10.17, 22.20, 28.73, 34.59, 10.23, 10.52, 6.87,
                    10.52, 6.81],
                "L1 miss/pkt": [0.33, 0.23, 1.14, 0.19, 0.42, 0.27, 0.17, 0.29,
                    0.14],
                "L2 hit/pkt": [0.32, 0.23, 1.14, 0.19, 0.36, 0.27, 0.17, 0.29,
                    0.14],
                "L2 miss/pkt": [0.00, 0.00, 0.00, 0.00, 0.06, 0.00, 0.00, 0.00,
                    0.00],
                "L3 hit/pkt": [0.00, 0.00, 0.00, 0.00, 0.06, 0.00, 0.00, 0.00,
                    0.00],
                "L3 miss/pkt": [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
                    0.00],
            }

            return [
                "Thread 1 vpp_wk_0",
                _generate_table(table),
                "Thread 2 vpp_wk_1",
                _generate_table(table),
            ]