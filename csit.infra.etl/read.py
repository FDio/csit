#!/usr/bin/env python3

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

"""ETL script running on top of the s3://"""

from os import environ
from time import time

import awswrangler as wr
from awswrangler.exceptions import EmptyDataFrame
from boto3 import session


S3_LOGS_BUCKET="fdio-logs-s3-cloudfront-index"
S3_DOCS_BUCKET="fdio-docs-s3-cloudfront-index"

my_filter = lambda x: True if x["test_type"] == "mrr" else False

start = time()
df = wr.s3.read_parquet(
    path=f"s3://{S3_DOCS_BUCKET}/csit/sandbox/parquet/trending",
    path_suffix="parquet",
    ignore_empty=True,
    use_threads=True,
    dataset=True,
    partition_filter=my_filter,
    boto3_session=session.Session(
        aws_access_key_id=environ["OUT_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=environ["OUT_AWS_SECRET_ACCESS_KEY"],
        region_name=environ["OUT_AWS_DEFAULT_REGION"]
    )
)
end = time()
print(df.to_string())
print(end - start)

print(
    wr.s3.size_objects(
        path=f"s3://{S3_DOCS_BUCKET}/csit/sandbox/parquet/trending",
        boto3_session=session.Session(
            aws_access_key_id=environ["OUT_AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=environ["OUT_AWS_SECRET_ACCESS_KEY"],
        )
    )
)
