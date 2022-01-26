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
        "nics": ("nitro-50g", ),
        "nitro-50g": {
            "ip4": "IPv4 Routing",
            "ip6": "IPv6 Routing",
        }
    },
    "2n-clx": {
        "nics": ("x710", "xxv710", "cx556a", )
    },
    "2n-dnv": {
        "nics": ("x553", )
    },
    "2n-icx": {
        "nics": ("xxv710", )
    },
    "2n-skx": {
        "nics": ("x710", "xxv710", )
    },
    "2n-tx2": {
        "nics": ("xl710", )
    },
    "2n-zn2": {
        "nics": ("x710", "xxv710", )
    },
    "3n-aws": {
        "nics": ("nitro-50g", )
    },
    "3n-dnv": {
        "nics": ("x553", )
    },
    "3n-icx": {
        "nics": ("xxv710", )
    },
    "3n-skx": {
        "nics": ("x710", "xxv710", )
    },
    "3n-tsh": {
        "nics": ("x520", )
    },
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
                id='dd-predefined-topo-arch',
                placeholder="Select a Physical Test Bed Topology",
                multi=False,
                clearable=False,
                options=[{'label': i, 'value': i} for i in test_beds.keys()],
            ),
            html.Br(),
            html.Div(
                children="NIC"
            ),
            dcc.Dropdown(
                id='dd-predefined-nic',
                disabled=True,
                multi=False,
                clearable=False,
                options=[{'label': i, 'value': i} for i in range(3)],
            ),
            html.Br(),
            html.Div(
                children="Area"
            ),
            dcc.Dropdown(
                id='dd-predefined-area',
                multi=False,
                clearable=False,
                options=[{'label': i, 'value': i} for i in range(3)],
            ),
            html.Br(),
            html.Div(
                children="Test Set"
            ),
            dcc.Dropdown(
                id='dd-predefined-testset',
                multi=False,
                clearable=False,
                options=[{'label': i, 'value': i} for i in range(3)],
            ),
            html.Br(),
            html.Div(
                children="Number of Cores"
            ),
            dcc.Dropdown(
                id='dd-predefined-cores',
                multi=False,
                clearable=False,
                options=[
                    {'label': i, 'value': i.lower()} for i in ("1C", "2C", "4C")
                ],
            ),
            html.Br(),
            html.Div(
                children="Frame Size"
            ),
            dcc.Dropdown(
                id='dd-predefined-framesize',
                multi=False,
                clearable=False,
                options=[
                    {'label': i, 'value': i.lower()}
                        for i in ("64B", "78B", "1518B", "9000B", "IMIX")
                ],
            ),
            html.Br(),
            html.Div(
                children="Test Type"
            ),
            dcc.Dropdown(
                id='dd-predefined-testtype',
                multi=False,
                clearable=False,
                options=[
                    {'label': i, 'value': i} for i in ("MRR", "NDR", "PDR")
                ],
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
                id='dd-custom-topo-arch',
                multi=True,
                clearable=True,
                options=[{'label': i, 'value': i} for i in test_beds.keys()],
            ),
            html.Br(),
            html.Div(
                children="NIC"
            ),
            dcc.Dropdown(
                id='dd-custom-nic',
                multi=True,
                clearable=True,
                options=[{'label': i, 'value': i} for i in range(3)],
            ),
            html.Br(),
            html.Div(
                children="Area"
            ),
            dcc.Dropdown(
                id='dd-custom-area',
                multi=True,
                clearable=True,
                options=[{'label': i, 'value': i} for i in range(3)],
            ),
            html.Br(),
            html.Div(
                children="Test"
            ),
            dcc.Dropdown(
                id='dd-custom-test',
                multi=True,
                clearable=True,
                options=[{'label': i, 'value': i} for i in range(3)],
            ),
            html.Br(),
            html.Div(
                children="Number of Cores"
            ),
            dcc.Dropdown(
                id='dd-custom-cores',
                multi=True,
                clearable=True,
                options=[
                    {'label': i, 'value': i.lower()} for i in ("1C", "2C", "4C")
                ],
            ),
            html.Br(),
            html.Div(
                children="Frame Size"
            ),
            dcc.Dropdown(
                id='dd-custom-framesize',
                multi=True,
                clearable=True,
                options=[
                    {'label': i, 'value': i.lower()}
                        for i in ("64B", "78B", "1518B", "9000B", "IMIX")
                ],
            ),
            html.Br(),
            html.Div(
                children="Test Type"
            ),
            dcc.Dropdown(
                id='dd-custom-testtype',
                multi=True,
                clearable=True,
                options=[
                    {'label': i, 'value': i} for i in ("MRR", "NDR", "PDR")
                ],
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
                id='div-controls-tabs',
                children=[
                    _add_ctrl_tab_predefined(),
                    _add_ctrl_tab_custom()
                ],
                value="test_sets"
            )
        ],
        style={
            "display": "inline-block",
            "width": "25%",
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
            "width": "70%",
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
