# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""
"""

import plotly.graph_objects as go
import pandas as pd

from ..utils.constants import Constants as C


def select_data(data: pd.DataFrame, itm: str) -> pd.DataFrame:
    """Select the data for graphs from the provided data frame.

    :param data: Data frame with data for graphs.
    :param itm: Item (in this case job name) which data will be selected from
        the input data frame.
    :type data: pandas.DataFrame
    :type itm: str
    :returns: A data frame with selected data.
    :rtype: pandas.DataFrame
    """

    df = data.loc[(data["job"] == itm)].sort_values(
        by="start_time", ignore_index=True)
    df = df.dropna(subset=["duration", ])

    return df


def graph_statistics(df: pd.DataFrame, job: str, layout: dict) -> tuple:
    """Generate graphs:
    1. Passed / failed tests,
    2. Job durations
    with additional information shown in hover.

    :param df: Data frame with input data.
    :param job: The name of job which data will be presented in the graphs.
    :param layout: Layout of plot.ly graph.
    :type df: pandas.DataFrame
    :type job: str
    :type layout: dict
    :returns: Tuple with two generated graphs (pased/failed tests and job
        duration).
    :rtype: tuple(plotly.graph_objects.Figure, plotly.graph_objects.Figure)
    """

    data = select_data(df, job)
    if data.empty:
        return None, None

    hover = list()
    for _, row in data.iterrows():
        hover_itm = (
            f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
            f"duration: "
            f"{(int(row['duration']) // 3600):02d}:"
            f"{((int(row['duration']) % 3600) // 60):02d}<br>"
            f"passed: {row['passed']}<br>"
            f"failed: {row['failed']}<br>"
            f"{row['dut_type']}-ref: {row['dut_version']}<br>"
            f"csit-ref: {row['job']}/{row['build']}<br>"
            f"hosts: {', '.join(row['hosts'])}"
        )
        hover.append(hover_itm)

    # Job durations:
    fig_duration = go.Figure(
        data=go.Scatter(
            x=data["start_time"],
            y=data["duration"],
            name="Duration",
            text=hover,
            hoverinfo="text"
        )
    )

    tickvals = [0, ]
    step = max(data["duration"]) / 5
    for i in range(5):
        tickvals.append(int(step * (i + 1)))
    layout_duration = layout.get("plot-stats-duration", dict())
    if layout_duration:
        layout_duration["yaxis"]["tickvals"] = tickvals
        layout_duration["yaxis"]["ticktext"] = [
            f"{(val // 3600):02d}:{((val % 3600) // 60):02d}" \
                for val in tickvals
        ]
        fig_duration.update_layout(layout_duration)

    # Passed / failed:
    bar_width = C.STATS_BAR_WIDTH_WEEKLY \
        if "weekly" in job else C.STATS_BAR_WIDTH_DAILY
    fig_passed = go.Figure(
        data=[
            go.Bar(
                x=data["start_time"],
                y=data["passed"],
                name="Passed",
                hovertext=hover,
                hoverinfo="text",
                width=bar_width
            ),
            go.Bar(
                x=data["start_time"],
                y=data["failed"],
                name="Failed",
                hovertext=hover,
                hoverinfo="text",
                width=bar_width
            )
        ]
    )
    layout_pf = layout.get("plot-stats-passed", dict())
    if layout_pf:
        fig_passed.update_layout(layout_pf)

    return fig_passed, fig_duration
