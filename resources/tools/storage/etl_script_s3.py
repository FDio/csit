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

"""ETL script running on top of s3://"""

from datetime import datetime, timedelta
from json import dump, load
from pytz import utc
import sys

import awswrangler as wr
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import UnnestFrame, DropNullFields
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import *
from pyspark.sql.types import *


S3_BUCKET=u"fdio-logs-s3-cloudfront-index"
S3_SILO=u"vex-yul-rot-jenkins-1"
PATH=f"s3://{S3_BUCKET}/{S3_SILO}/csit-vpp-perf"
SUFFIX=u"info.json.gz"
IGNORE_SUFFIX=[
    u"suite.info.json.gz",
    u"setup.info.json.gz",
    u"teardown.info.json.gz",
    u"suite.output.info.json.gz",
    u"setup.output.info.json.gz",
    u"teardown.output.info.json.gz"
]
LAST_MODIFIED_BEGIN=utc.localize(datetime.strptime(u"2021-11-23", u"%Y-%m-%d"))
LAST_MODIFIED_END=LAST_MODIFIED_BEGIN + timedelta(5)


def schema_dump(schema, option):
    """ """
    with open(f"/job_queue/schema_{option}.json", u"w") as f:
        dump(schema.jsonValue(), f, indent=4, sort_keys=True)

def schema_load(option):
    """ """
    with open(f"/job_queue/schema_{option}.json", u"r") as f:
        return StructType.fromJson(load(f))

def schema_from_json(file):
    """ """
    spark \
        .read \
        .option(u"multiline", u"true") \
        .json(file) \
        .printSchema()

def s3_path_get_job(path):
    """ """
    return path.split(u"/")[4]

def s3_path_get_build(path):
    """ """
    return int(path.split(u"/")[5])

def process_dataframe(schema_name, paths):
    """ """
    # load schemas
    schema = schema_load(schema_name)

    # create empty DF out of schemas
    df = spark.createDataFrame([], schema)

    # filter list
    filtered = [path for path in paths if schema_name in path]

    # select
    for path in filtered:
        print(path)
        df_loaded = spark \
            .read \
            .option(u"multiline", u"true") \
            .schema(schema) \
            .json(path) \
            .withColumn(u"job", lit(s3_path_get_job(path))) \
            .withColumn(u"build", lit(s3_path_get_build(path)))
        df = df.union(df_loaded)

    # post processing
    dyf = DynamicFrame.fromDF(df, glue_context, u"dyf")
    dyf = UnnestFrame.apply(frame=dyf)
    dyf = DropNullFields.apply(frame=dyf)

    return dyf

# create SparkContext and GlueContext
appName = u"etl_script_s3"
master = u"local[4]"
spark_context = SparkContext(master=master, appName=appName).getOrCreate()
spark_context.setLogLevel(u"WARN")
glue_context = GlueContext(spark_context)
spark = glue_context.spark_session

# files of interest
path_list = wr.s3.list_objects(
    path=PATH,
    suffix=SUFFIX,
    last_modified_begin=LAST_MODIFIED_BEGIN,
    last_modified_end=LAST_MODIFIED_END,
    ignore_suffix=IGNORE_SUFFIX,
    ignore_empty=True
)

df = process_dataframe(u"ndrpdr", path_list).toDF()
df.show(truncate=False)
df.repartition(1).write.partitionBy('test_type').mode('overwrite').parquet(u"/tmp/ndrpdr.parquet")
df = process_dataframe(u"soak", path_list).toDF()
df.show(truncate=False)
df.repartition(1).write.partitionBy('test_type').mode('overwrite').parquet(u"/tmp/soak.parquet")
df = process_dataframe(u"mrr", path_list).toDF()
df.show(truncate=False)
df.repartition(1).write.partitionBy('test_type').mode('overwrite').parquet(u"/tmp/mrr.parquet")
