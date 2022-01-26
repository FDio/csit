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

from dash import dcc
from dash import html
from dash import Input, Output, callback
from dash.exceptions import PreventUpdate


html_layout = """
<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>Continuous Performance Trending</title>
            {%favicon%}
            {%css%}
        </head>
        <body class="dash-template">
            <header>
              <div class="nav-wrapper">
                <a href="/">
                    <h1>FD.io CSIT</h1>
                </a>
                <a href="">
                  <h1>Continuous Performance Trending</h1>
                </a>
                <nav>
                </nav>
              </div>
            </header>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
"""


test_beds = {
    "2n-aws": {
        "nitro-50g": {
            "ip4": {
                "label": "IPv4 Routing",
                "test": (),
                "test-set": {
                    "ip4routing-base-scale": (
                        "ethip4-ip4base",
                        "ethip4-ip4scale20k",
                        "ethip4-ip4scale20k-rnd",
                    ),
                },
                "core": ("1C", "2C", ),
                "frame-size": ("64B", "1518B", ),
                "test-type": ("MRR", "NDR", "PDR", )
            },
            "ip6": {
                "label": "IPv6 Routing",
                "test": (),
                "test-set": {
                    "ip6routing-base-scale": (
                        "ethip6-ip4base",
                        "ethip6-ip4scale20k",
                        "ethip6-ip4scale20k-rnd",
                    ),
                },
                "core": ("1C", "2C", ),
                "frame-size": ("78B", "1518B", ),
                "test-type": ("MRR", "NDR", "PDR", )
            }
        },
    },
    # "2n-clx": {
    #     "nics": ("x710", "xxv710", "cx556a", )
    # },
    # "2n-dnv": {
    #     "nics": ("x553", )
    # },
    # "2n-icx": {
    #     "nics": ("xxv710", )
    # },
    # "2n-skx": {
    #     "nics": ("x710", "xxv710", )
    # },
    # "2n-tx2": {
    #     "nics": ("xl710", )
    # },
    # "2n-zn2": {
    #     "nics": ("x710", "xxv710", )
    # },
    "3n-aws": {
        "nitro-50g": {
            "ip4": {
                "label": "IPv4 Routing",
                "test-set": {
                    "ip4routing-base-scale": (
                        "ethip4-ip4base",
                        "ethip4-ip4scale20k",
                        "ethip4-ip4scale20k-rnd",
                    ),
                },
                "core": ("1C", "2C", ),
                "frame-size": ("64B", "1518B", ),
                "test-type": ("MRR", "NDR", "PDR", )
            },
            "ipsec": {
                "label": "IPSec IPv4 Routing",
                "test-set": {
                    "ipsec-ip4routing-base-scale": (
                        "ethip4ipsec40tnlsw-ip4base-int-aes256gcm",
                    ),
                },
                "core": ("1C", "2C", ),
                "frame-size": ("IMIX", "1518B", ),
                "test-type": ("MRR", "NDR", "PDR", )
            }
        },
    },
    # "3n-dnv": {
    #     "nics": ("x553", )
    # },
    # "3n-icx": {
    #     "nics": ("xxv710", )
    # },
    # "3n-skx": {
    #     "nics": ("x710", "xxv710", )
    # },
    # "3n-tsh": {
    #     "nics": ("x520", )
    # },
}


def _add_ctrl_tab_predefined():
    """
    """
    return dcc.Tab(
        id="ctrl-tab-predefined",
        label="Tests Sets",
        value="test_sets",
        children=[
            html.Br(),
            html.Div(
                children="Physical Test Bed Topology"
            ),
            dcc.Dropdown(
                id="dd-predefined-topo-arch",
                placeholder="Select a Physical Test Bed Topology...",
                multi=False,
                clearable=False,
                options=[{"label": k, "value": k} for k in test_beds.keys()],
            ),
            html.Br(),
            html.Div(
                children="NIC"
            ),
            dcc.Dropdown(
                id="dd-predefined-nic",
                placeholder="Select a NIC..",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Area"
            ),
            dcc.Dropdown(
                id="dd-predefined-area",
                placeholder="Select an Area...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Test Set"
            ),
            dcc.Dropdown(
                id="dd-predefined-testset",
                placeholder="Select a Test Set...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Number of Cores"
            ),
            dcc.Dropdown(
                id="dd-predefined-core",
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
                id="dd-predefined-framesize",
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
                id="dd-predefined-testtype",
                placeholder="Select a Test Type...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Button(
                id="btn-predefined-submit",
                children="Submit",
                disabled=True
            ),
            html.Br(),
            html.Div(
                id="div-predefined-info"
            )
        ]
    )


def _add_ctrl_tab_custom():
    """
    """
    return dcc.Tab(
        id="ctrl-tab-custom",
        label="Tests",
        value="tests",
        children=[
            html.Br(),
            html.Div(
                children="Physical Test Bed Topology"
            ),
            dcc.Dropdown(
                id="dd-custom-topo-arch",
                placeholder="Select a Physical Test Bed Topology...",
                multi=False,
                clearable=False,
                options=[{"label": k, "value": k} for k in test_beds.keys()],
            ),
            html.Br(),
            html.Div(
                children="NIC"
            ),
            dcc.Dropdown(
                id="dd-custom-nic",
                placeholder="Select a NIC..",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Area"
            ),
            dcc.Dropdown(
                id="dd-custom-area",
                placeholder="Select an Area...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Test Set"
            ),
            dcc.Dropdown(
                id="dd-custom-testset",
                placeholder="Select a Test Set...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Test"
            ),
            dcc.Dropdown(
                id="dd-custom-test",
                placeholder="Select a Test...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
            html.Br(),
            html.Div(
                children="Number of Cores"
            ),
            dcc.Dropdown(
                id="dd-custom-core",
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
                id="dd-custom-framesize",
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
                id="dd-custom-testtype",
                placeholder="Select a Test Type...",
                disabled=True,
                multi=False,
                clearable=False,
            ),
                        html.Br(),
            html.Button(
                id="btn-custom-submit",
                children="Submit",
                disabled=True
            ),
            html.Br(),
            html.Div(
                id="div-custom-info"
            )
        ]
    )


def _add_ctrl_div_tabs_info():
    """Add div with controls. It is placed on the left side.
    """
    return html.Div(
        id="div-controls",
        children=[
            dcc.Tabs(
                id="div-controls-tabs",
                children=[
                    _add_ctrl_tab_predefined(),
                    _add_ctrl_tab_custom()
                ],
                value="test_sets"
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
                    "text-align": "center"
                }
            )
        ],
        style={
            "display": "inline-block",
            "width": "80%",
            "padding": "5px"
        }
    )


def layout_add_content():
    """Add web page layout and content.

    :returns: layout
    :rtype: dash.html.Div
    """

    return html.Div(
        id="div-main",
        children=[
            _add_ctrl_div_tabs_info(),
            _add_plotting_div()
        ]
    )


# Callbacks:

# Predefined:

@callback(
    Output("dd-predefined-nic", "options"),
    Output("dd-predefined-nic", "disabled"),
    Input("dd-predefined-topo-arch", "value")
)
def _update_dd_predefined_nic(topo_arch: str):
    """
    """

    if topo_arch is None:
        raise PreventUpdate

    try:
        options = [
            {"label": i, "value": i} for i in test_beds[topo_arch].keys()
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-predefined-area", "options"),
    Output("dd-predefined-area", "disabled"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value")
)
def _update_dd_predefined_area(topo_arch: str, nic: str):
    """
    """

    if not all((topo_arch, nic, )):
        raise PreventUpdate

    try:
        options = [
            {"label": test_beds[topo_arch][nic][v]["label"], "value": v}
                for v in [v for v in test_beds[topo_arch][nic].keys()]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-predefined-testset", "options"),
    Output("dd-predefined-testset", "disabled"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value"),
    Input("dd-predefined-area", "value")
)
def _update_dd_predefined_testset(topo_arch: str, nic: str, area: str):
    """
    """

    if not all((topo_arch, nic, area, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["test-set"].keys()
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-predefined-core", "options"),
    Output("dd-predefined-core", "disabled"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value"),
    Input("dd-predefined-area", "value"),
    Input("dd-predefined-testset", "value")
)
def _update_dd_predefined_core(
    topo_arch: str, nic: str, area: str, testset: str):
    """
    """

    if not all((topo_arch, nic, area, testset, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["core"]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-predefined-framesize", "options"),
    Output("dd-predefined-framesize", "disabled"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value"),
    Input("dd-predefined-area", "value"),
    Input("dd-predefined-testset", "value"),
    Input("dd-predefined-core", "value"),
)
def _update_dd_predefined_framesize(
    topo_arch: str, nic: str, area: str, testset: str, core: str):
    """
    """

    if not all((topo_arch, nic, area, testset, core, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["frame-size"]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-predefined-testtype", "options"),
    Output("dd-predefined-testtype", "disabled"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value"),
    Input("dd-predefined-area", "value"),
    Input("dd-predefined-testset", "value"),
    Input("dd-predefined-core", "value"),
    Input("dd-predefined-framesize", "value"),
)
def _update_dd_predefined_testtype(
    topo_arch: str, nic: str, area: str, testset: str, core: str,
    framesize: str):
    """
    """

    if not all((topo_arch, nic, area, testset, core, framesize, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["test-type"]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("btn-predefined-submit", "disabled"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value"),
    Input("dd-predefined-area", "value"),
    Input("dd-predefined-testset", "value"),
    Input("dd-predefined-core", "value"),
    Input("dd-predefined-framesize", "value"),
    Input("dd-predefined-testtype", "value")
)
def _update_dd_predefined_submit(
    topo_arch: str, nic: str, area: str, testset: str, core: str,
    framesize: str, testtype: str):
    """
    """

    if all((topo_arch, nic, area, testset, core, framesize, testtype, )):
    # if testset:
        return False
    else:
        return True

@callback(
    Output("div-predefined-info", "children"),
    Input("dd-predefined-topo-arch", "value"),
    Input("dd-predefined-nic", "value"),
    Input("dd-predefined-area", "value"),
    Input("dd-predefined-testset", "value"),
    Input("dd-predefined-core", "value"),
    Input("dd-predefined-framesize", "value"),
    Input("dd-predefined-testtype", "value"),
    Input("btn-predefined-submit", "n_clicks")
)
def _print_text(
    topo_arch: str, nic: str, area: str, testset: str, core: str,
    framesize: str, testtype: str, n_clicks):
    """
    """
    return f"{topo_arch} {nic} {area} {testset} {core} {framesize} {testtype} {n_clicks}\n"


# Custom:

@callback(
    Output("dd-custom-nic", "options"),
    Output("dd-custom-nic", "disabled"),
    Input("dd-custom-topo-arch", "value")
)
def _update_dd_custom_nic(topo_arch: str):
    """
    """

    if topo_arch is None:
        raise PreventUpdate

    try:
        options = [
            {"label": i, "value": i} for i in test_beds[topo_arch].keys()
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-custom-area", "options"),
    Output("dd-custom-area", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value")
)
def _update_dd_custom_area(topo_arch: str, nic: str):
    """
    """

    if not all((topo_arch, nic, )):
        raise PreventUpdate

    try:
        options = [
            {"label": test_beds[topo_arch][nic][v]["label"], "value": v}
                for v in [v for v in test_beds[topo_arch][nic].keys()]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-custom-testset", "options"),
    Output("dd-custom-testset", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value")
)
def _update_dd_custom_testset(topo_arch: str, nic: str, area: str):
    """
    """

    if not all((topo_arch, nic, area, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["test-set"].keys()
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-custom-test", "options"),
    Output("dd-custom-test", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value"),
    Input("dd-custom-testset", "value")
)
def _update_dd_custom_test(topo_arch: str, nic: str, area: str, testset: str):
    """
    """

    if not all((topo_arch, nic, area, testset, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["test-set"][testset]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-custom-core", "options"),
    Output("dd-custom-core", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value"),
    Input("dd-custom-testset", "value"),
    Input("dd-custom-test", "value")
)
def _update_dd_custom_core(
    topo_arch: str, nic: str, area: str, testset: str, test: str):
    """
    """

    if not all((topo_arch, nic, area, testset, test, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["core"]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-custom-framesize", "options"),
    Output("dd-custom-framesize", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value"),
    Input("dd-custom-testset", "value"),
    Input("dd-custom-test", "value"),
    Input("dd-custom-core", "value"),
)
def _update_dd_custom_framesize(
    topo_arch: str, nic: str, area: str, testset: str, test: str, core: str):
    """
    """

    if not all((topo_arch, nic, area, testset, test, core, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["frame-size"]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-custom-testtype", "options"),
    Output("dd-custom-testtype", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value"),
    Input("dd-custom-testset", "value"),
    Input("dd-custom-test", "value"),
    Input("dd-custom-core", "value"),
    Input("dd-custom-framesize", "value"),
)
def _update_dd_custom_testtype(
    topo_arch: str, nic: str, area: str, testset: str, test: str, core: str,
    framesize: str):
    """
    """

    if not all((topo_arch, nic, area, testset, test, core, framesize, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[topo_arch][nic][area]["test-type"]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("btn-custom-submit", "disabled"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value"),
    Input("dd-custom-testset", "value"),
    Input("dd-custom-core", "value"),
    Input("dd-custom-framesize", "value"),
    Input("dd-custom-testtype", "value")
)
def _update_dd_custom_submit(
    topo_arch: str, nic: str, area: str, testset: str, core: str,
    framesize: str, testtype: str):
    """
    """

    if all((topo_arch, nic, area, testset, core, framesize, testtype, )):
    # if testset:
        return False
    else:
        return True

@callback(
    Output("div-custom-info", "children"),
    Input("dd-custom-topo-arch", "value"),
    Input("dd-custom-nic", "value"),
    Input("dd-custom-area", "value"),
    Input("dd-custom-testset", "value"),
    Input("dd-custom-core", "value"),
    Input("dd-custom-framesize", "value"),
    Input("dd-custom-testtype", "value"),
    Input("btn-custom-submit", "n_clicks")
)
def _print_text(
    topo_arch: str, nic: str, area: str, testset: str, core: str,
    framesize: str, testtype: str, n_clicks):
    """
    """
    return f"{topo_arch} {nic} {area} {testset} {core} {framesize} {testtype} {n_clicks}\n"
