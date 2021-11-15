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

"""ETL Backend."""

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter

import awswrangler as wr
from boto3 import Session

AWS_PROFILE_NAME=u"default"
S3_ENDPOINT_URL=u"http://minio.service.consul:9001"
S3_BUCKET=u"fdio-logs-s3-cloudfront-index"


class ETL:
    """Class implementing storage object retrieval.
    S3 Select API allows us to retrieve a subset of data by using simple SQL
    expressions. By using Select API to retrieve only the data needed by the
    application, drastic performance improvements can be achieved.
    """
    def __init__(
            self, endpoint_url=None, bucket=None, profile_name="default"):
        """Class init function to create S3 client object.

        :param endpoint_url: S3 storage endpoint url.
        :param bucket: S3 parent bucket.
        :param profile_name: S3 storage configuration.
        :type endpoint_url: str
        :type bucket: str
        :type profile_name: str
        """
        self.bucket = bucket
        self.session = Session(profile_name=profile_name)

        if endpoint_url:
            self.client = self.session.client(
                service_name=u"s3", endpoint_url=endpoint_url
            )
        else:
            self.client = self.session.client(
                service_name=u"s3"
            )

    def _get_matching_s3_keys(
            self, prefix=u"", suffix=u"info.json.gz"):
        """This function generates the keys in an S3 bucket. Function act as
        a Python generator object.

        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        :type prefix: str
        :type suffix: str
        :raises RuntimeError: If connection to storage fails.
        """
        return wr.s3.list_objects(
            path=f"s3://{self.bucket}/{prefix}",
            suffix=suffix,
            ignore_empty=True,
            boto3_session=self.session
        )

    def _get_matching_s3_content(
            self, path, sql):
        """This function filters the contents of an S3 object based on a simple
        structured query language (SQL) statement. In the request, along with
        the SQL expression, we are specifying JSON serialization of the object.
        S3 uses this format to parse object data into records, and returns only
        records that match the specified SQL expression. Data serialization
        format for the response is set to JSON.

        :param key: S3 path (file path).
        :param sql: S3 compatible SQL query.
        :type path: str
        :type sql: str
        :returns: Pandas Dataframe.
        :rtype: DataFrame
        """
        return wr.s3.select_query(
            sql=sql,
            path=path,
            input_serialization=u"JSON",
            input_serialization_params={
                u"Type": u"Document",
            },
            boto3_session=self.session,
            compression=u"gzip",
            use_threads=True
        )

    def s3_file_processing(
            self, prefix=u"", suffix=u"info.json.gz",
            sql=u"select * from s3object s"):
        """Batch S3 key processing. Function retrieves list of files and use
        S3 Select API to query content.

        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        :param sql: S3 compatible SQL query (optional).
        :type prefix: str
        :type suffix: str
        :type sql: str
        """
        path_list = self._get_matching_s3_keys(
            prefix=prefix,
            suffix=suffix
        )

        for path in path_list:
            try:
                pd = self._get_matching_s3_content(path=path, sql=sql)
                if not pd.empty:
                    print(pd)
                #yield key, self._get_matching_s3_content(
                #    path=path, sql=sql
                #)
            except ValueError:
                return


def main():
    """
    Main entry function when called from CLI.
    """
    parser = ArgumentParser(
        description=u"S3 Storage Backend Operation.",
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        u"-e", u"--expression", required=False, type=str,
        default=u"select * from s3object s",
        help=u"S3 compatible SQL query."
    )

    args = parser.parse_args()

    json_iterator = ETL(
        bucket=S3_BUCKET,
        profile_name=AWS_PROFILE_NAME
    ).s3_file_processing(
        prefix=u"vex-yul-rot-jenkins-1/csit-vpp-perf", sql=args.expression
    )


if __name__ == u"__main__":
    main()
