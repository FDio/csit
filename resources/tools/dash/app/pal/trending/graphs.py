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

from ..utils.constants import Constants as C
from ..utils.utils import classify_anomalies, get_color


def _get_hdrh_latencies(row: pd.Series, name: str) -> dict:
    """Get the HDRH latencies from the test data.

    :param row: A row fron the data frame with test data.
    :param name: The test name to be displayed as the graph title.
    :type row: pandas.Series
    :type name: str
    :returns: Dictionary with HDRH latencies.
    :rtype: dict
    """

    latencies = {"name": name}
    for key in C.LAT_HDRH:
        try:
            latencies[key] = row[key]
        except KeyError:
            return None

    return latencies


def select_trending_data(data: pd.DataFrame, itm:dict) -> pd.DataFrame:
    """Select the data for graphs from the provided data frame.

    :param data: Data frame with data for graphs.
    :param itm: Item (in this case job name) which data will be selected from
        the input data frame.
    :type data: pandas.DataFrame
    :type itm: str
    :returns: A data frame with selected data.
    :rtype: pandas.DataFrame
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
    start: datetime, end: datetime, color: str, norm_factor: float) -> list:
    """Generate the trending traces for the trending graph.

    :param ttype: Test type (MRR, NDR, PDR).
    :param name: The test name to be displayed as the graph title.
    :param df: Data frame with test data.
    :param start: The date (and time) when the selected data starts.
    :param end: The date (and time) when the selected data ends.
    :param color: The color of the trace (samples and trend line).
    :param norm_factor: The factor used for normalization of the results to CPU
        frequency set to Constants.NORM_FREQUENCY.
    :type ttype: str
    :type name: str
    :type df: pandas.DataFrame
    :type start: datetime.datetime
    :type end: datetime.datetime
    :type color: str
    :type norm_factor: float
    :returns: Traces (samples, trending line, anomalies)
    :rtype: list
    """

    df = df.dropna(subset=[C.VALUE[ttype], ])
    if df.empty:
        return list()
    df = df.loc[((df["start_time"] >= start) & (df["start_time"] <= end))]
    if df.empty:
        return list()

    x_axis = df["start_time"].tolist()
    if ttype == "pdr-lat":
        y_data = [(itm / norm_factor) for itm in df[C.VALUE[ttype]].tolist()]
    else:
        y_data = [(itm * norm_factor) for itm in df[C.VALUE[ttype]].tolist()]

    anomalies, trend_avg, trend_stdev = classify_anomalies(
        {k: v for k, v in zip(x_axis, y_data)}
    )

    hover = list()
    customdata = list()
    for idx, (_, row) in enumerate(df.iterrows()):
        d_type = "trex" if row["dut_type"] == "none" else row["dut_type"]
        hover_itm = (
            f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
            f"<prop> [{row[C.UNIT[ttype]]}]: {y_data[idx]:,.0f}<br>"
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
        else:
            customdata.append({"name": name})

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
            y=y_data,
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
                anomaly_color.append(C.ANOMALY_COLOR[anomaly])
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
                    "colorscale": C.COLORSCALE_LAT \
                        if ttype == "pdr-lat" else C.COLORSCALE_TPUT,
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
                        "ticktext": C.TICK_TEXT_LAT \
                            if ttype == "pdr-lat" else C.TICK_TEXT_TPUT,
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
    start: datetime, end: datetime, normalize: bool) -> tuple:
    """Generate the trending graph(s) - MRR, NDR, PDR and for PDR also Latences
    (result_latency_forward_pdr_50_avg).

    :param data: Data frame with test results.
    :param sel: Selected tests.
    :param layout: Layout of plot.ly graph.
    :param start: The date (and time) when the selected data starts.
    :param end: The date (and time) when the selected data ends.
    :param normalize: If True, the data is normalized to CPU frquency
        Constants.NORM_FREQUENCY.
    :type data: pandas.DataFrame
    :type sel: dict
    :type layout: dict
    :type start: datetime.datetime
    :type end: datetype.datetype
    :type normalize: bool
    :returns: Trending graph(s)
    :rtype: tuple(plotly.graph_objects.Figure, plotly.graph_objects.Figure)
    """

    if not sel:
        return None, None

    fig_tput = None
    fig_lat = None
    for idx, itm in enumerate(sel):

        df = select_trending_data(data, itm)
        if df is None or df.empty:
            continue

        if normalize:
            phy = itm["phy"].split("-")
            topo_arch = f"{phy[0]}-{phy[1]}" if len(phy) == 4 else str()
            norm_factor = (C.NORM_FREQUENCY / C.FREQUENCY[topo_arch]) \
                if topo_arch else 1.0
        else:
            norm_factor = 1.0
        traces = _generate_trending_traces(itm["testtype"], itm["id"], df,
            start, end, get_color(idx), norm_factor)
        if traces:
            if not fig_tput:
                fig_tput = go.Figure()
            fig_tput.add_traces(traces)

        if itm["testtype"] == "pdr":
            traces = _generate_trending_traces("pdr-lat", itm["id"], df, start,
                end, get_color(idx), norm_factor)
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
    """Generate HDR Latency histogram graphs.

    :param data: HDRH data.
    :param layout: Layout of plot.ly graph.
    :type data: dict
    :type layout: dict
    :returns: HDR latency Histogram.
    :rtype: plotly.graph_objects.Figure
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
            x_perc = min(percentile, C.PERCENTILE_MAX)
            xaxis.append(previous_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{C.GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
                f"Direction: {('W-E', 'E-W')[idx % 2]}<br>"
                f"Percentile: {prev_perc:.5f}-{percentile:.5f}%<br>"
                f"Latency: {item.value_iterated_to}uSec"
            )
            next_x = 100.0 / (100.0 - x_perc)
            xaxis.append(next_x)
            yaxis.append(item.value_iterated_to)
            hovertext.append(
                f"<b>{C.GRAPH_LAT_HDRH_DESC[lat_name]}</b><br>"
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
                name=C.GRAPH_LAT_HDRH_DESC[lat_name],
                mode="lines",
                legendgroup=C.GRAPH_LAT_HDRH_DESC[lat_name],
                showlegend=bool(idx % 2),
                line=dict(
                    color=get_color(int(idx/2)),
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
