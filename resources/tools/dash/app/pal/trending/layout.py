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

from dash import dcc
from dash import html
from dash import callback_context, no_update
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError

from pprint import pformat


class Layout:
    """
    """

    def __init__(self, app, html_layout_file, spec_file):
        """
        """

        # Inputs
        self._app = app
        self._html_layout_file = html_layout_file
        self._spec_file = spec_file

        # Read from files:
        self._html_layout = ""
        self._spec_tbs = None

        try:
            with open(self._html_layout_file, "r") as layout_file:
                self._html_layout = layout_file.read()
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {layout_file}\n{err}"
            )

        try:
            with open(self._spec_file, "r") as file_read:
                self._spec_tbs = load(file_read, Loader=FullLoader)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {spec_file}\n{err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the specification file "
                f"{spec_file}\n"
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
                # Only a visible note.
                # TODO: Add content.
                html.H3(
                    "Graphs and Tables",
                    style={
                        "vertical-align": "middle",
                        "text-align": "center"
                    }
                )
            ],
            style={
                "vertical-align": "middle",
                "display": "inline-block",
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
                # Debug output
                # TODO: Remove
                html.H5("Debug output"),
                html.Pre(id="div-ctrl-info")
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
                        dcc.RadioItems(
                            id="ri-ctrl-core",
                            labelStyle={"display": "inline-block"}
                        )
                    ],
                    style={"display": "none"}
                ),
                html.Div(
                    id="div-ctrl-framesize",
                    children=[
                        html.H5("Frame Size"),
                        dcc.RadioItems(
                            id="ri-ctrl-framesize",
                            labelStyle={"display": "inline-block"}
                        )
                    ],
                    style={"display": "none"}
                ),
                html.Div(
                    id="div-ctrl-testtype",
                    children=[
                        html.H5("Test Type"),
                        dcc.RadioItems(
                            id="ri-ctrl-testtype",
                            labelStyle={"display": "inline-block"}
                        )
                    ],
                    style={"display": "none"}
                ),
                html.Button(
                    id="btn-ctrl-add",
                    children="Add",
                    disabled=True
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
            Output("ri-ctrl-core", "options"),
            Output("ri-ctrl-core", "value"),
            Output("div-ctrl-framesize", "style"),
            Output("ri-ctrl-framesize", "options"),
            Output("ri-ctrl-framesize", "value"),
            Output("div-ctrl-testtype", "style"),
            Output("ri-ctrl-testtype", "options"),
            Output("ri-ctrl-testtype", "value"),
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
            core_val = None
            framesize_style = {"display": "none"}
            framesize_opts = []
            framesize_val = None
            testtype_style = {"display": "none"}
            testtype_opts = []
            testtype_val = None
            add_disabled = True
            if phy and area and test:
                core_style = {"display": "block"}
                core_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["core"]
                ]
                core_val = core_opts[0]["label"] if core_opts else None
                framesize_style = {"display": "block"}
                framesize_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["frame-size"]
                ]
                framesize_val = \
                    framesize_opts[0]["label"] if framesize_opts else None
                testtype_style = {"display": "block"}
                testtype_opts = [
                    {"label": v, "value": v}
                        for v in self.spec_tbs[phy][area]["test-type"]
                ]
                testtype_val = \
                    testtype_opts[0]["label"] if testtype_opts else None
                add_disabled = False

            return (
                core_style, core_opts, core_val,
                framesize_style, framesize_opts, framesize_val,
                testtype_style, testtype_opts, testtype_val,
                add_disabled
            )

        @app.callback(
            Output("div-ctrl-info", "children"),  # Debug output TODO: Remove
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
            State("ri-ctrl-core", "value"),
            State("ri-ctrl-framesize", "value"),
            State("ri-ctrl-testtype", "value"),
            Input("btn-ctrl-add", "n_clicks"),
            Input("btn-sel-display", "n_clicks"),
            Input("btn-sel-remove", "n_clicks"),
            prevent_initial_call=True
        )
        def _process_list(store_sel, list_sel, phy, area, test, core, framesize,
                testtype, btn_add, btn_display, btn_remove):
            """
            """

            if not (btn_add or btn_display or btn_remove):
                raise PreventUpdate

            def _display_tests():
                # Display selected tests with checkboxes:
                if store_sel:
                    return [
                        {"label": v["id"], "value": v["id"]} for v in store_sel
                    ]
                else:
                    return list()

            trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

            if trigger_id == "btn-ctrl-add":
                # Add selected test to the list of tests in store:
                if phy and area and test and core and framesize and testtype:

                    # TODO: Add validation

                    if store_sel is None:
                        store_sel = list()

                    store_sel.append({
                        "id": (
                            f"{phy}-"
                            f"{area}-"
                            f"{framesize.lower()}-"
                            f"{core.lower()}-"
                            f"{test}-"
                            f"{testtype.lower()}"
                        ),
                        "selected": False,
                        "phy": phy,
                        "area": area,
                        "test": test,
                        "framesize": framesize.lower(),
                        "core": core.lower(),
                        "testtype": testtype.lower()
                    })
                return no_update, store_sel, _display_tests(), None, None, None

            elif trigger_id == "btn-sel-display":
                # TODO: Add graph
                return (pformat(store_sel), no_update, no_update, no_update,
                    no_update, no_update)
            elif trigger_id == "btn-sel-remove":
                if list_sel:
                    logging.info(list_sel)
                    for item in store_sel:
                        if item["id"] in list_sel:
                            store_sel.remove(item)
                return (pformat(store_sel), store_sel, _display_tests(),
                    no_update, no_update, no_update)
