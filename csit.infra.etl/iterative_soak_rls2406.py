#!/usr/bin/env python3

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

"""ETL script running on top of the s3://"""

from datetime import datetime, timedelta
from json import load
from os import environ
from pytz import utc

import awswrangler as wr
from awswrangler.exceptions import EmptyDataFrame
from awsglue.context import GlueContext
from boto3 import session
from pyspark.context import SparkContext
from pyspark.sql.functions import col, lit, regexp_replace
from pyspark.sql.types import StructType


S3_LOGS_BUCKET=environ.get("S3_LOGS_BUCKET", "fdio-logs-s3-cloudfront-index")
S3_DOCS_BUCKET=environ.get("S3_DOCS_BUCKET", "fdio-docs-s3-cloudfront-index")
PATH=f"s3://{S3_LOGS_BUCKET}/vex-yul-rot-jenkins-1/csit-*-perf-*"
SUFFIX="info.json.gz"
IGNORE_SUFFIX=[
    "suite.info.json.gz",
    "setup.info.json.gz",
    "teardown.info.json.gz",
    "suite.output.info.json.gz",
    "setup.output.info.json.gz",
    "teardown.output.info.json.gz"
]
LAST_MODIFIED_END=utc.localize(
    datetime.strptime(
        f"{datetime.now().year}-{datetime.now().month}-{datetime.now().day}",
        "%Y-%m-%d"
    )
)
LAST_MODIFIED_BEGIN=LAST_MODIFIED_END - timedelta(1)


def flatten_frame(nested_sdf):
    """Unnest Spark DataFrame in case there nested structered columns.

    :param nested_sdf: Spark DataFrame.
    :type nested_sdf: DataFrame
    :returns: Unnest DataFrame.
    :rtype: DataFrame
    """
    stack = [((), nested_sdf)]
    columns = []
    while len(stack) > 0:
        parents, sdf = stack.pop()
        for column_name, column_type in sdf.dtypes:
            if column_type[:6] == "struct":
                projected_sdf = sdf.select(column_name + ".*")
                stack.append((parents + (column_name,), projected_sdf))
            else:
                columns.append(
                    col(".".join(parents + (column_name,))) \
                        .alias("_".join(parents + (column_name,)))
                )
    return nested_sdf.select(columns)


def process_json_to_dataframe(schema_name, paths):
    """Processes JSON to Spark DataFrame.

    :param schema_name: Schema name.
    :type schema_name: string
    :param paths: S3 paths to process.
    :type paths: list
    :returns: Spark DataFrame.
    :rtype: DataFrame
    """
    drop_subset = [
        "dut_type", "dut_version",
        "passed",
        "test_name_long", "test_name_short",
        "test_type",
        "version"
    ]

    # load schemas
    with open(f"iterative_{schema_name}.json", "r", encoding="UTF-8") as f_schema:
        schema = StructType.fromJson(load(f_schema))

    # create empty DF out of schemas
    sdf = spark.createDataFrame([], schema)

    # filter list
    filtered = [path for path in paths if schema_name in path]

    # select
    for path in filtered:
        print(path)

        sdf_loaded = spark \
            .read \
            .option("multiline", "true") \
            .schema(schema) \
            .json(path) \
            .withColumn("job", lit(path.split("/")[4])) \
            .withColumn("build", lit(path.split("/")[5]))
        sdf = sdf.unionByName(sdf_loaded, allowMissingColumns=True)

    # drop rows with all nulls and drop rows with null in critical frames
    sdf = sdf.na.drop(how="all")
    sdf = sdf.na.drop(how="any", thresh=None, subset=drop_subset)

    # flatten frame
    sdf = flatten_frame(sdf)

    return sdf


# create SparkContext and GlueContext
spark_context = SparkContext.getOrCreate()
spark_context.setLogLevel("WARN")
glue_context = GlueContext(spark_context)
spark = glue_context.spark_session

# files of interest
paths = wr.s3.list_objects(
    path=PATH,
    suffix=SUFFIX,
    last_modified_begin=LAST_MODIFIED_BEGIN,
    last_modified_end=LAST_MODIFIED_END,
    ignore_suffix=IGNORE_SUFFIX,
    ignore_empty=True
)

filtered_paths = [path for path in paths if "report-iterative-2406" in path]

out_sdf = process_json_to_dataframe("soak", filtered_paths)
out_sdf.printSchema()
out_sdf = out_sdf \
    .withColumn("year", lit(datetime.now().year)) \
    .withColumn("month", lit(datetime.now().month)) \
    .withColumn("day", lit(datetime.now().day)) \
    .repartition(1)

try:
    boto3_session = session.Session(
        aws_access_key_id=environ["OUT_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=environ["OUT_AWS_SECRET_ACCESS_KEY"],
        region_name=environ["OUT_AWS_DEFAULT_REGION"]
    )
except KeyError:
    boto3_session = session.Session()
)

try:
    wr.s3.to_parquet(
        df=out_sdf.toPandas(),
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/iterative_rls2406",
        dataset=True,
        partition_cols=["test_type", "year", "month", "day"],
        compression="snappy",
        use_threads=True,
        mode="overwrite_partitions",
        boto3_session=boto3_session
    )
except EmptyDataFrame:
    pass
