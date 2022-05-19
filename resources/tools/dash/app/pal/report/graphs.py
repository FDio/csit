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

import re
import plotly.graph_objects as go
import pandas as pd

import hdrh.histogram
import hdrh.codec


_COLORS = (
    u"#1A1110", u"#DA2647", u"#214FC6", u"#01786F", u"#BD8260", u"#FFD12A",
    u"#A6E7FF", u"#738276", u"#C95A49", u"#FC5A8D", u"#CEC8EF", u"#391285",
    u"#6F2DA8", u"#FF878D", u"#45A27D", u"#FFD0B9", u"#FD5240", u"#DB91EF",
    u"#44D7A8", u"#4F86F7", u"#84DE02", u"#FFCFF1", u"#614051"
)
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
REG_EX_VPP_VERSION = re.compile(r"^(\d{2}).(\d{2})-(rc0|rc1|rc2|release$)")

# def match_version(patern: str, version: str) -> bool:
#     """
#     """
#     return bool(patern in version.replace("_", "-"))


def get_short_version(version: str, dut_type: str="vpp") -> str:
    """
    """

    if dut_type in ("trex", "dpdk"):
        return version

    s_version = str()
    groups = re.search(pattern=REG_EX_VPP_VERSION, string=version)
    if groups:
        try:
            s_version = f"{groups.group(1)}.{groups.group(2)}_{groups.group(3)}"
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
        (df.dut_version.str.contains(itm["dutver"].replace("_", "-"))) &
        (df.test_id.str.contains(regex_test, regex=True))
    ]

    logging.info(df["job"].to_list())
    logging.info(df["build"].to_list())
    logging.info(df["test_type"].to_list())
    logging.info(df["dut_version"].to_list())
    logging.info(df["test_id"].to_list())
    logging.info(df["day"].to_list())
    logging.info(df["month"].to_list())

    return df


def graph_iterative(data: pd.DataFrame, sel:dict, layout: dict) -> tuple:
    """
    """

    for itm in sel:
        itm_data = select_iterative_data(data, itm)

    fig_tput = go.Figure()
    fig_tsa = go.Figure()

    return fig_tput, fig_tsa


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

    return table


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
