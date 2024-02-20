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

"""The search data tables.
"""


import pandas as pd
import dash_bootstrap_components as dbc

from dash import dash_table
from dash.dash_table.Format import Format, Scheme

from ..utils.constants import Constants as C


def select_search_data(data: pd.DataFrame, selection: list) -> pd.DataFrame:
    """
    """

    sel_data = data[selection["datatype"]]

    if selection["datatype"] == "trending":
        df = pd.DataFrame(sel_data.loc[
            sel_data["dut_type"] == selection["dut"]
        ])
    else:
        df = pd.DataFrame(sel_data.loc[(
            (sel_data["dut_type"] == selection["dut"]) &
            (sel_data["release"] == selection["release"])
        )])
    try:
        df = df[df.test_id.str.contains(selection["regexp"], regex=True)]
    except Exception:
        return pd.DataFrame()

    return df


def search_table(data: pd.DataFrame, selection: list) -> pd.DataFrame:
    """
    """

    sel = select_search_data(data, selection)
    if sel.empty:
        return pd.DataFrame()

    l_tb, l_nic, l_drv, l_test = list(), list(), list(), list()
    for _, row in sel[["job", "test_id"]].drop_duplicates().iterrows():
        l_id = row["test_id"].split(".")
        suite = l_id[-2].replace("2n1l-", "").replace("1n1l-", "").\
            replace("2n-", "")
        l_tb.append("-".join(row["job"].split("-")[-2:]))
        l_nic.append(suite.split("-")[0])
        for driver in C.DRIVERS:
            if driver in suite:
                l_drv.append(driver.replace("-", "_"))
                break
        else:
            l_drv.append("dpdk")
        l_test.append(l_id[-1])

    selected = pd.DataFrame.from_dict({
        "Test Bed": l_tb,
        "NIC": l_nic,
        "Driver": l_drv,
        "Test": l_test
    })

    selected.sort_values(
        by=["Test Bed", "NIC", "Driver", "Test"],
        ascending=True,
        inplace=True
    )

    return selected
