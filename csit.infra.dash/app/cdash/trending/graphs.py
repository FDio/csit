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

"""Implementation of graphs for trending data.
"""

import logging
import plotly.graph_objects as go
import pandas as pd

from numpy import nan

from ..utils.constants import Constants as C
from ..utils.utils import get_color, get_hdrh_latencies
from ..utils.anomalies import classify_anomalies


def select_trending_data(data: pd.DataFrame, itm: dict) -> pd.DataFrame:
    """Select the data for graphs from the provided data frame.

    :param data: Data frame with data for graphs.
    :param itm: Item (in this case job name) which data will be selected from
        the input data frame.
    :type data: pandas.DataFrame
    :type itm: dict
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

    if itm["testtype"] in ("ndr", "pdr"):
        test_type = "ndrpdr"
    elif itm["testtype"] == "mrr":
        test_type = "mrr"
    elif itm["testtype"] == "soak":
        test_type = "soak"
    elif itm["area"] == "hoststack":
        test_type = "hoststack"
    df = data.loc[(
        (data["test_type"] == test_type) &
        (data["passed"] == True)
    )]
    df = df[df.job.str.endswith(f"{topo}-{arch}")]
    core = str() if itm["dut"] == "trex" else f"{itm['core']}"
    ttype = "ndrpdr" if itm["testtype"] in ("ndr", "pdr") else itm["testtype"]
    df = df[df.test_id.str.contains(
        f"^.*[.|-]{nic}.*{itm['framesize']}-{core}-{drv}{itm['test']}-{ttype}$",
        regex=True
    )].sort_values(by="start_time", ignore_index=True)

    return df


def graph_trending(
        data: pd.DataFrame,
        sel: dict,
        layout: dict,
        normalize: bool=False,
        trials: bool=False
    ) -> tuple:
    """Generate the trending graph(s) - MRR, NDR, PDR and for PDR also Latences
    (result_latency_forward_pdr_50_avg).

    :param data: Data frame with test results.
    :param sel: Selected tests.
    :param layout: Layout of plot.ly graph.
    :param normalize: If True, the data is normalized to CPU frquency
        Constants.NORM_FREQUENCY.
    :param trials: If True, MRR trials are displayed in the trending graph.
    :type data: pandas.DataFrame
    :type sel: dict
    :type layout: dict
    :type normalize: bool
    :type: trials: bool
    :returns: Trending graph(s)
    :rtype: tuple(plotly.graph_objects.Figure, plotly.graph_objects.Figure)
    """

    if not sel:
        return None, None


    def _generate_trending_traces(
            ttype: str,
            name: str,
            df: pd.DataFrame,
            color: str,
            nf: float
        ) -> list:
        """Generate the trending traces for the trending graph.

        :param ttype: Test type (MRR, NDR, PDR).
        :param name: The test name to be displayed as the graph title.
        :param df: Data frame with test data.
        :param color: The color of the trace (samples and trend line).
        :param nf: The factor used for normalization of the results to
            CPU frequency set to Constants.NORM_FREQUENCY.
        :type ttype: str
        :type name: str
        :type df: pandas.DataFrame
        :type color: str
        :type nf: float
        :returns: Traces (samples, trending line, anomalies)
        :rtype: list
        """

        df = df.dropna(subset=[C.VALUE[ttype], ])
        if df.empty:
            return list(), list()

        hover = list()
        customdata = list()
        customdata_samples = list()
        name_lst = name.split("-")
        for _, row in df.iterrows():
            h_tput, h_band, h_lat = str(), str(), str()
            if ttype in ("mrr", "mrr-bandwidth"):
                h_tput = (
                    f"tput avg [{row['result_receive_rate_rate_unit']}]: "
                    f"{row['result_receive_rate_rate_avg'] * nf:,.0f}<br>"
                    f"tput stdev [{row['result_receive_rate_rate_unit']}]: "
                    f"{row['result_receive_rate_rate_stdev'] * nf:,.0f}<br>"
                )
                if pd.notna(row["result_receive_rate_bandwidth_avg"]):
                    h_band = (
                        f"bandwidth avg "
                        f"[{row['result_receive_rate_bandwidth_unit']}]: "
                        f"{row['result_receive_rate_bandwidth_avg'] * nf:,.0f}"
                        "<br>"
                        f"bandwidth stdev "
                        f"[{row['result_receive_rate_bandwidth_unit']}]: "
                        f"{row['result_receive_rate_bandwidth_stdev']* nf:,.0f}"
                        "<br>"
                    )
            elif ttype in ("ndr", "ndr-bandwidth"):
                h_tput = (
                    f"tput [{row['result_ndr_lower_rate_unit']}]: "
                    f"{row['result_ndr_lower_rate_value'] * nf:,.0f}<br>"
                )
                if pd.notna(row["result_ndr_lower_bandwidth_value"]):
                    h_band = (
                        f"bandwidth [{row['result_ndr_lower_bandwidth_unit']}]:"
                        f" {row['result_ndr_lower_bandwidth_value'] * nf:,.0f}"
                        "<br>"
                    )
            elif ttype in ("pdr", "pdr-bandwidth", "latency"):
                h_tput = (
                    f"tput [{row['result_pdr_lower_rate_unit']}]: "
                    f"{row['result_pdr_lower_rate_value'] * nf:,.0f}<br>"
                )
                if pd.notna(row["result_pdr_lower_bandwidth_value"]):
                    h_band = (
                        f"bandwidth [{row['result_pdr_lower_bandwidth_unit']}]:"
                        f" {row['result_pdr_lower_bandwidth_value'] * nf:,.0f}"
                        "<br>"
                    )
                if pd.notna(row["result_latency_forward_pdr_50_avg"]):
                    h_lat = (
                        f"latency "
                        f"[{row['result_latency_forward_pdr_50_unit']}]: "
                        f"{row['result_latency_forward_pdr_50_avg'] / nf:,.0f}"
                        "<br>"
                    )
            elif ttype in ("hoststack-cps", "hoststack-rps",
                           "hoststack-cps-bandwidth",
                           "hoststack-rps-bandwidth", "hoststack-latency"):
                h_tput = (
                    f"tput [{row['result_rate_unit']}]: "
                    f"{row['result_rate_value'] * nf:,.0f}<br>"
                )
                h_band = (
                    f"bandwidth [{row['result_bandwidth_unit']}]: "
                    f"{row['result_bandwidth_value'] * nf:,.0f}<br>"
                )
                h_lat = (
                    f"latency [{row['result_latency_unit']}]: "
                    f"{row['result_latency_value'] / nf:,.0f}<br>"
                )
            elif ttype in ("hoststack-bps", ):
                h_band = (
                    f"bandwidth [{row['result_bandwidth_unit']}]: "
                    f"{row['result_bandwidth_value'] * nf:,.0f}<br>"
                )
            elif ttype in ("soak", "soak-bandwidth"):
                h_tput = (
                    f"tput [{row['result_critical_rate_lower_rate_unit']}]: "
                    f"{row['result_critical_rate_lower_rate_value'] * nf:,.0f}"
                    "<br>"
                )
                if pd.notna(row["result_critical_rate_lower_bandwidth_value"]):
                    bv = row['result_critical_rate_lower_bandwidth_value']
                    h_band = (
                        "bandwidth "
                        f"[{row['result_critical_rate_lower_bandwidth_unit']}]:"
                        f" {bv * nf:,.0f}"
                        "<br>"
                    )
            try:
                hosts = f"<br>hosts: {', '.join(row['hosts'])}"
            except (KeyError, TypeError):
                hosts = str()
            hover_itm = (
                f"dut: {name_lst[0]}<br>"
                f"infra: {'-'.join(name_lst[1:5])}<br>"
                f"test: {'-'.join(name_lst[5:])}<br>"
                f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"{h_tput}{h_band}{h_lat}"
                f"{row['dut_type']}-ref: {row['dut_version']}<br>"
                f"csit-ref: {row['job']}/{row['build']}"
                f"{hosts}"
            )
            hover.append(hover_itm)
            if ttype == "latency":
                customdata_samples.append(get_hdrh_latencies(row, name))
                customdata.append({"name": name})
            else:
                customdata_samples.append(
                    {"name": name, "show_telemetry": True}
                )
                customdata.append({"name": name})

        x_axis = df["start_time"].tolist()
        if "latency" in ttype:
            y_data = [(v / nf) for v in df[C.VALUE[ttype]].tolist()]
        else:
            y_data = [(v * nf) for v in df[C.VALUE[ttype]].tolist()]
        units = df[C.UNIT[ttype]].unique().tolist()

        try:
            anomalies, trend_avg, trend_stdev = classify_anomalies(
                {k: v for k, v in zip(x_axis, y_data)}
            )
        except ValueError as err:
            logging.error(err)
            return list(), list()

        hover_trend = list()
        for avg, stdev, (_, row) in zip(trend_avg, trend_stdev, df.iterrows()):
            try:
                hosts = f"<br>hosts: {', '.join(row['hosts'])}"
            except (KeyError, TypeError):
                hosts = str()
            hover_itm = (
                f"dut: {name_lst[0]}<br>"
                f"infra: {'-'.join(name_lst[1:5])}<br>"
                f"test: {'-'.join(name_lst[5:])}<br>"
                f"date: {row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                f"trend [{row[C.UNIT[ttype]]}]: {avg:,.0f}<br>"
                f"stdev [{row[C.UNIT[ttype]]}]: {stdev:,.0f}<br>"
                f"{row['dut_type']}-ref: {row['dut_version']}<br>"
                f"csit-ref: {row['job']}/{row['build']}"
                f"{hosts}"
            )
            if ttype == "latency":
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
                    "symbol": "circle"
                },
                text=hover,
                hoverinfo="text",
                showlegend=True,
                legendgroup=name,
                customdata=customdata_samples
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
                hoverinfo="text",
                showlegend=False,
                legendgroup=name,
                customdata=customdata
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
                        f"dut: {name_lst[0]}<br>"
                        f"infra: {'-'.join(name_lst[1:5])}<br>"
                        f"test: {'-'.join(name_lst[5:])}<br>"
                        f"date: {x_axis[idx].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                        f"trend [pps]: {trend_avg[idx]:,.0f}<br>"
                        f"classification: {anomaly}"
                    )
                    if ttype == "latency":
                        hover_itm = hover_itm.replace("[pps]", "[us]")
                    hover.append(hover_itm)
            anomaly_color.extend([0.0, 0.5, 1.0])
            traces.append(
                go.Scatter(
                    x=anomaly_x,
                    y=anomaly_y,
                    mode="markers",
                    text=hover,
                    hoverinfo="text",
                    showlegend=False,
                    legendgroup=name,
                    name=name,
                    customdata=customdata,
                    marker={
                        "size": 15,
                        "symbol": "circle-open",
                        "color": anomaly_color,
                        "colorscale": C.COLORSCALE_LAT \
                            if ttype == "latency" else C.COLORSCALE_TPUT,
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
                                if ttype == "latency" else C.TICK_TEXT_TPUT,
                            "ticks": "",
                            "ticklen": 0,
                            "tickangle": -90,
                            "thickness": 10
                        }
                    }
                )
            )

        return traces, units


    def _add_mrr_trials_traces(
            ttype: str,
            name: str,
            df: pd.DataFrame,
            color: str,
            nf: float
        ) -> list:
        """Add the traces with mrr trials.

        :param ttype: Test type (mrr, mrr-bandwidth).
        :param name: The test name to be displayed in hover.
        :param df: Data frame with test data.
        :param color: The color of the trace.
        :param nf: The factor used for normalization of the results to
            CPU frequency set to Constants.NORM_FREQUENCY.
        :type ttype: str
        :type name: str
        :type df: pandas.DataFrame
        :type color: str
        :type nf: float
        :returns: list of Traces
        :rtype: list
        """
        traces = list()
        x_axis = df["start_time"].tolist()
        y_data = df[C.VALUE[ttype].replace("avg", "values")].tolist()

        for idx_trial in range(10):
            y_axis = list()
            for idx_run in range(len(x_axis)):
                try:
                    y_axis.append(y_data[idx_run][idx_trial] * nf)
                except IndexError:
                    y_axis.append(nan)
            traces.append(go.Scatter(
                x=x_axis,
                y=y_axis,
                name=name,
                mode="markers",
                marker={
                    "size": 2,
                    "color": color,
                    "symbol": "circle"
                },
                showlegend=True,
                legendgroup=name
            ))
        return traces


    fig_tput = None
    fig_lat = None
    fig_band = None
    y_units = set()
    for idx, itm in enumerate(sel):
        df = select_trending_data(data, itm)
        if df is None or df.empty:
            continue

        if normalize:
            phy = itm["phy"].split("-")
            topo_arch = f"{phy[0]}-{phy[1]}" if len(phy) == 4 else str()
            norm_factor = (C.NORM_FREQUENCY / C.FREQUENCY.get(topo_arch, 1.0)) \
                if topo_arch else 1.0
        else:
            norm_factor = 1.0

        if itm["area"] == "hoststack":
            ttype = f"hoststack-{itm['testtype']}"
        else:
            ttype = itm["testtype"]

        traces, units = _generate_trending_traces(
            ttype,
            itm["id"],
            df,
            get_color(idx),
            norm_factor
        )
        if traces:
            if not fig_tput:
                fig_tput = go.Figure()
            if trials and "mrr" in ttype:
                traces.extend(_add_mrr_trials_traces(
                    ttype,
                    itm["id"],
                    df,
                    get_color(idx),
                    norm_factor
                ))
            fig_tput.add_traces(traces)

        if ttype in C.TESTS_WITH_BANDWIDTH:
            traces, _ = _generate_trending_traces(
                f"{ttype}-bandwidth",
                itm["id"],
                df,
                get_color(idx),
                norm_factor
            )
            if traces:
                if not fig_band:
                    fig_band = go.Figure()
                if trials and "mrr" in ttype:
                    traces.extend(_add_mrr_trials_traces(
                        f"{ttype}-bandwidth",
                        itm["id"],
                        df,
                        get_color(idx),
                        norm_factor
                    ))
                fig_band.add_traces(traces)

        if ttype in C.TESTS_WITH_LATENCY:
            traces, _ = _generate_trending_traces(
                "latency" if ttype == "pdr" else "hoststack-latency",
                itm["id"],
                df,
                get_color(idx),
                norm_factor
            )
            if traces:
                if not fig_lat:
                    fig_lat = go.Figure()
                fig_lat.add_traces(traces)

        y_units.update(units)

    if fig_tput:
        fig_layout = layout.get("plot-trending-tput", dict())
        fig_layout["yaxis"]["title"] = \
            f"Throughput [{'|'.join(sorted(y_units))}]"
        fig_tput.update_layout(fig_layout)
    if fig_band:
        fig_band.update_layout(layout.get("plot-trending-bandwidth", dict()))
    if fig_lat:
        fig_lat.update_layout(layout.get("plot-trending-lat", dict()))

    return fig_tput, fig_band, fig_lat


def graph_tm_trending(
        data: pd.DataFrame,
        layout: dict,
        all_in_one: bool=False
    ) -> list:
    """Generates one trending graph per test, each graph includes all selected
    metrics.

    :param data: Data frame with telemetry data.
    :param layout: Layout of plot.ly graph.
    :param all_in_one: If True, all telemetry traces are placed in one graph,
        otherwise they are split to separate graphs grouped by test ID.
    :type data: pandas.DataFrame
    :type layout: dict
    :type all_in_one: bool
    :returns: List of generated graphs together with test names.
        list(tuple(plotly.graph_objects.Figure(), str()), tuple(...), ...)
    :rtype: list
    """

    if data.empty:
        return list()

    def _generate_traces(
            data: pd.DataFrame,
            test: str,
            all_in_one: bool,
            color_index: int
        ) -> list:
        """Generates a trending graph for given test with all metrics.

        :param data: Data frame with telemetry data for the given test.
        :param test: The name of the test.
        :param all_in_one: If True, all telemetry traces are placed in one
            graph, otherwise they are split to separate graphs grouped by
            test ID.
        :param color_index: The index of the test used if all_in_one is True.
        :type data: pandas.DataFrame
        :type test: str
        :type all_in_one: bool
        :type color_index: int
        :returns: List of traces.
        :rtype: list
        """
        traces = list()
        metrics = data.tm_metric.unique().tolist()
        for idx, metric in enumerate(metrics):
            if "-pdr" in test and "='pdr'" not in metric:
                continue
            if "-ndr" in test and "='ndr'" not in metric:
                continue

            df = data.loc[(data["tm_metric"] == metric)]
            x_axis = df["start_time"].tolist()
            y_data = [float(itm) for itm in df["tm_value"].tolist()]
            hover = list()
            for i, (_, row) in enumerate(df.iterrows()):
                if row["test_type"] == "mrr":
                    rate = (
                        f"mrr avg [{row[C.UNIT['mrr']]}]: "
                        f"{row[C.VALUE['mrr']]:,.0f}<br>"
                        f"mrr stdev [{row[C.UNIT['mrr']]}]: "
                        f"{row['result_receive_rate_rate_stdev']:,.0f}<br>"
                    )
                elif row["test_type"] == "ndrpdr":
                    if "-pdr" in test:
                        rate = (
                            f"pdr [{row[C.UNIT['pdr']]}]: "
                            f"{row[C.VALUE['pdr']]:,.0f}<br>"
                        )
                    elif "-ndr" in test:
                        rate = (
                            f"ndr [{row[C.UNIT['ndr']]}]: "
                            f"{row[C.VALUE['ndr']]:,.0f}<br>"
                        )
                    else:
                        rate = str()
                else:
                    rate = str()
                hover.append(
                    f"date: "
                    f"{row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                    f"value: {y_data[i]:,.2f}<br>"
                    f"{rate}"
                    f"{row['dut_type']}-ref: {row['dut_version']}<br>"
                    f"csit-ref: {row['job']}/{row['build']}<br>"
                )
            if any(y_data):
                anomalies, trend_avg, trend_stdev = classify_anomalies(
                    {k: v for k, v in zip(x_axis, y_data)}
                )
                hover_trend = list()
                for avg, stdev, (_, row) in \
                        zip(trend_avg, trend_stdev, df.iterrows()):
                    hover_trend.append(
                        f"date: "
                        f"{row['start_time'].strftime('%Y-%m-%d %H:%M:%S')}<br>"
                        f"trend: {avg:,.2f}<br>"
                        f"stdev: {stdev:,.2f}<br>"
                        f"{row['dut_type']}-ref: {row['dut_version']}<br>"
                        f"csit-ref: {row['job']}/{row['build']}"
                    )
            else:
                anomalies = None
            if all_in_one:
                color = get_color(color_index * len(metrics) + idx)
                metric_name = f"{test}<br>{metric}"
            else:
                color = get_color(idx)
                metric_name = metric

            traces.append(
                go.Scatter(  # Samples
                    x=x_axis,
                    y=y_data,
                    name=metric_name,
                    mode="markers",
                    marker={
                        "size": 5,
                        "color": color,
                        "symbol": "circle",
                    },
                    text=hover,
                    hoverinfo="text+name",
                    showlegend=True,
                    legendgroup=metric_name
                )
            )
            if anomalies:
                traces.append(
                    go.Scatter(  # Trend line
                        x=x_axis,
                        y=trend_avg,
                        name=metric_name,
                        mode="lines",
                        line={
                            "shape": "linear",
                            "width": 1,
                            "color": color,
                        },
                        text=hover_trend,
                        hoverinfo="text+name",
                        showlegend=False,
                        legendgroup=metric_name
                    )
                )

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
                            f"date: {x_axis[idx].strftime('%Y-%m-%d %H:%M:%S')}"
                            f"<br>trend: {trend_avg[idx]:,.2f}"
                            f"<br>classification: {anomaly}"
                        )
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
                        legendgroup=metric_name,
                        name=metric_name,
                        marker={
                            "size": 15,
                            "symbol": "circle-open",
                            "color": anomaly_color,
                            "colorscale": C.COLORSCALE_TPUT,
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
                                "ticktext": C.TICK_TEXT_TPUT,
                                "ticks": "",
                                "ticklen": 0,
                                "tickangle": -90,
                                "thickness": 10
                            }
                        }
                    )
                )

        unique_metrics = set()
        for itm in metrics:
            unique_metrics.add(itm.split("{", 1)[0])
        return traces, unique_metrics

    tm_trending_graphs = list()
    graph_layout = layout.get("plot-trending-telemetry", dict())

    if all_in_one:
        all_traces = list()

    all_metrics = set()
    all_tests = list()
    for idx, test in enumerate(data.test_name.unique()):
        df = data.loc[(data["test_name"] == test)]
        traces, metrics = _generate_traces(df, test, all_in_one, idx)
        if traces:
            all_metrics.update(metrics)
            if all_in_one:
                all_traces.extend(traces)
                all_tests.append(test)
            else:
                graph = go.Figure()
                graph.add_traces(traces)
                graph.update_layout(graph_layout)
                tm_trending_graphs.append((graph, [test, ], ))

    if all_in_one:
        graph = go.Figure()
        graph.add_traces(all_traces)
        graph.update_layout(graph_layout)
        tm_trending_graphs.append((graph, all_tests, ))

    return tm_trending_graphs, list(all_metrics)
