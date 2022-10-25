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

import pandas as pd

from ..trending.graphs import select_trending_data


class TelemetryData:
    """A class to store and manipulate the telemetry data.
    """

    def __init__(
            self,
            in_data: any=None,
            data_type: str="dataframe",
            tests: list=list()
        ) -> None:
        """Initialize the object.

        :param in_data: Input data. The class accepts these types of input data:
            - pandas dataframe
            - json structure
            - list (set) of unique metrics
        :param datatype: Type of input data, accepted values:
            - dataframe, for pandas dataframe,
            - json, for json structure,
            - metrics, for list of unique metrics.
        :param tests: List of selected tests.
        :type in_data: pandas.DataFrame, dict, list, set
        :type datatype: str
        :type tests: list
        """

        if not tests:
            raise RuntimeError("No tests defined.")
        if in_data is None:
            raise RuntimeError("No input data.")

        df = None  # Future pandas dataframe
        metrics = set()  # A set of unique metrics

        # Create a dataframe with metrics for selected tests:
        if data_type == "dataframe":
            df = pd.DataFrame()
            for itm in tests:
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
            # Transform metrics from stings to dataframes:
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

        elif data_type == "json":
            df = pd.read_json(in_data)
            lst_telemetry = list()
            for _, row in df.iterrows():
                telemetry = pd.DataFrame(row["telemetry"])
                lst_telemetry.append(telemetry)
                metrics.update(telemetry["metric"].to_list())
            df["telemetry"] = lst_telemetry

        elif data_type == "metrics":
            metrics = in_data

        else:
            raise RuntimeError(
                "Invalid data type. It must be one of 'dataframe', 'json' or"
                "'metrics'."
            )

        self._data = df
        self._unique_metrics = sorted(metrics)

    def to_json(self) -> dict:
        """Return the data transformed from dataframe to json.

        :returns: Telemetry data transformed to a json structure.
        :rtype: dict
        """
        return self._data.to_json()

    @property
    def unique_metrics(self) -> set:
        """Return a set of unique metrics.

        :returns: A set of unique metrics.
        :rtype: set
        """
        return self._unique_metrics

    def search_unique_metrics(self, string: str) -> list:
        """Return a list of metrics which name includes the given string.

        :param string: A string which must be in the name of metric.
        :type string: str
        :returns: A list of metrics which name includes the given string.
        :rtype: list
        """
        return [itm for itm in self._unique_metrics if string in itm]
