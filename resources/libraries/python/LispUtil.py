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

"""Lisp utilities library."""

from robot.api import logger
from ipaddress import IPv4Address, IPv6Address

from resources.libraries.python.topology import Topology
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.L2Util import L2Util

class LispUtil(object):
    """Implements keywords for Lisp tests."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_show_lisp_state(node):
        """Get lisp state from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: Lisp gpe state.
        :rtype: dict
        """
        cmd = u"show_lisp_status"
        err_msg = f"Failed to get LISP status on host {node['host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        data = dict()
        data[u"feature_status"] = u"enabled" if reply[u"feature_status"] else \
                                  u"disabled"
        data[u"gpe_status"] = u"enabled" if reply[u"gpe_status"] else \
                              u"disabled"
        return data

    @staticmethod
    def vpp_show_lisp_locator_set(node, items_filter):
        """Get lisp locator_set from VPP node.

        :param node: VPP node.
        :param items_filter: Filter which specifies which items should be
            retrieved - local, remote, empty string = both.
        :type node: dict
        :type items_filter: str
        :returns: Lisp locator_set data as python list.
        :rtype: list
        """

        ifilter = {u"_": 0, u"_local": 1, u"_remote": 2}
        args = dict(filter=ifilter["_" + items_filter])

        cmd = u"lisp_locator_set_dump"
        err_msg = f"Failed to get LISP locator set on host {node['host']}"

        try:
            with PapiSocketExecutor(node) as papi_exec:
                details = papi_exec.add(cmd, **args).get_details(err_msg)
            data = []
            for locator in details:
                data.append({u"ls_name": locator[u"ls_name"].rstrip(b'\x00'),
                             u"ls_index": locator[u"ls_index"]})
            return data
        except (ValueError, LookupError) as err:
            logger.warn(f"Failed to get LISP locator set {err}")
            return []

    @staticmethod
    def vpp_show_lisp_eid_table(node):
        """Get lisp eid table from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: Lisp eid table as python list.
        :rtype: list
        """

        cmd = u"lisp_eid_table_dump"
        err_msg = f"Failed to get LISP eid table on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        data = []
        for eid_details in details:
            eid = u"Bad eid type"
            if eid_details[u"eid_type"] == 0:
                prefix = str(eid_details[u"eid_prefix_len"])
                eid = str(IPv4Address(eid_details[u"eid"][0:4])) + u"/" + \
                      prefix
            elif eid_details[u"eid_type"] == 1:
                prefix = str(eid_details[u"eid_prefix_len"])
                eid = str(IPv6Address(eid_details[u"eid"])) + u"/" + prefix
            elif eid_details[u"eid_type"] == 2:
                eid = str(L2Util.bin_to_mac(eid_details[u"eid"][0:6]))
            data.append({u"action": eid_details[u"action"],
                         u"is_local": eid_details[u"is_local"],
                         u"eid": eid,
                         u"vni": eid_details[u"vni"],
                         u"ttl": eid_details[u"ttl"],
                         u"authoritative": eid_details[u"authoritative"]})
        return data

    @staticmethod
    def vpp_show_lisp_map_resolver(node):
        """Get lisp map resolver from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: Lisp map resolver as python list.
        :rtype: list
        """

        cmd = u"lisp_map_resolver_dump"
        err_msg = f"Failed to get LISP map resolver on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        data = []
        for resolver in details:
            address = u"Bad is_ipv6 flag"
            if resolver[u"is_ipv6"] == 0:
                address = str(IPv4Address(resolver[u"ip_address"][0:4]))
            elif resolver[u"is_ipv6"] == 1:
                address = str(IPv6Address(resolver[u"ip_address"]))
            data.append({u"map resolver": address})
        return data

    @staticmethod
    def vpp_show_lisp_map_register(node):
        """Get LISP Map Register from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: LISP Map Register as python dict.
        :rtype: dict
        """

        cmd = u"show_lisp_map_register_state"
        err_msg = u"Failed to get LISP map register state on host " \
                  f"{node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        data = dict()
        data[u"state"] = u"enabled" if reply[u"is_enabled"] else u"disabled"
        logger.info(data)
        return data

    @staticmethod
    def vpp_show_lisp_map_request_mode(node):
        """Get LISP Map Request mode from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: LISP Map Request mode as python dict.
        :rtype: dict
        """

        cmd = u"show_lisp_map_request_mode"
        err_msg = u"Failed to get LISP map request mode on host " \
                  f"{node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        data = dict()
        data[u"map_request_mode"] = u"src-dst" if reply[u"mode"] else \
                                    u"dst-only"
        logger.info(data)
        return data

    @staticmethod
    def vpp_show_lisp_map_server(node):
        """Get LISP Map Server from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: LISP Map Server as python list.
        :rtype: list
        """

        cmd = u"lisp_map_server_dump"
        err_msg = f"Failed to get LISP map server on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        data = []
        for server in details:
            address = u"Bad is_ipv6 flag"
            if server[u"is_ipv6"] == 0:
                address = str(IPv4Address(server[u"ip_address"][0:4]))
            elif server[u"is_ipv6"] == 1:
                address = str(IPv6Address(server[u"ip_address"]))
            data.append({u"map-server": address})
        logger.info(data)
        return data

    @staticmethod
    def vpp_show_lisp_petr_config(node):
        """Get LISP PETR configuration from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: LISP PETR configuration as python dict.
        :rtype: dict
        """

# Note: VAT is returning ipv6 address instead of ipv4

        cmd = u"show_lisp_use_petr"
        err_msg = f"Failed to get LISP petr config on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        data = dict()
        data[u"status"] = u"enabled" if reply[u"status"] else u"disabled"
        address = u"Bad is_ip4 flag"
        if reply[u"is_ip4"] == 0:
            address = str(IPv6Address(reply[u"address"]))
        elif reply[u"is_ip4"] == 1:
            address = str(IPv4Address(reply[u"address"][0:4]))
        data[u"address"] = address
        logger.info(data)
        return data

    @staticmethod
    def vpp_show_lisp_rloc_config(node):
        """Get LISP RLOC configuration from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: LISP RLOC configuration as python dict.
        :rtype: dict
        """

        cmd = u"show_lisp_rloc_probe_state"
        err_msg = f"Failed to get LISP rloc config on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        data = dict()
        data[u"state"] = u"enabled" if reply[u"is_enabled"] else u"disabled"
        logger.info(data)
        return data

    @staticmethod
    def vpp_show_lisp_pitr(node):
        """Get Lisp PITR feature config from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: Lisp PITR config data.
        :rtype: dict
        """

        cmd = u"show_lisp_pitr"
        err_msg = f"Failed to get LISP pitr on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        data = dict()
        data[u"status"] = u"enabled" if reply[u"status"] else u"disabled"
        return data

    @staticmethod
    def lisp_should_be_equal(lisp_val1, lisp_val2):
        """Fail if the lisp values are not equal.

        :param lisp_val1: First lisp value.
        :param lisp_val2: Second lisp value.
        :type lisp_val1: list
        :type lisp_val2: list
        """

        len1 = len(lisp_val1)
        len2 = len(lisp_val2)
        if len1 != len2:
            raise RuntimeError(u"Values are not same. "
                               f"Value 1 {lisp_val1} \n"
                               f"Value 2 {lisp_val2}."

        for tmp in lisp_val1:
            if tmp not in lisp_val2:
                raise RuntimeError(f"Value {tmp} not found in vpp:\n"
                                   f"{lisp_val2}")

    def lisp_locator_s_should_be_equal(self, locator_set1, locator_set2):
        """Fail if the lisp values are not equal.

        :param locator_set1: Generate lisp value.
        :param locator_set2: Lisp value from VPP.
        :type locator_set1: list
        :type locator_set2: list
        """

        locator_set_list = []
        for item in locator_set1:
            if item not in locator_set_list:
                locator_set_list.append(item)
        self.lisp_should_be_equal(locator_set_list, locator_set2)

    @staticmethod
    def generate_unique_lisp_locator_set_data(node, locator_set_number):
        """Generate a list of lisp locator_set we want set to VPP and
        then check if it is set correctly. All locator_sets are unique.

        :param node: VPP node.
        :param locator_set_number: Generate n locator_set.
        :type node: dict
        :type locator_set_number: str
        :returns: list of lisp locator_set, list of lisp locator_set expected
            from VAT.
        :rtype: tuple
        """

        topo = Topology()

        locator_set_list = []
        locator_set_list_vat = []
        i = 0
        for num in range(0, int(locator_set_number)):
            locator_list = []
            for interface in list(node[u"interfaces"].values()):
                link = interface.get("link")
                i += 1
                if link is None:
                    continue

                if_name = topo.get_interface_by_link_name(node, link)
                sw_if_index = topo.get_interface_sw_index(node, if_name)
                if if_name is not None:
                    locator = {u"locator-index": sw_if_index,
                               u"priority": i,
                               u"weight": i}
                    locator_list.append(locator)

            l_name = f"ls{num}"
            locator_set = {u"locator-set": l_name,
                           u"locator": locator_list}
            locator_set_list.append(locator_set)

            locator_set_vat = {u"ls_name": l_name,
                               u"ls_index": num}
            locator_set_list_vat.append(locator_set_vat)

        return locator_set_list, locator_set_list_vat

    @staticmethod
    def generate_duplicate_lisp_locator_set_data(node, locator_set_number):
        """Generate a list of lisp locator_set we want set to VPP and
        then check if it is set correctly. Some locator_sets are duplicated.

        :param node: VPP node.
        :param locator_set_number: Generate n locator_set.
        :type node: dict
        :type locator_set_number: str
        :returns: list of lisp locator_set, list of lisp locator_set expected
            from VAT.
        :rtype: tuple
        """

        topo = Topology()
        locator_set_list = []
        locator_set_list_vat = []
        i = 0
        for num in range(0, int(locator_set_number)):
            locator_list = []
            for interface in list(node[u"interfaces"].values()):
                link = interface.get(u"link")
                i += 1
                if link is None:
                    continue

                if_name = topo.get_interface_by_link_name(node, link)
                sw_if_index = topo.get_interface_sw_index(node, if_name)
                if if_name is not None:
                    l_name = f"ls{num}"
                    locator = {u"locator-index": sw_if_index,
                               u"priority": i,
                               u"weight": i}
                    locator_list.append(locator)
                    locator_set = {u"locator-set": l_name,
                                   u"locator": locator_list}
                    locator_set_list.append(locator_set)

                    locator_set_vat = {u"ls_name": l_name,
                                       u"ls_index": num}
                    locator_set_list_vat.append(locator_set_vat)

        return locator_set_list, locator_set_list_vat

    def lisp_is_empty(self, lisp_params):
        """Check if the input param are empty.

        :param lisp_params: Should be empty list.
        :type lisp_params: list
        """

        self.lisp_should_be_equal([], lisp_params)
