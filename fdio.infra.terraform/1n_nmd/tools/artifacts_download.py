#!/usr/bin/python3

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

"""Storage utilities library."""

from boto3 import resource
from botocore.client import Config


ENDPOINT_URL = u"http://storage.service.consul:9000"
AWS_ACCESS_KEY_ID = u"storage"
AWS_SECRET_ACCESS_KEY = u"Storage1234"
REGION_NAME = u"yul1"
LOGS_BUCKET = f"logs.fd.io"


if __name__ == u"__main__":
    """Main function for storage manipulation."""

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

    storage.Bucket(LOGS_BUCKET).download_file(
        "/vex-yul-rot-jenkins-1/csit-vpp-perf-report-iterative-2101-3n-skx/47/archives/output_info.xml.gz",
        "output.xml.gz"
    )