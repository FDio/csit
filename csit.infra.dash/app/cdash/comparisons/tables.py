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

from copy import deepcopy
from ..utils.constants import Constants as C
from ..utils.utils import relative_change_stdev


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
            d_data["mean"].append(int(mean_val))
            d_data["stdev"].append(int(std_val))
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
        normalize: bool,
        sort_by: str="Mean Value of Relative Change",
        sort_order: int=0,
        output="html"  # html or csv
    ) -> tuple:
    """
    """

    def _create_selection(sel: dict) -> list:
        """
        """
        l_infra = sel["infra"].split("-")
        selection = list()
        for core in sel["core"]:
            for fsize in sel["frmsize"]:
                for ttype in sel["ttype"]:
                    selection.append({
                        "dut": sel["dut"],
                        "dutver": sel["dutver"],
                        "tbed": f"{l_infra[0]}-{l_infra[1]}",
                        "nic": l_infra[2],
                        "driver": l_infra[-1].replace("_", "-"),
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
        return str(), pd.DataFrame()

    cmp_data = {
        "Test Name": list(),
        f"{r_name} Mean Value": list(),
        f"{r_name} Standard Deviation": list(),
        f"{c_name} Mean Value": list(),
        f"{c_name} Standard Deviation": list(),
        "Mean Value of Relative Change": list(),
        "Standard Deviation of Relative Change": list()
    }
    for _, row in r_data.iterrows():
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
        if not c_row.empty:
            r_mean = row["mean"]
            r_std = row["stdev"]
            c_mean = c_row["mean"].values[0]
            c_std = c_row["stdev"].values[0]
            cmp_data["Test Name"].append(row["name"])
            cmp_data[f"{r_name} Mean Value"].append(r_mean)
            cmp_data[f"{r_name} Standard Deviation"].append(r_std)
            cmp_data[f"{c_name} Mean Value"].append(c_mean)
            cmp_data[f"{c_name} Standard Deviation"].append(c_std)
            delta, d_stdev = relative_change_stdev(r_mean, c_mean, r_std, c_std)
            cmp_data["Mean Value of Relative Change"].append(delta)
            cmp_data["Standard Deviation of Relative Change"].append(d_stdev)

    df_cmp = pd.DataFrame.from_dict(cmp_data)
    df_cmp.sort_values(by=sort_by, ascending=bool(sort_order), inplace=True)

    if output == "csv":
        return (title, df_cmp)

    def _format_output(mean: float, stdev: float) -> str:
        return f"{mean:.2f} (SD={stdev:.2f})"
    
    df_cmp[r_name] = df_cmp.apply(
        lambda row: _format_output(
            row[f"{r_name} Mean Value"] / 1e6,
            row[f"{r_name} Standard Deviation"] / 1e6
        ),
        axis=1
    )
    df_cmp[c_name] = df_cmp.apply(
        lambda row: _format_output(
            row[f"{c_name} Mean Value"] / 1e6,
            row[f"{c_name} Standard Deviation"] / 1e6
        ),
        axis=1
    )
    df_cmp["Relative Change"] = df_cmp.apply(
        lambda row: _format_output(
            row["Mean Value of Relative Change"],
            row["Standard Deviation of Relative Change"]
        ),
        axis=1
    )

    return (title, df_cmp[["Test Name", r_name, c_name, "Relative Change"]])
