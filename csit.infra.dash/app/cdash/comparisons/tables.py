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

from copy import deepcopy
from ..utils.constants import Constants as C


def select_comparison_data(
        data: pd.DataFrame,
        selected: dict,
        normalize: bool=False
    ) -> pd.DataFrame:
    """
    """

    def _compact_data(
            data_in: pd.DataFrame,
            ttype: str,
            drv: str,
            norm_factor: float
        ) -> pd.DataFrame:
        """
        """
        tests = data_in["test_id"].unique().tolist()
        d_data = {
            "name": list(),
            "mean": list(),
            "stdev": list()
        }
        for itm in tests:
            itm_lst = itm.split(".")
            test = itm_lst[-1].rsplit("-", 1)[0]
            df = data_in.loc[(data_in["test_id"] == itm)]
            d_data["name"].append(f"{test.replace(f'{drv}-', '')}-{ttype}")
            mean_val = df[C.VALUE_ITER[ttype]].mean() * norm_factor
            std_val = df[C.VALUE_ITER[ttype]].std() * norm_factor
            d_data["mean"].append(mean_val)
            d_data["stdev"].append(std_val)
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
        )])

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
            if normalize:
                norm_factor = C.NORM_FREQUENCY / C.FREQUENCY[itm["tbed"]]
            else:
                norm_factor = 1.0
            tmp_df = _compact_data(
                tmp_df,
                itm["ttype"].lower(),
                itm["driver"],
                norm_factor
            )

        lst_df.append(tmp_df)

    if len(lst_df) == 1:
        df = lst_df[0]
    else:
        df = pd.concat(
            lst_df,
            ignore_index=True,
            copy=False
        )

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
        for core in sel["core"]:
            for fsize in sel["frmsize"]:
                for ttype in sel["ttype"]:
                    selection.append({
                        "dut": sel["dut"],
                        "dutver": sel["dutver"],
                        "tbed": sel["tbed"],
                        "nic": sel["nic"],
                        "driver": sel["driver"],
                        "core": core,
                        "frmsize": fsize,
                        "ttype": ttype
                    })
        return selection

    r_sel = deepcopy(selected["reference"]["selection"])
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
    r_data = select_comparison_data(data, r_selection, normalize)

    # Select compare data
    c_sel = deepcopy(selected["reference"]["selection"])
    if c_params["parameter"] in ("core", "frmsize", "ttype"):
        c_sel[c_params["parameter"]] = [c_params["value"], ]
    else:
        c_sel[c_params["parameter"]] = c_params["value"]

    c_selection = _create_selection(c_sel)
    c_data = select_comparison_data(data, c_selection, normalize)

    if r_data.empty or c_data.empty:
        return str(), None

    cmp_data = {
        "Test Name": list(),
        f"{r_name} mean": list(),
        f"{r_name} stdev": list(),
        f"{c_name} mean": list(),
        f"{c_name} stdev": list()
    }
    for _, row in r_data.iterrows():
        cmp_data["Test Name"].append(row["name"])
        cmp_data[f"{r_name} mean"].append(row["mean"])
        cmp_data[f"{r_name} stdev"].append(row["stdev"])
        if c_params["parameter"] in ("core", "frmsize", "ttype"):
            l_cmp = row["name"].split("-")
            if c_params["parameter"] == "core":
                c_row = c_data[
                    (c_data.name.str.contains(l_cmp[0])) &
                    (c_data.name.str.contains("-".join(l_cmp[2:])))
                ]
            elif c_params["parameter"] == "frmsize":
                c_row = c_data[c_data.name.str.contains("-".join(l_cmp[1:]))]
            elif c_params["parameter"] == "ttype":
                regex = r"^" + f"{'-'.join(l_cmp[:-1])}" + r"-.{3}$"
                c_row = c_data[c_data.name.str.contains(regex, regex=True)]
        else:
            c_row = c_data[c_data["name"] == row["name"]]
        cmp_data[f"{c_name} mean"].append(c_row["mean"].values[0])
        cmp_data[f"{c_name} stdev"].append(c_row["stdev"].values[0])








    logging.info(cmp_data)


    return (
        title,
        dbc.Table.from_dataframe(
            pd.DataFrame.from_dict(cmp_data),
            bordered=True,
            striped=True,
            hover=True,
            size="sm",
            color="info"
        )
    )
