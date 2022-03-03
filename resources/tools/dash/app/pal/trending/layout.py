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

from pprint import pformat


spec_file="pal/trending/spec_test_selection.yaml"
spec_tbs = None

try:
    with open(spec_file, "r") as file_read:
        spec_tbs = load(file_read, Loader=FullLoader)
except IOError as err:
    logging.error(f"Not possible to open the file {spec_file}\n{err}")
except YAMLError as err:
    logging.error(
        f"An error occurred while parsing the specification file "
        f"{spec_file}\n"
        f"{err}"
    )


# State of controls:
def _reset_ctrls():
    logging.info("### _reset_ctrls")
    ctrls = dict(
        # info_val=u"",
        phy_val=None,
        # area_opts=list(),
        area_val=None,
        # area_dis=True,
        # test_opts=list(),
        test_val=None,
        # test_dis=True,
        btn_val=None,
        # btn_dis=True,
    )
    return ctrls

_ctrls = _reset_ctrls()

def _set_ctrls(key, val):
    global _ctrls
    try:
        _ctrls[key] = val
    except KeyError as err:
        logging.error(err)
        raise RuntimeError


def create_layout(html_layout_file):
    """
    """
    try:
        with open(html_layout_file, "r") as layout_file:
            return layout_file.read()
    except IOError as err:
        logging.error(f"Not possible to open the file {layout_file}\n{err}")


def add_content():
    """
    """
    if spec_tbs:
        return html.Div(
            id="div-main",
            children=[
                _add_ctrl_div(),
                _add_plotting_div()
            ]
        )
    else:
        return html.Div(
        id="div-main-error",
        children="An Error Occured."
    )


def _add_ctrl_div():
    """Add div with controls. It is placed on the left side.
    """
    return html.Div(
        id="div-controls",
        children=[
            html.Div(
                id="div-controls-tabs",
                children=[
                    _add_ctrl_select(),
                    _add_ctrl_shown()
                ]
            )
        ],
        style={
            "display": "inline-block",
            "width": "18%",
            "padding": "5px"
        }
    )


def _add_plotting_div():
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


def _add_ctrl_shown():
    """
    """
    return html.Div(
        id="div-ctrl-shown",
        children="List of selected tests"
    )


def _add_ctrl_select():
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
                    {"label": k, "value": k} for k in spec_tbs.keys()
                ],
                # value=list(spec_tbs.keys())[0]
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


@callback(
    Output("dd-ctrl-area", "options"),
    Output("dd-ctrl-area", "disabled"),
    Input("dd-ctrl-phy", "value"),
)
def _update_dd_area(phy):
    """
    """

    logging.info("_update_dd_area")

    if phy is None:
        logging.info("_update_dd_area: PreventUpdate")
        raise PreventUpdate

    # _set_ctrls("phy_val", phy)

    try:
        options = [
            {"label": spec_tbs[phy][v]["label"], "value": v}
                for v in [v for v in spec_tbs[phy].keys()]
        ]
        disable = False
        logging.info("_update_dd_area: options")
        # logging.info(pformat(options))
    except KeyError:
        options = list()
        disable = True

    # _set_ctrls("area_opts", options)
    # _set_ctrls("area_dis", disable)

    logging.info("_update_dd_area: return")
    # logging.info(pformat(_ctrls))

    return options, disable


@callback(
    Output("dd-ctrl-test", "options"),
    Output("dd-ctrl-test", "disabled"),
    State("dd-ctrl-phy", "value"),
    Input("dd-ctrl-area", "value"),
)
def _update_dd_test(phy, area):
    """
    """

    if not area:
        logging.info("_update_dd_test: PreventUpdate")
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in spec_tbs[phy][area]["test"]
        ]
        disable = False
    except KeyError:
        options = list()
        disable = True

    return options, disable


@callback(
    Output("btn-ctrl-add", "disabled"),
    Input("dd-ctrl-test", "value"),
)
def _update_btn_add(test):
    """
    """

    logging.info("_update_btn_add")

    if test is None:
        logging.info("_update_btn_add: PreventUpdate")
        raise PreventUpdate

    if test:

        # TODO: Add validation

        # _set_ctrls("btn_dis", False)
        logging.info("_update_btn_add: return OK")
        return False
    else:
        logging.info("_update_btn_add: return BAD")
        return True


@callback(
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

    logging.info("_print_user_selection")
    logging.info(n_clicks)

    if not n_clicks:
        logging.info("_print_user_selection: PreventUpdate")
        raise PreventUpdate

    _set_ctrls("phy_val", phy)
    _set_ctrls("area_val", area)
    _set_ctrls("test_val", test)

    selected = (
        f"{_ctrls['phy_val']} - "
        f"{_ctrls['area_val']} - "
        f"{_ctrls['test_val']}\n\n"
    )
    logging.info(selected)

    _reset_ctrls()

    return selected, None, None, None, 0
