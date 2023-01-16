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

"""Prepare data for Plotly Dash applications.
"""

import logging
import awswrangler as wr

from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta
from time import time
from pytz import UTC
from pandas import DataFrame
from awswrangler.exceptions import EmptyDataFrame, NoFilesFound


ADD_DUMMY_TELEMETRY_DATA = True
PATH_DUMMY_TELEMETRY_MRR = "cdash/data/vpp_runtime_mrr.json"
PATH_DUMMY_TELEMETRY_NDRPDR = "cdash/data/vpp_runtime_ndrpdr.json"


class Data:
    """Gets the data from parquets and stores it for further use by dash
    applications.
    """

    def __init__(self, data_spec_file: str, debug: bool=False) -> None:
        """Initialize the Data object.

        :param data_spec_file: Path to file specifying the data to be read from
            parquets.
        :param debug: If True, the debuf information is printed to stdout.
        :type data_spec_file: str
        :type debug: bool
        :raises RuntimeError: if it is not possible to open data_spec_file or it
            is not a valid yaml file.
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

        # Read dummy telemetry data:
        if ADD_DUMMY_TELEMETRY_DATA:
            import json
            try:
                with open(PATH_DUMMY_TELEMETRY_MRR, "r") as fr:
                    self._tele_mrr = json.load(fr)["telemetry"]
            except (IOError, json.JSONDecodeError, KeyError) as err:
                logging.warning(
                    f"It is not possible to read or decode the file with dummy "
                    f"telemetry data {PATH_DUMMY_TELEMETRY_MRR}\n{err}"
                )
                self._tele_mrr = list()
            try:
                with open(PATH_DUMMY_TELEMETRY_NDRPDR, "r") as fr:
                    self._tele_ndrpdr = json.load(fr)["telemetry"]
            except (IOError, json.JSONDecodeError, KeyError) as err:
                logging.warning(
                    f"It is not possible to read or decode the file with dummy "
                    f"telemetry data {PATH_DUMMY_TELEMETRY_NDRPDR}\n{err}"
                )
                self._tele_ndrpdr = list()

    @property
    def data(self):
        return self._data

    def _get_columns(self, parquet: str) -> list:
        """Get the list of columns from the data specification file to be read
        from parquets.

        :param parquet: The parquet's name.
        :type parquet: str
        :raises RuntimeError: if the parquet is not defined in the data
            specification file or it does not have any columns specified.
        :returns: List of columns.
        :rtype: list
        """

        try:
            return self._data_spec[parquet]["columns"]
        except KeyError as err:
            raise RuntimeError(
                f"The parquet {parquet} is not defined in the specification "
                f"file {self._data_spec_file} or it does not have any columns "
                f"specified.\n{err}"
            )

    def _get_path(self, parquet: str) -> str:
        """Get the path from the data specification file to be read from
        parquets.

        :param parquet: The parquet's name.
        :type parquet: str
        :raises RuntimeError: if the parquet is not defined in the data
            specification file or it does not have the path specified.
        :returns: Path.
        :rtype: str
        """

        try:
            return self._data_spec[parquet]["path"]
        except KeyError as err:
            raise RuntimeError(
                f"The parquet {parquet} is not defined in the specification "
                f"file {self._data_spec_file} or it does not have the path "
                f"specified.\n{err}"
            )

    def _get_list_of_files(self,
        path,
        last_modified_begin=None,
        last_modified_end=None,
        days=None) -> list:
        """Get list of interested files stored in S3 compatible storage and
        returns it.

        :param path: S3 prefix (accepts Unix shell-style wildcards)
            (e.g. s3://bucket/prefix) or list of S3 objects paths
            (e.g. [s3://bucket/key0, s3://bucket/key1]).
        :param last_modified_begin: Filter the s3 files by the Last modified
            date of the object. The filter is applied only after list all s3
            files.
        :param last_modified_end: Filter the s3 files by the Last modified date
            of the object. The filter is applied only after list all s3 files.
        :param days: Number of days to filter.
        :type path: Union[str, List[str]]
        :type last_modified_begin: datetime, optional
        :type last_modified_end: datetime, optional
        :type days: integer, optional
        :returns: List of file names.
        :rtype: list
        """
        file_list = list()
        if days:
            last_modified_begin = datetime.now(tz=UTC) - timedelta(days=days)
        try:
            file_list = wr.s3.list_objects(
                path=path,
                suffix="parquet",
                last_modified_begin=last_modified_begin,
                last_modified_end=last_modified_end
            )
            if self._debug:
                logging.info("\n".join(file_list))
        except NoFilesFound as err:
            logging.error(f"No parquets found.\n{err}")
        except EmptyDataFrame as err:
            logging.error(f"No data.\n{err}")

        return file_list

    def _get_dummy_telemetry_data(self, df: DataFrame) -> list:
        """Return the list with dummy telemetry data depending on the test type.
        """

        if df["test_type"] == "mrr":
            return self._tele_mrr
        elif df["test_type"] == "ndrpdr":
            return self._tele_ndrpdr
        else:
            return list()

    def _add_dummy_telemetry_data(self, df: DataFrame) -> DataFrame:
        """Add dummy telemetry data to a dataframe.

        This method adds the column "telemetry" to provided pandas dataframe
        and fills it with dummy telemetry data. It supports ndrpdr amd mrr
        tests.
        The dummy telemetry data is read from json files with the structure:
        {
            "telemetry": [
                "list of strings, each string is a telemetry data item in open
                metrics format"
            ]
        }

        :param df: A pandas dataframe to be filled with dummy telemetry data.
        :type df: pandas.DataFrame
        :returns: A pandas dataframe with "telemetry" column.
        :rtype: pandas.DataFrame
        """
        df["telemetry"] = df.apply(self._get_dummy_telemetry_data, axis=1)
        return df

    def _create_dataframe_from_parquet(self,
        path, partition_filter=None,
        columns=None,
        validate_schema=False,
        last_modified_begin=None,
        last_modified_end=None,
        days=None) -> DataFrame:
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
        :param days: Number of days to filter.
        :type path: Union[str, List[str]]
        :type partition_filter: Callable[[Dict[str, str]], bool], optional
        :type columns: List[str], optional
        :type validate_schema: bool, optional
        :type last_modified_begin: datetime, optional
        :type last_modified_end: datetime, optional
        :type days: integer, optional
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
                if not ADD_DUMMY_TELEMETRY_DATA:
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

        # Add dummy telemetry data:
        if ADD_DUMMY_TELEMETRY_DATA:
            df = self._add_dummy_telemetry_data(df)
            if self._debug:
                df.info(verbose=True, memory_usage='deep')

        self._data = df
        return df

    def check_datasets(self, days: int=None):
        """Read structure from parquet.

        :param days: Number of days back to the past for which the data will be
            read.
        :type days: int
        """
        self._get_list_of_files(path=self._get_path("trending"), days=days)
        self._get_list_of_files(path=self._get_path("statistics"), days=days)

    def read_stats(self, days: int=None) -> tuple:
        """Read statistics from parquet.

        It reads from:
        - Suite Result Analysis (SRA) partition,
        - NDRPDR trending partition,
        - MRR trending partition.

        :param days: Number of days back to the past for which the data will be
            read.
        :type days: int
        :returns: tuple of pandas DataFrame-s with data read from specified
            parquets.
        :rtype: tuple of pandas DataFrame-s
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
                path=self._get_path("statistics-trending-mrr"),
                partition_filter=l_mrr,
                columns=self._get_columns("statistics-trending-mrr"),
                days=days
            ),
            self._create_dataframe_from_parquet(
                path=self._get_path("statistics-trending-ndrpdr"),
                partition_filter=l_ndrpdr,
                columns=self._get_columns("statistics-trending-ndrpdr"),
                days=days
            )
        )

    def read_trending_mrr(self, days: int=None) -> DataFrame:
        """Read MRR data partition from parquet.

        :param days: Number of days back to the past for which the data will be
            read.
        :type days: int
        :returns: Pandas DataFrame with read data.
        :rtype: DataFrame
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

        :param days: Number of days back to the past for which the data will be
            read.
        :type days: int
        :returns: Pandas DataFrame with read data.
        :rtype: DataFrame
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

        :param release: The CSIT release from which the data will be read.
        :type release: str
        :returns: Pandas DataFrame with read data.
        :rtype: DataFrame
        """

        lambda_f = lambda part: True if part["test_type"] == "mrr" else False

        return self._create_dataframe_from_parquet(
            path=self._get_path("iterative-mrr").format(release=release),
            partition_filter=lambda_f,
            columns=self._get_columns("iterative-mrr")
        )

    def read_iterative_ndrpdr(self, release: str) -> DataFrame:
        """Read NDRPDR data partition from parquet.

        :param release: The CSIT release from which the data will be read.
        :type release: str
        :returns: Pandas DataFrame with read data.
        :rtype: DataFrame
        """

        lambda_f = lambda part: True if part["test_type"] == "ndrpdr" else False

        return self._create_dataframe_from_parquet(
            path=self._get_path("iterative-ndrpdr").format(release=release),
            partition_filter=lambda_f,
            columns=self._get_columns("iterative-ndrpdr")
        )
