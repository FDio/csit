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

from logging import info
from time import time

import awswrangler as wr
from awswrangler.exceptions import EmptyDataFrame, NoFilesFound
from boto3 import session


S3_DOCS_BUCKET="fdio-docs-s3-cloudfront-index"

def create_dataframe_from_parquet(
        path, partition_filter=None, columns=None,
        validate_schema=False, last_modified_begin=None,
        last_modified_end=None):
    """Read parquet stored in S3 compatible storage and returns Pandas
    Dataframe.

    :param path: S3 prefix (accepts Unix shell-style wildcards) (e.g.
        s3://bucket/prefix) or list of S3 objects paths (e.g. [s3://bucket/key0,
        s3://bucket/key1]).
    :param partition_filter: Callback Function filters to apply on PARTITION
        columns (PUSH-DOWN filter). This function MUST receive a single argument
        (Dict[str, str]) where keys are partitions names and values are
        partitions values. Partitions values will be always strings extracted
        from S3. This function MUST return a bool, True to read the partition or
        False to ignore it. Ignored if dataset=False.
    :param columns: Names of columns to read from the file(s).
    :param validate_schema: Check that individual file schemas are all the
        same / compatible. Schemas within a folder prefix should all be the
        same. Disable if you have schemas that are different and want to disable
        this check.
    :param last_modified_begin: Filter the s3 files by the Last modified date of
        the object. The filter is applied only after list all s3 files.
    :param last_modified_end: Filter the s3 files by the Last modified date of
        the object. The filter is applied only after list all s3 files.
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
        info(f"Create dataframe {path} took: {time() - start}")
        info(df)
        info(df.info(memory_usage="deep"))
    except NoFilesFound:
        return df

    return df


def read_stats():
    """Read Suite Result Analysis data partition from parquet.
    """
    lambda_f = lambda part: True if part["stats_type"] == "sra" else False

    return create_dataframe_from_parquet(
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/stats",
        partition_filter=lambda_f
    )

def read_trending_mrr():
    """Read MRR data partition from parquet.
    """
    lambda_f = lambda part: True if part["test_type"] == "mrr" else False

    return create_dataframe_from_parquet(
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/trending",
        partition_filter=lambda_f,
        columns=["job", "build", "dut_type", "dut_version", "hosts",
            "start_time", "passed", "test_id", "test_name_long",
            "test_name_short", "version",
            "result_receive_rate_rate_avg",
            "result_receive_rate_rate_stdev",
            "result_receive_rate_rate_unit",
            "result_receive_rate_rate_values"
        ]
    )

def read_iterative_mrr():
    """Read MRR data partition from iterative parquet.
    """
    lambda_f = lambda part: True if part["test_type"] == "mrr" else False

    return create_dataframe_from_parquet(
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/iterative_rls2202",
        partition_filter=lambda_f,
        columns=["job", "build", "dut_type", "dut_version", "hosts",
            "start_time", "passed", "test_id", "test_name_long",
            "test_name_short", "version",
            "result_receive_rate_rate_avg",
            "result_receive_rate_rate_stdev",
            "result_receive_rate_rate_unit",
            "result_receive_rate_rate_values"
        ]
    )

def read_trending_ndrpdr():
    """Read NDRPDR data partition from iterative parquet.
    """
    lambda_f = lambda part: True if part["test_type"] == "ndrpdr" else False

    return create_dataframe_from_parquet(
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/trending",
        partition_filter=lambda_f,
        columns=["job", "build", "dut_type", "dut_version", "hosts",
            "start_time", "passed", "test_id", "test_name_long",
            "test_name_short", "version",
            "result_pdr_upper_rate_unit",
            "result_pdr_upper_rate_value",
            "result_pdr_upper_bandwidth_unit",
            "result_pdr_upper_bandwidth_value",
            "result_pdr_lower_rate_unit",
            "result_pdr_lower_rate_value",
            "result_pdr_lower_bandwidth_unit",
            "result_pdr_lower_bandwidth_value",
            "result_ndr_upper_rate_unit",
            "result_ndr_upper_rate_value",
            "result_ndr_upper_bandwidth_unit",
            "result_ndr_upper_bandwidth_value",
            "result_ndr_lower_rate_unit",
            "result_ndr_lower_rate_value",
            "result_ndr_lower_bandwidth_unit",
            "result_ndr_lower_bandwidth_value",
            "result_latency_reverse_pdr_90_avg",
            "result_latency_reverse_pdr_90_hdrh",
            "result_latency_reverse_pdr_90_max",
            "result_latency_reverse_pdr_90_min",
            "result_latency_reverse_pdr_90_unit",
            "result_latency_reverse_pdr_50_avg",
            "result_latency_reverse_pdr_50_hdrh",
            "result_latency_reverse_pdr_50_max",
            "result_latency_reverse_pdr_50_min",
            "result_latency_reverse_pdr_50_unit",
            "result_latency_reverse_pdr_10_avg",
            "result_latency_reverse_pdr_10_hdrh",
            "result_latency_reverse_pdr_10_max",
            "result_latency_reverse_pdr_10_min",
            "result_latency_reverse_pdr_10_unit",
            "result_latency_reverse_pdr_0_avg",
            "result_latency_reverse_pdr_0_hdrh",
            "result_latency_reverse_pdr_0_max",
            "result_latency_reverse_pdr_0_min",
            "result_latency_reverse_pdr_0_unit",
            "result_latency_forward_pdr_90_avg",
            "result_latency_forward_pdr_90_hdrh",
            "result_latency_forward_pdr_90_max",
            "result_latency_forward_pdr_90_min",
            "result_latency_forward_pdr_90_unit",
            "result_latency_forward_pdr_50_avg",
            "result_latency_forward_pdr_50_hdrh",
            "result_latency_forward_pdr_50_max",
            "result_latency_forward_pdr_50_min",
            "result_latency_forward_pdr_50_unit",
            "result_latency_forward_pdr_10_avg",
            "result_latency_forward_pdr_10_hdrh",
            "result_latency_forward_pdr_10_max",
            "result_latency_forward_pdr_10_min",
            "result_latency_forward_pdr_10_unit",
            "result_latency_forward_pdr_0_avg",
            "result_latency_forward_pdr_0_hdrh",
            "result_latency_forward_pdr_0_max",
            "result_latency_forward_pdr_0_min",
            "result_latency_forward_pdr_0_unit"
        ]
    )

def read_iterative_ndrpdr():
    """Read NDRPDR data partition from parquet.
    """
    lambda_f = lambda part: True if part["test_type"] == "ndrpdr" else False

    return create_dataframe_from_parquet(
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/iterative_rls2202",
        partition_filter=lambda_f,
        columns=["job", "build", "dut_type", "dut_version", "hosts",
            "start_time", "passed", "test_id", "test_name_long",
            "test_name_short", "version",
            "result_pdr_upper_rate_unit",
            "result_pdr_upper_rate_value",
            "result_pdr_upper_bandwidth_unit",
            "result_pdr_upper_bandwidth_value",
            "result_pdr_lower_rate_unit",
            "result_pdr_lower_rate_value",
            "result_pdr_lower_bandwidth_unit",
            "result_pdr_lower_bandwidth_value",
            "result_ndr_upper_rate_unit",
            "result_ndr_upper_rate_value",
            "result_ndr_upper_bandwidth_unit",
            "result_ndr_upper_bandwidth_value",
            "result_ndr_lower_rate_unit",
            "result_ndr_lower_rate_value",
            "result_ndr_lower_bandwidth_unit",
            "result_ndr_lower_bandwidth_value",
            "result_latency_reverse_pdr_90_avg",
            "result_latency_reverse_pdr_90_hdrh",
            "result_latency_reverse_pdr_90_max",
            "result_latency_reverse_pdr_90_min",
            "result_latency_reverse_pdr_90_unit",
            "result_latency_reverse_pdr_50_avg",
            "result_latency_reverse_pdr_50_hdrh",
            "result_latency_reverse_pdr_50_max",
            "result_latency_reverse_pdr_50_min",
            "result_latency_reverse_pdr_50_unit",
            "result_latency_reverse_pdr_10_avg",
            "result_latency_reverse_pdr_10_hdrh",
            "result_latency_reverse_pdr_10_max",
            "result_latency_reverse_pdr_10_min",
            "result_latency_reverse_pdr_10_unit",
            "result_latency_reverse_pdr_0_avg",
            "result_latency_reverse_pdr_0_hdrh",
            "result_latency_reverse_pdr_0_max",
            "result_latency_reverse_pdr_0_min",
            "result_latency_reverse_pdr_0_unit",
            "result_latency_forward_pdr_90_avg",
            "result_latency_forward_pdr_90_hdrh",
            "result_latency_forward_pdr_90_max",
            "result_latency_forward_pdr_90_min",
            "result_latency_forward_pdr_90_unit",
            "result_latency_forward_pdr_50_avg",
            "result_latency_forward_pdr_50_hdrh",
            "result_latency_forward_pdr_50_max",
            "result_latency_forward_pdr_50_min",
            "result_latency_forward_pdr_50_unit",
            "result_latency_forward_pdr_10_avg",
            "result_latency_forward_pdr_10_hdrh",
            "result_latency_forward_pdr_10_max",
            "result_latency_forward_pdr_10_min",
            "result_latency_forward_pdr_10_unit",
            "result_latency_forward_pdr_0_avg",
            "result_latency_forward_pdr_0_hdrh",
            "result_latency_forward_pdr_0_max",
            "result_latency_forward_pdr_0_min",
            "result_latency_forward_pdr_0_unit"
        ]
    )
