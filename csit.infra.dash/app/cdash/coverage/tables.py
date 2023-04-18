# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""The coverage data tables.
"""

import hdrh.histogram
import hdrh.codec
import pandas as pd
import dash_bootstrap_components as dbc

from dash import dash_table
from dash.dash_table.Format import Format, Scheme

from ..utils.constants import Constants as C


def select_coverage_data(
        data: pd.DataFrame,
        selected: dict,
        csv: bool=False
    ) -> list:
    """Select coverage data for the tables and generate tables as pandas data
    frames.

    :param data: Coverage data.
    :param selected: Dictionary with user selection.
    :param csv: If True, pandas data frame with selected coverage data is
        returned for "Download Data" feature.
    :type data: pandas.DataFrame
    :type selected: dict
    :type csv: bool
    :returns: List of tuples with suite name (str) and data (pandas dataframe)
        or pandas dataframe if csv is True.
    :rtype: list[tuple[str, pandas.DataFrame], ] or pandas.DataFrame
    """

    l_data = list()

    # Filter data selected by the user.
    phy = selected["phy"].split("-")
    if len(phy) == 4:
        topo, arch, nic, drv = phy
        drv = "" if drv == "dpdk" else drv.replace("_", "-")
    else:
        return l_data

    df = pd.DataFrame(data.loc[(
        (data["passed"] == True) &
        (data["dut_type"] == selected["dut"]) &
        (data["dut_version"] == selected["dutver"]) &
        (data["release"] == selected["rls"])
    )])
    df = df[
        (df.job.str.endswith(f"{topo}-{arch}")) &
        (df.test_id.str.contains(
            f"^.*\.{selected['area']}\..*{nic}.*{drv}.*$",
            regex=True
        ))
    ]
    if drv == "dpdk":
        for driver in C.DRIVERS:
            df.drop(
                df[df.test_id.str.contains(f"-{driver}-")].index,
                inplace=True
            )

    ttype = df["test_type"].to_list()[0]

    # Prepare the coverage data
    def _laten(hdrh_string: str, percentile: float) -> int:
        """Get latency from HDRH string for given percentile.

        :param hdrh_string: Encoded HDRH string.
        :param percentile: Given percentile.
        :type hdrh_string: str
        :type percentile: float
        :returns: The latency value for the given percentile from the encoded
            HDRH string.
        :rtype: int
        """
        try:
            hdr_lat = hdrh.histogram.HdrHistogram.decode(hdrh_string)
            return hdr_lat.get_value_at_percentile(percentile)
        except (hdrh.codec.HdrLengthException, TypeError):
            return None

    def _get_suite(test_id: str) -> str:
        """Get the suite name from the test ID.
        """
        return test_id.split(".")[-2].replace("2n1l-", "").\
            replace("1n1l-", "").replace("2n-", "").replace("-ndrpdr", "")

    def _get_test(test_id: str) -> str:
        """Get the test name from the test ID.
        """
        return test_id.split(".")[-1].replace("-ndrpdr", "")

    cov = pd.DataFrame()
    cov["Suite"] = df.apply(lambda row: _get_suite(row["test_id"]), axis=1)
    cov["Test Name"] = df.apply(lambda row: _get_test(row["test_id"]), axis=1)

    if ttype == "device":
        cov = cov.assign(Result="PASS")
    else:
        cov["Throughput_Unit"] = df["result_pdr_lower_rate_unit"]
        cov["Throughput_NDR"] = df.apply(
            lambda row: row["result_ndr_lower_rate_value"] / 1e6, axis=1
        )
        cov["Throughput_NDR_Mbps"] = df.apply(
            lambda row: row["result_ndr_lower_bandwidth_value"] /1e9, axis=1
        )
        cov["Throughput_PDR"] = df.apply(
            lambda row: row["result_pdr_lower_rate_value"] / 1e6, axis=1
        )
        cov["Throughput_PDR_Mbps"] = df.apply(
            lambda row: row["result_pdr_lower_bandwidth_value"] /1e9, axis=1
        )
        cov["Latency Forward [us]_10% PDR_P50"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_10_hdrh"], 50.0),
            axis=1
        )
        cov["Latency Forward [us]_10% PDR_P90"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_10_hdrh"], 90.0),
            axis=1
        )
        cov["Latency Forward [us]_10% PDR_P99"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_10_hdrh"], 99.0),
            axis=1
        )
        cov["Latency Forward [us]_50% PDR_P50"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_50_hdrh"], 50.0),
            axis=1
        )
        cov["Latency Forward [us]_50% PDR_P90"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_50_hdrh"], 90.0),
            axis=1
        )
        cov["Latency Forward [us]_50% PDR_P99"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_50_hdrh"], 99.0),
            axis=1
        )
        cov["Latency Forward [us]_90% PDR_P50"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_90_hdrh"], 50.0),
            axis=1
        )
        cov["Latency Forward [us]_90% PDR_P90"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_90_hdrh"], 90.0),
            axis=1
        )
        cov["Latency Forward [us]_90% PDR_P99"] = df.apply(
            lambda row: _laten(row["result_latency_forward_pdr_90_hdrh"], 99.0),
            axis=1
        )
        cov["Latency Reverse [us]_10% PDR_P50"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_10_hdrh"], 50.0),
            axis=1
        )
        cov["Latency Reverse [us]_10% PDR_P90"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_10_hdrh"], 90.0),
            axis=1
        )
        cov["Latency Reverse [us]_10% PDR_P99"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_10_hdrh"], 99.0),
            axis=1
        )
        cov["Latency Reverse [us]_50% PDR_P50"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_50_hdrh"], 50.0),
            axis=1
        )
        cov["Latency Reverse [us]_50% PDR_P90"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_50_hdrh"], 90.0),
            axis=1
        )
        cov["Latency Reverse [us]_50% PDR_P99"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_50_hdrh"], 99.0),
            axis=1
        )
        cov["Latency Reverse [us]_90% PDR_P50"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_90_hdrh"], 50.0),
            axis=1
        )
        cov["Latency Reverse [us]_90% PDR_P90"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_90_hdrh"], 90.0),
            axis=1
        )
        cov["Latency Reverse [us]_90% PDR_P99"] = df.apply(
            lambda row: _laten(row["result_latency_reverse_pdr_90_hdrh"], 99.0),
            axis=1
        )

    if csv:
        return cov

    # Split data into tables depending on the test suite.
    for suite in cov["Suite"].unique().tolist():
        df_suite = pd.DataFrame(cov.loc[(cov["Suite"] == suite)])

        if ttype !="device":
            unit = df_suite["Throughput_Unit"].tolist()[0]
            df_suite.rename(
                columns={
                    "Throughput_NDR": f"Throughput_NDR_M{unit}",
                    "Throughput_PDR": f"Throughput_PDR_M{unit}"
                },
                inplace=True
            )
            df_suite.drop(["Suite", "Throughput_Unit"], axis=1, inplace=True)

        l_data.append((suite, df_suite, ))

    return l_data


def coverage_tables(data: pd.DataFrame, selected: dict) -> list:
    """Generate an accordion with coverage tables.

    :param data: Coverage data.
    :param selected: Dictionary with user selection.
    :type data: pandas.DataFrame
    :type selected: dict
    :returns: Accordion with suite names (titles) and tables.
    :rtype: dash_bootstrap_components.Accordion
    """

    accordion_items = list()
    for suite, cov_data in select_coverage_data(data, selected):
        if len(cov_data.columns) == 3:  # VPP Device
            cols = [
                {
                    "name": col,
                    "id": col,
                    "deletable": False,
                    "selectable": False,
                    "type": "text"
                } for col in cov_data.columns
            ]
            style_cell={"textAlign": "left"}
            style_cell_conditional=[
                {
                    "if": {"column_id": "Result"},
                    "textAlign": "right"
                }
            ]
        else:  # Performance
            cols = list()
            for idx, col in enumerate(cov_data.columns):
                if idx == 0:
                    cols.append({
                        "name": ["", "", col],
                        "id": col,
                        "deletable": False,
                        "selectable": False,
                        "type": "text"
                    })
                elif idx < 5:
                    cols.append({
                        "name": col.split("_"),
                        "id": col,
                        "deletable": False,
                        "selectable": False,
                        "type": "numeric",
                        "format": Format(precision=2, scheme=Scheme.fixed)
                    })
                else:
                    cols.append({
                        "name": col.split("_"),
                        "id": col,
                        "deletable": False,
                        "selectable": False,
                        "type": "numeric",
                        "format": Format(precision=0, scheme=Scheme.fixed)
                    })
            style_cell={"textAlign": "right"}
            style_cell_conditional=[
                {
                    "if": {"column_id": "Test Name"},
                    "textAlign": "left"
                }
            ]

        accordion_items.append(
            dbc.AccordionItem(
                title=suite,
                children=dash_table.DataTable(
                    columns=cols,
                    data=cov_data.to_dict("records"),
                    merge_duplicate_headers=True,
                    editable=True,
                    filter_action="none",
                    sort_action="native",
                    sort_mode="multi",
                    selected_columns=[],
                    selected_rows=[],
                    page_action="none",
                    style_cell=style_cell,
                    style_cell_conditional=style_cell_conditional
                )
            )
        )
    return dbc.Accordion(
        children=accordion_items,
        class_name="gy-1 p-0",
        start_collapsed=True,
        always_open=True
    )
