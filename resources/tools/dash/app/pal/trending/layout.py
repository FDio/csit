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
from dash import callback_context
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

        # State of controls:
        self._ctrls = self._reset_ctrls()

    @property
    def html_layout(self):
        return self._html_layout

    @property
    def spec_tbs(self):
        return self._spec_tbs

    def _reset_ctrls(self):
        self._ctrls =  dict(
            phy_val=None,
            area_val=None,
            test_val=None,
            btn_val=None,
        )
        return self._ctrls

    def _set_ctrls(self, key, val):
        if key in list(self._ctrls.keys()):
            self._ctrls[key] = val
        else:
            raise RuntimeError(f"Invalid key '{key}'")

    def add_content(self):
        """
        """
        if self.html_layout and self.spec_tbs:
            return html.Div(
                id="div-main",
                children=[
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
            children="List of selected tests"
        )

    def _add_ctrl_select(self):
        """
        """
        return html.Div(
            id="div-ctrl-select",
            children=[
                html.Br(),
                html.Div(
                    children="Physical Test Bed Topology, NIC and Driver"
                ),
                dcc.Dropdown(
                    id="dd-ctrl-phy",
                    placeholder="Select a Physical Test Bed Topology...",
                    multi=False,
                    clearable=False,
                    options=[
                        {"label": k, "value": k} for k in self.spec_tbs.keys()
                    ],
                    # value=list(self.spec_tbs.keys())[0]
                ),
                html.Br(),
                html.Div(
                    children="Area"
                ),
                dcc.Dropdown(
                    id="dd-ctrl-area",
                    placeholder="Select an Area...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                html.Br(),
                html.Div(
                    children="Test"
                ),
                dcc.Dropdown(
                    id="dd-ctrl-test",
                    placeholder="Select a Test...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),

                # # Change to radio buttons:
                # html.Br(),
                # html.Div(
                #     children="Number of Cores"
                # ),
                # dcc.Dropdown(
                #     id="dd-ctrl-core",
                #     placeholder="Select a Number of Cores...",
                #     disabled=True,
                #     multi=False,
                #     clearable=False,
                # ),
                # html.Br(),
                # html.Div(
                #     children="Frame Size"
                # ),
                # dcc.Dropdown(
                #     id="dd-ctrl-framesize",
                #     placeholder="Select a Frame Size...",
                #     disabled=True,
                #     multi=False,
                #     clearable=False,
                # ),
                # html.Br(),
                # html.Div(
                #     children="Test Type"
                # ),
                # dcc.Dropdown(
                #     id="dd-ctrl-testtype",
                #     placeholder="Select a Test Type...",
                #     disabled=True,
                #     multi=False,
                #     clearable=False,
                # ),
                html.Br(),
                html.Button(
                    id="btn-ctrl-add",
                    children="Add",
                    disabled=True
                ),
                html.Br(),
                html.Div(
                    id="div-ctrl-info"
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

            if phy and area and test:
                return False
            else:
                return True

        @app.callback(
            Output("div-ctrl-info", "children"),
            Output("dd-ctrl-phy", "value"),
            Output("dd-ctrl-area", "value"),
            Output("dd-ctrl-test", "value"),
            Output("btn-ctrl-add", "n_clicks"),
            State("dd-ctrl-phy", "value"),
            State("dd-ctrl-area", "value"),
            State("dd-ctrl-test", "value"),
            Input("btn-ctrl-add", "n_clicks"),
        )
        def _print_user_selection(phy, area, test, n_clicks):
            """
            """

            if not n_clicks:
                raise PreventUpdate

            selected = u""
            if phy and area and test:

                # TODO: Add validation

                self._set_ctrls("phy_val", phy)
                self._set_ctrls("area_val", area)
                self._set_ctrls("test_val", test)

                selected = (
                    f"{self._ctrls['phy_val']} - "
                    f"{self._ctrls['area_val']} - "
                    f"{self._ctrls['test_val']}\n\n"
                )

            self._reset_ctrls()

            return selected, None, None, None, 0
