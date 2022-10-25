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
    """
    """

    def __init__(
            self,
            in_data: any=None,
            data_type: str="dataframe",
            tests: list=list()
        ) -> None:
        """
        """
        
        if not tests:
            raise RuntimeError("No tests defined.")
        if in_data is None:
            raise RuntimeError("No input data.")

        if data_type == "dataframe":
            df = pd.DataFrame()
            for itm in tests:
                sel_data = select_trending_data(in_data, itm)
                if sel_data is not None:
                    df = pd.concat([df, sel_data], ignore_index=True)
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
        elif data_type == "json":
            df = pd.read_json(in_data)
        else:
            raise RuntimeError(
                "Invalid data type. It must be one of 'dataframe' or 'json'"
            )

        # df.info(verbose=True, memory_usage="deep")

        self._data = df

    def to_json(self) -> dict:
        """"
        """
        return self._data.to_json()

    def get_metrics(self) -> set:
        """Return a set of unique metrics.
        """
        pass
