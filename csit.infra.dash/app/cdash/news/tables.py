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

"""The tables with news.
"""

import pandas as pd
import dash_bootstrap_components as dbc

from datetime import datetime, timedelta


def _table_info(job_data: pd.DataFrame) -> dbc.Table:
    """Generates table with info about the job.

    :param job_data: Dataframe with information about the job.
    :type job_data: pandas.DataFrame
    :returns: Table with job info.
    :rtype: dbc.Table
    """
    return dbc.Table.from_dataframe(
        pd.DataFrame.from_dict(
            {
                "Job": job_data["job"],
                "Last Build": job_data["build"],
                "Date": job_data["start"],
                "DUT": job_data["dut_type"],
                "DUT Version": job_data["dut_version"],
                "Hosts": ", ".join(job_data["hosts"].to_list()[0])
            }
        ),
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
        color="info"
    )


def _table_failed(job_data: pd.DataFrame, failed: list) -> dbc.Table:
    """Generates table with failed tests from the last run of the job.

    :param job_data: Dataframe with information about the job.
    :param failed: List of failed tests.
    :type job_data: pandas.DataFrame
    :type failed: list
    :returns: Table with fialed tests.
    :rtype: dbc.Table
    """
    return dbc.Table.from_dataframe(
        pd.DataFrame.from_dict(
            {
                (
                    f"Last Failed Tests on "
                    f"{job_data['start'].values[0]} ({len(failed)})"
                ): failed
            }
        ),
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
        color="danger"
    )


def _table_gressions(itms: dict, color: str) -> dbc.Table:
    """Generates table with regressions.

    :param itms: Dictionary with items (regressions or progressions) and their
        last occurence.
    :param color: Color of the table.
    :type regressions: dict
    :type color: str
    :returns: The table with regressions.
    :rtype: dbc.Table
    """
    return dbc.Table.from_dataframe(
        pd.DataFrame.from_dict(itms),
        bordered=True,
        striped=True,
        hover=True,
        size="sm",
        color=color
    )


def table_news(data: pd.DataFrame, job: str, period: int) -> list:
    """Generates the tables with news:
    1. Falied tests from the last run
    2. Regressions and progressions calculated from the last C.NEWS_TIME_PERIOD
       days.

    :param data: Trending data with calculated annomalies to be displayed in the
        tables.
    :param job: The job name.
    :param period: The time period (nr of days from now) taken into account.
    :type data: pandas.DataFrame
    :type job: str
    :type period: int
    :returns: List of tables.
    :rtype: list
    """

    last_day = datetime.utcnow() - timedelta(days=period)
    r_list = list()
    job_data = data.loc[(data["job"] == job)]
    r_list.append(_table_info(job_data))

    failed = job_data["failed"].to_list()[0]
    if failed:
        r_list.append(_table_failed(job_data, failed))

    title = f"Regressions in the last {period} days"
    regressions = {title: list(), "Last Regression": list()}
    for itm in job_data["regressions"].to_list()[0]:
        if itm[1] < last_day:
            break
        regressions[title].append(itm[0])
        regressions["Last Regression"].append(
            itm[1].strftime('%Y-%m-%d %H:%M'))
    if regressions["Last Regression"]:
        r_list.append(_table_gressions(regressions, "warning"))

    title = f"Progressions in the last {period} days"
    progressions = {title: list(), "Last Progression": list()}
    for itm in job_data["progressions"].to_list()[0]:
        if itm[1] < last_day:
            break
        progressions[title].append(itm[0])
        progressions["Last Progression"].append(
            itm[1].strftime('%Y-%m-%d %H:%M'))
    if progressions["Last Progression"]:
        r_list.append(_table_gressions(progressions, "success"))

    return r_list


def table_summary(data: pd.DataFrame, jobs: list, period: int) -> list:
    """Generates summary (failed tests, regressions and progressions) from the
    last week.

    :param data: Trending data with calculated annomalies to be displayed in the
        tables.
    :param jobs: List of jobs.
    :params period: The time period for the summary table.
    :type data: pandas.DataFrame
    :type job: str
    :type period: int
    :returns: List of tables.
    :rtype: list
    """

    return [
        dbc.Accordion(
            children=[
                dbc.AccordionItem(
                    title=job,
                    children=table_news(data, job, period)
                ) for job in jobs
            ],
            class_name="gy-2 p-0",
            start_collapsed=True,
            always_open=True
        )
    ]
