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

"""Instantiate the Trending Dash application.
"""
import dash

from ..utils.constants import Constants as C
from .layout import Layout


def init_trending(server, time_period=None):
    """Create a Plotly Dash dashboard.

    :param server: Flask server.
    :type server: Flask
    :returns: Dash app server.
    :rtype: Dash
    """

    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix=C.TREND_ROUTES_PATHNAME_PREFIX,
        external_stylesheets=C.EXTERNAL_STYLESHEETS
    )

    layout = Layout(
        app=dash_app,
        html_layout_file=C.TREND_HTML_LAYOUT_FILE,
        graph_layout_file=C.TREND_GRAPH_LAYOUT_FILE,
        data_spec_file=C.DATA_SPEC_FILE,
        tooltip_file=C.TOOLTIP_FILE,
        time_period=time_period
    )
    dash_app.index_string = layout.html_layout
    dash_app.layout = layout.add_content()

    return dash_app.server
