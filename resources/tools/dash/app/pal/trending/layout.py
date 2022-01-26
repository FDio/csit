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
from dash import Input, Output, callback
from dash.exceptions import PreventUpdate
from yaml import load, FullLoader, YAMLError


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
        self._spec_test = None

        try:
            with open(self._html_layout_file, "r") as layout_file:
                self._html_layout = layout_file.read()
        except IOError as err:
            logging.error(f"Not possible to open the file {layout_file}\n{err}")

        try:
            with open(self._spec_file, "r") as file_read:
                self._spec_test = load(file_read, Loader=FullLoader)
        except IOError as err:
            logging.error(f"Not possible to open the file {spec_file}\n{err}")
        except YAMLError as err:
            logging.error(
                f"An error occurred while parsing the specification file "
                f"{spec_file}\n"
                f"{err}"
            )

        # Callbacks:
        if self._app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self._app)

        # User choice (one test):
        self._test_selection = {
            "phy": "",
            "area": "",
            "test": "",
            "core": "",
            "frame-size": "",
            "test-type": ""
        }

    @property
    def html_layout(self):
        return self._html_layout

    @property
    def spec_test(self):
        return self._spec_test

    def _reset_test_selection(self):
        self._test_selection = {
            "phy": "",
            "area": "",
            "test": "",
            "core": "",
            "frame-size": "",
            "test-type": ""
        }

    def add_content(self):
        """
        """
        if self._html_layout and self._spec_test:
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
                        {"label": k, "value": k} for k in self._spec_test.keys()
                    ],
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

                # Change to radio buttons:
                html.Br(),
                html.Div(
                    children="Number of Cores"
                ),
                dcc.Dropdown(
                    id="dd-ctrl-core",
                    placeholder="Select a Number of Cores...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                html.Br(),
                html.Div(
                    children="Frame Size"
                ),
                dcc.Dropdown(
                    id="dd-ctrl-framesize",
                    placeholder="Select a Frame Size...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
                html.Br(),
                html.Div(
                    children="Test Type"
                ),
                dcc.Dropdown(
                    id="dd-ctrl-testtype",
                    placeholder="Select a Test Type...",
                    disabled=True,
                    multi=False,
                    clearable=False,
                ),
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
                    {"label": self._spec_test[phy][v]["label"], "value": v}
                        for v in [v for v in self._spec_test[phy].keys()]
                ]
            except KeyError:
                options = list()

            return options, False

        @app.callback(
            Output("dd-ctrl-test", "options"),
            Output("dd-ctrl-test", "disabled"),
            Input("dd-ctrl-phy", "value"),
            Input("dd-ctrl-area", "value"),
        )
        def _update_dd_test(phy, area):
            """
            """

            if not all((phy, area, )):
                raise PreventUpdate

            try:
                options = [
                    {"label": v, "value": v}
                        for v in self._spec_test[phy][area]["test"]
                ]
            except KeyError:
                options = list()

            return options, False

        @app.callback(
            Output("btn-ctrl-add", "disabled"),
            Input("dd-ctrl-phy", "value"),
            Input("dd-ctrl-area", "value"),
            Input("dd-ctrl-test", "value"),
        )
        def _update_btn_add(phy, area, test):
            """
            """

            if all((phy, area, test, )):
                self._test_selection["phy"] = phy
                self._test_selection["area"] = area
                self._test_selection["test"] = test
                return False
            else:
                return True

        @app.callback(
            Output("div-ctrl-info", "children"),
            Output("dd-ctrl-phy", "value"),
            Output("dd-ctrl-area", "value"),
            Output("dd-ctrl-test", "value"),
            Output("btn-ctrl-add", "n_clicks"),
            Input("btn-ctrl-add", "n_clicks")
        )
        def _print_user_selection(n_clicks):
            """
            """

            logging.info(f"\n\n{n_clicks}\n\n")

            if not n_clicks:
                raise PreventUpdate

            selected = (
                f"{self._test_selection['phy']} # "
                f"{self._test_selection['area']} # "
                f"{self._test_selection['test']} # "
                f"{n_clicks}\n"
            )

            self._reset_test_selection()

            return (
                selected,
                None,
                None,
                None,
                0,
            )
