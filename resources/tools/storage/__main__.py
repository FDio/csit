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

"""S3 Storage Backend."""

from json import dumps

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .storage import Storage


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

    json_iterator = Storage(
        endpoint_url=u"http://storage.service.consul:9000",
        bucket=u"docs",
        profile_name=u"nomad-s3"
    ).s3_dump_file_processing()

    for item in json_iterator:
        print(dumps(item, indent=4, sort_keys=False))


if __name__ == u"__main__":
    main()
