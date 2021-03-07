#!/usr/bin/python3

# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""Storage utilities library."""

import argparse
import gzip
import os
from mimetypes import MimeTypes

from boto3 import resource
from botocore.client import Config


ENDPOINT_URL = u"http://storage.service.consul:9000"
AWS_ACCESS_KEY_ID = u"storage"
AWS_SECRET_ACCESS_KEY = u"Storage1234"
REGION_NAME = u"yul1"
COMPRESS_MIME = (
    u"text/html",
    u"text/xml",
    u"application/octet-stream"
)


def compress(src_fpath):
    """Compress a single file.

    :param src_fpath: Input file path.
    :type src_fpath: str
    """
    with open(src_fpath, u"rb") as orig_file:
        with gzip.open(f"{src_fpath}.gz", u"wb") as zipped_file:
            zipped_file.writelines(orig_file)


def upload(storage, bucket, src_fpath, dst_fpath):
    """Upload single file to destination bucket.

    :param storage: S3 storage resource.
    :param bucket: S3 bucket name.
    :param src_fpath: Input file path.
    :param dst_fpath: Destination file path on remote storage.
    :type storage: Object
    :type bucket: str
    :type src_fpath: str
    :type dst_fpath: str
    """
    mime = MimeTypes().guess_type(src_fpath)[0]
    if not mime:
        mime = "application/octet-stream"

    if mime in COMPRESS_MIME and bucket in "logs":
        compress(src_fpath)
        src_fpath = f"{src_fpath}.gz"
        dst_fpath = f"{dst_fpath}.gz"

    storage.Bucket(f"{bucket}.fd.io").upload_file(
        src_fpath,
        dst_fpath,
        ExtraArgs={
            u"ContentType": mime
        }
    )
    print(f"https://{bucket}.nginx.service.consul/{dst_fpath}")


def upload_recursive(storage, bucket, src_fpath):
    """Recursively uploads input folder to destination.

    Example:
      - bucket: logs
      - src_fpath: /home/user
      - dst_fpath: logs.fd.io/home/user

    :param storage: S3 storage resource.
    :param bucket: S3 bucket name.
    :param src_fpath: Input folder path.
    :type storage: Object
    :type bucket: str
    :type src_fpath: str
    """
    for path, _, files in os.walk(src_fpath):
        for file in files:
            _path = path.replace(src_fpath, u"")
            _dir = src_fpath[1:] if src_fpath[0] == "/" else src_fpath
            _dst_fpath = os.path.normpath(f"{_dir}/{_path}/{file}")
            _src_fpath = os.path.join(path, file)
            upload(storage, bucket, _src_fpath, _dst_fpath)


def main():
    """Main function for storage manipulation."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        u"-d", u"--dir", required=True, type=str,
        help=u"Directory to upload to storage."
    )
    parser.add_argument(
        u"-b", u"--bucket", required=True, type=str,
        help=u"Target bucket on storage."
    )
    args = parser.parse_args()

    # Create main storage resource.
    storage = resource(
        u"s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=Config(
            signature_version=u"s3v4"
        ),
        region_name=REGION_NAME
    )

    upload_recursive(
        storage=storage,
        bucket=args.bucket,
        src_fpath=args.dir
    )


if __name__ == u"__main__":
    main()
