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


import logging
import plotly.graph_objects as go
import pandas as pd
import re

from datetime import datetime
from numpy import isnan
from dash import no_update

from ..jumpavg import classify


_COLORS = (
    u"#1A1110",
    u"#DA2647",
    u"#214FC6",
    u"#01786F",
    u"#BD8260",
    u"#FFD12A",
    u"#A6E7FF",
    u"#738276",
    u"#C95A49",
    u"#FC5A8D",
    u"#CEC8EF",
    u"#391285",
    u"#6F2DA8",
    u"#FF878D",
    u"#45A27D",
    u"#FFD0B9",
    u"#FD5240",
    u"#DB91EF",
    u"#44D7A8",
    u"#4F86F7",
    u"#84DE02",
    u"#FFCFF1",
    u"#614051"
)
_ANOMALY_COLOR = {
    u"regression": 0.0,
    u"normal": 0.5,
    u"progression": 1.0
}
_COLORSCALE = [
    [0.00, u"red"],
    [0.33, u"red"],
    [0.33, u"white"],
    [0.66, u"white"],
    [0.66, u"green"],
    [1.00, u"green"]
]
_VALUE = {
    "mrr": "result_receive_rate_rate_avg",
    "ndr": "result_ndr_lower_rate_value",
    "pdr": "result_pdr_lower_rate_value",
    "pdr-lat": "result_latency_forward_pdr_50_avg"
}
_UNIT = {
    "mrr": "result_receive_rate_rate_unit",
    "ndr": "result_ndr_lower_rate_unit",
    "pdr": "result_pdr_lower_rate_unit",
    "pdr-lat": "result_latency_forward_pdr_50_unit"
}


def _classify_anomalies(data):
    """Process the data and return anomalies and trending values.

    Gather data into groups with average as trend value.
    Decorate values within groups to be normal,
    the first value of changed average as a regression, or a progression.

    :param data: Full data set with unavailable samples replaced by nan.
    :type data: OrderedDict
    :returns: Classification and trend values
    :rtype: 3-tuple, list of strings, list of floats and list of floats
    """
    # NaN means something went wrong.
    # Use 0.0 to cause that being reported as a severe regression.
    bare_data = [0.0 if isnan(sample) else sample for sample in data.values()]
    # TODO: Make BitCountingGroupList a subclass of list again?
    group_list = classify(bare_data).group_list
    group_list.reverse()  # Just to use .pop() for FIFO.
    classification = list()
    avgs = list()
    stdevs = list()
    active_group = None
    values_left = 0
    avg = 0.0
    stdv = 0.0
    for sample in data.values():
        if isnan(sample):
            classification.append(u"outlier")
            avgs.append(sample)
            stdevs.append(sample)
            continue
        if values_left < 1 or active_group is None:
            values_left = 0
            while values_left < 1:  # Ignore empty groups (should not happen).
                active_group = group_list.pop()
                values_left = len(active_group.run_list)
            avg = active_group.stats.avg
            stdv = active_group.stats.stdev
            classification.append(active_group.comment)
            avgs.append(avg)
            stdevs.append(stdv)
            values_left -= 1
            continue
        classification.append(u"normal")
        avgs.append(avg)
        stdevs.append(stdv)
        values_left -= 1
    return classification, avgs, stdevs


def trending_tput(data: pd.DataFrame, sel:dict, layout: dict, start: datetime,
    end: datetime):
    """
    """

    if not sel:
        return no_update, no_update

    def _generate_traces(ttype: str, name: str, df: pd.DataFrame,
        start: datetime, end: datetime, color: str):

        df = df.dropna(subset=[_VALUE[ttype], ])
        if df.empty:
            return list()

        x_axis = [d for d in df["start_time"] if d >= start and d <= end]

        anomalies, trend_avg, trend_stdev = _classify_anomalies(
            {k: v for k, v in zip(x_axis, df[_VALUE[ttype]])}
        )

        hover = list()
        for _, row in df.iterrows():
            hover_itm = (
                f"date: "
                f"{row['start_time'].strftime('%d-%m-%Y %H:%M:%S')}<br>"
                f"average [{row[_UNIT[ttype]]}]: "
                f"{row[_VALUE[ttype]]}<br>"
                f"{row['dut_type']}-ref: {row['dut_version']}<br>"
                f"csit-ref: {row['job']}/{row['build']}"
            )
            if ttype == "mrr":
                stdev = (
                    f"stdev [{row['result_receive_rate_rate_unit']}]: "
                    f"{row['result_receive_rate_rate_stdev']}<br>"
                )
            else:
                stdev = ""
            hover_itm = hover_itm.replace("<stdev>", stdev)
            hover.append(hover_itm)

        hover_trend = list()
        for avg, stdev in zip(trend_avg, trend_stdev):
            hover_trend.append(
                f"trend [pps]: {avg}<br>"
                f"stdev [pps]: {stdev}"
            )

        traces = [
            go.Scatter(  # Samples
                x=x_axis,
                y=df[_VALUE[ttype]],
                name=name,
                mode="markers",
                marker={
                    u"size": 5,
                    u"color": color,
                    u"symbol": u"circle",
                },
                text=hover,
                hoverinfo=u"text+name",
                showlegend=True,
                legendgroup=name,
            ),
            go.Scatter(  # Trend line
                x=x_axis,
                y=trend_avg,
                name=name,
                mode="lines",
                line={
                    u"shape": u"linear",
                    u"width": 1,
                    u"color": color,
                },
                text=hover_trend,
                hoverinfo=u"text+name",
                showlegend=False,
                legendgroup=name,
            )
        ]

        if anomalies:
            anomaly_x = list()
            anomaly_y = list()
            anomaly_color = list()
            ticktext = [u"Regression", u"Normal", u"Progression"]
            for idx, anomaly in enumerate(anomalies):
                if anomaly in (u"regression", u"progression"):
                    anomaly_x.append(x_axis[idx])
                    anomaly_y.append(trend_avg[idx])
                    anomaly_color.append(_ANOMALY_COLOR[anomaly])
            anomaly_color.append([0.0, 0.5, 1.0])
            traces.append(
                go.Scatter(
                    x=anomaly_x,
                    y=anomaly_y,
                    mode=u"markers",
                    hoverinfo=u"none",
                    showlegend=False,
                    legendgroup=name,
                    name=f"{name}-anomalies",
                    marker={
                        u"size": 15,
                        u"symbol": u"circle-open",
                        u"color": anomaly_color,
                        u"colorscale": _COLORSCALE,
                        u"showscale": True,
                        u"line": {
                            u"width": 2
                        },
                        u"colorbar": {
                            u"y": 0.5,
                            u"len": 0.8,
                            u"title": u"Circles Marking Data Classification",
                            u"titleside": u"right",
                            u"titlefont": {
                                u"size": 14
                            },
                            u"tickmode": u"array",
                            u"tickvals": [0.167, 0.500, 0.833],
                            u"ticktext": ticktext,
                            u"ticks": u"",
                            u"ticklen": 0,
                            u"tickangle": -90,
                            u"thickness": 10
                        }
                    }
                )
            )

        return traces

    # Generate graph:
    fig = go.Figure()
    for idx, itm in enumerate(sel):
        phy = itm["phy"].split("-")
        if len(phy) == 4:
            topo, arch, nic, drv = phy
            if drv in ("dpdk", "ixgbe"):
                drv = ""
            else:
                drv += "-"
                drv = drv.replace("_", "-")
        else:
            continue
        cadence = \
            "weekly" if (arch == "aws" or itm["testtype"] != "mrr") else "daily"
        sel_topo_arch = (
            f"csit-vpp-perf-"
            f"{itm['testtype'] if itm['testtype'] == 'mrr' else 'ndrpdr'}-"
            f"{cadence}-master-{topo}-{arch}"
        )
        df_sel = data.loc[(data["job"] == sel_topo_arch)]
        regex = (
            f"^.*{nic}.*\.{itm['framesize']}-{itm['core']}-{drv}{itm['test']}-"
            f"{'mrr' if itm['testtype'] == 'mrr' else 'ndrpdr'}$"
        )
        df = df_sel.loc[
            df_sel["test_id"].apply(
                lambda x: True if re.search(regex, x) else False
            )
        ].sort_values(by="start_time", ignore_index=True)
        name = (
            f"{itm['phy']}-{itm['framesize']}-{itm['core']}-"
            f"{itm['test']}-{itm['testtype']}"
        )
        for trace in _generate_traces(itm['testtype'], name, df, start, end,
                _COLORS[idx % len(_COLORS)]):
            fig.add_trace(trace)

    style = {"display": "block"}

    layout = layout.get("plot-trending", dict())
    fig.update_layout(layout)

    return fig, style
