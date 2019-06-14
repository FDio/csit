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

    Contains mutable class variables and class methods to access them."""

    _crcs = OrderedDict()
    """Mapping from collection name to mapping from API name to CRC string.

    Colection name should be something useful for logging.
    API name is ordinary Python2 str, CRC is also str.

    Order of addition reflects the order colections should be queried.
    If an incompatible CRC is found, affected collections are removed.
    A CRC that would remove all does not, added to _reported instead,
    while causing a failure in single test.
    """

    _found = dict()
    """Mapping from API name to CRC string.

    This gets populated with CRCs found in .api.json,
    to serve as a hint when reporting errors."""

    _reported = dict()
    """Mapping from API name to CRC string.

    This gets populated with APIs used, but not found in collections,
    just before the fact is reported in an exception.
    The CRC comes from _found mapping (otherwise left as None).
    The idea is to not report those next time, allowing the job
    to find more problems in a single run."""

    @classmethod
    def _register_collection(cls, collection_name, collection_dict):
        """Add a named collection of CRCs.

        :param collection_name: Helpful string describing the collection.
        :param collection_dict: Mapping from API names to CRCs.
        :type collection_name: str
        :type collection_dict: dict from str to str
        """
        if collection_name in cls._crcs:
            raise RuntimeError("Collection {cl} already registered.".format(
                cl=collection_name))
        cls._crcs[collection_name] = collection_dict

    @staticmethod
    def _get_name(msg_obj):
        """Utility function to extract API name from an intermediate json.

        :param msg_obj: Loaded json object, item of "messages" list.
        :type msg_obj: list of various types
        :returns: Name of the message.
        :rtype: str or unicode
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
        :rtype: str or unicode
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
    def _process_crc(cls, api_name, crc)
        """Compare API to verified collections, update class state.

        Conflict is NOT when a collection does not recognize the API.
        Such APIs are merely added to _found for later reporting.
        Conflict is when a collection recognizes the API under a different CRC.
        If a partial match happens, only the matching collections are preserved.
        On no match, all current collections are preserved,
        but the offending API is added to _reported mapping.

        Note that it is expected that collections are incompatible
        with each other for some APIs. The removal of collections
        on partial match is there to help identify the intended collection
        for the VPP build under test. But if no collection fits perfectly,
        the last collections to determine the "known" flag
        depends on the order of api_name submitted,
        which tends to be fairly random (depends on order of .api.json files).
        Order of collection registrations does not help much in this regard.

        Attempts to overwrite value in _found or _reported should not happen,
        so the code does not check for that, simply overwriting.

        The intended usage is to call this method multiple times,
        and then raise exception listing all _reported.

        :param api_name: API name to check.
        :param crc: Discovered CRC to check for the name.
        :type api_name: str
        :type crc: str or unicode
        """
        # Regardless of the result, remember as found.
        cls._found[api_name] = crc
        old_crcs = cls._crcs
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
            cls._crcs = new_crcs
            return
        if known:
            # API name was found in a collection, but CRC does not match.
            # This has to be reported.
            cls._reported[api_name] = crc

    @classmethod
    def check_dir(cls, directory):
        """Parse every .api.json found under directory, fail on conflict.

        As several collections are supported, each conflict invalidates
        one of them, failure happens only when no collections would be left.
        In that case, set of collections just before the failure is preserved,
        the _reported mapping is filled with confilcting APIs.
        The _found mapping is filled with discovered api names and crcs.

        Intended use: Call once, as soon as directory value is known.

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
                    cls._process_crc(msg_name, msg_crc)
        logger.info("Surviving collections: {col}".format(col=cls._crcs.keys()))
        if cls._reported:
            cls._reported = OrderedDict(sorted(cls._reported.items()))
            raise RuntimeError("Dir check found incomparible API CRCs: {rep}"\
                .format(rep=cls._reported))

    @classmethod
    def check_api_name(cls, api_name):
        """Fail if the api_name has no known CRC associated.

        Do not fail if this particular failure has been already reported.

        Intended use: Call everytime an API call is queued.

        :param api_name: VPP API messagee name to check.
        :type api_name: str
        :raises RuntimeError: If no verified CRC for the api_name is found.
        """
        if api_name in cls._reported:
            return
        old_crcs = cls._crcs
        new_crcs = old_crcs.copy()
        for collection_name, collection_dict in old_crcs:
            if api_name in collection_dict:
                continue
            # Remove the offending collection.
            new_crcs.pop(collection_name, None)
        if new_crcs:
            # Some collections recognized the message name.
            cls._crcs = new_crcs
            return
        crc = cls._found.get(api_name, None)
        cls._reported[api_name] = crc
        raise RuntimeError("No active collection has API {api} CRC found {crc}"\
            .format(api=api_name, crc=crc))

    # Collection registrations.
    # Rework to read from files?

    VppApiCrcChecker._register_collection(
        "19.08-rc0~341-gb19bf8d~b7191", {
            "bridge_domain_add_del": "0xc6360720",
            "bridge_domain_dump": "0xc25fdce6",
            "cli_inband": "0xb1ad59b3",
            "create_loopback": "0x3b54129c",
            "create_vhost_user_if": "0xbd230b87",
            "create_vlan_subif": "0x70cadeda",
            "create_subif": "0x86cfe408",
            "gre_tunnel_add_del": "0xfb665f21",
            "ip_address_dump": "0x6b7bcd0a",
            "ip_source_check_interface_add_del": "0x0a60152a",
            "input_acl_set_interface": "0xe09537b0",
            "l2_fib_table_dump": "0xc25fdce6",
            "l2_interface_vlan_tag_rewrite": "0xb90be6b4",
            "memif_create": "0x6597cdb2",
            "memif_dump": "0x51077d14",
            "memif_socket_filename_add_del": "0x30e3929d",
            "proxy_arp_intfc_enable_disable": "0x69d24598",
            "show_version": "0x51077d14",
            "sw_interface_dump": "0x052753c5",
            "sw_interface_set_flags": "0x555485f5",
            "sw_interface_set_l2_bridge": "0x2af7795e",
            "sw_interface_set_l2_xconnect": "0x95de3988",
            "sw_interface_set_table": "0xacb25d89",
            "sw_interface_vhost_user_dump": "0x51077d14",
            "vxlan_add_del_tunnel": "0x00f4bdd0",
            "vxlan_tunnel_dump": "0x529cb13f",
        }
    )
