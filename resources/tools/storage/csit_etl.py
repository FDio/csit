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

import sys

import awswrangler as wr
from boto3 import Session
from pyspark.context import SparkContext
from pyspark.sql.types import *
from pyspark.sql import Row, SparkSession

AWS_PROFILE_NAME=u"default"
S3_BUCKET=u"fdio-logs-s3-cloudfront-index"


if __name__ == "__main__":

    boto3_session = Session(profile_name=AWS_PROFILE_NAME)
    path = f"s3://{S3_BUCKET}/vex-yul-rot-jenkins-1/csit-vpp-perf"
    proxy = False
    sql = u"select s.results.ndrpdr.ndr from s3object s"
    suffix = u"info.json.gz"

    # create SparkSession
    spark = SparkSession.builder \
        .master("local") \
        .appName("spark-select") \
        .getOrCreate()

    # filtered schema
    st = StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), False),
    ])

    # files of interest
    path_list = wr.s3.list_objects(
        path=path,
        suffix=suffix,
        ignore_empty=True,
        boto3_session=boto3_session
    )

    # select
    for path in path_list:
        try:
            df = wr.s3.select_query(
                sql=sql,
                path=path,
                input_serialization=u"JSON",
                input_serialization_params={
                    u"Type": u"Document",
                },
                boto3_session=boto3_session,
                compression=u"gzip",
                use_threads=True
            )
            if not df.empty:
                print(df)

            #df = spark \
            #    .read \
            #    .format('JSON') \
            #    .schema(st) \
            #    .load(path)
            ## show all rows.
            #df.show()
        except ValueError:
            pass
