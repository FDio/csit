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
from dash import callback_context, no_update, ALL, MATCH
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from datetime import datetime
from copy import deepcopy
from json import loads, JSONDecodeError
from ast import literal_eval

from ..utils.constants import Constants as C
from ..utils.utils import get_color, show_tooltip, label, sync_checklists, \
    gen_new_url, generate_options, Trigger
from ..utils.url_processing import url_decode
from ..utils.control_panel import ControlPanel
from ..data.data import Data
from .graphs import graph_trending, graph_hdrh_latency, \
    select_trending_data


# Control panel partameters and their default values.
CP_PARAMS = {
    "dd-dut-value": str(),
    "dd-phy-options": list(),
    "dd-phy-disabled": True,
    "dd-phy-value": str(),
    "dd-area-options": list(),
    "dd-area-disabled": True,
    "dd-area-value": str(),
    "dd-test-options": list(),
    "dd-test-disabled": True,
    "dd-test-value": str(),
    "cl-core-options": list(),
    "cl-core-value": list(),
    "cl-core-all-value": list(),
    "cl-core-all-options": C.CL_ALL_DISABLED,
    "cl-framesize-options": list(),
    "cl-framesize-value": list(),
    "cl-framesize-all-value": list(),
    "cl-framesize-all-options": C.CL_ALL_DISABLED,
    "cl-testtype-options": list(),
    "cl-testtype-value": list(),
    "cl-testtype-all-value": list(),
    "cl-testtype-all-options": C.CL_ALL_DISABLED,
    "cl-normalize-value": list(),
    "btn-add-disabled": True,
    #"cl-selected-options": list()
}

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
                        children=[
                            self._add_navbar(),
                        ]
                    ),
                    # dcc.Loading(
                    #     dbc.Offcanvas(
                    #         class_name="w-50",
                    #         id="offcanvas-metadata",
                    #         title="Throughput And Latency",
                    #         placement="end",
                    #         is_open=False,
                    #         children=[
                    #             dbc.Row(id="metadata-tput-lat"),
                    #             dbc.Row(id="metadata-hdrh-graph"),
                    #         ]
                    #     )
                    # ),
                    dbc.Row(
                        id="row-main",
                        class_name="g-0",
                        children=[
                            dcc.Store(id="store-selected-tests"),
                            dcc.Store(id="store-control-panel"),
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-dut",
                                    "DUT"
                                )
                            ),
                            dbc.Select(
                                # id="dd-ctrl-dut",
                                id={"type": "ctrl", "index": "dd-dut"},
                                placeholder="Select a Device under Test...",
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-infra",
                                    "Infra"
                                )
                            ),
                            dbc.Select(
                                # id="dd-ctrl-phy",
                                id={"type": "ctrl", "index": "dd-phy"},
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-area",
                                    "Area"
                                )
                            ),
                            dbc.Select(
                                # id="dd-ctrl-area",
                                id={"type": "ctrl", "index": "dd-area"},
                                placeholder="Select an Area...",
                                disabled=True
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
                            dbc.InputGroupText(
                                children=show_tooltip(
                                    self._tooltips,
                                    "help-test",
                                    "Test"
                                )
                            ),
                            dbc.Select(
                                # id="dd-ctrl-test",
                                id={"type": "ctrl", "index": "dd-test"},
                                placeholder="Select a Test...",
                                disabled=True
                            )
                        ],
                        size="sm"
                    )
                ]
            ),
            dbc.Row(
                class_name="g-0 p-1",
                children=[
                    dbc.Label(
                        children=show_tooltip(
                            self._tooltips,
                            "help-framesize",
                            "Frame Size"
                        )
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                # id="cl-ctrl-framesize-all",
                                id={"type": "ctrl", "index": "cl-framesize-all"},
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                switch=False
                            )
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                # id="cl-ctrl-framesize",
                                id={"type": "ctrl", "index": "cl-framesize"},
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
                        children=show_tooltip(
                            self._tooltips,
                            "help-cores",
                            "Number of Cores"
                        )
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                # id="cl-ctrl-core-all",
                                id={"type": "ctrl", "index": "cl-core-all"},
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
                                # id="cl-ctrl-core",
                                id={"type": "ctrl", "index": "cl-core"},
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
                        children=show_tooltip(
                            self._tooltips,
                            "help-ttype",
                            "Test Type"
                        )
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                # id="cl-ctrl-testtype-all",
                                id={"type": "ctrl", "index": "cl-testtype-all"},
                                options=C.CL_ALL_DISABLED,
                                inline=True,
                                switch=False
                            )
                        ],
                        width=3
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                # id="cl-ctrl-testtype",
                                id={"type": "ctrl", "index": "cl-testtype"},
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
                        children=show_tooltip(
                            self._tooltips,
                            "help-normalize",
                            "Normalize"
                        )
                    ),
                    dbc.Col(
                        children=[
                            dbc.Checklist(
                                # id="cl-ctrl-normalize",
                                id={"type": "ctrl", "index": "cl-normalize"},
                                options=[
                                    {
                                        "value": "normalize",
                                        "label": (
                                            "Normalize results to CPU "
                                            "frequency 2GHz"
                                        )
                                    }
                                ],
                                value=[],
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
                    dbc.Button(
                        # id="btn-ctrl-add",
                        id={"type": "ctrl", "index": "btn-add-test"},
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
                ]
            ),
            dbc.Row(
                id="row-btns-sel-tests",
                class_name="g-0 p-1",
                style=C.STYLE_DISABLED,
                children=[
                    dbc.ButtonGroup(
                        children=[
                            dbc.Button(
                                # id="btn-sel-remove",
                                id={"type": "ctrl", "index": "btn-remove-test"},
                                children="Remove Selected",
                                class_name="w-100",
                                color="info",
                                disabled=False
                            ),
                            dbc.Button(
                                # id="btn-sel-remove-all",
                                id={"type": "ctrl", "index": "btn-remove-all-tests"},
                                children="Remove All",
                                class_name="w-100",
                                color="info",
                                disabled=False
                            )
                        ]
                    )
                ]
            )
        ]

    def callbacks(self, app):
        """Callbacks for the whole application.

        :param app: The application.
        :type app: Flask
        """
        
        @app.callback(
            [
                Output("store-selected-tests", "data"),  # Store
            ],
            [
                State("store-control-panel", "data"),
                State("store-selected-tests", "data"),
            ],
            [
                Input({"type": "ctrl", "index": ALL}, "value"),
                Input({"type": "ctrl", "index": ALL}, "n_clicks"),
                Input("url", "href")
            ],
            # prevent_initial_call=True
        )
        def _update_ctrl_panel(
                ctrl_panel: dict,
                selected_tests: list,
                *_
            ) -> tuple:
            """
            """
            trigger = Trigger(callback_context.triggered)
            logging.info(trigger.id)
            logging.info(trigger.parameter)
            logging.info(trigger.value)

            return [1, ]










