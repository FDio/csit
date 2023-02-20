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

"""A module implementing the parsing of OpenMetrics data and elementary
operations with it.
"""


import binascii
import zlib
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
        self._unique_metrics_labels = pd.DataFrame()
        self._selected_metrics_labels = pd.DataFrame()

    def from_dataframe(self, in_data: pd.DataFrame=pd.DataFrame()) -> None:
        """Read the input from pandas DataFrame.

        This method must be called at the beginning to create all data
        structures.
        """

        if in_data.empty:
            return

        df = pd.DataFrame()
        metrics = set()  # A set of unique metrics

        # Create a dataframe with metrics for selected tests:
        for itm in self._tests:
            sel_data = select_trending_data(in_data, itm)
            if sel_data is not None:
                sel_data["test_name"] = itm["id"]
                df = pd.concat([df, sel_data], ignore_index=True, copy=False)
        # Use only neccessary data:
        df = df[[
            "job",
            "build",
            "dut_type",
            "dut_version",
            "start_time",
            "passed",
            "test_name",
            "test_type",
            "result_receive_rate_rate_avg",
            "result_receive_rate_rate_stdev",
            "result_receive_rate_rate_unit",
            "result_pdr_lower_rate_value",
            "result_pdr_lower_rate_unit",
            "result_ndr_lower_rate_value",
            "result_ndr_lower_rate_unit",
            "telemetry"
        ]]
        # Transform metrics from strings to dataframes:
        lst_telemetry = list()
        for _, row in df.iterrows():
            d_telemetry = {
                "metric": list(),
                "labels": list(),  # list of tuple(label, value)
                "value": list(),
                "timestamp": list()
            }
            
            # If there is no telemetry data, use empty dictionary
            if row["telemetry"] is None or isinstance(row["telemetry"], float):
                lst_telemetry.append(pd.DataFrame(data=d_telemetry))
                continue

            # Read telemetry data
            # - list of uncompressed strings List[str, ...], or
            # - list with only one compressed string List[str]
            try:
                tm_data = zlib.decompress(
                    binascii.a2b_base64(row["telemetry"][0].encode())
                ).decode().split("\n")
            except (binascii.Error, zlib.error, AttributeError, IndexError):
                tm_data = row["telemetry"]

            # Pre-process telemetry data
            for itm in tm_data:
                itm_lst = itm.replace("'", "").rsplit(" ", maxsplit=2)
                metric, labels = itm_lst[0].split("{")
                d_telemetry["metric"].append(metric)
                d_telemetry["labels"].append(
                    [tuple(x.split("=")) for x in labels[:-1].split(",")]
                )
                d_telemetry["value"].append(itm_lst[1])
                d_telemetry["timestamp"].append(itm_lst[2])

            metrics.update(d_telemetry["metric"])
            lst_telemetry.append(pd.DataFrame(data=d_telemetry))
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
                df_labels = pd.concat(
                    [df_labels, df],
                    ignore_index=True,
                    copy=False
                )
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
        """Returns all unique metrics as a string.
        """
        return TelemetryData.metrics_to_str(self._unique_metrics_labels)

    @staticmethod
    def metrics_to_str(in_data: pd.DataFrame) -> str:
        """Convert metrics from pandas dataframe to string. Metrics in string
        are separated by '\n'.

        :param in_data: Metrics to be converted to a string.
        :type in_data: pandas.DataFrame
        :returns: Metrics as a string.
        :rtype: str
        """
        metrics = str()
        for _, row in in_data.iterrows():
            labels = ','.join([f"{itm[0]}='{itm[1]}'" for itm in row["labels"]])
            metrics += f"{row['metric']}{{{labels}}}\n"
        return metrics[:-1]

    def search_unique_metrics(self, string: str) -> list:
        """Return a list of metrics which name includes the given string.

        :param string: A string which must be in the name of metric.
        :type string: str
        :returns: A list of metrics which name includes the given string.
        :rtype: list
        """
        return [itm for itm in self._unique_metrics if string in itm]

    def filter_selected_metrics_by_labels(
            self,
            selection: dict
        ) -> pd.DataFrame:
        """Filter selected unique metrics by labels and their values.

        :param selection: Labels and their values specified by the user.
        :type selection: dict
        :returns: Pandas dataframe with filtered metrics.
        :rtype: pandas.DataFrame
        """

        def _is_selected(labels: list, sel: dict) -> bool:
            """Check if the provided 'labels' are selected by the user.

            :param labels: List of labels and their values from a metric. The
                items in this lists are two-item-lists whre the first item is
                the label and the second one is its value.
            :param sel: User selection. The keys are the selected lables and the
                values are lists with label values.
            :type labels: list
            :type sel: dict
            :returns: True if the 'labels' are selected by the user.
            :rtype: bool
            """
            passed = list()
            labels = dict(labels)
            for key in sel.keys():
                if key in list(labels.keys()):
                    if sel[key]:
                        passed.append(labels[key] in sel[key])
                    else:
                        passed.append(True)
                else:
                    passed.append(False)
            return bool(passed and all(passed))

        self._selected_metrics_labels = pd.DataFrame()
        for _, row in self._unique_metrics_labels.iterrows():
            if _is_selected(row["labels"], selection):
                self._selected_metrics_labels = pd.concat(
                    [self._selected_metrics_labels, row.to_frame().T],
                    ignore_index=True,
                    axis=0,
                    copy=False
                )
        return self._selected_metrics_labels

    def select_tm_trending_data(self, selection: dict) -> pd.DataFrame:
        """Select telemetry data for trending based on user's 'selection'.

        The output dataframe includes these columns:
            - "job",
            - "build",
            - "dut_type",
            - "dut_version",
            - "start_time",
            - "passed",
            - "test_name",
            - "test_id",
            - "test_type",
            - "result_receive_rate_rate_avg",
            - "result_receive_rate_rate_stdev",
            - "result_receive_rate_rate_unit",
            - "result_pdr_lower_rate_value",
            - "result_pdr_lower_rate_unit",
            - "result_ndr_lower_rate_value",
            - "result_ndr_lower_rate_unit",
            - "tm_metric",
            - "tm_value".

        :param selection: User's selection (metrics and labels).
        :type selection: dict
        :returns: Dataframe with selected data.
        :rtype: pandas.DataFrame
        """

        df = pd.DataFrame()

        if self._data is None:
            return df
        if self._data.empty:
            return df
        if not selection:
            return df

        df_sel = pd.DataFrame.from_dict(selection)
        for _, row in self._data.iterrows():
            tm_row = row["telemetry"]
            for _, tm_sel in df_sel.iterrows():
                df_tmp = tm_row.loc[tm_row["metric"] == tm_sel["metric"]]
                for _, tm in df_tmp.iterrows():
                    if tm["labels"] == tm_sel["labels"]:
                        labels = ','.join(
                            [f"{itm[0]}='{itm[1]}'" for itm in tm["labels"]]
                        )
                        row["tm_metric"] = f"{tm['metric']}{{{labels}}}"
                        row["tm_value"] = tm["value"]
                        new_row = row.drop(labels=["telemetry", ])
                        df = pd.concat(
                            [df, new_row.to_frame().T],
                            ignore_index=True,
                            axis=0,
                            copy=False
                        )
        return df
