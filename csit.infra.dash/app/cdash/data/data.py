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

"""Prepare data for Plotly Dash applications.
"""

import logging
import resource
import awswrangler as wr
import pandas as pd
import pyarrow as pa

from yaml import load, FullLoader, YAMLError
from datetime import datetime, timedelta
from time import time
from pytz import UTC
from awswrangler.exceptions import EmptyDataFrame, NoFilesFound
from pyarrow.lib import ArrowInvalid, ArrowNotImplementedError

from ..utils.constants import Constants as C


# If True, pyarrow.Schema is generated. See also condition in the method
# _write_parquet_schema.
# To generate schema, select only one data set in data.yaml file.
GENERATE_SCHEMA = False


class Data:
    """Gets the data from parquets and stores it for further use by dash
    applications.
    """

    def __init__(self, data_spec_file: str) -> None:
        """Initialize the Data object.

        :param data_spec_file: Path to file specifying the data to be read from
            parquets.
        :type data_spec_file: str
        :raises RuntimeError: if it is not possible to open data_spec_file or it
            is not a valid yaml file.
        """

        # Inputs:
        self._data_spec_file = data_spec_file

        # Specification of data to be read from parquets:
        self._data_spec = list()

        # Data frame to keep the data:
        self._data = {
            "statistics": pd.DataFrame(),
            "trending": pd.DataFrame(),
            "iterative": pd.DataFrame(),
            "coverage": pd.DataFrame()
        }

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

    @staticmethod
    def _get_list_of_files(
            path,
            last_modified_begin=None,
            last_modified_end=None,
            days=None
        ) -> list:
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
            logging.debug("\n".join(file_list))
        except NoFilesFound as err:
            logging.error(f"No parquets found.\n{err}")
        except EmptyDataFrame as err:
            logging.error(f"No data.\n{err}")

        return file_list

    def _validate_columns(self, data_type: str) -> str:
        """Check if all columns are present in the dataframe.

        :param data_type: The data type defined in data.yaml
        :type data_type: str
        :returns: Error message if validation fails, otherwise empty string.
        :rtype: str
        """
        defined_columns = set()
        for data_set in self._data_spec:
            if data_set.get("data_type", str()) == data_type:
                defined_columns.update(data_set.get("columns", set()))

        if not defined_columns:
            return "No columns defined in the data set(s)."

        if self.data[data_type].empty:
            return "No data."

        ret_msg = str()
        for col in defined_columns:
            if col not in self.data[data_type].columns:
                if not ret_msg:
                    ret_msg = "Missing columns: "
                else:
                    ret_msg += ", "
                ret_msg += f"{col}"
        return ret_msg

    @staticmethod
    def _write_parquet_schema(
            path,
            partition_filter=None,
            columns=None,
            validate_schema=False,
            last_modified_begin=None,
            last_modified_end=None,
            days=None
        ) -> None:
        """Auxiliary function to write parquet schemas. Use it instead of
        "_create_dataframe_from_parquet" in "read_all_data".

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
        """
        if days:
            last_modified_begin = datetime.now(tz=UTC) - timedelta(days=days)

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
            last_modified_end=last_modified_end,
            chunked=1
        )

        for itm in df:
            try:
                # Specify the condition or remove it:
                if all((
                        pd.api.types.is_string_dtype(itm["column_name"]),
                        pd.api.types.is_string_dtype(itm["telemetry"][0])
                    )):
                    schema = pa.Schema.from_pandas(itm)
                    pa.parquet.write_metadata(
                        schema, f"{C.PATH_TO_SCHEMAS}_tmp_schema"
                    )
                    logging.info(schema.to_string(
                        truncate_metadata=False,
                        show_field_metadata=True,
                        show_schema_metadata=True
                    ))
                    break
            except KeyError:
                pass

    @staticmethod
    def _create_dataframe_from_parquet(
            path,
            partition_filter=None,
            columns=None,
            validate_schema=False,
            last_modified_begin=None,
            last_modified_end=None,
            days=None,
            schema=None
        ) -> pd.DataFrame:
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
        :param schema: Path to schema to use when reading data from the parquet.
        :type path: Union[str, List[str]]
        :type partition_filter: Callable[[Dict[str, str]], bool], optional
        :type columns: List[str], optional
        :type validate_schema: bool, optional
        :type last_modified_begin: datetime, optional
        :type last_modified_end: datetime, optional
        :type days: integer, optional
        :type schema: string
        :returns: Pandas DataFrame or None if DataFrame cannot be fetched.
        :rtype: DataFrame
        """
        df = pd.DataFrame()
        start = time()
        if days:
            last_modified_begin = datetime.now(tz=UTC) - timedelta(days=days)
        try:
            df = wr.s3.read_parquet(
                path=path,
                path_suffix="parquet",
                ignore_empty=True,
                schema=schema,
                validate_schema=validate_schema,
                use_threads=True,
                dataset=True,
                columns=columns,
                partition_filter=partition_filter,
                last_modified_begin=last_modified_begin,
                last_modified_end=last_modified_end,
                dtype_backend="pyarrow"
            )

            df.info(verbose=True, memory_usage="deep")
            logging.debug(
                f"\nCreation of dataframe {path} took: {time() - start}\n"
            )
        except (ArrowInvalid, ArrowNotImplementedError) as err:
            logging.error(f"Reading of data from parquets FAILED.\n{repr(err)}")
        except NoFilesFound as err:
            logging.error(
                f"Reading of data from parquets FAILED.\n"
                f"No parquets found in specified time period.\n"
                f"Nr of days: {days}\n"
                f"last_modified_begin: {last_modified_begin}\n"
                f"{repr(err)}"
            )
        except EmptyDataFrame as err:
            logging.error(
                f"Reading of data from parquets FAILED.\n"
                f"No data in parquets in specified time period.\n"
                f"Nr of days: {days}\n"
                f"last_modified_begin: {last_modified_begin}\n"
                f"{repr(err)}"
            )

        return df

    def read_all_data(self, days: int=None) -> dict:
        """Read all data necessary for all applications.

        :param days: Number of days to filter. If None, all data will be
            downloaded.
        :type days: int
        :returns: A dictionary where keys are names of parquets and values are
            the pandas dataframes with fetched data.
        :rtype: dict(str: pandas.DataFrame)
        """

        data_lists = {
            "statistics": list(),
            "trending": list(),
            "iterative": list(),
            "coverage": list()
        }

        logging.info("\n\nReading data:\n" + "-" * 13 + "\n")
        for data_set in self._data_spec:
            logging.info(
                f"\n\nReading data for {data_set['data_type']} "
                f"{data_set['partition_name']} {data_set.get('release', '')}\n"
            )
            schema_file = data_set.get("schema", None)
            if schema_file:
                try:
                    schema = pa.parquet.read_schema(
                        f"{C.PATH_TO_SCHEMAS}{schema_file}"
                    )
                except FileNotFoundError as err:
                    logging.error(repr(err))
                    logging.error("Proceeding without schema.")
                    schema = None
            else:
                schema = None
            partition_filter = lambda part: True \
                if part[data_set["partition"]] == data_set["partition_name"] \
                    else False
            if data_set["data_type"] in ("trending", "statistics"):
                time_period = days
            else:
                time_period = None

            if GENERATE_SCHEMA:
                # Generate schema:
                Data._write_parquet_schema(
                    path=data_set["path"],
                    partition_filter=partition_filter,
                    columns=data_set.get("columns", None),
                    days=time_period
                )
                return

            # Read data:
            data = Data._create_dataframe_from_parquet(
                path=data_set["path"],
                partition_filter=partition_filter,
                columns=data_set.get("columns", None),
                days=time_period,
                schema=schema
            )
            if data_set["data_type"] in ("iterative", "coverage"):
                data["release"] = data_set["release"]
                data["release"] = data["release"].astype("category")

            data_lists[data_set["data_type"]].append(data)

        logging.info(
            "\n\nData post-processing, validation and summary:\n" +
            "-" * 45 + "\n"
        )
        for key in self._data.keys():
            logging.info(f"\n\nDataframe {key}:\n")
            if len(data_lists[key]) == 0:
                self._data[key] = pd.DataFrame()
            elif len(data_lists[key]) == 1:
                self._data[key] = data_lists[key][0]
            else:
                self._data[key] = pd.concat(
                    data_lists[key],
                    ignore_index=True,
                    copy=False
                )
            self._data[key].info(verbose=True, memory_usage="deep")
            err_msg = self._validate_columns(key)
            if err_msg:
                self._data[key] = pd.DataFrame()
                logging.error(
                    f"Data validation FAILED.\n"
                    f"{err_msg}\n"
                    "Generated dataframe replaced by an empty dataframe."
                )

        mem_alloc = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000
        logging.info(f"\n\nMemory allocation: {mem_alloc:.0f}MB\n")

        return self._data
