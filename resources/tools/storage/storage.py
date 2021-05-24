#!/usr/bin/env/env python3

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

"""Storage Backend Class."""

from json import loads
from struct import unpack
from gzip import GzipFile

from boto3 import Session
from botocore import exceptions

S3_API_LIMIT = 1048576


class Storage:
    """Class implementing storage object retrieval.
    S3 Select API allows us to retrieve a subset of data by using simple SQL
    expressions. By using Select API to retrieve only the data needed by the
    application, drastic performance improvements can be achieved.
    """
    def __init__(self, endpoint_url, bucket, profile_name):
        """Class init function to create S3 client object.

        :param endpoint_url: S3 storage endpoint url.
        :param bucket: S3 parent bucket.
        :param profile_name: S3 storage configuration.
        :type endpoint_url: str
        :type bucket: str
        :type profile_name: str
        """
        self.endpoint_url = endpoint_url
        self.bucket = bucket
        self.profile_name = profile_name

        self.session = Session(profile_name=self.profile_name)
        self.client = self.session.client(
            service_name=u"s3", endpoint_url=self.endpoint_url
        )
        self.resource = self.session.resource(
            service_name=u"s3", endpoint_url=self.endpoint_url
        )

    def __repr__(self):
        """Return a string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return (
            f"Storage(endpoint_url={self.endpoint_url!r}, "
            f"bucket={self.bucket!r}, "
            f"profile_name={self.profile_name!r})"
        )

    def _get_matching_s3_keys(
            self, bucket, prefix=u"", suffix=u""):
        """This function generates the keys in an S3 bucket. Function act as
        a Python generator object.

        :param bucket: Name of the S3 bucket.
        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        :type bucket: str
        :type prefix: str
        :type suffix: str
        :raises RuntimeError: If connection to storage fails.
        """
        kwargs = {
            u"Bucket": bucket
        }

        prefixes = (prefix, ) if isinstance(prefix, str) else prefix

        for key_prefix in prefixes:
            kwargs[u"Prefix"] = key_prefix
            try:
                paginator = self.client.get_paginator(u"list_objects_v2")
                for page in paginator.paginate(**kwargs):
                    try:
                        contents = page[u"Contents"]
                    except KeyError:
                        break

                    for obj in contents:
                        key = obj[u"Key"]
                        if key.endswith(suffix):
                            yield obj
            except exceptions.EndpointConnectionError:
                raise RuntimeError(
                    u"Connection Error!"
                )

    def _get_matching_s3_content(
            self, key, expression):
        """This function filters the contents of an S3 object based on a simple
        structured query language (SQL) statement. In the request, along with
        the SQL expression, we are specifying JSON serialization of the object.
        S3 uses this format to parse object data into records, and returns only
        records that match the specified SQL expression. Data serialization
        format for the response is set to JSON.

        :param key: S3 Key (file path).
        :param expression: S3 compatible SQL query.
        :type key: str
        :type expression: str
        :returns: JSON content of interest.
        :rtype: str
        :raises RuntimeError: If connection to storage fails.
        :raises ValueError: If JSON reading fails.
        """
        try:
            content = self.client.select_object_content(
                Bucket=self.bucket,
                Key=key,
                ExpressionType=u"SQL",
                Expression=expression,
                InputSerialization={
                    u"JSON": {
                        u"Type": u"Document"
                    },
                    u"CompressionType": u"GZIP"
                },
                OutputSerialization={
                    u"JSON": {
                        u"RecordDelimiter": u""
                    }
                }
            )
            records = u""
            for event in content[u"Payload"]:
                if u"Records" in event:
                    records = event[u"Records"][u"Payload"].decode(u"utf-8")
            return records
        except exceptions.EndpointConnectionError:
            raise RuntimeError(
                u"Connection Error!"
            )
        except exceptions.EventStreamError:
            raise ValueError(
                u"Malformed JSON content!"
            )

    def _get_matching_s3_object(
            self, key):
        """Gets full S3 object. If the file is gzip'd it will be unpacked.

        :param key: Name of the S3 key (file).
        :type key: str
        :returns: JSON file of interest.
        :rtype: str
        :raises RuntimeError: If connection to storage fails.
        """
        try:
            streaming_object = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )[u"Body"]
            with GzipFile(fileobj=streaming_object) as gzipfile:
                content = gzipfile.read()
            return content
        except exceptions.EndpointConnectionError:
            raise RuntimeError(
                u"Connection Error!"
            )

    def _get_matching_s3_length(
            self, key):
        """Gets the file size of S3 object. If the file is gzip'd the packed
        size is reported.

        :param key: Name of the S3 key (file).
        :type key: str
        :returns: File size in bytes. Defaults to 0 if any error.
        :rtype: int
        :raises RuntimeError: If connection to storage fails.
        """
        try:
            compressed_size = self.client.get_object(
                Bucket=self.bucket,
                Key=key
            )[u"ContentLength"]
            last_four_bytes = self.client.get_object(
                Bucket=self.bucket,
                Key=key,
                Range=f"bytes={compressed_size-4}-{compressed_size}"
            )[u"Body"]
            return unpack(u"I", last_four_bytes.read(4))[0]
        except exceptions.EndpointConnectionError:
            return 0

    def is_large_file(
            self, key):
        """Returns True if file is larger then 1MB that S3 select allows.

        :param key: Name of the S3 key (file).
        :type key: str
        :returns: Returns True if file is large then 1MB that S3 select allows.
        :rtype: bool
        """
        return bool(
            self._get_matching_s3_length(key=key[u"Key"]) > S3_API_LIMIT
        )

    def s3_file_processing(
            self, prefix=u"", suffix=u"json.gz",
            expression=u"select * from s3object s"):
        """Batch S3 key processing. Function retrieves list of files and use
        S3 Select API to query content.

        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        :param expression: S3 compatible SQL query (optional).
        :type prefix: str
        :type suffix: str
        :type expression: str
        """
        key_iterator = self._get_matching_s3_keys(
            bucket=self.bucket,
            prefix=prefix,
            suffix=suffix
        )

        for key in key_iterator:
            try:
                yield key[u"Key"], loads(
                    self._get_matching_s3_content(
                        key=key[u"Key"], expression=expression
                    )
                )
            except ValueError:
                return

    def s3_dump_file_processing(
            self, prefix=u"", suffix=u"json.gz"):
        """Batch S3 key processing. Function retrieves list of files and use
        S3 Get Object API to query content.

        :param prefix: Only fetch keys that start with this prefix (optional).
        :param suffix: Only fetch keys that end with this suffix (optional).
        :type prefix: str
        :type suffix: str
        """
        key_iterator = self._get_matching_s3_keys(
            bucket=self.bucket,
            prefix=prefix,
            suffix=suffix
        )

        for key in key_iterator:
            try:
                yield key[u"Key"], loads(
                    self._get_matching_s3_object(
                        key=key[u"Key"]
                    )
                )
            except ValueError:
                return
