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

import re
import plotly.graph_objects as go
import pandas as pd

from copy import deepcopy

import hdrh.histogram
import hdrh.codec


_VALUE = {
    "mrr": "result_receive_rate_rate_values",
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


def get_short_version(version: str, dut_type: str="vpp") -> str:
    """
    """

    if dut_type in ("trex", "dpdk"):
        return version

    s_version = str()
    groups = re.search(
        pattern=re.compile(r"^(\d{2}).(\d{2})-(rc0|rc1|rc2|release$)"),
        string=version
    )
    if groups:
        try:
            s_version = \
                f"{groups.group(1)}.{groups.group(2)}.{groups.group(3)}".\
                    replace("release", "rls")
        except IndexError:
            pass

    return s_version


def select_iterative_data(data: pd.DataFrame, itm:dict) -> pd.DataFrame:
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
        (data["release"] == itm["rls"]) &
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
    regex_test = \
        f"^.*[.|-]{nic}.*{itm['framesize']}-{core}-{drv}{itm['test']}-{ttype}$"
    df = df[
        (df.job.str.endswith(f"{topo}-{arch}")) &
        (df.dut_version.str.contains(itm["dutver"].replace(".r", "-r").\
            replace("rls", "release"))) &
        (df.test_id.str.contains(regex_test, regex=True))
    ]

    return df


def graph_iterative(data: pd.DataFrame, sel:dict, layout: dict) -> tuple:
    """
    """

    fig_tput = None
    fig_lat = None

    tput_traces = list()
    y_tput_max = 0
    lat_traces = list()
    y_lat_max = 0
    x_lat = list()
    show_latency = False
    show_tput = False
    for idx, itm in enumerate(sel):
        itm_data = select_iterative_data(data, itm)
        if itm_data.empty:
            continue
        if itm["testtype"] == "mrr":
            y_data = itm_data[_VALUE[itm["testtype"]]].to_list()[0]
            if y_data.size > 0:
                y_tput_max = \
                    max(y_data) if max(y_data) > y_tput_max else y_tput_max
        else:
            y_data = itm_data[_VALUE[itm["testtype"]]].to_list()
            if y_data:
                y_tput_max = \
                    max(y_data) if max(y_data) > y_tput_max else y_tput_max
        nr_of_samples = len(y_data)
        tput_kwargs = dict(
            y=y_data,
            name=(
                f"{idx + 1}. "
                f"({nr_of_samples:02d} "
                f"run{'s' if nr_of_samples > 1 else ''}) "
                f"{itm['id']}"
            ),
            hoverinfo=u"y+name",
            boxpoints="all",
            jitter=0.3,
            marker=dict(color=_get_color(idx))
        )
        tput_traces.append(go.Box(**tput_kwargs))
        show_tput = True

        if itm["testtype"] == "pdr":
            y_lat = itm_data[_VALUE["pdr-lat"]].to_list()
            if y_lat:
                y_lat_max = max(y_lat) if max(y_lat) > y_lat_max else y_lat_max
            nr_of_samples = len(y_lat)
            lat_kwargs = dict(
                y=y_lat,
                name=(
                    f"{idx + 1}. "
                    f"({nr_of_samples:02d} "
                    f"run{u's' if nr_of_samples > 1 else u''}) "
                    f"{itm['id']}"
                ),
                hoverinfo="all",
                boxpoints="all",
                jitter=0.3,
            )
            x_lat.append(idx + 1)
            lat_traces.append(go.Box(**lat_kwargs))
            show_latency = True
        else:
            lat_traces.append(go.Box())

    if show_tput:
        pl_tput = deepcopy(layout["plot-throughput"])
        pl_tput["xaxis"]["tickvals"] = [i for i in range(len(sel))]
        pl_tput["xaxis"]["ticktext"] = [str(i + 1) for i in range(len(sel))]
        if y_tput_max:
            pl_tput["yaxis"]["range"] = [0, (int(y_tput_max / 1e6) + 1) * 1e6]
        fig_tput = go.Figure(data=tput_traces, layout=pl_tput)

    if show_latency:
        pl_lat = deepcopy(layout["plot-latency"])
        pl_lat["xaxis"]["tickvals"] = [i for i in range(len(x_lat))]
        pl_lat["xaxis"]["ticktext"] = x_lat
        if y_lat_max:
            pl_lat["yaxis"]["range"] = [0, (int(y_lat_max / 10) + 1) * 10]
        fig_lat = go.Figure(data=lat_traces, layout=pl_lat)

    return fig_tput, fig_lat


def table_comparison(data: pd.DataFrame, sel:dict) -> pd.DataFrame:
    """
    """
    table = pd.DataFrame(
        {
            "Test Case": [
                "64b-2t1c-avf-eth-l2xcbase-eth-2memif-1dcr",
                "64b-2t1c-avf-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc",
                "64b-2t1c-avf-ethip4udp-ip4base-iacl50sl-10kflows",
                "78b-2t1c-avf-ethip6-ip6scale2m-rnd "],
            "2106.0-8": [
                "14.45 +- 0.08",
                "9.63 +- 0.05",
                "9.7 +- 0.02",
                "8.95 +- 0.06"],
            "2110.0-8": [
                "14.45 +- 0.08",
                "9.63 +- 0.05",
                "9.7 +- 0.02",
                "8.95 +- 0.06"],
            "2110.0-9": [
                "14.45 +- 0.08",
                "9.63 +- 0.05",
                "9.7 +- 0.02",
                "8.95 +- 0.06"],
            "2202.0-9": [
                "14.45 +- 0.08",
                "9.63 +- 0.05",
                "9.7 +- 0.02",
                "8.95 +- 0.06"],
            "2110.0-9 vs 2110.0-8": [
                "-0.23 +-  0.62",
                "-1.37 +-   1.3",
                "+0.08 +-   0.2",
                "-2.16 +-  0.83"],
            "2202.0-9 vs 2110.0-9": [
                "+6.95 +-  0.72",
                "+5.35 +-  1.26",
                "+4.48 +-  1.48",
                "+4.09 +-  0.95"]
        }
    )

    return pd.DataFrame()  #table


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
