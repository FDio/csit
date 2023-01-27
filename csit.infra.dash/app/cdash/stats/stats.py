# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""Instantiate the Statistics Dash application.
"""
import dash
import pandas as pd

from ..utils.constants import Constants as C
from .layout import Layout


def init_stats(
        server,
        data_stats: pd.DataFrame,
        data_mrr: pd.DataFrame,
        data_ndrpdr: pd.DataFrame,
        # time_period=None
    ) -> dash.Dash:
    """Create a Plotly Dash dashboard.

    :param server: Flask server.
    :type server: Flask
    :returns: Dash app server.
    :rtype: Dash
    """

    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix=C.STATS_ROUTES_PATHNAME_PREFIX,
        external_stylesheets=C.EXTERNAL_STYLESHEETS,
        title=C.STATS_TITLE
    )

    layout = Layout(
        app=dash_app,
        data_stats=data_stats,
        data_mrr=data_mrr,
        data_ndrpdr=data_ndrpdr,
        html_layout_file=C.HTML_LAYOUT_FILE,
        graph_layout_file=C.STATS_GRAPH_LAYOUT_FILE,
        # data_spec_file=C.DATA_SPEC_FILE,
        tooltip_file=C.TOOLTIP_FILE,
        # time_period=time_period
    )
    dash_app.index_string = layout.html_layout
    dash_app.layout = layout.add_content()

    return dash_app.server
