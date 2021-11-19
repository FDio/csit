#!/usr/bin/env python3

# Copyright (c) 2021 Cisco and/or its affiliates.
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

from datetime import date, datetime, timedelta
from json import dump, load
from pytz import utc

import awswrangler as wr
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, lit
from pyspark.sql.types import StructType, StructField, StringType, FloatType

APP_NAME = "etl_script_s3"
MASTER = "local[*]"
S3_BUCKET="fdio-logs-s3-cloudfront-index"
S3_SILO="vex-yul-rot-jenkins-1"
PATH=f"s3://{S3_BUCKET}/{S3_SILO}/csit-vpp-perf"
SUFFIX="info.json.gz"
IGNORE_SUFFIX=[
    "suite.info.json.gz",
    "setup.info.json.gz",
    "teardown.info.json.gz",
    "suite.output.info.json.gz",
    "setup.output.info.json.gz",
    "teardown.output.info.json.gz"
]
LAST_MODIFIED_BEGIN=utc.localize(datetime.strptime("2021-11-29", "%Y-%m-%d"))
LAST_MODIFIED_END=LAST_MODIFIED_BEGIN + timedelta(10)


def schema_dump(schema, option):
    """Dumps Spark DataFrame schema into JSON file.

    :param schema: DataFrame schema.
    :type schema: StructType
    :param option: File name suffix for the DataFrame schema.
    :type option: string
    """
    path = f"/job_queue/schema_{option}.json"
    with open(path, "w", encoding="UTF-8") as f_schema:
        dump(schema.jsonValue(), f_schema, indent=4, sort_keys=True)


def schema_load(option):
    """Loads Spark DataFrame schema from JSON file.

    :param option: File name suffix for the DataFrame schema.
    :type option: string
    :returns: DataFrame schema.
    :rtype: StructType
    """
    path = f"/job_queue/schema_{option}.json"
    with open(path, "r", encoding="UTF-8") as f_schema:
        return StructType.fromJson(load(f_schema))


def schema_dump_from_json(option):
    """Loads JSON with data and dumps Spark DataFrame schema into JSON file.

    :param option: File name suffix for the JSON data.
    :type option: string
    """
    path = f"/job_queue/data_{option}.json"
    schema_dump(spark \
        .read \
        .option("multiline", "true") \
        .json(path) \
        .schema, option
    )


def s3_path_get_job(path):
    """Parse S3 path and returns Jenkins job id.

    :param path: S3 path.
    :type path: string
    :returns: Jenkins job id.
    :rtype: string
    """
    return path.split("/")[4]


def s3_path_get_build(path):
    """Parse S3 path and returns Jenkins build id.

    :param path: S3 path.
    :type path: string
    :returns: Jenkins build id.
    :rtype: integer
    """
    return int(path.split("/")[5])


def s3_path_get_root_suite_file(path):
    """Parse S3 path and returns Root Suite JSON.

    :param path: S3 path.
    :type path: string
    :returns: Root Suite JSON.
    :rtype: string
    """
    return "/".join(path.split("/")[:7]) + "/suite.info.json.gz"


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


def process_dataframe(schema_name, paths):
    """Processes Spark DataFrame.

    :param schema_name: Schema name.
    :type schema_name: string
    :param paths: S3 paths to process.
    :type paths: list
    :returns: Spark DataFrame.
    :rtype: DataFrame
    """
    # load schemas
    schema = schema_load(schema_name)
    drop_subset = [
        "dut_type", "dut_version",
        "suite_id", "suite_name",
        "status",
        "test_id", "test_name",
        "version"
    ]

    info_schema = StructType([
        StructField("version", StringType(), True),
        StructField("duration", FloatType(), True)
    ])

    # create empty DF out of schemas
    sdf = spark.createDataFrame([], schema)

    # filter list
    filtered = [path for path in paths if schema_name in path]

    # select
    for path in filtered:
        print(path)
        schema_info = spark \
            .read \
            .option("multiline", "true") \
            .schema(info_schema) \
            .json(s3_path_get_root_suite_file(path)) \
            .collect()[0][1]

        sdf_loaded = spark \
            .read \
            .option("multiline", "true") \
            .schema(schema) \
            .json(path) \
            .withColumn("job", lit(s3_path_get_job(path))) \
            .withColumn("build", lit(s3_path_get_build(path))) \
            .withColumn("duration", lit(schema_info))
        sdf = sdf.unionByName(sdf_loaded, allowMissingColumns=True)

    # drop rows with all nulls and drop null in critical frames
    sdf = sdf.na.drop(how="all")
    sdf = sdf.na.drop(how="any", thresh=None, subset=drop_subset)

    # cast the columns
    sdf = sdf \
        .replace(["PASS", "FAIL"], ["True", "False"], subset=["status"]) \
        .withColumn("status", col("status").cast("boolean"))
    # flatten frame
    sdf = flatten_frame(sdf)

    return sdf


# create SparkContext and GlueContext
spark_context = SparkContext(master=MASTER, appName=APP_NAME).getOrCreate()
spark_context.setLogLevel("WARN")
glue_context = GlueContext(spark_context)
spark = glue_context.spark_session

#schema_dump_from_json("ndrpdr")
#schema_dump_from_json("soak")
#schema_dump_from_json("mrr")

# files of interest
path_list = wr.s3.list_objects(
    path=PATH,
    suffix=SUFFIX,
    last_modified_begin=LAST_MODIFIED_BEGIN,
    last_modified_end=LAST_MODIFIED_END,
    ignore_suffix=IGNORE_SUFFIX,
    ignore_empty=True
)

for result_type in ["mrr", "ndrpdr", "soak"]:
    out_sdf = process_dataframe(result_type, path_list)
    out_sdf.show(truncate=False)
    out_sdf \
        .withColumn("Year", lit(datetime.now().year)) \
        .withColumn("Month", lit(datetime.now().month)) \
        .withColumn("Day", lit(datetime.now().day)) \
        .repartition(1) \
        .write \
        .partitionBy("Year", "Month", "Day") \
        .mode("overwrite") \
        .parquet(f"/job_queue/{result_type}.parquet")
