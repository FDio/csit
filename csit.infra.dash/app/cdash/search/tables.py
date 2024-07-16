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

"""The search data tables.
"""


import pandas as pd

from ..utils.constants import Constants as C
from ..utils.utils import get_topo_arch


def select_search_data(data: pd.DataFrame, selection: list) -> pd.DataFrame:
    """Return the searched data based on the user's "selection".

    :param data: Input data to be searched through.
    :param selection: User selection.
    :type data: pandas.DataFrame
    :type selection: list[dict]
    :returns: A dataframe with selected tests.
    :trype: pandas.DataFrame
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
        df = df[
            df.full_id.str.contains(
                selection["regexp"].replace(" ", ".*"),
                regex=True
            )
        ]
    except Exception:
        return pd.DataFrame()

    return df


def search_table(data: pd.DataFrame, selection: list) -> pd.DataFrame:
    """Generate a table listing tests based on user's selection.

    :param data: Input data (all tests).
    :param selection: User selection.
    :type data: pandas.DataFrame
    :type selection: list[dict]
    :returns: A dataframe with selected tests/
    :rtype: pandas.DataFrame
    """

    sel = select_search_data(data, selection)
    if sel.empty:
        return pd.DataFrame()

    l_tb, l_nic, l_drv, l_test, = list(), list(), list(), list()
    if selection["datatype"] == "trending":
        cols = ["job", "test_id"]
    else:
        l_dutver = list()
        cols = ["job", "test_id", "dut_version"]
    for _, row in sel[cols].drop_duplicates().iterrows():
        l_id = row["test_id"].split(".")
        suite = l_id[-2].replace("2n1l-", "").replace("1n1l-", "").\
            replace("2n-", "")
        l_tb.append(get_topo_arch(row["job"].split("-")))
        l_nic.append(suite.split("-")[0])
        if selection["datatype"] != "trending":
            l_dutver.append(row["dut_version"])
        for driver in C.DRIVERS:
            if driver in suite:
                l_drv.append(driver)
                break
        else:
            l_drv.append("dpdk")
        l_test.append(l_id[-1])

    if selection["datatype"] == "trending":
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
    else:
        selected = pd.DataFrame.from_dict({
            "DUT Version": l_dutver,
            "Test Bed": l_tb,
            "NIC": l_nic,
            "Driver": l_drv,
            "Test": l_test
        })

        selected.sort_values(
            by=["DUT Version", "Test Bed", "NIC", "Driver", "Test"],
            ascending=True,
            inplace=True
        )

    return selected
