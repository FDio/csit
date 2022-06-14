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

"""Prepare data for Plotly Dash."""

import logging

from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta
from time import time
from pytz import UTC
from pandas import DataFrame

import awswrangler as wr

from awswrangler.exceptions import EmptyDataFrame, NoFilesFound


class Data:
    """
    """

    def __init__(self, data_spec_file: str, debug: bool=False) -> None:
        """
        """

        # Inputs:
        self._data_spec_file = data_spec_file
        self._debug = debug

        # Specification of data to be read from parquets:
        self._data_spec = None

        # Data frame to keep the data:
        self._data = None

        # Read from files:
        try:
            with open(self._data_spec_file, "r") as file_read:
                self._data_spec = load(file_read, Loader=FullLoader)
        except IOError as err:
            raise RuntimeError(
                f"Not possible to open the file {self._data_spec_file,}\n{err}"
            )
        except YAMLError as err:
            raise RuntimeError(
                f"An error occurred while parsing the specification file "
                f"{self._data_spec_file,}\n"
                f"{err}"
            )

    @property
    def data(self):
        return self._data

    def _get_columns(self, parquet: str) -> list:
        try:
            return self._data_spec[parquet]["columns"]
        except KeyError as err:
            raise RuntimeError(
                f"The parquet {parquet} is not defined in the specification "
                f"file {self._data_spec_file} or it does not have any columns "
                f"specified.\n{err}"
            )

    def _get_path(self, parquet: str) -> str:
        try:
            return self._data_spec[parquet]["path"]
        except KeyError as err:
            raise RuntimeError(
                f"The parquet {parquet} is not defined in the specification "
                f"file {self._data_spec_file} or it does not have the path "
                f"specified.\n{err}"
            )

    def _create_dataframe_from_parquet(self,
        path, partition_filter=None, columns=None,
        validate_schema=False, last_modified_begin=None,
        last_modified_end=None, days=None) -> DataFrame:
        """Read parquet stored in S3 compatible storage and returns Pandas
        Dataframe.

        :param path: S3 prefix (accepts Unix shell-style wildcards)
            (e.g. s3://bucket/prefix) or list of S3 objects paths
            (e.g. [s3://bucket/key0, s3://bucket/key1]).
        :param partition_filter: Callback Function filters to apply on PARTITION
            columns (PUSH-DOWN filter). This function MUST receive a single
            argument (Dict[str, str]) where keys are partitions names and values
            are partitions values. Partitions values will be always strings
            extracted from S3. This function MUST return a bool, True to read
            the partition or False to ignore it. Ignored if dataset=False.
        :param columns: Names of columns to read from the file(s).
        :param validate_schema: Check that individual file schemas are all the
            same / compatible. Schemas within a folder prefix should all be the
            same. Disable if you have schemas that are different and want to
            disable this check.
        :param last_modified_begin: Filter the s3 files by the Last modified
            date of the object. The filter is applied only after list all s3
            files.
        :param last_modified_end: Filter the s3 files by the Last modified date
            of the object. The filter is applied only after list all s3 files.
        :type path: Union[str, List[str]]
        :type partition_filter: Callable[[Dict[str, str]], bool], optional
        :type columns: List[str], optional
        :type validate_schema: bool, optional
        :type last_modified_begin: datetime, optional
        :type last_modified_end: datetime, optional
        :returns: Pandas DataFrame or None if DataFrame cannot be fetched.
        :rtype: DataFrame
        """
        df = None
        start = time()
        if days:
            last_modified_begin = datetime.now(tz=UTC) - timedelta(days=days)
        try:
            df = wr.s3.read_parquet(
                path=path,
                path_suffix="parquet",
                ignore_empty=True,
                validate_schema=validate_schema,
                use_threads=True,
                dataset=True,
                columns=columns,
                partition_filter=partition_filter,
                last_modified_begin=last_modified_begin,
                last_modified_end=last_modified_end
            )
            if self._debug:
                df.info(verbose=True, memory_usage='deep')
                logging.info(
                    u"\n"
                    f"Creation of dataframe {path} took: {time() - start}"
                    u"\n"
                )
        except NoFilesFound as err:
            logging.error(f"No parquets found.\n{err}")
        except EmptyDataFrame as err:
            logging.error(f"No data.\n{err}")

        self._data = df
        return df

    def read_stats(self, days: int=None) -> tuple:
        """Read Suite Result Analysis data partition from parquet.
        """
        l_stats = lambda part: True if part["stats_type"] == "sra" else False
        l_mrr = lambda part: True if part["test_type"] == "mrr" else False
        l_ndrpdr = lambda part: True if part["test_type"] == "ndrpdr" else False

        return (
            self._create_dataframe_from_parquet(
                path=self._get_path("statistics"),
                partition_filter=l_stats,
                columns=self._get_columns("statistics"),
                days=days
            ),
            self._create_dataframe_from_parquet(
                path=self._get_path("statistics-trending"),
                partition_filter=l_mrr,
                columns=self._get_columns("statistics-trending"),
                days=days
            ),
            self._create_dataframe_from_parquet(
                path=self._get_path("statistics-trending"),
                partition_filter=l_ndrpdr,
                columns=self._get_columns("statistics-trending"),
                days=days
            )
        )

    def read_news(self, days: int=None) -> tuple:
        """Read Suite Result Analysis data partition from parquet.
        """
        l_mrr = lambda part: True if part["test_type"] == "mrr" else False
        l_ndrpdr = lambda part: True if part["test_type"] == "ndrpdr" else False

        return (
            self._create_dataframe_from_parquet(
                path=self._get_path("statistics-trending"),
                partition_filter=l_mrr,
                columns=self._get_columns("statistics-trending"),
                days=days
            ),
            self._create_dataframe_from_parquet(
                path=self._get_path("statistics-trending"),
                partition_filter=l_ndrpdr,
                columns=self._get_columns("statistics-trending"),
                days=days
            )
        )

    def read_trending_mrr(self, days: int=None) -> DataFrame:
        """Read MRR data partition from parquet.
        """
        lambda_f = lambda part: True if part["test_type"] == "mrr" else False

        return self._create_dataframe_from_parquet(
            path=self._get_path("trending-mrr"),
            partition_filter=lambda_f,
            columns=self._get_columns("trending-mrr"),
            days=days
        )

    def read_trending_ndrpdr(self, days: int=None) -> DataFrame:
        """Read NDRPDR data partition from iterative parquet.
        """
        lambda_f = lambda part: True if part["test_type"] == "ndrpdr" else False

        return self._create_dataframe_from_parquet(
            path=self._get_path("trending-ndrpdr"),
            partition_filter=lambda_f,
            columns=self._get_columns("trending-ndrpdr"),
            days=days
        )

    def read_iterative_mrr(self, release: str) -> DataFrame:
        """Read MRR data partition from iterative parquet.
        """
        lambda_f = lambda part: True if part["test_type"] == "mrr" else False

        return self._create_dataframe_from_parquet(
            path=self._get_path("iterative-mrr").format(release=release),
            partition_filter=lambda_f,
            columns=self._get_columns("iterative-mrr")
        )

    def read_iterative_ndrpdr(self, release: str) -> DataFrame:
        """Read NDRPDR data partition from parquet.
        """
        lambda_f = lambda part: True if part["test_type"] == "ndrpdr" else False

        return self._create_dataframe_from_parquet(
            path=self._get_path("iterative-ndrpdr").format(release=release),
            partition_filter=lambda_f,
            columns=self._get_columns("iterative-ndrpdr")
        )
