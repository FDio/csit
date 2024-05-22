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

"""Implementation of graphs for iterative data.
"""

import plotly.graph_objects as go
import pandas as pd

from copy import deepcopy
from numpy import percentile

from ..utils.constants import Constants as C
from ..utils.utils import get_color, get_hdrh_latencies


def select_iterative_data(data: pd.DataFrame, itm:dict) -> pd.DataFrame:
    """Select the data for graphs and tables from the provided data frame.

    :param data: Data frame with data for graphs and tables.
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

    if itm["testtype"] in ("ndr", "pdr"):
        test_type = "ndrpdr"
    elif itm["testtype"] == "mrr":
        test_type = "mrr"
    elif itm["testtype"] == "soak":
        test_type = "soak"
    elif itm["area"] == "hoststack":
        test_type = "hoststack"
    df = data.loc[(
        (data["release"] == itm["rls"]) &
        (data["test_type"] == test_type) &
        (data["passed"] == True)
    )]

    core = str() if itm["dut"] == "trex" else f"{itm['core']}"
    ttype = "ndrpdr" if itm["testtype"] in ("ndr", "pdr") else itm["testtype"]
    regex_test = \
        f"^.*[.|-]{nic}.*{itm['framesize']}-{core}-{drv}{itm['test']}-{ttype}$"
    df = df[
        (df.job.str.endswith(f"{topo}-{arch}")) &
        (df.dut_version.str.contains(itm["dutver"].replace(".r", "-r").\
            replace("rls", "release"))) &
        (df.test_id.str.contains(regex_test, regex=True))
    ]

    return df


def graph_iterative(data: pd.DataFrame, sel: list, layout: dict,
        normalize: bool=False, remove_outliers: bool=False) -> tuple:
    """Generate the statistical box graph with iterative data (MRR, NDR and PDR,
    for PDR also Latencies).

    :param data: Data frame with iterative data.
    :param sel: Selected tests.
    :param layout: Layout of plot.ly graph.
    :param normalize: If True, the data is normalized to CPU frequency
        Constants.NORM_FREQUENCY.
    :param remove_outliers: If True the outliers are removed before
        generating the table.
    :type data: pandas.DataFrame
    :type sel: list
    :type layout: dict
    :type normalize: bool
    :type remove_outliers: bool
    :returns: Tuple of graphs - throughput and latency.
    :rtype: tuple(plotly.graph_objects.Figure, plotly.graph_objects.Figure)
    """

    def get_y_values(data, y_data_max, param, norm_factor, release=str(),
                     remove_outliers=False):
        if param == "result_receive_rate_rate_values":
            if release in ("rls2402", "rls2406", "rls2410"):
                y_vals_raw = data["result_receive_rate_rate_avg"].to_list()
            else:
                y_vals_raw = data[param].to_list()[0]
        else:
            y_vals_raw = data[param].to_list()
        y_data = [(y * norm_factor) for y in y_vals_raw]

        if remove_outliers:
            try:
                q1 = percentile(y_data, 25, method=C.COMP_PERCENTILE_METHOD)
                q3 = percentile(y_data, 75, method=C.COMP_PERCENTILE_METHOD)
                irq = q3 - q1
                lif = q1 - C.COMP_OUTLIER_TYPE * irq
                uif = q3 + C.COMP_OUTLIER_TYPE * irq
                y_data = [i for i in y_data if i >= lif and i <= uif]
            except TypeError:
                pass
        try:
            y_data_max = max(max(y_data), y_data_max)
        except TypeError:
            y_data_max = 0
        return y_data, y_data_max

    fig_tput = None
    fig_band = None
    fig_lat = None

    tput_traces = list()
    y_tput_max = 0
    y_units = set()

    lat_traces = list()
    y_lat_max = 0
    x_lat = list()

    band_traces = list()
    y_band_max = 0
    y_band_units = set()
    x_band = list()

    for idx, itm in enumerate(sel):

        itm_data = select_iterative_data(data, itm)
        if itm_data.empty:
            continue

        phy = itm["phy"].split("-")
        topo_arch = f"{phy[0]}-{phy[1]}" if len(phy) == 4 else str()
        norm_factor = (C.NORM_FREQUENCY / C.FREQUENCY[topo_arch]) \
            if normalize else 1.0

        if itm["area"] == "hoststack":
            ttype = f"hoststack-{itm['testtype']}"
        else:
            ttype = itm["testtype"]

        y_units.update(itm_data[C.UNIT[ttype]].unique().tolist())

        y_data, y_tput_max = get_y_values(
            itm_data,
            y_tput_max,
            C.VALUE_ITER[ttype],
            norm_factor,
            itm["rls"],
            remove_outliers
        )

        nr_of_samples = len(y_data)

        customdata = list()
        metadata = {
            "csit release": itm["rls"],
            "dut": itm["dut"],
            "dut version": itm["dutver"],
            "infra": itm["phy"],
            "test": (
                f"{itm['area']}-{itm['framesize']}-{itm['core']}-"
                f"{itm['test']}-{itm['testtype']}"
            )
        }

        if itm["testtype"] == "mrr" and itm["rls"] == "rls2310":
            trial_run = "trial"
            metadata["csit-ref"] = (
                f"{itm_data['job'].to_list()[0]}/",
                f"{itm_data['build'].to_list()[0]}"
            )
            customdata = [{"metadata": metadata}, ] * nr_of_samples
        else:
            trial_run = "run"
            for _, row in itm_data.iterrows():
                metadata["csit-ref"] = f"{row['job']}/{row['build']}"
                try:
                    metadata["hosts"] = ", ".join(row["hosts"])
                except (KeyError, TypeError):
                    pass
                customdata.append({"metadata": deepcopy(metadata)})
        tput_kwargs = dict(
            y=y_data,
            name=(
                f"{idx + 1}. "
                f"({nr_of_samples:02d} "
                f"{trial_run}{'s' if nr_of_samples > 1 else ''}) "
                f"{itm['id']}"
            ),
            hoverinfo=u"y+name",
            boxpoints="all",
            jitter=0.3,
            marker=dict(color=get_color(idx)),
            customdata=customdata
        )
        tput_traces.append(go.Box(**tput_kwargs))

        if ttype in C.TESTS_WITH_BANDWIDTH:
            y_band, y_band_max = get_y_values(
                itm_data,
                y_band_max,
                C.VALUE_ITER[f"{ttype}-bandwidth"],
                norm_factor,
                remove_outliers=remove_outliers
            )
            if not all(pd.isna(y_band)):
                y_band_units.update(
                    itm_data[C.UNIT[f"{ttype}-bandwidth"]].unique().\
                        dropna().tolist()
                )
                band_kwargs = dict(
                    y=y_band,
                    name=(
                        f"{idx + 1}. "
                        f"({nr_of_samples:02d} "
                        f"run{'s' if nr_of_samples > 1 else ''}) "
                        f"{itm['id']}"
                    ),
                    hoverinfo=u"y+name",
                    boxpoints="all",
                    jitter=0.3,
                    marker=dict(color=get_color(idx)),
                    customdata=customdata
                )
                x_band.append(idx + 1)
                band_traces.append(go.Box(**band_kwargs))

        if ttype in C.TESTS_WITH_LATENCY:
            y_lat, y_lat_max = get_y_values(
                itm_data,
                y_lat_max,
                C.VALUE_ITER["latency"],
                1 / norm_factor,
                remove_outliers=remove_outliers
            )
            if not all(pd.isna(y_lat)):
                customdata = list()
                for _, row in itm_data.iterrows():
                    hdrh = get_hdrh_latencies(
                        row,
                        f"{metadata['infra']}-{metadata['test']}"
                    )
                    metadata["csit-ref"] = f"{row['job']}/{row['build']}"
                    customdata.append({
                        "metadata": deepcopy(metadata),
                        "hdrh": hdrh
                    })
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
                    marker=dict(color=get_color(idx)),
                    customdata=customdata
                )
                x_lat.append(idx + 1)
                lat_traces.append(go.Box(**lat_kwargs))

    if tput_traces:
        pl_tput = deepcopy(layout["plot-throughput"])
        pl_tput["xaxis"]["tickvals"] = [i for i in range(len(sel))]
        pl_tput["xaxis"]["ticktext"] = [str(i + 1) for i in range(len(sel))]
        pl_tput["yaxis"]["title"] = f"Throughput [{'|'.join(sorted(y_units))}]"
        if y_tput_max:
            pl_tput["yaxis"]["range"] = [0, int(y_tput_max) * 1.1]
        fig_tput = go.Figure(data=tput_traces, layout=pl_tput)

    if band_traces:
        pl_band = deepcopy(layout["plot-bandwidth"])
        pl_band["xaxis"]["tickvals"] = [i for i in range(len(x_band))]
        pl_band["xaxis"]["ticktext"] = x_band
        pl_band["yaxis"]["title"] = \
            f"Bandwidth [{'|'.join(sorted(y_band_units))}]"
        if y_band_max:
            pl_band["yaxis"]["range"] = [0, int(y_band_max) * 1.1]
        fig_band = go.Figure(data=band_traces, layout=pl_band)

    if lat_traces:
        pl_lat = deepcopy(layout["plot-latency"])
        pl_lat["xaxis"]["tickvals"] = [i for i in range(len(x_lat))]
        pl_lat["xaxis"]["ticktext"] = x_lat
        if y_lat_max:
            pl_lat["yaxis"]["range"] = [0, int(y_lat_max) + 5]
        fig_lat = go.Figure(data=lat_traces, layout=pl_lat)

    return fig_tput, fig_band, fig_lat
