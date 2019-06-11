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


class VppApiCrcChecker(object):
    """Nothing dynamic here, just a wrapper to import."""

    VPP_API_CRC_VERIFIED = {
        "cli_inband": (),
    }
    """Dictionary from message name to tuple of supported CRC values."""

    VPP_API_CRC_FOUND = dict()
    """Dictionary from message to CRC, filled by what is found and not known."""

    @staticmethod
    def _get_name(msg_obj):
        """FIXME"""
        for item in msg_obj:
            if isinstance(item, (dict, list)):
                continue
            return item

    @staticmethod
    def _get_crc(msg_obj):
        """FIXME"""
        for item in msg_obj:
            if not isinstance(item, dict):
                continue
            if item.keys() != "crc":
                continue
            return item["crc"]

    @classmethod
    def check_dir(cls, directory):
        """Parse every .api.json found under directory, fail on conflict.

        :param directory: Root directory of the search for .api.json files.
        :type directory: str
        :raises RuntimeError: If CRC mismatch is detected.
        """
        for root, _, files in os.walk(directory):
            for filename in files:
                if not filename.endswith(".api.json"):
                    continue
                with open(root + '/' + filename, "r") as file_in:
                    json_obj = json.load(file_in)
                msgs = json_obj["messages"]
                for msg_obj in msgs:
                    msg_name = cls._get_name(msg_obj)
                    msg_crc = msg_obj["crc"]
                    if msg_name not in cls.VPP_API_CRC_VERIFIED:
                        if msg_name not in cls.VPP_API_CRC_FOUND:
                            cls.VPP_API_CRC_FOUND[msg_name] = [msg_crc]
                        elif msg_crc not in cls.VPP_API_CRC_FOUND[msg_name]:
                            cls.VPP_API_CRC_FOUND[msg_name].append(msg_crc)
                        continue
                    if msg_crc in cls.VPP_API_CRC_VERIFIED[msg_name]:
                        continue
                    raise RuntimeError(
                        "Found message with unsupported crc: "
                        "{root} {file} {msg} {crc}".format(
                            root=root, file=filename, msg=msg_name, crc=msg_crc))

    @classmethod
    def check_message(cls, message):
        """Fail if the message has no known CRC associated.

        :param message: VPP API message name to check.
        :type message: str
        :raises RuntimeError: If no verified CRC for the message is found.
        """
        if cls.VPP_API_CRC_VERIFIED.get(message, tuple()):
            return
        candidates = cls.VPP_API_CRC_FOUND.get(message, tuple())
        raise RuntimeError(
            "Attempt to use message with no verified CRC: {message}, "
            "candidate CRCs found: {crcs}".format(
                message=message, crcs=candidates))
