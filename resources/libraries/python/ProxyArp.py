# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Proxy ARP library"""

from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.VatExecutor import VatTerminal


class ProxyArp(object):
    """Proxy ARP utilities."""

    @staticmethod
    def vpp_add_proxy_arp(node, lo_ip4_addr, hi_ip4_addr):
        """Enable proxy ARP for a range of IP addresses.

        :param node: VPP node to enable proxy ARP.
        :param lo_ip4_addr: The lower limit of the IP addresses.
        :param hi_ip4_addr: The upper limit of the IP addresses.
        :type node: dict
        :type lo_ip4_addr: str
        :type hi_ip4_addr: str
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template("add_proxy_arp.vat",
                                                    lo_ip4_addr=lo_ip4_addr,
                                                    hi_ip4_addr=hi_ip4_addr)

    @staticmethod
    def vpp_proxy_arp_interface_enable(node, interface):
        """Enable proxy ARP on interface.

        :param node: VPP node to enable proxy ARP on interface.
        :param interface: Interface to enable proxy ARP.
        :type node: dict
        :type interface: str or int
        """

        cmd = 'proxy_arp_intfc_enable_disable'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_sw_index(node, interface),
            enable_disable=1)
        err_msg = 'Failed to enable proxy ARP on interface {ifc}'.format(
            ifc=interface)
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)
