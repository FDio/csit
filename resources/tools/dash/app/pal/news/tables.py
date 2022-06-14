# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""
"""

import logging
import pandas as pd
import dash_bootstrap_components as dbc


def table_failed(data: pd.DataFrame, job: str) -> list:
    """
    """

    job_data = data.loc[(data["job"] == job)]

    dict_details = {
        "Job": job_data["job"],
        "Build": job_data["build"],
        "DUT": job_data["dut_type"],
        "DUT Version": job_data["dut_version"],
        "Hosts": ", ".join(job_data["hosts"].to_list()[0])
    }
    tab_details = dbc.Table.from_dataframe(pd.DataFrame.from_dict(dict_details))

    lst_failed = job_data["lst_failed"].to_list()[0]
    dict_failed = {
        f"Last Failed Tests ({len(lst_failed)})": lst_failed
    }

    tab_failed = dbc.Table.from_dataframe(pd.DataFrame.from_dict(dict_failed))

    return [tab_details, tab_failed, ]
