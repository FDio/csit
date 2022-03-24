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

from dash import no_update


def trending_tput(data: pd.DataFrame, sel:dict, layout: dict, start: datetime,
    end: datetime):
    """
    """

    if not sel:
        return no_update, no_update

    def _generate_trace(ttype: str, name: str, df: pd.DataFrame,
        start: datetime, end: datetime):

        value = {
            "mrr": "result_receive_rate_rate_avg",
            "ndr": "result_ndr_lower_rate_value",
            "pdr": "result_pdr_lower_rate_value"
        }
        unit = {
            "mrr": "result_receive_rate_rate_unit",
            "ndr": "result_ndr_lower_rate_unit",
            "pdr": "result_pdr_lower_rate_unit"
        }

        x_axis = [
            d for d in df["start_time"] if d >= start and d <= end
        ]
        hover_txt = list()
        for _, row in df.iterrows():
            hover_itm = (
                f"date: "
                f"{row['start_time'].strftime('%d-%m-%Y %H:%M:%S')}<br>"
                f"average [{row[unit[ttype]]}]: "
                f"{int(row[value[ttype]]):,}<br>"
                f"{row['dut_type']}-ref: {row['dut_version']}<br>"
                f"csit-ref: {row['job']}/{row['build']}"
            )
            if ttype == "mrr":
                stdev = (
                    f"stdev [{row['result_receive_rate_rate_unit']}]: "
                    f"{int(row['result_receive_rate_rate_stdev']):,}<br>"
                )
            else:
                stdev = ""
            hover_itm = hover_itm.replace("<stdev>", stdev)
            hover_txt.append(hover_itm)

        return go.Scatter(
            x=x_axis,
            y=df[value[ttype]],
            name=name,
            mode="markers+lines",
            text=hover_txt,
            hoverinfo=u"text+name"
        )

    # Generate graph:
    fig = go.Figure()
    for itm in sel:
        phy = itm["phy"].split("-")
        if len(phy) == 4:
            topo, arch, nic, drv = phy
            if drv in ("dpdk", "ixgbe"):
                drv = ""
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
            f".*{nic}.*{itm['framesize']}.*{itm['core']}.*"
            f"{drv}.*{itm['test']}"
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
        fig.add_trace(_generate_trace(itm['testtype'], name, df, start, end))

        logging.info(f"sel_topo_arch: {sel_topo_arch}")
        logging.info(f"regex: {regex}")
        logging.info(f"name: {name}")

    style={
        "vertical-align": "top",
        "display": "inline-block",
        "width": "80%",
        "padding": "5px"
    }

    layout = layout.get("plot-trending", dict())
    fig.update_layout(layout)

    return fig, style
