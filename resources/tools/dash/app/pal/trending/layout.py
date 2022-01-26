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


html_layout = u"""
<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body class="dash-template">
            <header>
              <div class="nav-wrapper">
                <a href="/">
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

def layout_add_content():
    return html.Div(children=[
        html.Div(children=[
            html.Div(children=[
                dcc.RadioItems(
                    id=u"test-type",
                    options=[
                        {u"label": u"MRR", u"value": u"MRR"},
                        {u"label": u"NDR", u"value": u"NDR"},
                        {u"label": u"PDR", u"value": u"PDR"},
                    ],
                    value="MRR")
            ], style={'height': '10%'}),
            html.Div(children=[
                dcc.Tabs(id='ctrl-tabs', value='predefined', children=[
                    dcc.Tab(label=u"Tests Sets", value=u"predefined", children=[
                        html.Div(
                            children=u"Area"
                        ),
                        dcc.Dropdown(
                            id='p1',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                        ),
                        html.Br(),
                        html.Div(
                            children=u"NIC"
                        ),
                        dcc.Dropdown(
                            id='p2',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                        ),
                        html.Br(),
                        html.Div(
                            children=u"Frame Size"
                        ),
                        dcc.Dropdown(
                            id='p3',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                        ),
                        html.Br(),
                        html.Div(
                            children=u"Cores"
                        ),
                        dcc.Dropdown(
                            id='p4',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                        ),
                        html.Br(),
                        html.Div(
                            children=u"Test Set"
                        ),
                        dcc.Dropdown(
                            id='p5',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                        ),
                    ]),
                    dcc.Tab(label=u"Tests", value=u"custom", children=[
                        html.Div(
                            children=u"Area"
                        ),
                        dcc.Dropdown(
                            id='c1',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                            value=u'0'
                        ),
                        html.Br(),
                        html.Div(
                            children=u"NIC"
                        ),
                        dcc.Dropdown(
                            id='c2',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                            value=u'0'
                        ),
                        html.Br(),
                        html.Div(
                            children=u"Frame Size"
                        ),
                        dcc.Dropdown(
                            id='c3',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                            value=u'0'
                        ),
                        html.Br(),
                        html.Div(
                            children=u"Cores"
                        ),
                        dcc.Dropdown(
                            id='c4',
                            multi=False,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                            value=u'0'
                        ),
                        html.Br(),
                        html.Div(
                            children=u"Test"
                        ),
                        dcc.Dropdown(
                            id='c5',
                            multi=True,
                            clearable=True,
                            options=[{'label': i, 'value': i} for i in range(5)],
                            value=u'0'
                        ),
                        html.Br(),
                        html.Button(id='btn-submit', children='Submit'),
                    ])
                ])
            ], style={'height': '40%'}),
            html.Div(children=[
                html.H4(u"Info Box")
            ], style={'height': '50%'}),
        ], style={'display': 'inline-block', 'width': '24%'}),
        html.Div(children=[
            u"graph"
        ], style={'display': 'inline-block', 'width': '74%'})
    ], id=u"dash-container")
