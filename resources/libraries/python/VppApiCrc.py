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

        self._expected = dict()
        """Mapping from collection name to mapping from API name to CRC string.

        Colection name should be something useful for logging.
        API name is ordinary Python2 str, CRC is also str.

        Order of addition reflects the order colections should be queried.
        If an incompatible CRC is found, affected collections are removed.
        A CRC that would remove all does not, added to _reported instead,
        while causing a failure in single test.
        """

        self._missing = dict()
        """Mapping from collection name to mapping from API name to CRC string.

        Starts the same as _expected, but each time an encountered api,crc pair
        fits the expectation, the pair is removed from this mapping.
        Ideally, the active mappings will become empty.
        If not, it is an error, VPP removed or renamed a message CSIT needs."""

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
        """Add a named (copy of) collection of CRCs.

        :param collection_name: Helpful string describing the collection.
        :param collection_dict: Mapping from API names to CRCs.
        :type collection_name: str
        :type collection_dict: dict from str to str
        """
        if collection_name in self._expected:
            raise RuntimeError("Collection {cl} already registered.".format(
                cl=collection_name))
        self._expected[collection_name] = collection_dict.copy()
        self._missing[collection_name] = collection_dict.copy()

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
        old_expected = self._expected
        new_expected = old_expected.copy()
        for collection_name, collection_dict in old_expected.items():
            if api_name not in collection_dict:
                continue
            if collection_dict[api_name] == crc:
                self._missing[collection_name].pop(api_name, None)
                continue
            # Remove the offending collection.
            new_expected.pop(collection_name, None)
        if new_expected:
            # Some collections recognized the CRC.
            self._expected = new_expected
            self._missing = {name: self._missing[name] for name in new_expected}
            return
        # No new_expected means some colections knew the api_name,
        # but CRC does not match any. This has to be reported.
        self._reported[api_name] = crc

    def _check_dir(self, directory):
        """Parse every .api.json found under directory, remember conflicts.

        As several collections are supported, each conflict invalidates
        one of them, failure happens only when no collections would be left.
        In that case, set of collections just before the failure is preserved,
        the _reported mapping is filled with conflicting APIs.
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
        logger.info("Surviving collections: {col}".format(
            col=self._expected.keys()))

    def report_initial_conflicts(self, report_missing=False):
        """Report issues discovered by _check_dir, if not done that already.

        Intended use: Call once after init, at a time when throwing exception
        is convenient.

        Optionally, report also missing messages.
        Missing reporting is disabled by default, because some messages
        come from plugins that might not be enabled at runtime.

        :param report_missing: Whether to raise on missing messages.
        :type report_missing: bool
        :raises RuntimeError: If CRC mismatch or missing messages are detected.
        """
        if self._initial_conflicts_reported:
            return
        self._initial_conflicts_reported = True
        if self._reported:
            raise RuntimeError("Dir check found incompatible API CRCs: {rep!r}"\
                .format(rep=self._reported))
        if not report_missing:
            return
        missing = {name: mapp for name, mapp in self._missing.items() if mapp}
        if missing:
            raise RuntimeError("Dir check found missing API CRCs: {mis!r}"\
                .format(mis=missing))

    def check_api_name(self, api_name):
        """Fail if the api_name has no known CRC associated.

        Do not fail if this particular failure has been already reported.

        Intended use: Call everytime an API call is queued or response received.

        :param api_name: VPP API messagee name to check.
        :type api_name: str
        :raises RuntimeError: If no verified CRC for the api_name is found.
        """
        if api_name in self._reported:
            return
        old_expected = self._expected
        new_expected = old_expected.copy()
        for collection_name, collection_dict in old_expected.items():
            if api_name in collection_dict:
                continue
            # Remove the offending collection.
            new_expected.pop(collection_name, None)
        if new_expected:
            # Some collections recognized the message name.
            self._expected = new_expected
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
            "19.08-rc0~680-g456d2f9~b7573", {
                "acl_add_replace": "0x13bc8539",  # perf
                "acl_add_replace_reply": "0xac407b0c",  # perf
                "acl_dump": "0xef34fea4",  # perf teardown
                "acl_interface_list_dump": "0x529cb13f",  # perf teardown
                # ^^^^ tc01-64B-1c-ethip4udp-ip4base-iacl1sf-10kflows-mrr
                "acl_interface_set_acl_list": "0x8baece38",  # perf
                "acl_interface_set_acl_list_reply": "0xe8d4e804",  # perf
                "acl_details": "0xf89d7a88",  # perf teardown
                "acl_interface_list_details": "0xd5e80809",  # perf teardown
                # ^^^^ tc01-64B-1c-ethip4udp-ip4base-iacl1sl-10kflows-mrr
                "avf_create": "0xdaab8ae2",  # perf
                "avf_create_reply": "0xfda5941f",  # perf
                # ^^ tc01-64B-1c-avf-eth-l2bdbasemaclrn-mrr
                "bridge_domain_add_del": "0xc6360720",  # dev
                "bridge_domain_add_del_reply": "0xe8d4e804",  # dev
                "classify_add_del_session": "0x85fd79f4",  # dev
                "classify_add_del_session_reply": "0xe8d4e804",  # dev
                "classify_add_del_table": "0x9bd794ae",  # dev
                "classify_add_del_table_reply": "0x05486349",  # dev
                "cli_inband": "0xb1ad59b3",  # dev setup
                "cli_inband_reply": "0x6d3c80a4",  # dev setup
                "create_loopback": "0x3b54129c",  # dev
                "create_loopback_reply": "0xfda5941f",  # dev
                "create_subif": "0x86cfe408",  # virl
                "create_subif_reply": "0xfda5941f",  # virl
                "create_vhost_user_if": "0xbd230b87",  # dev
                "create_vhost_user_if_reply": "0xfda5941f",  # dev
                "create_vlan_subif": "0x70cadeda",  # virl
                "create_vlan_subif_reply": "0xfda5941f",  # virl
                "gre_tunnel_add_del": "0x04199f47",  # virl
                "gre_tunnel_add_del_reply": "0x903324db",  # virl
                "hw_interface_set_mtu": "0x132da1e7",  # dev
                "hw_interface_set_mtu_reply": "0xe8d4e804",  # dev
                "input_acl_set_interface": "0xe09537b0",  # dev
                "input_acl_set_interface_reply": "0xe8d4e804",  # dev
                "ip_address_details": "0x2f1dbc7d",  # dev
                "ip_address_dump": "0x6b7bcd0a",  # dev
                "ip_neighbor_add_del": "0x7a68a3c4",  # dev
                "ip_neighbor_add_del_reply": "0x1992deab",  # dev
                "ip_probe_neighbor": "0x2736142d",  # virl
                "ip_route_add_del": "0x83e086ce",  # dev
                "ip_route_add_del_reply": "0x1992deab",  # dev
                "ip_source_check_interface_add_del": "0x0a60152a",  # virl
                "ip_source_check_interface_add_del_reply": "0xe8d4e804",  # virl
                "ip_table_add_del": "0xe5d378f2",  # dev
                "ip_table_add_del_reply": "0xe8d4e804",  # dev
                "ipsec_interface_add_del_spd": "0x1e3b8286",  # dev
                "ipsec_interface_add_del_spd_reply": "0xe8d4e804",  # dev
                "ipsec_sad_entry_add_del": "0xa25ab61e",  # dev
                "ipsec_sad_entry_add_del_reply": "0x9ffac24b",  # dev
                "ipsec_spd_add_del": "0x9ffdf5da",  # dev
                "ipsec_spd_add_del_reply": "0xe8d4e804",  # dev
                "ipsec_spd_entry_add_del": "0x6bc6a3b5",  # dev
                "ipsec_spd_entry_add_del_reply": "0x9ffac24b",  # dev
                "l2_interface_vlan_tag_rewrite": "0xb90be6b4",  # virl
                "l2_interface_vlan_tag_rewrite_reply": "0xe8d4e804",  # virl
                "l2_patch_add_del": "0x62506e63",  # perf
                "l2_patch_add_del_reply": "0xe8d4e804",  # perf
                # ^^ tc01-64B-1c-avf-eth-l2patch-mrr
                "lisp_eid_table_details": "0xdcd9f414",  # virl
                "lisp_eid_table_dump": "0xe0df64da",  # virl
                "lisp_locator_set_details": "0x6b846882",  # virl
                "lisp_locator_set_dump": "0xc79e8ab0",  # virl
                "lisp_map_resolver_details": "0x60a5f5ca",  # virl
                "lisp_map_resolver_dump": "0x51077d14",  # virl
                "memif_create": "0x6597cdb2",  # dev
                "memif_create_reply": "0xfda5941f",  # dev
                "memif_details": "0x4f5a3397",  # dev
                "memif_dump": "0x51077d14",  # dev
                "memif_socket_filename_add_del": "0x30e3929d",  # dev
                "memif_socket_filename_add_del_reply": "0xe8d4e804",  # dev
                "nat44_interface_add_del_feature": "0xef3edad1",  # perf
                "nat44_interface_add_del_feature_reply": "0xe8d4e804",  # perf
                # ^^ tc01-64B-1c-ethip4udp-ip4base-nat44-mrr
                "proxy_arp_intfc_enable_disable": "0x69d24598",  # virl
                "proxy_arp_intfc_enable_disable_reply": "0xe8d4e804",  # virl
                "show_lisp_status": "0x51077d14",  # virl
                "show_lisp_status_reply": "0xddcf48ef",  # virl
                "show_threads": "0x51077d14",  # dev
                "show_threads_reply": "0xf5e0b66f",  # dev
                "show_version": "0x51077d14",  # dev setup
                "show_version_reply": "0xb9bcf6df",  # dev setup
                "sw_interface_add_del_address": "0x7b583179",  # dev
                "sw_interface_add_del_address_reply": "0xe8d4e804",  # dev
                "sw_interface_details": "0xe4ee7eb6",  # dev setup
                "sw_interface_dump": "0x052753c5",  # dev setup
                "sw_interface_ip6nd_ra_config": "0xc3f02daa",  # dev
                "sw_interface_ip6nd_ra_config_reply": "0xe8d4e804",  # dev
                "sw_interface_rx_placement_details": "0x0e9e33f4",  # perf
                "sw_interface_rx_placement_dump": "0x529cb13f",  # perf
                # ^^ tc01-64B-1c-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
                "sw_interface_set_flags": "0x555485f5",  # dev
                "sw_interface_set_flags_reply": "0xe8d4e804",  # dev
                "sw_interface_set_l2_bridge": "0x5579f809",  # dev
                "sw_interface_set_l2_bridge_reply": "0xe8d4e804",  # dev
                "sw_interface_set_l2_xconnect": "0x95de3988",  # dev
                "sw_interface_set_l2_xconnect_reply": "0xe8d4e804",  # dev
                "sw_interface_set_rx_placement": "0x4ef4377d",  # perf
                "sw_interface_set_rx_placement_reply": "0xe8d4e804",  # perf
                # ^^ tc01-64B-1c-eth-l2xcbase-eth-2memif-1dcr-mrr
                "sw_interface_set_table": "0xacb25d89",  # dev
                "sw_interface_set_table_reply": "0xe8d4e804",  # dev
                "sw_interface_vhost_user_details": "0x91ff3307",  # dev
                "sw_interface_vhost_user_dump": "0x51077d14",  # dev
                "vxlan_add_del_tunnel": "0x00f4bdd0",  # virl
                "vxlan_add_del_tunnel_reply": "0xfda5941f",  # virl
                "vxlan_tunnel_details": "0xce38e127",  # virl
                "vxlan_tunnel_dump": "0x529cb13f",  # virl
            }
        )
