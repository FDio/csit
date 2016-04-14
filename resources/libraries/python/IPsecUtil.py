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

"""IPsec utilities library."""

from ipaddress import ip_network

from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.topology import Topology

class IPsecUtil(object):
    """IPsec utilities."""

    # pylint: disable=too-many-arguments
    @staticmethod
    def vpp_ipsec_add_sad_entry(node, sad_id, spi, crypto_alg, crypto_key,
                                integ_alg, integ_key, tunnel_src=None,
                                tunnel_dst=None):
        """Create Security Association Database entry on the VPP node.

        :param node: VPP node to add SAD entry on.
        :param sad_id: SAD entry ID.
        :param spi: Security Parameter Index of this SAD entry.
        :param crypto_alg: The encryption algorithm name (aes-cbc-128,
            aes-cbc-192, aes-cbc-256).
        :param crypto_key: The encryption key string.
        :param integ_alg: The integrity algorithm name(sha1-96, sha-256-96,
            sha-256-128, sha-384-192, sha-512-256).
        :param integ_key: The integrity key string.
        :param tunnel_src: Tunnel header source IPv4 or IPv6 address. If not
            specified ESP transport mode is used.
        :param tunnel_dst: Tunnel header destination IPv4 or IPv6 address. If
            not specified ESP transport mode is used.
        :type node: dict
        :type sad_id: int
        :type spi: int
        :type crypto_alg: str
        :type crypto_key: str
        :type integ_alg: str
        :type integ_key: str
        :type tunnel_src: str
        :type tunnel_dst: str
        """
        ckey = crypto_key.encode('hex')
        ikey = integ_key.encode('hex')
        tunnel = ''
        if tunnel_src is not None and tunnel_dst is not None:
            tunnel = 'tunnel_src {0} tunnel_dst {1}'.format(tunnel_src,
                                                            tunnel_dst)
        VatExecutor.cmd_from_template(node, "ipsec_sad_add_entry.vat",
                                      sad_id=sad_id, spi=spi, calg=crypto_alg,
                                      ckey=ckey, ialg=integ_alg, ikey=ikey,
                                      tunnel=tunnel)

    @staticmethod
    def vpp_ipsec_add_spd(node, spd_id):
        """Create Security Policy Database on the VPP node.

        :param node: VPP node to add SPD on.
        :param spd_id: SPD ID.
        :type node: dict
        :type spd_id: int
        """
        VatExecutor.cmd_from_template(node, "ipsec_spd_add.vat", spd_id=spd_id)

    @staticmethod
    def vpp_ipsec_spd_add_if(node, spd_id, interface):
        """Add interface to the SPD.

        :param node: VPP node.
        :param spd_id: SPD ID to add interface on.
        :param interface: Interface name or sw_if_index.
        :type node: dict
        :type spd_id: int
        :type interface: str or int
        """
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface
        VatExecutor.cmd_from_template(node, "ipsec_interface_add_spd.vat",
                                      spd_id=spd_id, sw_if_id=sw_if_index)

    @staticmethod
    def vpp_ipsec_spd_add_entry(node, spd_id, priority, action, direction,
                                sa_id=None, laddr_range=None, raddr_range=None,
                                proto=None, lport_range=None, rport_range=None):
        """Create Security Policy Database entry on the VPP node.

        :param node: VPP node to add SPD entry on.
        :param spd_id: SPD ID to add entry on.
        :param priority: SPD entry priority, higher number = higher priority.
        :param action: Policy action (bypass, discard, protect).
        :param direction: Inbound or outbound traffic.
        :param sa_id: SAD entry ID for protect action.
        :param laddr_range: Policy selector local IPv4 or IPv6 address range in
            format IP/prefix or IP/mask. If no mask is provided, it's considered
            to be /32.
        :param raddr_range: Policy selector remote IPv4 or IPv6 address range in
            format IP/prefix or IP/mask. If no mask is provided, it's considered
            to be /32.
        :param proto: Policy selector next layer protocol number.
        :param lport_range: Policy selector local TCP/UDP port range in foramt
            <port_start>-<port_end>.
        :param rport_range: Policy selector remote TCP/UDP port range in foramt
            <port_start>-<port_end>.
        """
        if 'protect' == action and sa_id is not None:
            action += 'sa_id {0}'.format(sa_id)

        selector = ''
        if laddr_range is not None:
            net = ip_network(unicode(laddr_range), strict=False)
            selector += 'laddr_start {0} laddr_stop {1} '.format(
                net.network_address, net.broadcast_address)
        if raddr_range is not None:
            net = ip_network(unicode(raddr_range), strict=False)
            selector += 'raddr_start {0} raddr_stop {1} '.format(
                net.network_address, net.broadcast_address)
        if proto is not None:
            selector += 'protocol {0} '.format(proto)
        if lport_range is not None:
            selector += 'lport_start {p[0]} lport_stop {p[1]} '.format(
                p=lport_range.split('-'))
        if rport_range is not None:
            selector += 'rport_start {p[0]} rport_stop {p[1]} '.format(
                p=rport_range.split('-'))

        VatExecutor.cmd_from_template(node, "ipsec_spd_add_entry.vat",
                                      spd_id=spd_id, priority=priority,
                                      action=action, direction=direction,
                                      selector=selector)

    @staticmethod
    def vpp_ipsec_show(node):
        """Run "show ipsec" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("ipsec_show.vat", node, json_out=False)
