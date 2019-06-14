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

from collections import OrderedDict
import json
import os

from robot.api import logger


class VppApiCrcChecker(object):
    """Nothing related to instances here, just a wrapper for import.

    Contains mutable class variables and class method to access them."""

    crcs = OrderedDict()
    """Mapping from collection name to mapping from API name to CRC string.

    Colection name should be something useful for logging.
    API name is ordinary Python2 str, CRC string is unicode.

    Order of addition reflects the order colections should be queried.
    If an incompatible CRC is found, affected collections are removed.
    A CRC that would remove all does not, added to "found" instead,
    while causing a failure in single test.
    """

    found = dict()
    """Mapping from API name to CRC string.

    This gets populated with CRCs found in .api.json,
    to serve as a hint when reporting errors."""

    reported = dict()
    """Mapping from API name to CRC string.

    This gets populated with APIs not found in verified collections,
    just before the fact is reported in an exception.
    The CRC comes from "found" mapping (otherwise left as None).
    The idea is to not report those next time, allowing the job
    to find more problems in a single run."""

    @classmethod
    def register_collection(cls, collection_name, collection_dict):
        """Add a named collection of CRCs.

        :param collection_name: Helpful string describing the collection.
        :param collection_dict: Mapping from API names to CRCs.
        :type collection_name: str
        :type collection_dict: dict from str to unicode
        """
        if collection_name in cls.crcs:
            raise RuntimeError("Collection {cl} already registered.".format(
                cl=collection_name))
        cls.crcs[collection_name] = collection_dict

    @staticmethod
    def _get_name(msg_obj):
        """Utility function to extract API name from an intermediate json.

        :param msg_obj: Loaded json object, item of "messages" list.
        :type msg_obj: list of various types
        :returns: Name of the message.
        :rtype: unicode
        :raises RuntimeError: If no name is found.
        """
        for item in msg_obj:
            if isinstance(item, (dict, list)):
                continue
            return item
        raise RuntimeError("No name found for message: {obj!r}".format(
            obj=msg_obj))

    @staticmethod
    def _get_crc(msg_obj):
        """Utility function to extract API CRC from an intermediate json.

        :param msg_obj: Loaded json object, item of "messages" list.
        :type msg_obj: list of various types
        :returns: CRC of the message.
        :rtype: unicode
        :raises RuntimeError: If no CRC is found.
        """
        for item in msg_obj:
            if not isinstance(item, dict):
                continue
            crc = item.get("crc", None)
            if crc:
                return crc
        raise RuntimeError("No CRC found for message: {obj!r}".format(
            obj=msg_obj))

    @classmethod
    def process_crc(cls, api_name, crc)
        """Compare API to verified collections, update class state.

        Conflict is NOT when a collection does not recognize the API.
        Such APIs are merely added to "found" for later reporting.
        Conflict is when a collection recognizes the API under a different CRC.
        If a partial match happens, only the matching collections are preserved.
        On no match, all current collections are preserved,
        but the offending API is added to "reported" mapping.

        Note that it is expected that collections are incompatible
        with each other for some APIs. The removal of collections
        on partial match is intended to identify the intended collection
        for the VPP build under test. But if no collection fits perfectly,
        the last collections to determine "known" flag
        depends on the order of api_name submitted,
        which tends to be fairly random.
        Order of collection registrations does not help much in this regard.

        Attempts to overwrite value in "found" or "reported" should not happen,
        so the code does not check for that, simply overwriting.

        The intended usage is to call this method multiple times,
        and then raise exception listing all "reported".

        :param api_name: API name to check.
        :param crc: Discovered CRC to check for the name.
        :type api_name: str
        :type crc: str or unicode
        """
        old_crcs = cls.crcs
        new_crcs = old_crcs.copy()
        known = False
        for collection_name, collection_dict in old_crcs:
            if api_name not in collection_dict:
                continue
            known = True
            if collection_dict[api_name] == crc:
                continue
            # Remove the offending collection.
            new_crcs.pop(collection_name, None)
        if new_crcs:
            # Some collections recognized the CRC.
            cls.crcs = new_crcs
            return
        if known:
            # API name was found in a collection, but CRC does not match.
            # This has to be reported.
            cls.reported[api_name] = crc
        # Both unknown and conflicting APIs have to be remembered as found.
        cls.found[api_name] = crc

    @classmethod
    def check_dir(cls, directory):
        """Parse every .api.json found under directory, fail on conflict.

        As several collections are supported, each conflict reduces them,
        failure happens only when no collections would be left.
        In that case, set of collections just before failure is preserved,
        the "reported" mapping is filled with confilcting APIs.
        The "found" mapping is filled with discovered api names and crcs.

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
                    msg_crc = cls._get_crc(msg_obj)
                    cls.process_crc(msg_name, msg_crc)
        logger.info("Surviving collections: {col}".format(col=cls.crcs.keys()))
        if cls.reported:
            cls.reported = OrderedDict(sorted(cls.reported.items()))
            raise RuntimeError("Dir check found incomparible API CRCs: {rep}"\
                .format(rep=cls.reported))

    @classmethod
    def check_message(cls, message):
        """Fail if the message has no known CRC associated.

        Do not fail if this particular failure has been already reported.

        :param message: VPP API message name to check.
        :type message: str
        :raises RuntimeError: If no verified CRC for the message is found.
        """
        old_crcs = cls.crcs
        new_crcs = old_crcs.copy()
        for collection_name, collection_dict in old_crcs:
            if message in collection_dict:
                continue
            # Remove the offending collection.
            new_crcs.pop(collection_name, None)
        if new_crcs:
            # Some collections recognized the message name.
            cls.crcs = new_crcs
            return
        if message in cls.reported:
            return
        crc = cls.found.get(message, None)
        cls.reported[message] = crc
        raise RuntimeError("No collection recognizes API {api} CRC {crc}"\
            .format(api=message, crc=crc))

    # Collection registrations.
    # Rework to read from files?

    VppApiCrcChecker.register_collection(
        "19.08-rc0~341-gb19bf8d~b7191", {
            "bridge_domain_add_del": u'0xc6360720',
            "bridge_domain_dump": u'0xc25fdce6',
            "cli_inband": u'0xb1ad59b3',
            "create_loopback": u'0x3b54129c',
            "create_vhost_user_if": u'0xbd230b87',
            "create_vlan_subif": u'0x70cadeda',
            "create_subif": u'0x86cfe408',
            "gre_tunnel_add_del": u'0xfb665f21',
            "ip_address_dump": u'0x6b7bcd0a',
            "ip_source_check_interface_add_del": u'0x0a60152a',
            "input_acl_set_interface": u'0xe09537b0',
            "l2_fib_table_dump": u'0xc25fdce6',
            "l2_interface_vlan_tag_rewrite": u'0xb90be6b4',
            "memif_create": u'0x6597cdb2',
            "memif_dump": u'0x51077d14',
            "memif_socket_filename_add_del": u'0x30e3929d',
            "proxy_arp_intfc_enable_disable": u'0x69d24598',
            "show_version": u'0x51077d14',
            "sw_interface_dump": u'0x052753c5',
            "sw_interface_set_flags": u'0x555485f5',
            "sw_interface_set_l2_bridge": u'0x2af7795e',
            "sw_interface_set_l2_xconnect": u'0x95de3988',
            "sw_interface_set_table": u'0xacb25d89',
            "sw_interface_vhost_user_dump": u'0x51077d14',
            "vxlan_add_del_tunnel": u'0x00f4bdd0',
            "vxlan_tunnel_dump": u'0x529cb13f',
        }
    )
