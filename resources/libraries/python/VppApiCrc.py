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
    """Holder of data related to tracking VPP API CRCs.

    Each instance of this class starts with same default state,
    so make sure the calling libraries have appropriate robot library scope.
    For usual testing, it means "GLOBAL" scope."""

    def __init__(self, directory):
        """Initialize empty state, then register known collections.

        This also scans directory for .api.json files
        and performs initial checks, but does not report the findings yet.

        :param directory: Root directory of the search for .api.json files.
        :type directory: str
        """

        self._crcs = OrderedDict()
        """Mapping from collection name to mapping from API name to CRC string.

        Colection name should be something useful for logging.
        API name is ordinary Python2 str, CRC is also str.

        Order of addition reflects the order colections should be queried.
        If an incompatible CRC is found, affected collections are removed.
        A CRC that would remove all does not, added to _reported instead,
        while causing a failure in single test.
        """

        self._found = dict()
        """Mapping from API name to CRC string.

        This gets populated with CRCs found in .api.json,
        to serve as a hint when reporting errors."""

        self._reported = dict()
        """Mapping from API name to CRC string.

        This gets populated with APIs used, but not found in collections,
        just before the fact is reported in an exception.
        The CRC comes from _found mapping (otherwise left as None).
        The idea is to not report those next time, allowing the job
        to find more problems in a single run."""

        self._initial_conflicts_reported = False
        self._register_all()
        self._check_dir(directory)

    def _register_collection(self, collection_name, collection_dict):
        """Add a named collection of CRCs.

        :param collection_name: Helpful string describing the collection.
        :param collection_dict: Mapping from API names to CRCs.
        :type collection_name: str
        :type collection_dict: dict from str to str
        """
        if collection_name in self._crcs:
            raise RuntimeError("Collection {cl} already registered.".format(
                cl=collection_name))
        self._crcs[collection_name] = collection_dict

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
        for item in reversed(msg_obj):
            if not isinstance(item, dict):
                continue
            crc = item.get("crc", None)
            if crc:
                return crc
        raise RuntimeError("No CRC found for message: {obj!r}".format(
            obj=msg_obj))

    def _process_crc(self, api_name, crc):
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
        self._found[api_name] = crc
        old_crcs = self._crcs
        new_crcs = old_crcs.copy()
        for collection_name, collection_dict in old_crcs.items():
            if api_name not in collection_dict:
                continue
            if collection_dict[api_name] == crc:
                continue
            # Remove the offending collection.
            new_crcs.pop(collection_name, None)
        if new_crcs:
            # Some collections recognized the CRC.
            self._crcs = new_crcs
            return
        # No new_crcs means some colections knew the api_name,
        # but CRC does not match any. This has to be reported.
        self._reported[api_name] = crc

    def _check_dir(self, directory):
        """Parse every .api.json found under directory, remember conflicts.

        As several collections are supported, each conflict invalidates
        one of them, failure happens only when no collections would be left.
        In that case, set of collections just before the failure is preserved,
        the _reported mapping is filled with confilcting APIs.
        The _found mapping is filled with discovered api names and crcs.

        The exception is not thrown here, but from report_initial_conflicts.

        :param directory: Root directory of the search for .api.json files.
        :type directory: str
        """
        for root, _, files in os.walk(directory):
            for filename in files:
                if not filename.endswith(".api.json"):
                    continue
                with open(root + '/' + filename, "r") as file_in:
                    json_obj = json.load(file_in)
                msgs = json_obj["messages"]
                for msg_obj in msgs:
                    msg_name = self._get_name(msg_obj)
                    msg_crc = self._get_crc(msg_obj)
                    self._process_crc(msg_name, msg_crc)
        logger.info("Surviving collections: {col}".format(col=self._crcs.keys()))

    def report_initial_conflicts(self):
        """Report issues discovered by _check_dir, if not done that already.

        Intended use: Call once after init, at a time when throwing exception
        is convenient.

        :raises RuntimeError: If CRC mismatch is detected.
        """
        if self._initial_conflicts_reported:
            return
        self._initial_conflicts_reported = True
        if self._reported:
            self._reported = OrderedDict(sorted(self._reported.items()))
            raise RuntimeError("Dir check found incomparible API CRCs: {rep}"\
                .format(rep=self._reported))

    def check_api_name(self, api_name):
        """Fail if the api_name has no known CRC associated.

        Do not fail if this particular failure has been already reported.

        Intended use: Call everytime an API call is queued.

        :param api_name: VPP API messagee name to check.
        :type api_name: str
        :raises RuntimeError: If no verified CRC for the api_name is found.
        """
        if api_name in self._reported:
            return
        old_crcs = self._crcs
        new_crcs = old_crcs.copy()
        for collection_name, collection_dict in old_crcs.items():
            if api_name in collection_dict:
                continue
            # Remove the offending collection.
            new_crcs.pop(collection_name, None)
        if new_crcs:
            # Some collections recognized the message name.
            self._crcs = new_crcs
            return
        crc = self._found.get(api_name, None)
        self._reported[api_name] = crc
        raise RuntimeError("No active collection has API {api} CRC found {crc}"\
            .format(api=api_name, crc=crc))

    # Moved to the end as this part will be edited frequently.
    def _register_all(self):
        """Add all collections this CSIT codebase is tested against."""

        # Rework to read from files?
        self._register_collection(
            "19.08-rc0~663-g692b9498e", {
#                "bridge_domain_add_del": "0xc6360720",
#                "bridge_domain_dump": "0xc25fdce6",
                "cli_inband": "0xb1ad59b3",
#                "create_loopback": "0x3b54129c",
#                "create_vhost_user_if": "0xbd230b87",
#                "create_vlan_subif": "0x70cadeda",
#                "create_subif": "0x86cfe408",
#                "gre_tunnel_add_del": "0xfb665f21",
#                "ip_address_dump": "0x6b7bcd0a",
#                "ip_source_check_interface_add_del": "0x0a60152a",
#                "input_acl_set_interface": "0xe09537b0",
#                "l2_fib_table_dump": "0xc25fdce6",
#                "l2_interface_vlan_tag_rewrite": "0xb90be6b4",
#                "memif_create": "0x6597cdb2",
#                "memif_dump": "0x51077d14",
#                "memif_socket_filename_add_del": "0x30e3929d",
#                "proxy_arp_intfc_enable_disable": "0x69d24598",
                "show_version": "0x51077d14",
                "sw_interface_dump": "0x052753c5",
#                "sw_interface_set_flags": "0x555485f5",
#                "sw_interface_set_l2_bridge": "0x2af7795e",
#                "sw_interface_set_l2_xconnect": "0x95de3988",
#                "sw_interface_set_table": "0xacb25d89",
#                "sw_interface_vhost_user_dump": "0x51077d14",
#                "vxlan_add_del_tunnel": "0x00f4bdd0",
#                "vxlan_tunnel_dump": "0x529cb13f",
            }
        )
