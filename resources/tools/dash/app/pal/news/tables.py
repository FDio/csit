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

from numpy import isnan

from ..jumpavg import classify


def _classify_anomalies(data):
    """Process the data and return anomalies and trending values.

    Gather data into groups with average as trend value.
    Decorate values within groups to be normal,
    the first value of changed average as a regression, or a progression.

    :param data: Full data set with unavailable samples replaced by nan.
    :type data: OrderedDict
    :returns: Classification and trend values
    :rtype: 3-tuple, list of strings, list of floats and list of floats
    """
    # NaN means something went wrong.
    # Use 0.0 to cause that being reported as a severe regression.
    bare_data = [0.0 if isnan(sample) else sample for sample in data.values()]
    # TODO: Make BitCountingGroupList a subclass of list again?
    group_list = classify(bare_data).group_list
    group_list.reverse()  # Just to use .pop() for FIFO.
    classification = list()
    avgs = list()
    stdevs = list()
    active_group = None
    values_left = 0
    avg = 0.0
    stdv = 0.0
    for sample in data.values():
        if isnan(sample):
            classification.append("outlier")
            avgs.append(sample)
            stdevs.append(sample)
            continue
        if values_left < 1 or active_group is None:
            values_left = 0
            while values_left < 1:  # Ignore empty groups (should not happen).
                active_group = group_list.pop()
                values_left = len(active_group.run_list)
            avg = active_group.stats.avg
            stdv = active_group.stats.stdev
            classification.append(active_group.comment)
            avgs.append(avg)
            stdevs.append(stdv)
            values_left -= 1
            continue
        classification.append("normal")
        avgs.append(avg)
        stdevs.append(stdv)
        values_left -= 1
    return classification, avgs, stdevs


def table_news(data: pd.DataFrame, job: str) -> list:
    """
    """

    job_data = data.loc[(data["job"] == job)]
    failed = job_data["lst_failed"].to_list()[0]

    return [
        dbc.Table.from_dataframe(pd.DataFrame.from_dict({
            "Job": job_data["job"],
            "Build": job_data["build"],
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
        }), bordered=True, striped=True, hover=True, size="sm", color="light")
    ]
