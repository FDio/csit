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

import hdrh.histogram
import hdrh.codec

from datetime import datetime
from numpy import isnan

from ..jumpavg import classify


_ANOMALY_COLOR = {
    "regression": 0.0,
    "normal": 0.5,
    "progression": 1.0
}
_COLORSCALE_TPUT = [
    [0.00, "red"],
    [0.33, "red"],
    [0.33, "white"],
    [0.66, "white"],
    [0.66, "green"],
    [1.00, "green"]
]
_TICK_TEXT_TPUT = ["Regression", "Normal", "Progression"]
_COLORSCALE_LAT = [
    [0.00, "green"],
    [0.33, "green"],
    [0.33, "white"],
    [0.66, "white"],
    [0.66, "red"],
    [1.00, "red"]
]
_TICK_TEXT_LAT = ["Progression", "Normal", "Regression"]
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
_LAT_HDRH = (  # Do not change the order
    "result_latency_forward_pdr_0_hdrh",
    "result_latency_reverse_pdr_0_hdrh",
    "result_latency_forward_pdr_10_hdrh",
    "result_latency_reverse_pdr_10_hdrh",
    "result_latency_forward_pdr_50_hdrh",
    "result_latency_reverse_pdr_50_hdrh",
    "result_latency_forward_pdr_90_hdrh",
    "result_latency_reverse_pdr_90_hdrh",
)
# This value depends on latency stream rate (9001 pps) and duration (5s).
# Keep it slightly higher to ensure rounding errors to not remove tick mark.
PERCENTILE_MAX = 99.999501

_GRAPH_LAT_HDRH_DESC = {
    "result_latency_forward_pdr_0_hdrh": "No-load.",
    "result_latency_reverse_pdr_0_hdrh": "No-load.",
    "result_latency_forward_pdr_10_hdrh": "Low-load, 10% PDR.",
    "result_latency_reverse_pdr_10_hdrh": "Low-load, 10% PDR.",
    "result_latency_forward_pdr_50_hdrh": "Mid-load, 50% PDR.",
    "result_latency_reverse_pdr_50_hdrh": "Mid-load, 50% PDR.",
    "result_latency_forward_pdr_90_hdrh": "High-load, 90% PDR.",
    "result_latency_reverse_pdr_90_hdrh": "High-load, 90% PDR."
}


def _get_color(idx: int) -> str:
    """
    """
    _COLORS = (
        "#1A1110", "#DA2647", "#214FC6", "#01786F", "#BD8260", "#FFD12A",
        "#A6E7FF", "#738276", "#C95A49", "#FC5A8D", "#CEC8EF", "#391285",
        "#6F2DA8", "#FF878D", "#45A27D", "#FFD0B9", "#FD5240", "#DB91EF",
        "#44D7A8", "#4F86F7", "#84DE02", "#FFCFF1", "#614051"
    )
    return _COLORS[idx % len(_COLORS)]


def _get_hdrh_latencies(row: pd.Series, name: str) -> dict:
    """
    """

    latencies = {"name": name}
    for key in _LAT_HDRH:
        try:
            latencies[key] = row[key]
        except KeyError:
            return None

    return latencies


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
            classification.append("outlier")
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
        classification.append("normal")
        avgs.append(avg)
        stdevs.append(stdv)
        values_left -= 1
    return classification, avgs, stdevs


def select_trending_data(data: pd.DataFrame, itm:dict) -> pd.DataFrame:
    """
    """

    phy = itm["phy"].split("-")
    if len(phy) == 4:
        topo, arch, nic, drv = phy
        if drv == "dpdk":
            drv = ""
        else:
            drv += "-"
            drv = drv.replace("_", "-")
    else:
        return None

    core = str() if itm["dut"] == "trex" else f"{itm['core']}"
    ttype = "ndrpdr" if itm["testtype"] in ("ndr", "pdr") else itm["testtype"]
    dut_v100 = "none" if itm["dut"] == "trex" else itm["dut"]
    dut_v101 = itm["dut"]

    df = data.loc[(
        (
            (
                (data["version"] == "1.0.0") &
                (data["dut_type"].str.lower() == dut_v100)
            ) |
            (
                (data["version"] == "1.0.1") &
                (data["dut_type"].str.lower() == dut_v101)
            )
        ) &
        (data["test_type"] == ttype) &
        (data["passed"] == True)
    )]
    df = df[df.job.str.endswith(f"{topo}-{arch}")]
    df = df[df.test_id.str.contains(
        f"^.*[.|-]{nic}.*{itm['framesize']}-{core}-{drv}{itm['test']}-{ttype}$",
        regex=True
    )].sort_values(by="start_time", ignore_index=True)

    return df


def _generate_trending_traces(ttype: str, name: str, df: pd.DataFrame,
    start: datetime, end: datetime, color: str) -> list:
    """
    """

    df = df.dropna(subset=[_VALUE[ttype], ])
    if df.empty:
        return list()
    df = df.loc[((df["start_time"] >= start) & (df["start_time"] <= end))]
    if df.empty:
        return list()

    x_axis = df["start_time"].tolist()

    anomalies, trend_avg, trend_stdev = _classify_anomalies(
        {k: v for k, v in zip(x_axis, df[_VALUE[ttype]])}
    )

    hover = list()
    customdata = list()
    for _, row in df.iterrows():
        d_type = "trex" if row["dut_type"] == "none" else row["dut_type"]
        hover_itm = (
            f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
            f"<prop> [{row[_UNIT[ttype]]}]: {row[_VALUE[ttype]]:,.0f}<br>"
            f"<stdev>"
            f"{d_type}-ref: {row['dut_version']}<br>"
            f"csit-ref: {row['job']}/{row['build']}<br>"
            f"hosts: {', '.join(row['hosts'])}"
        )
        if ttype == "mrr":
            stdev = (
                f"stdev [{row['result_receive_rate_rate_unit']}]: "
                f"{row['result_receive_rate_rate_stdev']:,.0f}<br>"
            )
        else:
            stdev = ""
        hover_itm = hover_itm.replace(
            "<prop>", "latency" if ttype == "pdr-lat" else "average"
        ).replace("<stdev>", stdev)
        hover.append(hover_itm)
        if ttype == "pdr-lat":
            customdata.append(_get_hdrh_latencies(row, name))

    hover_trend = list()
    for avg, stdev, (_, row) in zip(trend_avg, trend_stdev, df.iterrows()):
        d_type = "trex" if row["dut_type"] == "none" else row["dut_type"]
        hover_itm = (
            f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
            f"trend [pps]: {avg:,.0f}<br>"
            f"stdev [pps]: {stdev:,.0f}<br>"
            f"{d_type}-ref: {row['dut_version']}<br>"
            f"csit-ref: {row['job']}/{row['build']}<br>"
            f"hosts: {', '.join(row['hosts'])}"
        )
        if ttype == "pdr-lat":
            hover_itm = hover_itm.replace("[pps]", "[us]")
        hover_trend.append(hover_itm)

    traces = [
        go.Scatter(  # Samples
            x=x_axis,
            y=df[_VALUE[ttype]],
            name=name,
            mode="markers",
            marker={
                "size": 5,
                "color": color,
                "symbol": "circle",
            },
            text=hover,
            hoverinfo="text+name",
            showlegend=True,
            legendgroup=name,
            customdata=customdata
        ),
        go.Scatter(  # Trend line
            x=x_axis,
            y=trend_avg,
            name=name,
            mode="lines",
            line={
                "shape": "linear",
                "width": 1,
                "color": color,
            },
            text=hover_trend,
            hoverinfo="text+name",
            showlegend=False,
            legendgroup=name,
        )
    ]

    if anomalies:
        anomaly_x = list()
        anomaly_y = list()
        anomaly_color = list()
        hover = list()
        for idx, anomaly in enumerate(anomalies):
            if anomaly in ("regression", "progression"):
                anomaly_x.append(x_axis[idx])
                anomaly_y.append(trend_avg[idx])
                anomaly_color.append(_ANOMALY_COLOR[anomaly])
                hover_itm = (
                    f"date: {x_axis[idx].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                    f"trend [pps]: {trend_avg[idx]:,.0f}<br>"
                    f"classification: {anomaly}"
                )
                if ttype == "pdr-lat":
                    hover_itm = hover_itm.replace("[pps]", "[us]")
                hover.append(hover_itm)
        anomaly_color.extend([0.0, 0.5, 1.0])
        traces.append(
            go.Scatter(
                x=anomaly_x,
                y=anomaly_y,
                mode="markers",
                text=hover,
                hoverinfo="text+name",
                showlegend=False,
                legendgroup=name,
                name=name,
                marker={
                    "size": 15,
                    "symbol": "circle-open",
                    "color": anomaly_color,
                    "colorscale": _COLORSCALE_LAT \
                        if ttype == "pdr-lat" else _COLORSCALE_TPUT,
                    "showscale": True,
                    "line": {
                        "width": 2
                    },
                    "colorbar": {
                        "y": 0.5,
                        "len": 0.8,
                        "title": "Circles Marking Data Classification",
                        "titleside": "right",
                        "tickmode": "array",
                        "tickvals": [0.167, 0.500, 0.833],
                        "ticktext": _TICK_TEXT_LAT \
                            if ttype == "pdr-lat" else _TICK_TEXT_TPUT,
                        "ticks": "",
                        "ticklen": 0,
                        "tickangle": -90,
                        "thickness": 10
                    }
                }
            )
        )

    return traces


def graph_trending(data: pd.DataFrame, sel:dict, layout: dict,
    start: datetime, end: datetime) -> tuple:
    """
    """

    if not sel:
        return None, None

    fig_tput = None
    fig_lat = None
    for idx, itm in enumerate(sel):

        df = select_trending_data(data, itm)
        if df is None or df.empty:
            continue

        name = "-".join((itm["dut"], itm["phy"], itm["framesize"], itm["core"],
            itm["test"], itm["testtype"], ))
        traces = _generate_trending_traces(
            itm["testtype"], name, df, start, end, _get_color(idx)
        )
        if traces:
            if not fig_tput:
                fig_tput = go.Figure()
            fig_tput.add_traces(traces)

        if itm["testtype"] == "pdr":
            traces = _generate_trending_traces(
                "pdr-lat", name, df, start, end, _get_color(idx)
            )
            if traces:
                if not fig_lat:
                    fig_lat = go.Figure()
                fig_lat.add_traces(traces)

    if fig_tput:
        fig_tput.update_layout(layout.get("plot-trending-tput", dict()))
    if fig_lat:
        fig_lat.update_layout(layout.get("plot-trending-lat", dict()))

    return fig_tput, fig_lat


def graph_hdrh_latency(data: dict, layout: dict) -> go.Figure:
    """
    """

    fig = None

    traces = list()
    for idx, (lat_name, lat_hdrh) in enumerate(data.items()):
        try:
            decoded = hdrh.histogram.HdrHistogram.decode(lat_hdrh)
        except (hdrh.codec.HdrLengthException, TypeError) as err:
            continue
        previous_x = 0.0
        prev_perc = 0.0
        xaxis = list()
        yaxis = list()
        hovertext = list()
        for item in decoded.get_recorded_iterator():
            # The real value is "percentile".
            # For 100%, we cut that down to "x_perc" to avoid
            # infinity.
            percentile = item.percentile_level_iterated_to
            x_perc = min(percentile, PERCENTILE_MAX)
            xaxis.append(previous_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{_GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
                f"Direction: {('W-E', 'E-W')[idx % 2]}<br>"
                f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                f"Latency: {item.value_iterated_to}uSec"
            )
            next_x = 100.0 / (100.0 - x_perc)
            xaxis.append(next_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{_GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
                f"Direction: {('W-E', 'E-W')[idx % 2]}<br>"
                f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                f"Latency: {item.value_iterated_to}uSec"
            )
            previous_x = next_x
            prev_perc = percentile

        traces.append(
            go.Scatter(
                x=xaxis,
                y=yaxis,
                name=_GRAPH_LAT_HDRH_DESC[lat_name],
                mode="lines",
                legendgroup=_GRAPH_LAT_HDRH_DESC[lat_name],
                showlegend=bool(idx % 2),
                line=dict(
                    color=_get_color(int(idx/2)),
                    dash="solid",
                    width=1 if idx % 2 else 2
                ),
                hovertext=hovertext,
                hoverinfo="text"
            )
        )
    if traces:
        fig = go.Figure()
        fig.add_traces(traces)
        layout_hdrh = layout.get("plot-hdrh-latency", None)
        if lat_hdrh:
            fig.update_layout(layout_hdrh)

    return fig
