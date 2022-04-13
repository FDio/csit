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

from dash import dcc
from dash import html
from dash import callback_context, no_update
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta

from ..data.data import Data
from .graphs import graph_trending, graph_hdrh_latency, \
    select_trending_data


class Layout:
    """
    """

    STYLE_HIDEN = {"display": "none"}
    STYLE_BLOCK = {"display": "block", "vertical-align": "top"}
    STYLE_INLINE ={
        "display": "inline-block",
        "vertical-align": "top"
    }
    NO_GRAPH = {"data": [], "layout": {}, "frames": []}

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
                        className="g-0",
                        children=[
                            self._add_navbar(),
                        ]
                    ),
                    dbc.Row(
                        id="row-main",
                        className="g-0",
                        children=[
                            dcc.Store(
                                id="selected-tests"
                            ),
                            self._add_ctrl_col(),
                            self._add_plotting_col(),
                        ]
                    ),
                    dbc.Offcanvas(
                        id="offcanvas-metadata",
                        title="Throughput And Latency",
                        placement="end",
                        is_open=True,
                        children=[
                            html.P(
                                id="metadata",
                                children=[
                                    "This is the placeholder for metadata."
                                ],
                            )
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
                        external_link=True,
                        href="#"
                    )
                )
            ],
            brand="Dashboard",
            brand_href="/",
            brand_external_link=True,
            #color="dark",
            #dark=True,
            fluid=True,
        )

    def _add_ctrl_col(self) -> dbc.Col:
        """Add column with controls. It is placed on the left side.
        """
        return dbc.Col(
            id="col-controls",
            children=[
                self._add_ctrl_panel(),
                self._add_ctrl_shown()
            ],
        )

    def _add_plotting_col(self) -> dbc.Col:
        """Add column with plots and tables. It is placed on the right side.
        """
        return dbc.Col(
            id="col-plotting-area",
            children=[
                # Empty for now
            ],
            width=9,
        )

    def _add_ctrl_panel(self) -> dbc.Row:
        """
        """
        return dbc.Row(
            id="row-ctrl-panel",
            className="g-0",
            children=[
                dbc.Label("Physical Test Bed Topology, NIC and Driver"),
                dcc.Dropdown(
                    id="dd-ctrl-phy",
                    placeholder="Select a Physical Test Bed Topology...",
                    multi=False,
                    clearable=False,
                    options=[
                        {"label": k, "value": k} for k in self.spec_tbs.keys()
                    ],
                ),
                dbc.Label("Area"),
                dcc.Dropdown(
                    id="dd-ctrl-area",
                    placeholder="Select an Area...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                dbc.Label("Test"),
                dcc.Dropdown(
                    id="dd-ctrl-test",
                    placeholder="Select a Test...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                dbc.Row(
                    id="row-ctrl-core",
                    className="g-0",
                    children=[
                        dbc.Label("Number of Cores"),
                        dbc.Checklist(
                            id="cl-ctrl-core-all",
                            options=[{"label": "All", "value": "all"}, ],
                            inline=True,
                            switch=False
                        ),
                        dbc.Checklist(
                            id="cl-ctrl-core",
                            inline=True,
                            switch=False
                        )
                    ]
                ),
                dbc.Row(
                    id="row-ctrl-framesize",
                    className="g-0",
                    children=[
                        dbc.Label("Frame Size"),
                        dbc.Checklist(
                            id="cl-ctrl-framesize-all",
                            options=[{"label": "All", "value": "all"}, ],
                            inline=True,
                            switch=False
                        ),
                        dbc.Checklist(
                            id="cl-ctrl-framesize",
                            inline=True,
                            switch=False
                        )
                    ]
                ),
                dbc.Row(
                    id="row-ctrl-testtype",
                    className="g-0",
                    children=[
                        dbc.Label("Test Type"),
                        dbc.Checklist(
                            id="cl-ctrl-testtype-all",
                            options=[{"label": "All", "value": "all"}, ],
                            inline=True,
                            switch=False
                        ),
                        dbc.Checklist(
                            id="cl-ctrl-testtype",
                            inline=True,
                            switch=False
                        )
                    ]
                ),
                dbc.Row(
                    className="g-0",
                    children=[
                        dbc.Button(
                            id="btn-ctrl-add",
                            children="Add",
                        )
                    ]
                ),
                dbc.Row(
                    className="g-0",
                    children=[
                        dcc.DatePickerRange(
                            id="dpr-period",
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
            ]
        )

    def _add_ctrl_shown(self) -> dbc.Row:
        """
        """
        return dbc.Row(
            id="div-ctrl-shown",
            className="g-0",
            children=[
                dbc.Row(
                    className="g-0",
                    children=[
                        dbc.Label("Selected tests"),
                        dbc.Checklist(
                            id="cl-selected",
                            options=[],
                            inline=False
                        )
                    ]
                ),
                dbc.Row(
                    className="g-0",
                    children=[
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    id="btn-sel-remove",
                                    children="Remove Selected",
                                    color="secondary",
                                    disabled=False
                                ),
                                dbc.Button(
                                    id="btn-sel-remove-all",
                                    children="Remove All",
                                    color="secondary",
                                    disabled=False
                                ),
                                dbc.Button(
                                    id="btn-sel-display",
                                    children="Display",
                                    color="secondary",
                                    disabled=False
                                )
                            ],
                            size="md",
                            className="me-1",
                        ),
                    ]
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
            # Output("row-ctrl-core", "style"),
            Output("cl-ctrl-core", "options"),
            # Output("row-ctrl-framesize", "style"),
            Output("cl-ctrl-framesize", "options"),
            # Output("row-ctrl-testtype", "style"),
            Output("cl-ctrl-testtype", "options"),
            # Output("btn-ctrl-add", "disabled"),
            State("dd-ctrl-phy", "value"),
            State("dd-ctrl-area", "value"),
            Input("dd-ctrl-test", "value"),
        )
        def _update_btn_add(phy, area, test):
            """
            """

            if test is None:
                raise PreventUpdate

            # core_style = {"display": "none"}
            core_opts = []
            # framesize_style = {"display": "none"}
            framesize_opts = []
            # testtype_style = {"display": "none"}
            testtype_opts = []
            # add_disabled = True
            if phy and area and test:
                # core_style = {"display": "block"}
                core_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["core"]
                ]
                # framesize_style = {"display": "block"}
                framesize_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["frame-size"]
                ]
                # testtype_style = {"display": "block"}
                testtype_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["test-type"]
                ]
                # add_disabled = False

            return (
                # core_style,
                core_opts,
                # framesize_style,
                framesize_opts,
                # testtype_style,
                testtype_opts,
                # add_disabled
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
            # Output("graph-tput", "figure"),
            # Output("graph-latency", "figure"),
            # Output("div-tput", "style"),
            # Output("div-latency", "style"),
            # Output("div-lat-metadata", "style"),
            # Output("div-download", "style"),
            Output("selected-tests", "data"),  # Store
            Output("cl-selected", "options"),  # User selection
            Output("dd-ctrl-phy", "value"),
            Output("dd-ctrl-area", "value"),
            Output("dd-ctrl-test", "value"),
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
            Input("btn-sel-remove-all", "n_clicks"),
            Input("dpr-period", "start_date"),
            Input("dpr-period", "end_date"),
            prevent_initial_call=True
        )
        def _process_list(store_sel, list_sel, phy, area, test, cores,
                framesizes, testtypes, btn_add, btn_display, btn_remove,
                btn_remove_all, d_start, d_end):
            """
            """

            if not (btn_add or btn_display or btn_remove or btn_remove_all or \
                    d_start or d_end):
                raise PreventUpdate

            def _list_tests():
                # Display selected tests with checkboxes:
                if store_sel:
                    return [
                        {"label": v["id"], "value": v["id"]} for v in store_sel
                    ]
                else:
                    return list()

            class RetunValue:
                def __init__(self) -> None:
                    self._output = {
                        # "graph-tput-figure": no_update,
                        # "graph-lat-figure": no_update,
                        # "div-tput-style": no_update,
                        # "div-latency-style": no_update,
                        # "div-lat-metadata-style": no_update,
                        # "div-download-style": no_update,
                        "selected-tests-data": no_update,
                        "cl-selected-options": no_update,
                        "dd-ctrl-phy-value": no_update,
                        "dd-ctrl-area-value": no_update,
                        "dd-ctrl-test-value": no_update,
                    }

                def value(self):
                    return tuple(self._output.values())

                def set_values(self, kwargs: dict) -> None:
                    for key, val in kwargs.items():
                        if key in self._output:
                            self._output[key] = val
                        else:
                            raise KeyError(f"The key {key} is not defined.")


            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            d_start = datetime(int(d_start[0:4]), int(d_start[5:7]),
                int(d_start[8:10]))
            d_end = datetime(int(d_end[0:4]), int(d_end[5:7]), int(d_end[8:10]))

            output = RetunValue()

            if trigger_id == "btn-ctrl-add":
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
                output.set_values({
                    "selected-tests-data": store_sel,
                    "cl-selected-options": _list_tests(),
                    "dd-ctrl-phy-value": None,
                    "dd-ctrl-area-value": None,
                    "dd-ctrl-test-value": None,
                })

            elif trigger_id in ("btn-sel-display", "dpr-period"):
                fig_tput, fig_lat = graph_trending(
                    self.data, store_sel, self.layout, d_start, d_end
                )
                # output.set_values({
                #     "graph-tput-figure": \
                #         fig_tput if fig_tput else self.NO_GRAPH,
                #     "graph-lat-figure": \
                #         fig_lat if fig_lat else self.NO_GRAPH,
                #     "div-tput-style": \
                #         self.STYLE_BLOCK if fig_tput else self.STYLE_HIDEN,
                #     "div-latency-style": \
                #         self.STYLE_BLOCK if fig_lat else self.STYLE_HIDEN,
                #     "div-lat-metadata-style": \
                #         self.STYLE_BLOCK if fig_lat else self.STYLE_HIDEN,
                #     "div-download-style": \
                #         self.STYLE_BLOCK if fig_tput else self.STYLE_HIDEN,
                # })
            elif trigger_id == "btn-sel-remove-all":
                output.set_values({
                    "selected-tests-data": list(),
                    "cl-selected-options": list()
                })
            elif trigger_id == "btn-sel-remove":
                if list_sel:
                    new_store_sel = list()
                    for item in store_sel:
                        if item["id"] not in list_sel:
                            new_store_sel.append(item)
                    store_sel = new_store_sel
                if store_sel:
                    fig_tput, fig_lat = graph_trending(
                        self.data, store_sel, self.layout, d_start, d_end
                    )
                    output.set_values({
                        # "graph-tput-figure": \
                        #     fig_tput if fig_tput else self.NO_GRAPH,
                        # "graph-lat-figure": \
                        #     fig_lat if fig_lat else self.NO_GRAPH,
                        # "div-tput-style": \
                        #     self.STYLE_BLOCK if fig_tput else self.STYLE_HIDEN,
                        # "div-latency-style": \
                        #     self.STYLE_BLOCK if fig_lat else self.STYLE_HIDEN,
                        # "div-lat-metadata-style": \
                        #     self.STYLE_BLOCK if fig_lat else self.STYLE_HIDEN,
                        # "div-download-style": \
                        #     self.STYLE_BLOCK if fig_tput else self.STYLE_HIDEN,
                        "selected-tests-data": store_sel,
                        "cl-selected-options": _list_tests()
                    })
                else:
                    output.set_values({
                        # "graph-tput-figure": self.NO_GRAPH,
                        # "graph-lat-figure": self.NO_GRAPH,
                        # "div-tput-style": self.STYLE_HIDEN,
                        # "div-latency-style": self.STYLE_HIDEN,
                        # "div-lat-metadata-style": self.STYLE_HIDEN,
                        # "div-download-style": self.STYLE_HIDEN,
                        "selected-tests-data": store_sel,
                        "cl-selected-options": _list_tests()
                    })

            return output.value()

        # @app.callback(
        #     Output("tput-metadata", "children"),
        #     Input("graph-tput", "clickData")
        # )
        # def _show_tput_metadata(hover_data):
        #     """
        #     """
        #     if not hover_data:
        #         raise PreventUpdate

        #     return hover_data["points"][0]["text"].replace("<br>", "\n")

        # @app.callback(
        #     Output("graph-latency-hdrh", "figure"),
        #     Output("graph-latency-hdrh", "style"),
        #     Output("lat-metadata", "children"),
        #     Input("graph-latency", "clickData")
        # )
        # def _show_latency_hdhr(hover_data):
        #     """
        #     """
        #     if not hover_data:
        #         raise PreventUpdate

        #     graph = no_update
        #     hdrh_data = hover_data["points"][0].get("customdata", None)
        #     if hdrh_data:
        #         graph = graph_hdrh_latency(hdrh_data, self.layout)

        #     return (
        #         graph,
        #         self.STYLE_INLINE,
        #         hover_data["points"][0]["text"].replace("<br>", "\n")
        #     )

        # @app.callback(
        #     Output("download-data", "data"),
        #     State("selected-tests", "data"),
        #     Input("btn-download-data", "n_clicks"),
        #     prevent_initial_call=True
        # )
        # def _download_data(store_sel, n_clicks):
        #     """
        #     """

        #     if not n_clicks:
        #         raise PreventUpdate

        #     df = pd.DataFrame()
        #     for itm in store_sel:
        #         sel_data = select_trending_data(self.data, itm)
        #         if sel_data is None:
        #             continue
        #         df = pd.concat([df, sel_data], ignore_index=True)

        #     return dcc.send_data_frame(df.to_csv, "trending_data.csv")
