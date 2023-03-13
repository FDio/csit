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


def select_comparison_data(
        data: pd.DataFrame,
        selected: dict,
        normalize: bool
    ) -> pd.DataFrame:
    """
    """

    df = pd.DataFrame()

    lst_df = list()
    for itm in selected:
        if itm["ttype"] in ("NDR", "PDR"):
            test_type = "ndrpdr"
        else:
            test_type = itm["ttype"]

        dutver = itm["dutver"].split("-", 1)
        tmp_df = data.loc[(
            (data["passed"] == True) &
            (data["dut_type"] == itm["dut"]) &
            (data["dut_version"] == dutver[1]) &
            (data["test_type"] == test_type) &
            (data["release"] == dutver[0])
        )].drop_duplicates(ignore_index=True)

        # Zmenit ttype na "ndr" alebo "pdr" namiesto "ndrpdr" v data frejme.
        lst_df.append(tmp_df)

    if len(lst_df) == 1:
        df = lst_df[0]
    else:
        df = pd.concat(
            lst_df,
            ignore_index=True,
            copy=False
        )

    # TODO: Normalization.

    logging.info(df)
    df.info()

    return df


def comparison_table(
        data: pd.DataFrame,
        selected: dict,
        normalize: bool
    ) -> dbc.Table:
    """
    """

    logging.info(selected)

    rdata = select_comparison_data(
        data,
        selected["reference"]["selection"],
        normalize
    )
    # cdata = select_comparison_data(
    #     data,
    #     selected["compare"]["selection"],
    #     normalize
    # )

    if rdata.empty:  # or cdata.empty:
        return None


    return dbc.Table.from_dataframe(
        pd.DataFrame.from_dict(
            {
                "Test Name": ("Test 1", "Test 2", "Test 3", "Test 4", "Test 5", "Test 6", "Test 7", "Test 8", "Test 9", "Test 10"),
                "Reference [Mpps]": (1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                "Compare [Mpps]": ((1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8, 9.9, 10.1)),
                "Relative Diff [%]": (10, 20, 30, 40, 50, 60, 70, 80, 90, 10)
            }
        ),
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
        color="info"
    )
