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

from robot.api import logger


class VppApiCrcChecker(object):
    """Nothing related to instances here, just a wrapper for import."""

    VPP_API_CRC_VERIFIED = {
        "bridge_domain_add_del": (u'0xc6360720',),
        "bridge_domain_dump": (u'0xc25fdce6',),
        "cli_inband": (u'0xb1ad59b3',),
        "create_loopback": (u'0x3b54129c',),
        "create_vhost_user_if": (u'0xbd230b87',),
        "ip_address_dump": (u'0x6b7bcd0a',),
        "memif_create": (u'0x6597cdb2',),
        "memif_dump": (u'0x51077d14',),
        "memif_socket_filename_add_del": (u'0x30e3929d',),
        "show_version": (u'0x51077d14',),
        "sw_interface_dump": (u'0x052753c5',),
        "sw_interface_set_flags": (u'0x555485f5',),
        "sw_interface_set_l2_bridge": (u'0x2af7795e', u'0x5579f809'),
        "sw_interface_set_l2_xconnect": (u'0x95de3988',),
        "sw_interface_set_table": (u'0xacb25d89',),
        "sw_interface_vhost_user_dump": (u'0x51077d14',),
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
            crc = item.get("crc", None)
            if crc:
                return crc
        raise RuntimeError("No CRC found for message: {obj!r}".format(
            obj=msg_obj))

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
#                logger.debug("Found filename {name}".format(name=filename))
                with open(root + '/' + filename, "r") as file_in:
                    json_obj = json.load(file_in)
                msgs = json_obj["messages"]
                for msg_obj in msgs:
                    msg_name = cls._get_name(msg_obj)
                    msg_crc = cls._get_crc(msg_obj)
#                    logger.debug("Found message name {name} crc {crc}".format(
#                        name=msg_name, crc=msg_crc))
                    if msg_name not in cls.VPP_API_CRC_VERIFIED:
#                        logger.debug("Not verified.")
                        if msg_name not in cls.VPP_API_CRC_FOUND:
                            cls.VPP_API_CRC_FOUND[msg_name] = [msg_crc]
#                            logger.debug("Added to found.")
                        elif msg_crc not in cls.VPP_API_CRC_FOUND[msg_name]:
                            cls.VPP_API_CRC_FOUND[msg_name].append(msg_crc)
#                            logger.debug("Appended to found.")
                        continue
                    if msg_crc in cls.VPP_API_CRC_VERIFIED[msg_name]:
#                        logger.debug("Verified.")
                        continue
                    raise RuntimeError(
                        "Found message with unsupported crc: "
                        "{root} {file} {msg} {crc}".format(
                            root=root, file=filename, msg=msg_name, crc=msg_crc))

    @classmethod
    def check_message(cls, message):
        """Fail if the message has no known CRC associated.

        Before failing, associate the CRC found,
        so that the next test failure can discover another message.

        :param message: VPP API message name to check.
        :type message: str
        :raises RuntimeError: If no verified CRC for the message is found.
        """
        if cls.VPP_API_CRC_VERIFIED.get(message, tuple()):
            return
        candidates = cls.VPP_API_CRC_FOUND.get(message, None)
        if candidates:
            cls.VPP_API_CRC_VERIFIED[message] = candidates
        raise RuntimeError(
            "Attempt to use message with no verified CRC: {message}, "
            "candidate CRC found: {crcs}".format(
                message=message, crcs=candidates))
