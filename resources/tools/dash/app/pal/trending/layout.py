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

from dash import dcc
from dash import html
from dash import callback_context, no_update
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta

from ..data.data import Data
from .graphs import trending_tput


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
        data_mrr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_trending_mrr()

        data_ndrpdr = Data(
            data_spec_file=self._data_spec_file,
            debug=True
        ).read_trending_ndrpdr()

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
                    dcc.Store(id="selected-tests"),
                    self._add_ctrl_div(),
                    self._add_plotting_div()
                ]
            )
        else:
            return html.Div(
            id="div-main-error",
            children="An Error Occured."
        )

    def _add_ctrl_div(self):
        """Add div with controls. It is placed on the left side.
        """
        return html.Div(
            id="div-controls",
            children=[
                html.Div(
                    id="div-controls-tabs",
                    children=[
                        self._add_ctrl_select(),
                        self._add_ctrl_shown()
                    ]
                )
            ],
            style={
                "display": "inline-block",
                "width": "18%",
                "padding": "5px"
            }
        )

    def _add_plotting_div(self):
        """Add div with plots and tables. It is placed on the right side.
        """
        return html.Div(
            id="div-plotting-area",
            children=[
                dcc.Loading(
                    id="loading-graph",
                    children=[
                        dcc.Graph(
                            id="graph"
                        )
                    ],
                    type="circle"
                ),
                
            ],
            style={
                "vertical-align": "top",
                "display": "none",
                "width": "80%",
                "padding": "5px"
            }
        )

    def _add_ctrl_shown(self):
        """
        """
        return html.Div(
            id="div-ctrl-shown",
            children=[
                html.H5("Selected tests"),
                html.Div(
                    id="container-selected-tests",
                    children=[
                        dcc.Checklist(
                            id="cl-selected",
                            options=[],
                            labelStyle={"display": "block"}
                        ),
                        html.Button(
                            id="btn-sel-remove",
                            children="Remove Selected",
                            disabled=False
                        ),
                        html.Button(
                            id="btn-sel-display",
                            children="Display",
                            disabled=False
                        )
                    ]
                ),
            ]
        )

    def _add_ctrl_select(self):
        """
        """
        return html.Div(
            id="div-ctrl-select",
            children=[
                html.H5("Physical Test Bed Topology, NIC and Driver"),
                dcc.Dropdown(
                    id="dd-ctrl-phy",
                    placeholder="Select a Physical Test Bed Topology...",
                    multi=False,
                    clearable=False,
                    options=[
                        {"label": k, "value": k} for k in self.spec_tbs.keys()
                    ],
                ),
                html.H5("Area"),
                dcc.Dropdown(
                    id="dd-ctrl-area",
                    placeholder="Select an Area...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                html.H5("Test"),
                dcc.Dropdown(
                    id="dd-ctrl-test",
                    placeholder="Select a Test...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                html.Div(
                    id="div-ctrl-core",
                    children=[
                        html.H5("Number of Cores"),
                        dcc.Checklist(
                            id="cl-ctrl-core-all",
                            options=[{"label": "All", "value": "all"}, ],
                            labelStyle={"display": "inline-block"}
                        ),
                        dcc.Checklist(
                            id="cl-ctrl-core",
                            labelStyle={"display": "inline-block"}
                        )
                    ],
                    style={"display": "none"}
                ),
                html.Div(
                    id="div-ctrl-framesize",
                    children=[
                        html.H5("Frame Size"),
                        dcc.Checklist(
                            id="cl-ctrl-framesize-all",
                            options=[{"label": "All", "value": "all"}, ],
                            labelStyle={"display": "inline-block"}
                        ),
                        dcc.Checklist(
                            id="cl-ctrl-framesize",
                            labelStyle={"display": "inline-block"}
                        )
                    ],
                    style={"display": "none"}
                ),
                html.Div(
                    id="div-ctrl-testtype",
                    children=[
                        html.H5("Test Type"),
                        dcc.Checklist(
                            id="cl-ctrl-testtype-all",
                            options=[{"label": "All", "value": "all"}, ],
                            labelStyle={"display": "inline-block"}
                        ),
                        dcc.Checklist(
                            id="cl-ctrl-testtype",
                            labelStyle={"display": "inline-block"}
                        )
                    ],
                    style={"display": "none"}
                ),
                html.Button(
                    id="btn-ctrl-add",
                    children="Add",
                    disabled=True
                ),
                html.Br(),
                dcc.DatePickerRange(
                    id="dpr-period",
                    min_date_allowed=datetime.utcnow() - timedelta(days=180),
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
            Output("dd-ctrl-area", "options"),
            Output("dd-ctrl-area", "disabled"),
            Input("dd-ctrl-phy", "value"),
        )
        def _update_dd_area(phy):
            """
            """

            if phy is None:
                raise PreventUpdate

            try:
                options = [
                    {"label": self.spec_tbs[phy][v]["label"], "value": v}
                        for v in [v for v in self.spec_tbs[phy].keys()]
                ]
                disable = False
            except KeyError:
                options = list()
                disable = True

            return options, disable

        @app.callback(
            Output("dd-ctrl-test", "options"),
            Output("dd-ctrl-test", "disabled"),
            State("dd-ctrl-phy", "value"),
            Input("dd-ctrl-area", "value"),
        )
        def _update_dd_test(phy, area):
            """
            """

            if not area:
                raise PreventUpdate

            try:
                options = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["test"]
                ]
                disable = False
            except KeyError:
                options = list()
                disable = True

            return options, disable

        @app.callback(
            Output("div-ctrl-core", "style"),
            Output("cl-ctrl-core", "options"),
            Output("div-ctrl-framesize", "style"),
            Output("cl-ctrl-framesize", "options"),
            Output("div-ctrl-testtype", "style"),
            Output("cl-ctrl-testtype", "options"),
            Output("btn-ctrl-add", "disabled"),
            State("dd-ctrl-phy", "value"),
            State("dd-ctrl-area", "value"),
            Input("dd-ctrl-test", "value"),
        )
        def _update_btn_add(phy, area, test):
            """
            """

            if test is None:
                raise PreventUpdate

            core_style = {"display": "none"}
            core_opts = []
            framesize_style = {"display": "none"}
            framesize_opts = []
            testtype_style = {"display": "none"}
            testtype_opts = []
            add_disabled = True
            if phy and area and test:
                core_style = {"display": "block"}
                core_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["core"]
                ]
                framesize_style = {"display": "block"}
                framesize_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["frame-size"]
                ]
                testtype_style = {"display": "block"}
                testtype_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["test-type"]
                ]
                add_disabled = False

            return (
                core_style, core_opts,
                framesize_style, framesize_opts,
                testtype_style, testtype_opts,
                add_disabled
            )

        def _sync_checklists(opt, sel, all, id):
            """
            """
            options = {v["value"] for v in opt}
            input_id = callback_context.triggered[0]["prop_id"].split(".")[0]
            if input_id == id:
                all = ["all"] if set(sel) == options else list()
            else:
                sel = list(options) if all else list()
            return sel, all

        @app.callback(
            Output("cl-ctrl-core", "value"),
            Output("cl-ctrl-core-all", "value"),
            State("cl-ctrl-core", "options"),
            Input("cl-ctrl-core", "value"),
            Input("cl-ctrl-core-all", "value"),
            prevent_initial_call=True
        )
        def _sync_cl_core(opt, sel, all):
            return _sync_checklists(opt, sel, all, "cl-ctrl-core")

        @app.callback(
            Output("cl-ctrl-framesize", "value"),
            Output("cl-ctrl-framesize-all", "value"),
            State("cl-ctrl-framesize", "options"),
            Input("cl-ctrl-framesize", "value"),
            Input("cl-ctrl-framesize-all", "value"),
            prevent_initial_call=True
        )
        def _sync_cl_framesize(opt, sel, all):
            return _sync_checklists(opt, sel, all, "cl-ctrl-framesize")

        @app.callback(
            Output("cl-ctrl-testtype", "value"),
            Output("cl-ctrl-testtype-all", "value"),
            State("cl-ctrl-testtype", "options"),
            Input("cl-ctrl-testtype", "value"),
            Input("cl-ctrl-testtype-all", "value"),
            prevent_initial_call=True
        )
        def _sync_cl_testtype(opt, sel, all):
            return _sync_checklists(opt, sel, all, "cl-ctrl-testtype")

        @app.callback(
            Output("graph", "figure"),
            Output("selected-tests", "data"),  # Store
            Output("cl-selected", "options"),  # User selection
            Output("dd-ctrl-phy", "value"),
            Output("dd-ctrl-area", "value"),
            Output("dd-ctrl-test", "value"),
            Output("div-plotting-area", "style"),
            State("selected-tests", "data"),  # Store
            State("cl-selected", "value"),
            State("dd-ctrl-phy", "value"),
            State("dd-ctrl-area", "value"),
            State("dd-ctrl-test", "value"),
            State("cl-ctrl-core", "value"),
            State("cl-ctrl-framesize", "value"),
            State("cl-ctrl-testtype", "value"),
            Input("btn-ctrl-add", "n_clicks"),
            Input("btn-sel-display", "n_clicks"),
            Input("btn-sel-remove", "n_clicks"),
            Input("dpr-period", "start_date"),
            Input("dpr-period", "end_date"),
            prevent_initial_call=True
        )
        def _process_list(store_sel, list_sel, phy, area, test, cores,
                framesizes, testtypes, btn_add, btn_display, btn_remove,
                d_start, d_end):
            """
            """

            if not (btn_add or btn_display or btn_remove or d_start or d_end):
                raise PreventUpdate

            def _list_tests():
                # Display selected tests with checkboxes:
                if store_sel:
                    return [
                        {"label": v["id"], "value": v["id"]} for v in store_sel
                    ]
                else:
                    return list()

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            d_start = datetime(
                 int(d_start[0:4]), int(d_start[5:7]), int(d_start[8:10])
            )
            d_end = datetime(
                 int(d_end[0:4]), int(d_end[5:7]), int(d_end[8:10])
            )

            if trigger_id == "btn-ctrl-add":
                # Add selected test to the list of tests in store:
                if phy and area and test and cores and framesizes and testtypes:

                    # TODO: Add validation

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
                return (no_update, store_sel, _list_tests(), None,
                    None, None, no_update)

            elif trigger_id in ("btn-sel-display", "dpr-period"):
                fig, style = trending_tput(
                    self.data, store_sel, self.layout, d_start, d_end
                )
                return (fig, no_update, no_update,
                    no_update, no_update, no_update, style)

            elif trigger_id == "btn-sel-remove":
                if list_sel:
                    new_store_sel = list()
                    for item in store_sel:
                        if item["id"] not in list_sel:
                            new_store_sel.append(item)
                    store_sel = new_store_sel
                if store_sel:
                    fig, style = trending_tput(
                        self.data, store_sel, self.layout, d_start, d_end
                    )
                    return (fig, store_sel, _list_tests(),
                    no_update, no_update, no_update, style)
                else:
                    style={
                        "vertical-align": "top",
                        "display": "none",
                        "width": "80%",
                        "padding": "5px"
                    }
                    return (no_update, store_sel, _list_tests(),
                        no_update, no_update, no_update, style)
