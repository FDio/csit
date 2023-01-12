#!/usr/bin/env python3

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

"""ETL script running on top of the localhost"""

from datetime import datetime
from json import dump, load
from pathlib import Path

from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, lit, regexp_replace
from pyspark.sql.types import StructType


PATH="/app/tests"
SUFFIX="info.json"
IGNORE_SUFFIX=[
    "suite.info.json",
    "setup.info.json",
    "teardown.info.json",
    "suite.output.info.json",
    "setup.output.info.json",
    "teardown.output.info.json"
]


def schema_dump(schema, option):
    """Dumps Spark DataFrame schema into JSON file.

    :param schema: DataFrame schema.
    :type schema: StructType
    :param option: File name suffix for the DataFrame schema.
    :type option: string
    """
    with open(f"trending_{option}.json", "w", encoding="UTF-8") as f_schema:
        dump(schema.jsonValue(), f_schema, indent=4, sort_keys=True)


def schema_load(option):
    """Loads Spark DataFrame schema from JSON file.

    :param option: File name suffix for the DataFrame schema.
    :type option: string
    :returns: DataFrame schema.
    :rtype: StructType
    """
    with open(f"trending_{option}.json", "r", encoding="UTF-8") as f_schema:
        return StructType.fromJson(load(f_schema))


def schema_dump_from_json(option):
    """Loads JSON with data and dumps Spark DataFrame schema into JSON file.

    :param option: File name suffix for the JSON data.
    :type option: string
    """
    schema_dump(spark \
        .read \
        .option("multiline", "true") \
        .json(f"data_{option}.json") \
        .schema, option
    )


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
    schema = schema_load(schema_name)

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
            .withColumn("job", lit("local")) \
            .withColumn("build", lit("unknown"))
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
paths = []
for file in Path(PATH).glob(f"**/*{SUFFIX}"):
    if file.name not in IGNORE_SUFFIX:
        paths.append(str(file))

for schema_name in ["mrr", "ndrpdr", "soak"]:
    out_sdf = process_json_to_dataframe(schema_name, paths)
    out_sdf.show()
    out_sdf.printSchema()
    out_sdf \
        .withColumn("year", lit(datetime.now().year)) \
        .withColumn("month", lit(datetime.now().month)) \
        .withColumn("day", lit(datetime.now().day)) \
        .repartition(1) \
        .write \
        .partitionBy("test_type", "year", "month", "day") \
        .mode("append") \
        .parquet("local.parquet")
