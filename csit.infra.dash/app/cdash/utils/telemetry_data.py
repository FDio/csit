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

"""A module implementing the parsing of OpenMetrics data and elementary
operations with it.
"""

import logging
import pandas as pd

from ..trending.graphs import select_trending_data


class TelemetryData:
    """A class to store and manipulate the telemetry data.
    """

    def __init__(self, tests: list=list()) -> None:
        """Initialize the object.

        :param in_data: Input data.
        :param tests: List of selected tests.
        :type in_data: pandas.DataFrame
        :type tests: list
        """

        self._tests = tests
        self._data = None
        self._unique_metrics = list()
        self._unique_metrics_labels = list()

    def from_dataframe(self, in_data: pd.DataFrame=pd.DataFrame()) -> None:
        """Read the input from pandas DataFrame.

        This method must be call at the begining to create all data structures.
        """

        if in_data.empty:
            return 

        df = pd.DataFrame()
        metrics = set()  # A set of unique metrics

        # Create a dataframe with metrics for selected tests:
        for itm in self._tests:
            sel_data = select_trending_data(in_data, itm)
            if sel_data is not None:
                df = pd.concat([df, sel_data], ignore_index=True)
        # Use only neccessary data:
        df = df[
            [
                "job",
                "build",
                "dut_type",
                "dut_version",
                "start_time",
                "passed",
                "test_id",
                "test_type",
                "result_receive_rate_rate_avg",
                "result_receive_rate_rate_stdev",
                "result_receive_rate_rate_unit",
                "result_pdr_lower_rate_unit",
                "result_ndr_lower_rate_unit",
                "telemetry"
            ]
        ]
        # Transform metrics from strings to dataframes:
        lst_telemetry = list()
        for _, row in df.iterrows():
            d_telemetry = {
                "metric": list(),
                "labels": list(),  # list of tuple(label, value)
                "value": list(),
                "timestamp": list()
            }
            for itm in row["telemetry"]:
                itm_lst = itm.replace("'", "").rsplit(" ", maxsplit=2)
                metric, labels = itm_lst[0].split("{")
                d_telemetry["metric"].append(metric)
                d_telemetry["labels"].append(
                    [tuple(x.split("=")) for x in labels[:-1].split(",")]
                )
                d_telemetry["value"].append(itm_lst[1])
                d_telemetry["timestamp"].append(itm_lst[2])
            lst_telemetry.append(pd.DataFrame(data=d_telemetry))
            metrics.update(d_telemetry["metric"])
        df["telemetry"] = lst_telemetry

        self._data = df
        self._unique_metrics = sorted(metrics)

    def from_json(self, in_data: dict) -> None:
        """Read the input data from json.
        """

        df = pd.read_json(in_data)
        lst_telemetry = list()
        metrics = set()  # A set of unique metrics
        for _, row in df.iterrows():
            telemetry = pd.DataFrame(row["telemetry"])
            lst_telemetry.append(telemetry)
            metrics.update(telemetry["metric"].to_list())
        df["telemetry"] = lst_telemetry

        self._data = df
        self._unique_metrics = sorted(metrics)

    def from_metrics(self, in_data: set) -> None:
        """Read only the metrics.
        """
        self._unique_metrics = in_data

    def from_metrics_with_labels(self, in_data: dict) -> None:
        """Read only metrics with labels.
        """
        self._unique_metrics_labels = pd.DataFrame.from_dict(in_data)

    def to_json(self) -> str:
        """Return the data transformed from dataframe to json.

        :returns: Telemetry data transformed to a json structure.
        :rtype: dict
        """
        return self._data.to_json()

    @property
    def unique_metrics(self) -> list:
        """Return a set of unique metrics.

        :returns: A set of unique metrics.
        :rtype: set
        """
        return self._unique_metrics

    @property
    def unique_metrics_with_labels(self) -> dict:
        """
        """
        return self._unique_metrics_labels.to_dict()

    def get_selected_labels(self, metrics: list) -> dict:
        """Return a dictionary with labels (keys) and all their possible values
        (values) for all selected 'metrics'.

        :param metrics: List of metrics we are interested in.
        :type metrics: list
        :returns: A dictionary with labels and all their possible values.
        :rtype: dict
        """

        df_labels = pd.DataFrame()
        tmp_labels = dict()
        for _, row in self._data.iterrows():
            telemetry = row["telemetry"]
            for itm in metrics:
                df = telemetry.loc[(telemetry["metric"] == itm)]
                df_labels = pd.concat([df_labels, df], ignore_index=True)
                for _, tm in df.iterrows():
                    for label in tm["labels"]:
                        if label[0] not in tmp_labels:
                            tmp_labels[label[0]] = set()
                        tmp_labels[label[0]].add(label[1])

        selected_labels = dict()
        for key in sorted(tmp_labels):
            selected_labels[key] = sorted(tmp_labels[key])

        self._unique_metrics_labels = df_labels[["metric", "labels"]].\
            loc[df_labels[["metric", "labels"]].astype(str).\
                drop_duplicates().index]

        return selected_labels

    @property
    def str_metrics(self) -> str:
        """
        """
        metrics = str()
        for _, row in self._unique_metrics_labels.iterrows():
            labels = ','.join([f"{itm[0]}='{itm[1]}'" for itm in row["labels"]])
            metrics += f"{row['metric']}{{{labels}}}\n"
        return metrics[:-1]

    def search_selected_metrics_by_labels(self, labels: dict) -> list:
        """
        """
        metrics = list()

        # search in self._unique_metrics_labels metrics with 'labels'.

        return metrics

    def search_unique_metrics(self, string: str) -> list:
        """Return a list of metrics which name includes the given string.

        :param string: A string which must be in the name of metric.
        :type string: str
        :returns: A list of metrics which name includes the given string.
        :rtype: list
        """
        return [itm for itm in self._unique_metrics if string in itm]
