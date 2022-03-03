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

import time
from copy import deepcopy
import logging

from dash import dcc
from dash import html
from dash import callback_context
from dash import Input, Output, State, callback
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

        # State of controls:
        self._ctrls = dict(
            info_val=u"",
            phy_val=None,
            area_opts=list(),
            area_val=None,
            area_dis=True,
            test_opts=list(),
            test_val=None,
            test_dis=True,
            btn_val=None,
            btn_dis=True,
        )

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

    def _reset_ctrls(self):
        self._ctrls = dict(
            info_val=u"",
            phy_val=None,
            area_opts=list(),
            area_val=None,
            area_dis=True,
            test_opts=list(),
            test_val=None,
            test_dis=True,
            btn_val=None,
            btn_dis=True,
        )

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
                    value=list(self._spec_test.keys())[0]
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
                # html.Br(),
                # html.Div(
                #     children="Test"
                # ),
                # dcc.Dropdown(
                #     id="dd-ctrl-test",
                #     placeholder="Select a Test...",
                #     disabled=True,
                #     multi=False,
                #     clearable=False,
                # ),

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
            prevent_initial_call=False
        )
        def _update_dd_area(phy):
            """
            """

            logging.info("_update_dd_area")

            if phy is None:
                logging.info("_update_dd_area: PreventUpdate")
                raise PreventUpdate

            self._ctrls["phy_val"] = phy

            try:
                options = [
                    {"label": self._spec_test[phy][v]["label"], "value": v}
                        for v in [v for v in self._spec_test[phy].keys()]
                ]
                logging.info("_update_dd_area: options")
                logging.info(options)
            except KeyError:
                options = list()

            self._ctrls["area_opts"] = options
            self._ctrls["area_dis"] = False

            logging.info("_update_dd_area: return")
            logging.info(self._ctrls)

            return options, False

        @app.callback(
            Output("btn-ctrl-add", "disabled"),
            Input("dd-ctrl-area", "value"),
        )
        def _update_btn_add(area):
            """
            """

            logging.info("_update_btn_add")

            if area is None:
                logging.info("_update_btn_add: PreventUpdate")
                raise PreventUpdate

            if area:
                self._ctrls["area_val"] = area
                self._ctrls["btn_dis"] = False
                logging.info("_update_btn_add: return OK")
                logging.info(self._ctrls)
                return False
            else:
                logging.info("_update_btn_add: return BAD")
                logging.info(self._ctrls)
                return True

        # @app.callback(
        #     # Output("div-ctrl-info", "children"),
        #     # Output("dd-ctrl-phy", "value"),
        #     # Output("dd-ctrl-area", "value"),
        #     # Output("dd-ctrl-area", "disabled"),
        #     # Output("btn-ctrl-add", "disabled"),
        #     # Output("btn-ctrl-add", "n_clicks"),
        #     Input("btn-ctrl-add", "n_clicks"),
        #     #prevent_initial_call=True
        # )
        # def _print_user_selection(n_clicks):
        #     """
        #     """

        #     logging.info("_print_user_selection")
        #     logging.info(n_clicks)

            # if not n_clicks:
            #     logging.info("_print_user_selection: PreventUpdate")
            #     raise PreventUpdate

            # disable = True if n_clicks else False
            # selected = (
            #     f"{self._test_selection['phy']} # "
            #     f"{self._test_selection['area']}\n\n"
            # )

            # logging.info(
            #     f"selected = {selected}\n"
            #     f"phy_val = {self._ctrls[u'phy_val']}\n"
            #     f"area_opts = {self._ctrls[u'area_opts']}\n"
            #     f"area_val = {self._ctrls[u'area_val']}\n"
            #     f"area_dis = {self._ctrls[u'area_dis']}\n"
            #     f"test_opts = {self._ctrls[u'test_opts']}\n"
            #     f"test_val = {self._ctrls[u'test_val']}\n"
            #     f"test_dis = {self._ctrls[u'test_dis']}\n"
            #     f"btn_val = {self._ctrls[u'btn_val']}\n"
            #     f"btn_dis = {self._ctrls[u'btn_dis']}\n\n"
            # )

            # self._reset_test_selection()

            # return (
            #     selected,
            #     None,
            #     None,
            #     disable,
            #     disable,
            #     0,
            # )












        # @app.callback(
        #     Output("div-ctrl-info", "children"),
        #     Output("dd-ctrl-phy", "value"),
        #     Output("dd-ctrl-area", "options"),
        #     Output("dd-ctrl-area", "value"),
        #     Output("dd-ctrl-area", "disabled"),
        #     Output("dd-ctrl-test", "options"),
        #     Output("dd-ctrl-test", "value"),
        #     Output("dd-ctrl-test", "disabled"),
        #     Output("btn-ctrl-add", "n_clicks"),
        #     Output("btn-ctrl-add", "disabled"),
        #     Input("dd-ctrl-phy", "value"),
        #     Input("dd-ctrl-area", "value"),
        #     Input("dd-ctrl-test", "value"),
        #     Input("btn-ctrl-add", "n_clicks"),
        #     prevent_initial_call=True
        # )
        # def _update_ctrls(phy, area, test, btn):
        #     """
        #     """

        #     trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        #     logging.info(trigger_id)
        #     logging.info(
        #         u"Before:\n"
        #         f"info_val = {self._ctrls[u'info_val']}\n"
        #         f"phy_val = {self._ctrls[u'phy_val']}\n"
        #         f"area_opts = {self._ctrls[u'area_opts']}\n"
        #         f"area_val = {self._ctrls[u'area_val']}\n"
        #         f"area_dis = {self._ctrls[u'area_dis']}\n"
        #         f"test_opts = {self._ctrls[u'test_opts']}\n"
        #         f"test_val = {self._ctrls[u'test_val']}\n"
        #         f"test_dis = {self._ctrls[u'test_dis']}\n"
        #         f"btn_val = {self._ctrls[u'btn_val']}\n"
        #         f"btn_dis = {self._ctrls[u'btn_dis']}\n\n"
        #     )

        #     if trigger_id == "dd-ctrl-phy":
        #         try:
        #             self._ctrls[u'phy_val'] = phy
        #             self._ctrls[u'area_opts'] = [
        #                 {"label": self._spec_test[self._ctrls[u'phy_val']][v]["label"], "value": v}
        #                     for v in [v for v in self._spec_test[self._ctrls[u'phy_val']].keys()]
        #             ]
        #             self._ctrls[u'area_dis'] = False
        #             self._ctrls[u'area_val'] = None
        #             self._ctrls[u'test_dis'] = True
        #             self._ctrls[u'test_val'] = None
        #             self._ctrls[u'btn_dis'] = True
        #         except KeyError:
        #             self._ctrls[u'area_opts'] = list()

        #     elif trigger_id == u"dd-ctrl-area":
        #         self._ctrls[u'area_val'] = area
        #         try:
        #             self._ctrls[u'test_opts'] = [
        #                 {"label": v, "value": v}
        #                     for v in self._spec_test[self._ctrls[u'phy_val']][self._ctrls[u'area_val']]["test"]
        #             ]
        #             self._ctrls[u'test_dis'] = False
        #             self._ctrls[u'test_val'] = None
        #             self._ctrls[u'btn_dis'] = True
        #         except KeyError:
        #             self._ctrls[u'test_opts'] = list()

        #     elif trigger_id == u"dd-ctrl-test":
        #         self._ctrls[u'test_val'] = test
        #         self._ctrls[u'btn_dis'] = False
        #     elif trigger_id == u"btn-ctrl-add":
        #         self._ctrls[u'info_val'] = (
        #             f"phy_val = {self._ctrls[u'phy_val']}\n"
        #             f"area_val = {self._ctrls[u'area_val']}\n"
        #             f"test_val = {self._ctrls[u'test_val']}\n"
        #         )
        #         self._reset_ctrls()
        #     else:
        #         raise PreventUpdate

        #     trigger_id = None

        #     logging.info(
        #         u"After:\n"
        #         f"info_val = {self._ctrls[u'info_val']}\n"
        #         f"phy_val = {self._ctrls[u'phy_val']}\n"
        #         f"area_opts = {self._ctrls[u'area_opts']}\n"
        #         f"area_val = {self._ctrls[u'area_val']}\n"
        #         f"area_dis = {self._ctrls[u'area_dis']}\n"
        #         f"test_opts = {self._ctrls[u'test_opts']}\n"
        #         f"test_val = {self._ctrls[u'test_val']}\n"
        #         f"test_dis = {self._ctrls[u'test_dis']}\n"
        #         f"btn_val = {self._ctrls[u'btn_val']}\n"
        #         f"btn_dis = {self._ctrls[u'btn_dis']}\n\n"
        #     )

        #     return (
        #         self._ctrls[u'info_val'],
        #         self._ctrls[u'phy_val'],
        #         self._ctrls[u'area_opts'],
        #         self._ctrls[u'area_val'],
        #         self._ctrls[u'area_dis'],
        #         self._ctrls[u'test_opts'],
        #         self._ctrls[u'test_val'],
        #         self._ctrls[u'test_dis'],
        #         self._ctrls[u'btn_val'],
        #         self._ctrls[u'btn_dis'],
        #     )








        # @app.callback(
        #     Output("dd-ctrl-test", "options"),
        #     Output("dd-ctrl-test", "disabled"),
        #     State("dd-ctrl-phy", "value"),
        #     Input("dd-ctrl-area", "value"),
        # )
        # def _update_dd_test(phy, area):
        #     """
        #     """

        #     if not all((phy, area, )):
        #         raise PreventUpdate

        #     try:
        #         options = [
        #             {"label": v, "value": v}
        #                 for v in self._spec_test[phy][area]["test"]
        #         ]
        #     except KeyError:
        #         options = list()

        #     return options, False

        # @app.callback(
        #     Output("btn-ctrl-add", "disabled"),
        #     State("dd-ctrl-phy", "value"),
        #     State("dd-ctrl-area", "value"),
        #     Input("dd-ctrl-test", "value"),
        # )
        # def _update_btn_add(phy, area, test):
        #     """
        #     """

        #     if all((phy, area, test, )):
        #         self._test_selection["phy"] = phy
        #         self._test_selection["area"] = area
        #         self._test_selection["test"] = test
        #         return False
        #     else:
        #         return True

        # @app.callback(
        #     Output("div-ctrl-info", "children"),
        #     Output("dd-ctrl-phy", "value"),
        #     Output("dd-ctrl-area", "value"),
        #     # Output("dd-ctrl-area", "disabled"),
        #     Output("dd-ctrl-test", "value"),
        #     # Output("dd-ctrl-test", "disabled"),
        #     Output("btn-ctrl-add", "n_clicks"),
        #     Input("btn-ctrl-add", "n_clicks"),
        #     # prevent_initial_call=True
        # )
        # def _print_user_selection(n_clicks):
        #     """
        #     """

        #     logging.info(f"\n\n{n_clicks}\n\n")

        #     disable_area = True if n_clicks else False

        #     if not n_clicks:
        #         raise PreventUpdate

        #     selected = (
        #         f"{self._test_selection['phy']} # "
        #         f"{self._test_selection['area']} # "
        #         f"{self._test_selection['test']} # "
        #         f"{n_clicks}\n"
        #     )

        #     self._reset_test_selection()

        #     return (
        #         selected,
        #         None,
        #         None,
        #         # disable_area,
        #         None,
        #         # True,
        #         0,
        #     )
