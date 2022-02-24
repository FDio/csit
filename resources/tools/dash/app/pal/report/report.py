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

"""Instantiate the Report Dash application.
"""

import dash
from dash import dcc
from dash import html
from dash import dash_table

from .data import read_stats
from .data import read_trending_mrr, read_trending_ndrpdr
from .data import read_iterative_mrr, read_iterative_ndrpdr
from .layout import html_layout


def init_report(server):
    """Create a Plotly Dash dashboard.

    :param server: Flask server.
    :type server: Flask
    :returns: Dash app server.
    :rtype: Dash
    """

    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix=u"/report/",
        external_stylesheets=[
            u"/static/dist/css/styles.css",
            u"https://fonts.googleapis.com/css?family=Lato",
        ],
    )

    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout
    dash_app.layout = html.Div(
        children=[
            html.Div(
                children=create_data_table(
                    read_stats().dropna(),
                    u"database-table-stats"
                )
            ),
            html.Div(
                children=create_data_table(
                    read_trending_mrr().dropna(),
                    u"database-table-mrr"
                )
            ),
            html.Div(
                children=create_data_table(
                    read_trending_ndrpdr().dropna(),
                    u"database-table-ndrpdr"
                )
            ),
            html.Div(
                children=create_data_table(
                    read_iterative_mrr().dropna(),
                    u"database-table-iterative-mrr"
                )
            ),
            html.Div(
                children=create_data_table(
                    read_iterative_ndrpdr().dropna(),
                    u"database-table-iterative-ndrpdr"
                )
            )
        ],
        id=u"dash-container",
    )
    return dash_app.server


def create_data_table(df, id):
    """Create Dash datatable from Pandas DataFrame.

    DEMO
    """

    table = dash_table.DataTable(
        id=id,
        columns=[{u"name": i, u"id": i} for i in df.columns],
        data=df.to_dict(u"records"),
        fixed_rows={'headers': True},
        sort_action=u"native",
        sort_mode=u"native",
        page_size=5,
        style_header={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'minWidth': 95, 'maxWidth': 95, 'width': 95,
        }
    )
    return table
