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

"""The comparison tables.
"""

import pandas as pd

from numpy import mean, std, percentile
from copy import deepcopy

from ..utils.constants import Constants as C
from ..utils.utils import relative_change_stdev


def select_comp_data(
        data: pd.DataFrame,
        selected: dict,
        normalize: bool=False,
        remove_outliers: bool=False,
        raw_data: bool=False
    ) -> pd.DataFrame:
    """Select data for a comparison table.

    :param data: Data to be filtered for the comparison table.
    :param selected: A dictionary with parameters and their values selected by
        the user.
    :param normalize: If True, the data is normalized to CPU frequency
        Constants.NORM_FREQUENCY.
    :param remove_outliers: If True the outliers are removed before
        generating the table.
    :param raw_data: If True, returns data as it is in parquets without any
        processing. It is used for "download raw data" feature.
    :type data: pandas.DataFrame
    :type selected: dict
    :type normalize: bool
    :type remove_outliers: bool
    :type raw_data: bool
    :returns: A data frame with selected data.
    :rtype: pandas.DataFrame
    """

    def _calculate_statistics(
            data_in: pd.DataFrame,
            ttype: str,
            drv: str,
            norm_factor: float,
            remove_outliers: bool=False
        ) -> pd.DataFrame:
        """Calculates mean value and standard deviation for provided data.

        :param data_in: Input data for calculations.
        :param ttype: The test type.
        :param drv: The driver.
        :param norm_factor: The data normalization factor.
        :param remove_outliers: If True the outliers are removed before
            generating the table.
        :type data_in: pandas.DataFrame
        :type ttype: str
        :type drv: str
        :type norm_factor: float
        :type remove_outliers: bool
        :returns: A pandas dataframe with: test name, mean value, standard
            deviation and unit.
        :rtype: pandas.DataFrame
        """
        d_data = {
            "name": list(),
            "mean": list(),
            "stdev": list(),
            "unit": list()
        }
        for itm in data_in["test_id"].unique().tolist():
            itm_lst = itm.split(".")
            test = itm_lst[-1].rsplit("-", 1)[0]
            if "hoststack" in itm:
                test_type = f"hoststack-{ttype}"
            else:
                test_type = ttype
            df = data_in.loc[(data_in["test_id"] == itm)]
            l_df = df[C.VALUE_ITER[test_type]].to_list()
            if len(l_df) and isinstance(l_df[0], list):
                tmp_df = list()
                for l_itm in l_df:
                    tmp_df.extend(l_itm)
                l_df = tmp_df

            try:
                if remove_outliers:
                    q1 = percentile(l_df, 25, method=C.COMP_PERCENTILE_METHOD)
                    q3 = percentile(l_df, 75, method=C.COMP_PERCENTILE_METHOD)
                    irq = q3 - q1
                    lif = q1 - C.COMP_OUTLIER_TYPE * irq
                    uif = q3 + C.COMP_OUTLIER_TYPE * irq
                    l_df = [i for i in l_df if i >= lif and i <= uif]
                mean_val = mean(l_df)
                std_val = std(l_df)
            except (TypeError, ValueError):
                continue
            d_data["name"].append(f"{test.replace(f'{drv}-', '')}-{ttype}")
            d_data["mean"].append(int(mean_val * norm_factor))
            d_data["stdev"].append(int(std_val * norm_factor))
            d_data["unit"].append(df[C.UNIT[test_type]].to_list()[0])
        return pd.DataFrame(d_data)

    lst_df = list()
    for itm in selected:
        if itm["ttype"] in ("NDR", "PDR", "Latency"):
            test_type = "ndrpdr"
        elif itm["ttype"] in ("CPS", "RPS", "BPS"):
            test_type  = "hoststack"
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
        core = str() if itm["dut"] == "trex" else itm["core"].lower()
        ttype = "ndrpdr" if itm["ttype"] in ("NDR", "PDR", "Latency") \
            else itm["ttype"].lower()
        tmp_df = tmp_df[
            (tmp_df.job.str.endswith(itm["tbed"])) &
            (tmp_df.test_id.str.contains(
                (
                    f"^.*[.|-]{itm['nic']}.*{itm['frmsize'].lower()}-"
                    f"{core}-{drv}.*-{ttype}$"
                ),
                regex=True
            ))
        ]
        if itm["driver"] == "dpdk":
            for drv in C.DRIVERS:
                tmp_df.drop(
                    tmp_df[tmp_df.test_id.str.contains(f"-{drv}-")].index,
                    inplace=True
                )

        # Change the data type from ndrpdr to one of ("NDR", "PDR", "Latency")
        if test_type == "ndrpdr":
            tmp_df = tmp_df.assign(test_type=itm["ttype"].lower())

        if not tmp_df.empty:
            if normalize:
                if itm["ttype"] == "Latency":
                    norm_factor = C.FREQUENCY[itm["tbed"]] / C.NORM_FREQUENCY
                else:
                    norm_factor = C.NORM_FREQUENCY / C.FREQUENCY[itm["tbed"]]
            else:
                norm_factor = 1.0
            if not raw_data:
                tmp_df = _calculate_statistics(
                    tmp_df,
                    itm["ttype"].lower(),
                    itm["driver"],
                    norm_factor,
                    remove_outliers=remove_outliers
                )

        lst_df.append(tmp_df)

    if len(lst_df) == 1:
        df = lst_df[0]
    elif len(lst_df) > 1:
        df = pd.concat(
            lst_df,
            ignore_index=True,
            copy=False
        )
    else:
        df = pd.DataFrame()

    return df


def comparison_table(
        data: pd.DataFrame,
        selected: dict,
        normalize: bool,
        format: str="html",
        remove_outliers: bool=False,
        raw_data: bool=False
    ) -> tuple:
    """Generate a comparison table.

    :param data: Iterative data for the comparison table.
    :param selected: A dictionary with parameters and their values selected by
        the user.
    :param normalize: If True, the data is normalized to CPU frequency
        Constants.NORM_FREQUENCY.
    :param format: The output format of the table:
        - html: To be displayed on html page, the values are shown in millions
          of the unit.
        - csv: To be downloaded as a CSV file the values are stored in base
          units.
    :param remove_outliers: If True the outliers are removed before
        generating the table.
    :param raw_data: If True, returns data as it is in parquets without any
        processing. It is used for "download raw data" feature.
    :type data: pandas.DataFrame
    :type selected: dict
    :type normalize: bool
    :type format: str
    :type remove_outliers: bool
    :type raw_data: bool
    :returns: A tuple with the tabe title and the comparison table.
    :rtype: tuple[str, pandas.DataFrame]
    """

    def _create_selection(sel: dict) -> list:
        """Transform the complex dictionary with user selection to list
            of simple items.

        :param sel: A complex dictionary with user selection.
        :type sel: dict
        :returns: A list of simple items.
        :rtype: list
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

    # Select reference data
    r_sel = deepcopy(selected["reference"]["selection"])
    r_selection = _create_selection(r_sel)
    r_data = select_comp_data(
        data, r_selection, normalize, remove_outliers, raw_data
    )

    # Select compare data
    c_sel = deepcopy(selected["reference"]["selection"])
    c_params = selected["compare"]
    if c_params["parameter"] in ("core", "frmsize", "ttype"):
        c_sel[c_params["parameter"]] = [c_params["value"], ]
    else:
        c_sel[c_params["parameter"]] = c_params["value"]
    c_selection = _create_selection(c_sel)
    c_data = select_comp_data(
        data, c_selection, normalize, remove_outliers, raw_data
    )

    if raw_data:
        r_data["ref/cmp"] = "reference"
        c_data["ref/cmp"] = "compare"
        return str(), pd.concat([r_data, c_data], ignore_index=True, copy=False)

    if r_data.empty or c_data.empty:
        return str(), pd.DataFrame()

    if format == "html" and "Latency" not in r_sel["ttype"]:
        unit_factor, s_unit_factor = (1e6, "M")
    else:
        unit_factor, s_unit_factor = (1, str())

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

    l_name, l_r_mean, l_r_std, l_c_mean, l_c_std, l_rc_mean, l_rc_std, unit = \
        list(), list(), list(), list(), list(), list(), list(), set()
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
            if r_mean == 0.0 or c_mean == 0.0:
                break
            unit.add(f"{s_unit_factor}{row['unit']}")
            l_name.append(row["name"])
            l_r_mean.append(r_mean / unit_factor)
            l_r_std.append(r_std / unit_factor)
            l_c_mean.append(c_mean / unit_factor)
            l_c_std.append(c_std / unit_factor)
            delta, d_stdev = relative_change_stdev(r_mean, c_mean, r_std, c_std)
            l_rc_mean.append(delta)
            l_rc_std.append(d_stdev)

    s_unit = "|".join(unit)
    df_cmp = pd.DataFrame.from_dict({
        "Test Name": l_name,
        f"{r_name} Mean [{s_unit}]": l_r_mean,
        f"{r_name} Stdev [{s_unit}]": l_r_std,
        f"{c_name} Mean [{s_unit}]": l_c_mean,
        f"{c_name} Stdev [{s_unit}]": l_c_std,
        "Relative Change Mean [%]": l_rc_mean,
        "Relative Change Stdev [%]": l_rc_std
    })
    df_cmp.sort_values(
        by="Relative Change Mean [%]",
        ascending=False,
        inplace=True
    )

    return (title, df_cmp)
