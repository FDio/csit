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

"""Spark job."""

from datetime import fromisoformat

import awswrangler as wr
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.transforms import *
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

S3_BUCKET="fdio-logs-s3-cloudfront-index"
DBG_MAX_DF=30
DBG_TRUNCATE=False


def lowerCase(str):
    return str.lower()

upperCaseUDF = udf(lambda z:lowerCase(z), StringType())


if __name__ == "__main__":

    path = f"s3://{S3_BUCKET}/vex-yul-rot-jenkins-1/csit-vpp-perf"
    suffix = u"info.json.gz"
    ignore_suffix = [u"teardown.info.json.gz", u"setup.info.json.gz"]

    # create GlueContext and get Spark session
    glue_context = GlueContext(SparkContext.getOrCreate())
    spark = glue_context.spark_session
    spark.sparkContext.setLogLevel(u"WARN")

    # filtered schema
    schema = StructType([
        StructField("duration", StringType(), True),
        StructField("results", StructType([
            StructField("ndrpdr", StructType([
                StructField("latency_unit", StringType(), True),
                StructField("ndr", StructType([
                    StructField("lower", StructType([
                        StructField("bandwidth", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ])),
                        StructField("rate", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ]))
                    ])),
                    StructField("upper", StructType([
                        StructField("bandwidth", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ])),
                        StructField("rate", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ]))
                    ]))
                ])),
                StructField("pdr", StructType([
                    StructField("lower", StructType([
                        StructField("bandwidth", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ])),
                        StructField("rate", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ]))
                    ])),
                    StructField("upper", StructType([
                        StructField("bandwidth", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ])),
                        StructField("rate", StructType([
                            StructField("unit", StringType(), True),
                            StructField("value", DoubleType(), True)
                        ]))
                    ]))
                ]))
            ]))
        ])),
        StructField("end_time", StringType(), True),
        StructField("start_time", StringType(), True),
        StructField("status", StringType(), True),
        StructField("sut_type", StringType(), True),
        StructField("sut_version", StringType(), True),
        StructField("test_id", StringType(), True),
        StructField("test_name", StringType(), True),
        StructField("test_type", StringType(), True),
        StructField("version", StringType(), True)
    ])

    # create empty DF out of schema
    df = spark.sparkContext.emptyRDD().toDF(schema)
    df.printSchema()
    df.show()

    last_modified_begin = fromisoformat("2021-11-19T00:00:00.000000Z")
    last_modified_end = fromisoformat("2021-11-19T23:59:59.999999Z")

    # files of interest
    path_list = wr.s3.list_objects(
        path=path,
        suffix=suffix,
        last_modified_begin=last_modified_begin,
        ignore_suffix=ignore_suffix,
        ignore_empty=True
    )

    # select
    for path in path_list:
        print(path)
        df_loaded = spark \
            .read \
            .option(u"multiline", u"true") \
            .schema(schema) \
            .json(path)
        df = df.union(df_loaded)

    df.show(DBG_MAX_DF, truncate=DBG_TRUNCATE)

    dyf = DynamicFrame.fromDF(df, glue_context, "dyf")
    df_unnest = UnnestFrame.apply(frame=dyf)
    df_unnest.toDF().show(DBG_MAX_DF, truncate=DBG_TRUNCATE)
    dyf_dropfields = DropNullFields.apply(frame=df_unnest)
    dyf_dropfields.toDF().show(DBG_MAX_DF, truncate=DBG_TRUNCATE)
