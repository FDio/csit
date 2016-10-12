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

from enum import Enum

from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatJsonUtil import VatJsonUtil


# pylint: disable=too-few-public-methods
class PolicyAction(Enum):
    """Policy actions."""
    BYPASS = 'bypass'
    DISCARD = 'discard'
    PROTECT = 'protect'

    def __init__(self, string):
        self.string = string


class CryptoAlg(Enum):
    """Encryption algorithms."""
    AES_CBC_128 = ('aes-cbc-128', 'AES-CBC', 16)
    AES_CBC_192 = ('aes-cbc-192', 'AES-CBC', 24)
    AES_CBC_256 = ('aes-cbc-256', 'AES-CBC', 32)

    def __init__(self, alg_name, scapy_name, key_len):
        self.alg_name = alg_name
        self.scapy_name = scapy_name
        self.key_len = key_len


class IntegAlg(Enum):
    """Integrity algorithm."""
    SHA1_96 = ('sha1-96', 'HMAC-SHA1-96', 20)
    SHA_256_128 = ('sha-256-128', 'SHA2-256-128', 32)
    SHA_384_192 = ('sha-384-192', 'SHA2-384-192', 48)
    SHA_512_256 = ('sha-512-256', 'SHA2-512-256', 64)

    def __init__(self, alg_name, scapy_name, key_len):
        self.alg_name = alg_name
        self.scapy_name = scapy_name
        self.key_len = key_len


class IPsecUtil(object):
    """IPsec utilities."""

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-locals

    @staticmethod
    def policy_action_bypass():
        """Return policy action bypass.

        :return: PolicyAction enum BYPASS object.
        :rtype: PolicyAction
        """
        return PolicyAction.BYPASS

    @staticmethod
    def policy_action_discard():
        """Return policy action discard.

        :return: PolicyAction enum DISCARD object.
        :rtype: PolicyAction
        """
        return PolicyAction.DISCARD

    @staticmethod
    def policy_action_protect():
        """Return policy action protect.

        :return: PolicyAction enum PROTECT object.
        :rtype: PolicyAction
        """
        return PolicyAction.PROTECT

    @staticmethod
    def crypto_alg_aes_cbc_128():
        """Return encryption algorithm aes-cbc-128.

        :return: CryptoAlg enum AES_CBC_128 object.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_CBC_128

    @staticmethod
    def crypto_alg_aes_cbc_192():
        """Return encryption algorithm aes-cbc-192.

        :return: CryptoAlg enum AES_CBC_192 objec.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_CBC_192

    @staticmethod
    def crypto_alg_aes_cbc_256():
        """Return encryption algorithm aes-cbc-256.

        :return: CryptoAlg enum AES_CBC_256 object.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_CBC_256

    @staticmethod
    def get_crypto_alg_key_len(crypto_alg):
        """Return encryption algorithm key length.

        :param crypto_alg: Encryption algorithm.
        :type crypto_alg: CryptoAlg
        :return: Key length.
        :rtype: int
        """
        return crypto_alg.key_len

    @staticmethod
    def get_crypto_alg_scapy_name(crypto_alg):
        """Return encryption algorithm scapy name.

        :param crypto_alg: Encryption algorithm.
        :type crypto_alg: CryptoAlg
        :return: Algorithm scapy name.
        :rtype: str
        """
        return crypto_alg.scapy_name

    @staticmethod
    def integ_alg_sha1_96():
        """Return integrity algorithm SHA1-96.

        :return: IntegAlg enum SHA1_96 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA1_96

    @staticmethod
    def integ_alg_sha_256_128():
        """Return integrity algorithm SHA-256-128.

        :return: IntegAlg enum SHA_256_128 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_256_128

    @staticmethod
    def integ_alg_sha_384_192():
        """Return integrity algorithm SHA-384-192.

        :return: IntegAlg enum SHA_384_192 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_384_192

    @staticmethod
    def integ_alg_sha_512_256():
        """Return integrity algorithm SHA-512-256.

        :return: IntegAlg enum SHA_512_256 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_512_256

    @staticmethod
    def get_integ_alg_key_len(integ_alg):
        """Return integrity algorithm key length.

        :param integ_alg: Integrity algorithm.
        :type integ_alg: IntegAlg
        :return: Key length.
        :rtype: int
        """
        return integ_alg.key_len

    @staticmethod
    def get_integ_alg_scapy_name(integ_alg):
        """Return integrity algorithm scapy name.

        :param integ_alg: Integrity algorithm.
        :type integ_alg: IntegAlg
        :return: Algorithm scapy name.
        :rtype: str
        """
        return integ_alg.scapy_name

    @staticmethod
    def vpp_ipsec_add_sad_entry(node, sad_id, spi, crypto_alg, crypto_key,
                                integ_alg, integ_key, tunnel_src=None,
                                tunnel_dst=None):
        """Create Security Association Database entry on the VPP node.

        :param node: VPP node to add SAD entry on.
        :param sad_id: SAD entry ID.
        :param spi: Security Parameter Index of this SAD entry.
        :param crypto_alg: The encryption algorithm name.
        :param crypto_key: The encryption key string.
        :param integ_alg: The integrity algorithm name.
        :param integ_key: The integrity key string.
        :param tunnel_src: Tunnel header source IPv4 or IPv6 address. If not
            specified ESP transport mode is used.
        :param tunnel_dst: Tunnel header destination IPv4 or IPv6 address. If
            not specified ESP transport mode is used.
        :type node: dict
        :type sad_id: int
        :type spi: int
        :type crypto_alg: CryptoAlg
        :type crypto_key: str
        :type integ_alg: str
        :type integ_key: str
        :type tunnel_src: str
        :type tunnel_dst: str
        """
        ckey = crypto_key.encode('hex')
        ikey = integ_key.encode('hex')
        tunnel = 'tunnel_src {0} tunnel_dst {1}'.format(tunnel_src, tunnel_dst)\
            if tunnel_src is not None and tunnel_dst is not None else ''

        out = VatExecutor.cmd_from_template(node,
                                            "ipsec/ipsec_sad_add_entry.vat",
                                            sad_id=sad_id, spi=spi,
                                            calg=crypto_alg.alg_name, ckey=ckey,
                                            ialg=integ_alg.alg_name, ikey=ikey,
                                            tunnel=tunnel)
        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add SAD entry failed on {0}'.format(node['host']))

    @staticmethod
    def vpp_ipsec_sa_set_key(node, sa_id, crypto_key, integ_key):
        """Update Security Association (SA) keys.

        :param node: VPP node to update SA keys.
        :param sa_id: SAD entry ID.
        :param crypto_key: The encryption key string.
        :param integ_key: The integrity key string.
        :type node: dict
        :type sa_id: int
        :type crypto_key: str
        :type integ_key: str
        """
        ckey = crypto_key.encode('hex')
        ikey = integ_key.encode('hex')

        out = VatExecutor.cmd_from_template(node,
                                            "ipsec/ipsec_sa_set_key.vat",
                                            sa_id=sa_id,
                                            ckey=ckey, ikey=ikey)
        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Update SA key failed on {0}'.format(node['host']))

    @staticmethod
    def vpp_ipsec_add_spd(node, spd_id):
        """Create Security Policy Database on the VPP node.

        :param node: VPP node to add SPD on.
        :param spd_id: SPD ID.
        :type node: dict
        :type spd_id: int
        """
        out = VatExecutor.cmd_from_template(node, "ipsec/ipsec_spd_add.vat",
                                            spd_id=spd_id)
        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add SPD {0} failed on {1}'.format(spd_id, node['host']))

    @staticmethod
    def vpp_ipsec_spd_add_if(node, spd_id, interface):
        """Add interface to the Security Policy Database.

        :param node: VPP node.
        :param spd_id: SPD ID to add interface on.
        :param interface: Interface name or sw_if_index.
        :type node: dict
        :type spd_id: int
        :type interface: str or int
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)\
            if isinstance(interface, basestring) else interface

        out = VatExecutor.cmd_from_template(node,
                                            "ipsec/ipsec_interface_add_spd.vat",
                                            spd_id=spd_id, sw_if_id=sw_if_index)
        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add interface {0} to SPD {1} failed on {2}'.format(
                interface, spd_id, node['host']))

    @staticmethod
    def vpp_ipsec_spd_add_entry(node, spd_id, priority, action, inbound=True,
                                sa_id=None, laddr_range=None, raddr_range=None,
                                proto=None, lport_range=None, rport_range=None):
        """Create Security Policy Database entry on the VPP node.

        :param node: VPP node to add SPD entry on.
        :param spd_id: SPD ID to add entry on.
        :param priority: SPD entry priority, higher number = higher priority.
        :param action: Policy action.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param sa_id: SAD entry ID for protect action.
        :param laddr_range: Policy selector local IPv4 or IPv6 address range in
            format IP/prefix or IP/mask. If no mask is provided, it's considered
            to be /32.
        :param raddr_range: Policy selector remote IPv4 or IPv6 address range in
            format IP/prefix or IP/mask. If no mask is provided, it's considered
            to be /32.
        :param proto: Policy selector next layer protocol number.
        :param lport_range: Policy selector local TCP/UDP port range in format
            <port_start>-<port_end>.
        :param rport_range: Policy selector remote TCP/UDP port range in format
            <port_start>-<port_end>.
        :type node: dict
        :type spd_id: int
        :type priority: int
        :type action: PolicyAction
        :type inbound: bool
        :type sa_id: int
        :type laddr_range: string
        :type raddr_range: string
        :type proto: int
        :type lport_range: string
        :type rport_range: string
        """
        direction = 'inbound' if inbound else 'outbound'

        act_str = action.value
        if PolicyAction.PROTECT == action and sa_id is not None:
            act_str += 'sa_id {0}'.format(sa_id)

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

        out = VatExecutor.cmd_from_template(node,
                                            "ipsec/ipsec_spd_add_entry.vat",
                                            spd_id=spd_id, priority=priority,
                                            action=act_str, direction=direction,
                                            selector=selector)
        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add entry to SPD {0} failed on {1}'.format(spd_id,
                                                                node['host']))

    @staticmethod
    def vpp_ipsec_show(node):
        """Run "show ipsec" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        VatExecutor().execute_script("ipsec/ipsec_show.vat", node,
                                     json_out=False)
