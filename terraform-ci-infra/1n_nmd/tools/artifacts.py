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
import mimetypes
import os

from boto3 import resource
from botocore.client import Config

ENDPOINT_URL = u"http://storage.service.consul:9000"
AWS_ACCESS_KEY_ID = u"storage"
AWS_SECRET_ACCESS_KEY = u"Storage1234"
REGION_NAME = u"yul1"


def upload(storage, input_dir):
    """Upload function will recursively upload anything in input folder to
    destination directory of same name.

    Example:
      - input: /home/user
      - bucket: logs
      - destination: logs.fd.io/home/user

    :param storage: S3 bucket object.
    :param input_dir: Input directory to upload.
    :type storage: Bucket
    :type input_dir: str
    """
    mime = mimetypes.MimeTypes()

    for path, subdirs, files in os.walk(input_dir):
        for file in files:
            _path = path.replace(input_dir, u"")
            _dir = input_dir[1:] if input_dir[0] == "/" else input_dir
            _file = os.path.normpath(f"{_dir}/{_path}/{file}")
            _local_file = os.path.join(path, file)
            print(f"uploading: {_local_file} to: {_file}", end=u"")
            storage.upload_file(
                _local_file,
                _file,
                ExtraArgs={
                    u"ContentType": mime.guess_type(_file)[0]
                }
            )
            print(u" ... [success]")


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

    # Create main resource.
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

    upload(
        storage=storage.Bucket(f"{args.bucket}.fd.io"),
        input_dir=args.dir
    )


if __name__ == u"__main__":
    main()
