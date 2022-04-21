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

import pandas as pd
import dash_bootstrap_components as dbc

from dash import dcc
from dash import html
from dash import callback_context, no_update, ALL
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta
from copy import deepcopy
from json import loads, JSONDecodeError

from ..data.data import Data
from .graphs import graph_trending, graph_hdrh_latency, \
    select_trending_data


class Layout:
    """
    """

    STYLE_DISABLED = {"display": "none"}
    STYLE_ENABLED = {"display": "inherit"}

    CL_ALL_DISABLED = [{
        "label": "All",
        "value": "all",
        "disabled": True
    }]
    CL_ALL_ENABLED = [{
        "label": "All",
        "value": "all",
        "disabled": False
    }]

    PLACEHOLDER = html.Nobr("")

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
        data_mrr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_trending_mrr(days=5)

        data_ndrpdr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_trending_ndrpdr(days=14)

        self._data = pd.concat([data_mrr, data_ndrpdr], ignore_index=True)

        # Read from files:
        self._html_layout = ""
        self._spec_tbs = None
        self._graph_layout = None

        try:
            with open(self._html_layout_file, "r") as file_read:
                self._html_layout = file_read.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._html_layout_file}\n{err}"
            )

        try:
            with open(self._spec_file, "r") as file_read:
                self._spec_tbs = load(file_read, Loader=FullLoader)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._spec_file,}\n{err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the specification file "
                f"{self._spec_file,}\n"
                f"{err}"
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

    def add_content(self):
        """
        """
        if self.html_layout and self.spec_tbs:
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
                            dcc.Store(
                                id="selected-tests"
                            ),
                            dcc.Store(
                                id="control-panel"
                            ),
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
                        "Continuous Performance Trending",
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
                dbc.Row(  # Throughput
                    id="row-graph-tput",
                    class_name="g-0 p-2",
                    children=[
                        self.PLACEHOLDER
                    ]
                ),
                dbc.Row(  # Latency
                    id="row-graph-lat",
                    class_name="g-0 p-2",
                    children=[
                        self.PLACEHOLDER
                    ]
                ),
                dbc.Row(  # Download
                    id="row-btn-download",
                    class_name="g-0 p-2",
                    children=[
                        self.PLACEHOLDER
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
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Infra"),
                                dbc.Select(
                                    id="dd-ctrl-phy",
                                    placeholder="Select a Physical Test Bed Topology...",
                                    options=[
                                        {"label": k, "value": k} for k in self.spec_tbs.keys()
                                    ],
                                ),
                            ],
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Area"),
                                dbc.Select(
                                    id="dd-ctrl-area",
                                    placeholder="Select an Area...",
                                    disabled=True,
                                ),
                            ],
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    class_name="g-0",
                    children=[
                        dbc.InputGroup(
                            [
                                dbc.InputGroupText("Test"),
                                dbc.Select(
                                    id="dd-ctrl-test",
                                    placeholder="Select a Test...",
                                    disabled=True,
                                ),
                            ],
                            class_name="mb-3",
                            size="sm",
                        ),
                    ]
                ),
                dbc.Row(
                    id="row-ctrl-core",
                    class_name="gy-1",
                    children=[
                        dbc.Label(
                            "Number of Cores",
                            class_name="p-0"
                        ),
                        dbc.Col(
                            children=[
                                dbc.Checklist(
                                    id="cl-ctrl-core-all",
                                    options=self.CL_ALL_DISABLED,
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
                    id="row-ctrl-framesize",
                    class_name="gy-1",
                    children=[
                        dbc.Label(
                            "Frame Size",
                            class_name="p-0"
                        ),
                        dbc.Col(
                            children=[
                                dbc.Checklist(
                                    id="cl-ctrl-framesize-all",
                                    options=self.CL_ALL_DISABLED,
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
                    id="row-ctrl-testtype",
                    class_name="gy-1",
                    children=[
                        dbc.Label(
                            "Test Type",
                            class_name="p-0"
                        ),
                        dbc.Col(
                            children=[
                                dbc.Checklist(
                                    id="cl-ctrl-testtype-all",
                                    options=self.CL_ALL_DISABLED,
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
                    class_name="gy-1",
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    id="btn-ctrl-add",
                                    children="Add Selected",
                                    color="secondary",
                                )
                            ],
                            size="md",
                        )
                    ]
                ),
                dbc.Row(
                    class_name="gy-1",
                    children=[
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
                ),
                dbc.Row(
                    id="row-card-sel-tests",
                    class_name="gy-1",
                    style=self.STYLE_DISABLED,
                    children=[
                        dbc.Label(
                            "Selected tests",
                            class_name="p-0"
                        ),
                        dbc.Checklist(
                            class_name="overflow-auto",
                            id="cl-selected",
                            options=[],
                            inline=False,
                            style={"max-height": "12em"},
                        )
                    ],
                ),
                dbc.Row(
                    id="row-btns-sel-tests",
                    style=self.STYLE_DISABLED,
                    children=[
                        dbc.ButtonGroup(
                            children=[
                                dbc.Button(
                                    id="btn-sel-remove-all",
                                    children="Remove All",
                                    class_name="w-100",
                                    color="secondary",
                                    disabled=False
                                ),
                                dbc.Button(
                                    id="btn-sel-remove",
                                    children="Remove Selected",
                                    class_name="w-100",
                                    color="secondary",
                                    disabled=False
                                ),
                            ],
                            size="md",
                        )
                    ]
                ),
            ]
        )

    class ControlPanel:
        def __init__(self, panel: dict) -> None:

            CL_ALL_DISABLED = [{
                "label": "All",
                "value": "all",
                "disabled": True
            }]

            # Defines also the order of keys
            self._defaults = {
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
                "cl-ctrl-core-all-options": CL_ALL_DISABLED,
                "cl-ctrl-framesize-options": list(),
                "cl-ctrl-framesize-value": list(),
                "cl-ctrl-framesize-all-value": list(),
                "cl-ctrl-framesize-all-options": CL_ALL_DISABLED,
                "cl-ctrl-testtype-options": list(),
                "cl-ctrl-testtype-value": list(),
                "cl-ctrl-testtype-all-value": list(),
                "cl-ctrl-testtype-all-options": CL_ALL_DISABLED,
                "btn-ctrl-add-disabled": True,
                "cl-selected-options": list(),
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
            for key, val in kwargs.items():
                if key in self._panel:
                    self._panel[key] = val
                else:
                    raise KeyError(f"The key {key} is not defined.")

        def get(self, key: str) -> any:
            return self._panel[key]

        def values(self) -> tuple:
            return tuple(self._panel.values())

    @staticmethod
    def _sync_checklists(opt: list, sel: list, all: list, id: str) -> tuple:
        """
        """
        options = {v["value"] for v in opt}
        if id =="all":
            sel = list(options) if all else list()
        else:
            all = ["all", ] if set(sel) == options else list()
        return sel, all

    @staticmethod
    def _list_tests(selection: dict) -> list:
        """Display selected tests with checkboxes
        """
        if selection:
            return [
                {"label": v["id"], "value": v["id"]} for v in selection
            ]
        else:
            return list()

    def callbacks(self, app):

        def _generate_plotting_arrea(args: tuple) -> tuple:
            """
            """

            (fig_tput, fig_lat) = args

            row_fig_tput = self.PLACEHOLDER
            row_fig_lat = self.PLACEHOLDER
            row_btn_dwnld = self.PLACEHOLDER

            if fig_tput:
                row_fig_tput = [
                    dcc.Loading(
                        dcc.Graph(
                            id={"type": "graph", "index": "tput"},
                            figure=fig_tput
                        )
                    ),
                ]
                row_btn_dwnld = [
                    dcc.Loading(children=[
                        dbc.Button(
                            id="btn-download-data",
                            children=["Download Data"]
                        ),
                        dcc.Download(id="download-data")
                    ]),
                ]
            if fig_lat:
                row_fig_lat = [
                    dcc.Loading(
                        dcc.Graph(
                            id={"type": "graph", "index": "lat"},
                            figure=fig_lat
                        )
                    )
                ]

            return row_fig_tput, row_fig_lat, row_btn_dwnld

        @app.callback(
            Output("control-panel", "data"),  # Store
            Output("selected-tests", "data"),  # Store
            Output("row-graph-tput", "children"),
            Output("row-graph-lat", "children"),
            Output("row-btn-download", "children"),
            Output("row-card-sel-tests", "style"),
            Output("row-btns-sel-tests", "style"),
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
            Output("cl-selected", "options"),  # User selection
            State("control-panel", "data"),  # Store
            State("selected-tests", "data"),  # Store
            State("cl-selected", "value"),  # User selection
            Input("dd-ctrl-phy", "value"),
            Input("dd-ctrl-area", "value"),
            Input("dd-ctrl-test", "value"),
            Input("cl-ctrl-core", "value"),
            Input("cl-ctrl-core-all", "value"),
            Input("cl-ctrl-framesize", "value"),
            Input("cl-ctrl-framesize-all", "value"),
            Input("cl-ctrl-testtype", "value"),
            Input("cl-ctrl-testtype-all", "value"),
            Input("btn-ctrl-add", "n_clicks"),
            Input("dpr-period", "start_date"),
            Input("dpr-period", "end_date"),
            Input("btn-sel-remove", "n_clicks"),
            Input("btn-sel-remove-all", "n_clicks"),
        )
        def _update_ctrl_panel(cp_data: dict, store_sel: list, list_sel: list,
            dd_phy: str, dd_area: str, dd_test: str, cl_core: list,
            cl_core_all: list, cl_framesize: list, cl_framesize_all: list,
            cl_testtype: list, cl_testtype_all: list, btn_add: int,
            d_start: str, d_end: str, btn_remove: int,
            btn_remove_all: int) -> tuple:
            """
            """

            d_start = datetime(int(d_start[0:4]), int(d_start[5:7]),
                int(d_start[8:10]))
            d_end = datetime(int(d_end[0:4]), int(d_end[5:7]), int(d_end[8:10]))

            row_fig_tput = no_update
            row_fig_lat = no_update
            row_btn_dwnld = no_update
            row_card_sel_tests = no_update
            row_btns_sel_tests = no_update

            ctrl_panel = self.ControlPanel(cp_data)

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "dd-ctrl-phy":
                try:
                    options = [
                        {"label": self.spec_tbs[dd_phy][v]["label"], "value": v}
                            for v in [v for v in self.spec_tbs[dd_phy].keys()]
                    ]
                    disabled = False
                except KeyError:
                    options = list()
                    disabled = no_update
                ctrl_panel.set({
                    "dd-ctrl-phy-value": dd_phy,
                    "dd-ctrl-area-value": str(),
                    "dd-ctrl-area-options": options,
                    "dd-ctrl-area-disabled": disabled,
                    "dd-ctrl-test-options": list(),
                    "dd-ctrl-test-disabled": True,
                    "cl-ctrl-core-options": list(),
                    "cl-ctrl-core-value": list(),
                    "cl-ctrl-core-all-value": list(),
                    "cl-ctrl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-ctrl-framesize-options": list(),
                    "cl-ctrl-framesize-value": list(),
                    "cl-ctrl-framesize-all-value": list(),
                    "cl-ctrl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-ctrl-testtype-options": list(),
                    "cl-ctrl-testtype-value": list(),
                    "cl-ctrl-testtype-all-value": list(),
                    "cl-ctrl-testtype-all-options": self.CL_ALL_DISABLED,
                    "btn-ctrl-add-disabled": True,
                })
            elif trigger_id == "dd-ctrl-area":
                try:
                    phy = ctrl_panel.get("dd-ctrl-phy-value")
                    options = [
                        {"label": v, "value": v}
                            for v in self.spec_tbs[phy][dd_area]["test"]
                    ]
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
                    "cl-ctrl-core-all-options": self.CL_ALL_DISABLED,
                    "cl-ctrl-framesize-options": list(),
                    "cl-ctrl-framesize-value": list(),
                    "cl-ctrl-framesize-all-value": list(),
                    "cl-ctrl-framesize-all-options": self.CL_ALL_DISABLED,
                    "cl-ctrl-testtype-options": list(),
                    "cl-ctrl-testtype-value": list(),
                    "cl-ctrl-testtype-all-value": list(),
                    "cl-ctrl-testtype-all-options": self.CL_ALL_DISABLED,
                    "btn-ctrl-add-disabled": True,
                })
            elif trigger_id == "dd-ctrl-test":
                core_opts = list()
                framesize_opts = list()
                testtype_opts = list()
                phy = ctrl_panel.get("dd-ctrl-phy-value")
                area = ctrl_panel.get("dd-ctrl-area-value")
                if phy and area and dd_test:
                    core_opts = [
                        {"label": v, "value": v}
                            for v in self.spec_tbs[phy][area]["core"]
                    ]
                    framesize_opts = [
                        {"label": v, "value": v}
                            for v in self.spec_tbs[phy][area]["frame-size"]
                    ]
                    testtype_opts = [
                        {"label": v, "value": v}
                            for v in self.spec_tbs[phy][area]["test-type"]
                    ]
                    ctrl_panel.set({
                        "dd-ctrl-test-value": dd_test,
                        "cl-ctrl-core-options": core_opts,
                        "cl-ctrl-core-value": list(),
                        "cl-ctrl-core-all-value": list(),
                        "cl-ctrl-core-all-options": self.CL_ALL_ENABLED,
                        "cl-ctrl-framesize-options": framesize_opts,
                        "cl-ctrl-framesize-value": list(),
                        "cl-ctrl-framesize-all-value": list(),
                        "cl-ctrl-framesize-all-options": self.CL_ALL_ENABLED,
                        "cl-ctrl-testtype-options": testtype_opts,
                        "cl-ctrl-testtype-value": list(),
                        "cl-ctrl-testtype-all-value": list(),
                        "cl-ctrl-testtype-all-options": self.CL_ALL_ENABLED,
                        "btn-ctrl-add-disabled": False,
                    })
            elif trigger_id == "cl-ctrl-core":
                val_sel, val_all = self._sync_checklists(
                    opt=ctrl_panel.get("cl-ctrl-core-options"),
                    sel=cl_core,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-ctrl-core-value": val_sel,
                    "cl-ctrl-core-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-core-all":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-ctrl-core-options"),
                    sel=list(),
                    all=cl_core_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-ctrl-core-value": val_sel,
                    "cl-ctrl-core-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-ctrl-framesize-options"),
                    sel=cl_framesize,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-ctrl-framesize-value": val_sel,
                    "cl-ctrl-framesize-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-framesize-all":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-ctrl-framesize-options"),
                    sel=list(),
                    all=cl_framesize_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-ctrl-framesize-value": val_sel,
                    "cl-ctrl-framesize-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-ctrl-testtype-options"),
                    sel=cl_testtype,
                    all=list(),
                    id=""
                )
                ctrl_panel.set({
                    "cl-ctrl-testtype-value": val_sel,
                    "cl-ctrl-testtype-all-value": val_all,
                })
            elif trigger_id == "cl-ctrl-testtype-all":
                val_sel, val_all = self._sync_checklists(
                    opt = ctrl_panel.get("cl-ctrl-testtype-options"),
                    sel=list(),
                    all=cl_testtype_all,
                    id="all"
                )
                ctrl_panel.set({
                    "cl-ctrl-testtype-value": val_sel,
                    "cl-ctrl-testtype-all-value": val_all,
                })
            elif trigger_id == "btn-ctrl-add":
                _ = btn_add
                phy = ctrl_panel.get("dd-ctrl-phy-value")
                area = ctrl_panel.get("dd-ctrl-area-value")
                test = ctrl_panel.get("dd-ctrl-test-value")
                cores = ctrl_panel.get("cl-ctrl-core-value")
                framesizes = ctrl_panel.get("cl-ctrl-framesize-value")
                testtypes = ctrl_panel.get("cl-ctrl-testtype-value")
                # Add selected test to the list of tests in store:
                if phy and area and test and cores and framesizes and testtypes:
                    if store_sel is None:
                        store_sel = list()
                    for core in cores:
                        for framesize in framesizes:
                            for ttype in testtypes:
                                tid = (
                                    f"{phy.replace('af_xdp', 'af-xdp')}-"
                                    f"{area}-"
                                    f"{framesize.lower()}-"
                                    f"{core.lower()}-"
                                    f"{test}-"
                                    f"{ttype.lower()}"
                                )
                                if tid not in [itm["id"] for itm in store_sel]:
                                    store_sel.append({
                                        "id": tid,
                                        "phy": phy,
                                        "area": area,
                                        "test": test,
                                        "framesize": framesize.lower(),
                                        "core": core.lower(),
                                        "testtype": ttype.lower()
                                    })
                    row_card_sel_tests = self.STYLE_ENABLED
                    row_btns_sel_tests = self.STYLE_ENABLED
                    ctrl_panel.set(ctrl_panel.defaults)
                    ctrl_panel.set({
                        "cl-selected-options": self._list_tests(store_sel)
                    })
                    row_fig_tput, row_fig_lat, row_btn_dwnld = \
                    _generate_plotting_arrea(
                        graph_trending(
                            self.data, store_sel, self.layout, d_start, d_end
                        )
                    )
            elif trigger_id == "dpr-period":
                row_fig_tput, row_fig_lat, row_btn_dwnld = \
                    _generate_plotting_arrea(
                        graph_trending(
                            self.data, store_sel, self.layout, d_start, d_end
                        )
                    )
            elif trigger_id == "btn-sel-remove-all":
                _ = btn_remove_all
                row_fig_tput = self.PLACEHOLDER
                row_fig_lat = self.PLACEHOLDER
                row_btn_dwnld = self.PLACEHOLDER
                row_card_sel_tests = self.STYLE_DISABLED
                row_btns_sel_tests = self.STYLE_DISABLED
                store_sel = list()
                ctrl_panel.set({
                        "cl-selected-options": list()
                })
            elif trigger_id == "btn-sel-remove":
                _ = btn_remove
                if list_sel:
                    new_store_sel = list()
                    for item in store_sel:
                        if item["id"] not in list_sel:
                            new_store_sel.append(item)
                    store_sel = new_store_sel
                if store_sel:
                    row_fig_tput, row_fig_lat, row_btn_dwnld = \
                    _generate_plotting_arrea(
                        graph_trending(
                            self.data, store_sel, self.layout, d_start, d_end
                        )
                    )
                    ctrl_panel.set({
                        "cl-selected-options": self._list_tests(store_sel)
                    })
                else:
                    row_fig_tput = self.PLACEHOLDER
                    row_fig_lat = self.PLACEHOLDER
                    row_btn_dwnld = self.PLACEHOLDER
                    row_card_sel_tests = self.STYLE_DISABLED
                    row_btns_sel_tests = self.STYLE_DISABLED
                    store_sel = list()
                    ctrl_panel.set({
                            "cl-selected-options": list()
                    })

            ret_val = [
                ctrl_panel.panel, store_sel,
                row_fig_tput, row_fig_lat, row_btn_dwnld,
                row_card_sel_tests, row_btns_sel_tests
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
            """
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
            Input("btn-download-data", "n_clicks"),
            prevent_initial_call=True
        )
        def _download_data(store_sel, n_clicks):
            """
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

            return dcc.send_data_frame(df.to_csv, "trending_data.csv")
