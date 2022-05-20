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

"""
"""

import plotly.graph_objects as go
import pandas as pd

from datetime import datetime, timedelta

def select_data(data: pd.DataFrame, itm:str, start: datetime,
        end: datetime) -> pd.DataFrame:
    """
    """

    df = data.loc[
        (data["job"] == itm) &
        (data["start_time"] >= start) & (data["start_time"] <= end)
    ].sort_values(by="start_time", ignore_index=True)
    df = df.dropna(subset=["duration", ])

    return df


def graph_statistics(df: pd.DataFrame, job:str, layout: dict,
        start: datetime=datetime.utcnow()-timedelta(days=180),
        end: datetime=datetime.utcnow()) -> tuple:
    """
    """

    data = select_data(df, job, start, end)
    if data.empty:
        return None, None

    hover = list()
    for _, row in data.iterrows():
        d_type = "trex" if row["dut_type"] == "none" else row["dut_type"]
        hover_itm = (
            f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
            f"duration: "
            f"{(int(row['duration']) // 3600):02d}:"
            f"{((int(row['duration']) % 3600) // 60):02d}<br>"
            f"passed: {row['passed']}<br>"
            f"failed: {row['failed']}<br>"
            f"{d_type}-ref: {row['dut_version']}<br>"
            f"csit-ref: {row['job']}/{row['build']}<br>"
            f"hosts: {', '.join(row['hosts'])}"
        )
        hover.append(hover_itm)

    # Job durations:
    fig_duration = go.Figure(
        data=go.Scatter(
            x=data["start_time"],
            y=data["duration"],
            name=u"Duration",
            text=hover,
            hoverinfo=u"text"
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
    fig_passed = go.Figure(
        data=[
            go.Bar(
                x=data["start_time"],
                y=data["passed"],
                name=u"Passed",
                hovertext=hover,
                hoverinfo=u"text"
            ),
            go.Bar(
                x=data["start_time"],
                y=data["failed"],
                name=u"Failed",
                hovertext=hover,
                hoverinfo=u"text"
            )
        ]
    )
    layout_pf = layout.get("plot-stats-passed", dict())
    if layout_pf:
        fig_passed.update_layout(layout_pf)

    return fig_passed, fig_duration
