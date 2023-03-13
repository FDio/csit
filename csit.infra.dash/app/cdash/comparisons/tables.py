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

"""The comparison tables.
"""

import logging

import pandas as pd
import dash_bootstrap_components as dbc

from ..utils.constants import Constants as C


def select_comparison_data(
        data: pd.DataFrame,
        selected: dict
    ) -> pd.DataFrame:
    """
    """

    def _compact_data(data_in: pd.DataFrame, ttype: str) -> pd.DataFrame:
        """
        """

        tests = data_in["test_id"].unique().tolist()
        d_data = {
            "id": list(),
            "mean": list(),
            "stdev": list()
        }
        for itm in tests:
            itm_lst = itm.split(".")
            test = itm_lst[-1].rsplit("-", 1)[0]
            nic = itm_lst[-2].replace("2n1l-", "").replace("1n1l-", "").\
                replace("2n-", "").split("-", 1)[0]
            df = data_in.loc[(data_in["test_id"] == itm)]
            d_data["id"].append(f"{nic}-{test}-{ttype}")
            d_data["mean"].append(df[C.VALUE_ITER[ttype]].mean())
            d_data["stdev"].append(df[C.VALUE_ITER[ttype]].std())
        data_out = pd.DataFrame(d_data)

        return data_out

    df = pd.DataFrame()

    lst_df = list()
    for itm in selected:
        if itm["ttype"] in ("NDR", "PDR"):
            test_type = "ndrpdr"
        else:
            test_type = itm["ttype"].lower()

        dutver = itm["dutver"].split("-", 1)  # 0 -> release, 1 -> dut version
        tmp_df = pd.DataFrame(data.loc[(
            (data["passed"] == True) &
            (data["dut_type"] == itm["dut"]) &
            (data["dut_version"] == dutver[1]) &
            (data["test_type"] == test_type) &
            (data["release"] == dutver[0])
        )])  # .drop_duplicates(ignore_index=True) ???

        drv = "" if itm["driver"] == "dpdk" else itm["driver"].replace("_", "-")
        reg_id = (
            f"^.*[.|-]{itm['nic']}.*{itm['frmsize'].lower()}-"
            f"{itm['core'].lower()}-{drv}.*$"
        )
        tmp_df = tmp_df[
            (tmp_df.job.str.endswith(itm["tbed"])) &
            (tmp_df.test_id.str.contains(reg_id, regex=True))
        ]
        if itm["driver"] == "dpdk":
            for drv in C.DRIVERS:
                tmp_df.drop(
                    tmp_df[tmp_df.test_id.str.contains(f"-{drv}-")].index,
                    inplace=True
                )

        # Change the data type from ndrpdr to one of ("NDR", "PDR")
        if test_type == "ndrpdr":
            tmp_df = tmp_df.assign(test_type=itm["ttype"].lower())

        if not tmp_df.empty:
            tmp_df = _compact_data(tmp_df, itm["ttype"].lower())

        lst_df.append(tmp_df)

    if len(lst_df) == 1:
        df = lst_df[0]
    else:
        df = pd.concat(
            lst_df,
            ignore_index=True,
            copy=False
        )

    logging.info("Data frame with selected data:")
    df.info()

    return df


def comparison_table(
        data: pd.DataFrame,
        selected: dict,
        normalize: bool
    ) -> dbc.Table:
    """
    """

    def _create_selection(sel: dict) -> list:
        """
        """
        selection = list()
        for core in r_sel["core"]:
            for fsize in r_sel["frmsize"]:
                for ttype in r_sel["ttype"]:
                    selection.append({
                        "dut": r_sel["dut"],
                        "dutver": r_sel["dutver"],
                        "tbed": r_sel["tbed"],
                        "nic": r_sel["nic"],
                        "driver": r_sel["driver"],
                        "core": core,
                        "frmsize": fsize,
                        "ttype": ttype
                    })
        return selection

    logging.info("Selected:")
    logging.info(selected)

    r_sel = selected["reference"]["selection"]
    c_params = selected["compare"]
    r_selection = _create_selection(r_sel)

    # Create Table title and titles of columns with data
    params = list(r_sel)
    params.remove(c_params["parameter"])
    lst_title = list()
    for param in params:
        value = r_sel[param]
        if isinstance(value, list):
            lst_title.append("|".join(value))
        else:
            lst_title.append(value)
    title = "Comparison for: " + "-".join(lst_title)
    r_name = r_sel[c_params["parameter"]]
    if isinstance(r_name, list):
        r_name = "|".join(r_name)
    c_name = c_params["value"]

    # Select reference data
    r_data = select_comparison_data(data, r_selection)

    # Select compare data
    c_sel = selected["reference"]["selection"]
    if c_params["parameter"] in ("core", "frmsize", "ttype"):
        c_sel[c_params["parameter"]] = [c_params["value"], ]
    else:
        c_sel[c_params["parameter"]] = c_params["value"]

    c_selection = _create_selection(c_sel)
    c_data = select_comparison_data(data, c_selection)

    if r_data.empty or c_data.empty:
        return str(), None






    # TODO: Normalization.


    return (
        title,
        dbc.Table.from_dataframe(
            r_data,
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
            color="info"
        )
    )

    # return (
    #     title,
    #     dbc.Table.from_dataframe(
    #         pd.DataFrame.from_dict(
    #             {
    #                 "Test Name (Reference)": ("Test 1", "Test 2", "Test 3", "Test 4", "Test 5", "Test 6", "Test 7", "Test 8", "Test 9", "Test 10"),
    #                 f"{r_name} [Mpps]": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
    #                 f"{c_name} [Mpps]": ((1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.1)),
    #                 "Relative Diff [%]": (10, 20, 30, 40, 50, 60, 70, 80, 90, 10)
    #             }
    #         ),
    #         bordered=True,
    #         striped=True,
    #         hover=True,
    #         size="sm",
    #         color="info"
    #     )
    # )
