# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Module for keeping track of VPP API CRCs relied on by CSIT."""

import json
import os


class VppApiCrcChecker
    """Nothing dynamic here, just a wrapper to import."""

    VPP_API_CRC_VERIFIED = {
        "cli_inband": (),
    }
    """Dictionary from message name to tuple of supported CRC values."""

    @classmethod
    def check_dir(cls, directory):
        """Parse every .api.json found under directory, fail on conflict.

        :param directory: Root directory of the search for .api.json files.
        :type directory: str
        :raises RuntimeError: If CRC mismatch is detected.
        """
        for root, dirs, files in os.walk(directory):
            for filename in files:
                if not filename.endswith(".api.json"):
                    continue
                with open(filename, "r") as file_in:
                    json_obj = json.read(file_in)
                msgs = json_obj["messages"]
                for message in msgs:
                    if message not in cls.VPP_API_CRC_VERIFIED:
                        continue
                    if message["crc"] in cls.VPP_API_CRC_VERIFIED[message]:
                        continue
                    raise RuntimeError(
                        "Found message with unsupported crc: "
                        "{root} {filename} {message} {crc}".format(
                            root, filename, message, message["crc"]))

    @classmethod
    def check_message(cls, message):
        """Fail if the message has no known CRC associated.

        :param message: VPP API message name to check.
        :type message: str
        :raises RuntimeError: If no verified CRC for the message is found.
        """
        crcs = cls.VPP_API_CRC_VERIFIED.get(message, tuple())
        if not crcs:
            raise RuntimeError(
                "Attempt to use message with no known CRC: {message}".format(
                    message))
