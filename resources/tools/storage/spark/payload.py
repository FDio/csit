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

"""CSIT ETL."""

from datetime import datetime, timedelta
from json import dump, load
from pytz import utc

import awswrangler as wr
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SparkSession
from awsglue.transforms import *
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *


DBG_MAX_DF=50
DBG_TRUNCATE=False
S3_BUCKET=u"fdio-logs-s3-cloudfront-index"
PATH=f"s3://{S3_BUCKET}/vex-yul-rot-jenkins-1/csit-vpp-perf"
SUFFIX=u"info.json.gz"
IGNORE_SUFFIX=[u"teardown.info.json.gz", u"setup.info.json.gz"]
LAST_MODIFIED_BEGIN=utc.localize(datetime.strptime(u"2021-11-19", u"%Y-%m-%d"))
LAST_MODIFIED_END=LAST_MODIFIED_BEGIN + timedelta(5)


def schema_dump(schema, option):
    """ """
    with open(f"schema_{option}.json", u"w") as f:
        dump(schema.jsonValue(), f, indent=4, sort_keys=True)

def schema_load(option):
    """ """
    with open(f"schema_{option}.json", u"r") as f:
        return StructType.fromJson(load(f))

def schema_from_json(file):
    """ """
    spark \
        .read \
        .option(u"multiline", u"true") \
        .json(file) \
        .printSchema()


if __name__ == "__main__":

    # create GlueContext and get Spark Session
    appName = "PySpark CSIT ETL"
    master = "local[8]"
    spark = SparkSession.builder \
        .appName(appName) \
        .master(master) \
        .getOrCreate()

    glue_context = GlueContext(SparkContext.getOrCreate())
    spark = glue_context.spark_session
    spark.sparkContext.setLogLevel(u"WARN")

    # files of interest
    path_list = wr.s3.list_objects(
        path=PATH,
        suffix=SUFFIX,
        last_modified_begin=LAST_MODIFIED_BEGIN,
        last_modified_end=LAST_MODIFIED_END,
        ignore_suffix=IGNORE_SUFFIX,
        ignore_empty=True
    )

    # load schemas
    schema_ndrpdr = schema_load(u"ndrpdr")
    schema_soak = schema_load(u"soak")
    schema_mrr = schema_load(u"mrr")

    # create empty DF out of schemas
    df_ndrpdr = spark.sparkContext.emptyRDD().toDF(schema_ndrpdr)
    df_soak = spark.sparkContext.emptyRDD().toDF(schema_soak)
    df_mrr = spark.sparkContext.emptyRDD().toDF(schema_mrr)

    # select
    for path in path_list:
        print(path)
        if "mrr" in path:
            df_loaded = spark \
                .read \
                .option(u"multiline", u"true") \
                .schema(schema_mrr) \
                .json(path)
            df_mrr = df_mrr.union(df_loaded)
        elif "ndrpdr" in path:
            df_loaded = spark \
                .read \
                .option(u"multiline", u"true") \
                .schema(schema_ndrpdr) \
                .json(path)
            df_ndrpdr = df_ndrpdr.union(df_loaded)
        elif "soak" in path:
            df_loaded = spark \
                .read \
                .option(u"multiline", u"true") \
                .schema(schema_soak) \
                .json(path)
            df_soak = df_soak.union(df_loaded)

    dyf = DynamicFrame.fromDF(df_ndrpdr, glue_context, u"dyf")
    df_unnest = UnnestFrame.apply(frame=dyf)
    dyf_dropfields = DropNullFields.apply(frame=df_unnest)
    dyf_dropfields.toDF().show(DBG_MAX_DF, truncate=DBG_TRUNCATE)

    dyf = DynamicFrame.fromDF(df_mrr, glue_context, u"dyf")
    df_unnest = UnnestFrame.apply(frame=dyf)
    dyf_dropfields = DropNullFields.apply(frame=df_unnest)
    dyf_dropfields.toDF().show(DBG_MAX_DF, truncate=DBG_TRUNCATE)

    dyf = DynamicFrame.fromDF(df_soak, glue_context, u"dyf")
    df_unnest = UnnestFrame.apply(frame=dyf)
    dyf_dropfields = DropNullFields.apply(frame=df_unnest)
    dyf_dropfields.toDF().show(DBG_MAX_DF, truncate=DBG_TRUNCATE)
