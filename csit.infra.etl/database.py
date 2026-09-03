#!/usr/bin/env python3

"""GLUE script running on top of the s3://"""

from os import environ

import awswrangler as wr
from boto3 import session


S3_DOCS_BUCKET=environ.get("S3_DOCS_BUCKET", "csit-docs-s3-cloudfront-index")
GLUE_DATABASE=environ.get("GLUE_DATABASE", "csit")


try:
    boto3_session = session.Session(
        aws_access_key_id=environ["OUT_AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=environ["OUT_AWS_SECRET_ACCESS_KEY"],
        region_name=environ["OUT_AWS_DEFAULT_REGION"]
    )
except KeyError:
    boto3_session = session.Session()

wr.catalog.create_database(
    name=GLUE_DATABASE,
    description="FD.io CSIT statistics",
    exist_ok=True,
    boto3_session=boto3_session,
)

datasets = {
    "trending": "trending",
    "iterative_rls2610": "iterative_rls2610",
    "coverage_rls2610": "coverage_rls2610",
    "stats": "stats",
}

for table, prefix in datasets.items():
    wr.s3.store_parquet_metadata(
        path=f"s3://{S3_DOCS_BUCKET}/csit/parquet/{prefix}/",
        database=GLUE_DATABASE,
        table=table,
        dataset=True,
        mode="overwrite",
        catalog_versioning=True,
        ignore_empty=True,
        ignore_null=True,
        description=f"FD.io CSIT {table} dataset",
        parameters={"source": "csit.infra.etl"},
        boto3_session=boto3_session,
    )
