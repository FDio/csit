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
    "2n-aws-nitro-50g-ena": {
        "ip4-base": {
            "label": "IPv4 Routing Base",
            "test": (
                "ethip4-ip4base",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("64B", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        },
        "ip4-scale": {
            "label": "IPv4 Routing Scale",
            "test": (
                "ethip4-ip4scale20k",
                "ethip4-ip4scale20k-rnd",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("64B", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        },
        "ip6-base": {
            "label": "IPv6 Routing Base",
            "test": (
                "ethip6-ip4base",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("78B", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        },
        "ip6-scale": {
            "label": "IPv6 Routing Scale",
            "test": (
                "ethip6-ip4scale20k",
                "ethip6-ip4scale20k-rnd",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("78B", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        }
    },
    "2n-clx-cx556a-rdma": {},
    "2n-clx-x710-avf": {},
    "2n-clx-x710-dpdk": {},
    "2n-clx-xxv710-af-xdp": {},
    "2n-clx-xxv710-avf": {
        "l2-base": {},
        "l2-scale": {},
        "ip4-base": {},
        "ip4-scale": {},
        "ip4-features": {},
        "ip6-base": {},
        "ip6-scale": {},
        "ethip4-ethip4udpgeneve": {},
        "nat44det-ip4-stl-bidir": {},
        "nat44ed-ip4-stl-unidir": {},
        "nat44ed-ip4-udp-stf-cps": {},
        "nat44ed-ip4-tcp-stf-cps": {},
        "nat44ed-ip4-udp-stf-pps": {},
        "nat44ed-ip4-tcp-stf-pps": {},
        "nat44ed-ip4-udp-tput": {},
        "nat44ed-ip4-tcp-tput": {},
        "vhost-base": {},
        "memif-base": {},
        "vnf-service-chains-routing": {},
        "cnf-service-chains-routing": {},
        "cnf-service-pipelines-routing": {},
        "vnf-service-chains-tunnels": {},
    },
    "2n-clx-xxv710-dpdk": {},
    "2n-dnv-x553-ixgbe": {},
    "2n-icx-xxv710-avf": {},
    "2n-icx-xxv710-dpdk": {},
    "2n-skx-x710-avf": {},
    "2n-skx-x710-dpdk": {},
    "2n-skx-xxv710-avf": {},
    "2n-skx-xxv710-dpdk": {},
    "2n-tx2-xl710-af-xdp": {},
    "2n-tx2-xl710-avf": {},
    "2n-tx2-xl710-dpdk": {},
    "2n-zn2-x710-avf": {},
    "2n-zn2-x710-dpdk": {},
    "2n-zn2-cx556a-rdma": {},
    "2n-zn2-xxv710-avf": {},
    "2n-zn2-xxv710-dpdk": {},
    "3n-aws-nitro-50g-ena": {
        "ip4-base": {
            "label": "IPv4 Routing Base",
            "test": (
                "ethip4-ip4base",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("64B", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        },
        "ip4-scale": {
            "label": "IPv4 Routing Scale",
            "test": (
                "ethip4-ip4scale20k",
                "ethip4-ip4scale20k-rnd",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("64B", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        },
        "ipsec-base": {
            "label": "IPSec IPv4 Routing Base",
            "test": (
                "ethip4ipsec40tnlsw-ip4base-int-aes256gcm",
            ),
            "core": ("1C", "2C", ),
            "frame-size": ("IMIX", "1518B", ),
            "test-type": ("MRR", "NDR", "PDR", )
        }
    },
    "3n-dnv-x553-ixgbe": {},
    "3n-icx-xxv710-avf": {},
    "3n-icx-xxv710-dpdk": {},
    "3n-skx-x710-avf": {},
    "3n-skx-xxv710-avf": {},
    "3n-skx-xxv710-dpdk": {},
    "3n-tsh-x520-ixgbe": {}
}


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
                options=[{"label": k, "value": k} for k in test_beds.keys()],
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


def _add_ctrl_shown():
    """
    """
    return html.Div(
        id="div-ctrl-shown",
        children="List of selected tests"
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


def layout_add_content():
    """Add web page layout and content.

    :returns: layout
    :rtype: dash.html.Div
    """

    return html.Div(
        id="div-main",
        children=[
            _add_ctrl_div(),
            _add_plotting_div()
        ]
    )


# Callbacks:

@callback(
    Output("dd-ctrl-area", "options"),
    Output("dd-ctrl-area", "disabled"),
    Input("dd-ctrl-phy", "value"),
)
def _update_dd_area(phy: str):
    """
    """

    if phy is None:
        raise PreventUpdate

    try:
        options = [
            {"label": test_beds[phy][v]["label"], "value": v}
                for v in [v for v in test_beds[phy].keys()]
        ]
    except KeyError:
        options = list()

    return options, False


@callback(
    Output("dd-ctrl-test", "options"),
    Output("dd-ctrl-test", "disabled"),
    Input("dd-ctrl-phy", "value"),
    Input("dd-ctrl-area", "value"),
)
def _update_dd_test(phy: str, area: str):
    """
    """

    if not all((phy, area, )):
        raise PreventUpdate

    try:
        options = [
            {"label": v, "value": v}
                for v in test_beds[phy][area]["test"]
        ]
    except KeyError:
        options = list()

    return options, False





@callback(
    Output("btn-ctrl-add", "disabled"),
    Input("dd-ctrl-phy", "value"),
    Input("dd-ctrl-area", "value"),
    Input("dd-ctrl-test", "value"),
)
def _update_btn_add(phy: str, area: str, test: str):
    """
    """

    if all((phy, area, test, )):
        return False
    else:
        return True

@callback(
    Output("div-ctrl-info", "children"),
    Input("dd-ctrl-phy", "value"),
    Input("dd-ctrl-area", "value"),
    Input("dd-ctrl-test", "value"),
    Input("btn-ctrl-add", "n_clicks")
)
def _print_text(phy: str, area: str, test: str, n_clicks: int):
    """
    """
    return f"{phy} {area} {test} {n_clicks}\n"
