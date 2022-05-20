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


_COLORS = (
    u"#1A1110", u"#DA2647", u"#214FC6", u"#01786F", u"#BD8260", u"#FFD12A",
    u"#A6E7FF", u"#738276", u"#C95A49", u"#FC5A8D", u"#CEC8EF", u"#391285",
    u"#6F2DA8", u"#FF878D", u"#45A27D", u"#FFD0B9", u"#FD5240", u"#DB91EF",
    u"#44D7A8", u"#4F86F7", u"#84DE02", u"#FFCFF1", u"#614051"
)
_ANOMALY_COLOR = {
    u"regression": 0.0,
    u"normal": 0.5,
    u"progression": 1.0
}
_COLORSCALE_TPUT = [
    [0.00, u"red"],
    [0.33, u"red"],
    [0.33, u"white"],
    [0.66, u"white"],
    [0.66, u"green"],
    [1.00, u"green"]
]
_TICK_TEXT_TPUT = [u"Regression", u"Normal", u"Progression"]
_COLORSCALE_LAT = [
    [0.00, u"green"],
    [0.33, u"green"],
    [0.33, u"white"],
    [0.66, u"white"],
    [0.66, u"red"],
    [1.00, u"red"]
]
_TICK_TEXT_LAT = [u"Progression", u"Normal", u"Regression"]
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
    u"result_latency_forward_pdr_0_hdrh": u"No-load.",
    u"result_latency_reverse_pdr_0_hdrh": u"No-load.",
    u"result_latency_forward_pdr_10_hdrh": u"Low-load, 10% PDR.",
    u"result_latency_reverse_pdr_10_hdrh": u"Low-load, 10% PDR.",
    u"result_latency_forward_pdr_50_hdrh": u"Mid-load, 50% PDR.",
    u"result_latency_reverse_pdr_50_hdrh": u"Mid-load, 50% PDR.",
    u"result_latency_forward_pdr_90_hdrh": u"High-load, 90% PDR.",
    u"result_latency_reverse_pdr_90_hdrh": u"High-load, 90% PDR."
}


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
    dut = "none" if itm["dut"] == "trex" else itm["dut"].upper()

    df = data.loc[(
        (data["dut_type"] == dut) &
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
                u"size": 5,
                u"color": color,
                u"symbol": u"circle",
            },
            text=hover,
            hoverinfo=u"text+name",
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
        hover = list()
        for idx, anomaly in enumerate(anomalies):
            if anomaly in (u"regression", u"progression"):
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
                mode=u"markers",
                text=hover,
                hoverinfo=u"text+name",
                showlegend=False,
                legendgroup=name,
                name=name,
                marker={
                    u"size": 15,
                    u"symbol": u"circle-open",
                    u"color": anomaly_color,
                    u"colorscale": _COLORSCALE_LAT \
                        if ttype == "pdr-lat" else _COLORSCALE_TPUT,
                    u"showscale": True,
                    u"line": {
                        u"width": 2
                    },
                    u"colorbar": {
                        u"y": 0.5,
                        u"len": 0.8,
                        u"title": u"Circles Marking Data Classification",
                        u"titleside": u"right",
                        u"tickmode": u"array",
                        u"tickvals": [0.167, 0.500, 0.833],
                        u"ticktext": _TICK_TEXT_LAT \
                            if ttype == "pdr-lat" else _TICK_TEXT_TPUT,
                        u"ticks": u"",
                        u"ticklen": 0,
                        u"tickangle": -90,
                        u"thickness": 10
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
            itm["testtype"], name, df, start, end, _COLORS[idx % len(_COLORS)]
        )
        if traces:
            if not fig_tput:
                fig_tput = go.Figure()
            fig_tput.add_traces(traces)

        if itm["testtype"] == "pdr":
            traces = _generate_trending_traces(
                "pdr-lat", name, df, start, end, _COLORS[idx % len(_COLORS)]
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
                f"Direction: {(u'W-E', u'E-W')[idx % 2]}<br>"
                f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                f"Latency: {item.value_iterated_to}uSec"
            )
            next_x = 100.0 / (100.0 - x_perc)
            xaxis.append(next_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{_GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
                f"Direction: {(u'W-E', u'E-W')[idx % 2]}<br>"
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
                mode=u"lines",
                legendgroup=_GRAPH_LAT_HDRH_DESC[lat_name],
                showlegend=bool(idx % 2),
                line=dict(
                    color=_COLORS[int(idx/2)],
                    dash=u"solid",
                    width=1 if idx % 2 else 2
                ),
                hovertext=hovertext,
                hoverinfo=u"text"
            )
        )
    if traces:
        fig = go.Figure()
        fig.add_traces(traces)
        layout_hdrh = layout.get("plot-hdrh-latency", None)
        if lat_hdrh:
            fig.update_layout(layout_hdrh)

    return fig
