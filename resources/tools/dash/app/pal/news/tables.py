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

import pandas as pd
import dash_bootstrap_components as dbc


# Time period for regressions and progressions.
TIME_PERIOD = 21  # [days]


def table_news(data: pd.DataFrame, job: str) -> list:
    """
    """

    job_data = data.loc[(data["job"] == job)]
    failed = job_data["failed"].to_list()[0]
    regressions = {"Test Name": list(), "Last Regression": list()}
    for itm in job_data["regressions"].to_list()[0]:
        regressions["Test Name"].append(itm[0])
        regressions["Last Regression"].append(itm[1].strftime('%Y-%m-%d %H:%M'))
    progressions = {"Test Name": list(), "Last Progression": list()}
    for itm in job_data["progressions"].to_list()[0]:
        progressions["Test Name"].append(itm[0])
        progressions["Last Progression"].append(
            itm[1].strftime('%Y-%m-%d %H:%M'))

    return [
        dbc.Table.from_dataframe(pd.DataFrame.from_dict({
            "Job": job_data["job"],
            "Last Build": job_data["build"],
            "Date": job_data["start"],
            "DUT": job_data["dut_type"],
            "DUT Version": job_data["dut_version"],
            "Hosts": ", ".join(job_data["hosts"].to_list()[0])
        }), bordered=True, striped=True, hover=True, size="sm", color="light"),
        dbc.Table.from_dataframe(pd.DataFrame.from_dict({
            (
                f"Last Failed Tests on "
                f"{job_data['start'].values[0]} ({len(failed)})"
            ): failed
        }), bordered=True, striped=True, hover=True, size="sm", color="light"),
        dbc.Label(
            class_name="p-0",
            size="lg",
            children=(
                f"Regressions during the last {TIME_PERIOD} days "
                f"({len(regressions['Test Name'])})"
            )
        ),
        dbc.Table.from_dataframe(
            pd.DataFrame.from_dict(regressions),
            bordered=True, striped=True, hover=True, size="sm", color="light"),
        dbc.Label(
            class_name="p-0",
            size="lg",
            children=(
                f"Progressions during the last {TIME_PERIOD} days "
                f"({len(progressions['Test Name'])})"
            )
        ),
        dbc.Table.from_dataframe(
            pd.DataFrame.from_dict(progressions),
            bordered=True, striped=True, hover=True, size="sm", color="light")
    ]
