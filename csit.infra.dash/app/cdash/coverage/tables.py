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

import pandas as pd
import dash_bootstrap_components as dbc


def select_coverage_data(data: pd.DataFrame, selected: dict) -> list:
    """

    :returns: List of tuples with suite name (str) and data (pandas dataframe).
    :rtype: list[tuple[str, pandas.DataFrame], ]
    """

    l_data = list()

    return l_data


def coverage_tables(data: pd.DataFrame, selected: dict) -> list:
    """

    :returns: Accordion with suite names (titles) and tables.
    :rtype: dash_bootstrap_components.Accordion
    """

    accordion_items = list()
    for suite, cov_data in select_coverage_data(data, selected):

        d_table = dict()
        accordion_items.append(
            dbc.AccordionItem(
                title=suite,
                children=dbc.Table.from_dataframe(
                    pd.DataFrame.from_dict(d_table),
                    bordered=True,
                    striped=True,
                    hover=True,
                    size="sm",
                    color="info"
                )
            )
        )

    return dbc.Accordion(
            children=accordion_items,
            class_name="gy-2 p-0",
            start_collapsed=True,
            always_open=True
        )
