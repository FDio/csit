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

"""IPsec utilities library."""

import os

from random import choice
from string import letters

from enum import Enum, IntEnum
from ipaddress import ip_network, ip_address

from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.InterfaceUtil import InterfaceUtil, \
    InterfaceStatusFlags
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import scp_node
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor


def gen_key(length):
    """Generate random string as a key.

    :param length: Length of generated payload.
    :type length: int
    :returns: The generated payload.
    :rtype: str
    """
    return ''.join(choice(letters) for _ in range(length))


class PolicyAction(Enum):
    """Policy actions."""
    BYPASS = ('bypass', 0)
    DISCARD = ('discard', 1)
    PROTECT = ('protect', 3)

    def __init__(self, policy_name, policy_int_repr):
        self.policy_name = policy_name
        self.policy_int_repr = policy_int_repr


class CryptoAlg(Enum):
    """Encryption algorithms."""
    AES_CBC_128 = ('aes-cbc-128', 1, 'AES-CBC', 16)
    AES_CBC_256 = ('aes-cbc-256', 3, 'AES-CBC', 32)
    AES_GCM_128 = ('aes-gcm-128', 7, 'AES-GCM', 16)
    AES_GCM_256 = ('aes-gcm-256', 9, 'AES-GCM', 32)

    def __init__(self, alg_name, alg_int_repr, scapy_name, key_len):
        self.alg_name = alg_name
        self.alg_int_repr = alg_int_repr
        self.scapy_name = scapy_name
        self.key_len = key_len


class IntegAlg(Enum):
    """Integrity algorithm."""
    SHA_256_128 = ('sha-256-128', 4, 'SHA2-256-128', 32)
    SHA_512_256 = ('sha-512-256', 6, 'SHA2-512-256', 64)

    def __init__(self, alg_name, alg_int_repr, scapy_name, key_len):
        self.alg_name = alg_name
        self.alg_int_repr = alg_int_repr
        self.scapy_name = scapy_name
        self.key_len = key_len


class IPsecProto(IntEnum):
    """IPsec protocol."""
    ESP = 1
    SEC_AH = 0


class IPsecSadFlags(IntEnum):
    """IPsec Security Association Database flags."""
    IPSEC_API_SAD_FLAG_NONE = 0
    IPSEC_API_SAD_FLAG_IS_TUNNEL = 4
    IPSEC_API_SAD_FLAG_IS_TUNNEL_V6 = 8


class IPsecUtil(object):
    """IPsec utilities."""

    @staticmethod
    def policy_action_bypass():
        """Return policy action bypass.

        :returns: PolicyAction enum BYPASS object.
        :rtype: PolicyAction
        """
        return PolicyAction.BYPASS

    @staticmethod
    def policy_action_discard():
        """Return policy action discard.

        :returns: PolicyAction enum DISCARD object.
        :rtype: PolicyAction
        """
        return PolicyAction.DISCARD

    @staticmethod
    def policy_action_protect():
        """Return policy action protect.

        :returns: PolicyAction enum PROTECT object.
        :rtype: PolicyAction
        """
        return PolicyAction.PROTECT

    @staticmethod
    def crypto_alg_aes_cbc_128():
        """Return encryption algorithm aes-cbc-128.

        :returns: CryptoAlg enum AES_CBC_128 object.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_CBC_128

    @staticmethod
    def crypto_alg_aes_cbc_256():
        """Return encryption algorithm aes-cbc-256.

        :returns: CryptoAlg enum AES_CBC_256 object.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_CBC_256

    @staticmethod
    def crypto_alg_aes_gcm_128():
        """Return encryption algorithm aes-gcm-128.

        :returns: CryptoAlg enum AES_GCM_128 object.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_GCM_128

    @staticmethod
    def crypto_alg_aes_gcm_256():
        """Return encryption algorithm aes-gcm-256.

        :returns: CryptoAlg enum AES_GCM_128 object.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_GCM_256

    @staticmethod
    def get_crypto_alg_key_len(crypto_alg):
        """Return encryption algorithm key length.

        :param crypto_alg: Encryption algorithm.
        :type crypto_alg: CryptoAlg
        :returns: Key length.
        :rtype: int
        """
        return crypto_alg.key_len

    @staticmethod
    def get_crypto_alg_scapy_name(crypto_alg):
        """Return encryption algorithm scapy name.

        :param crypto_alg: Encryption algorithm.
        :type crypto_alg: CryptoAlg
        :returns: Algorithm scapy name.
        :rtype: str
        """
        return crypto_alg.scapy_name

    @staticmethod
    def integ_alg_sha_256_128():
        """Return integrity algorithm SHA-256-128.

        :returns: IntegAlg enum SHA_256_128 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_256_128

    @staticmethod
    def integ_alg_sha_512_256():
        """Return integrity algorithm SHA-512-256.

        :returns: IntegAlg enum SHA_512_256 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_512_256

    @staticmethod
    def get_integ_alg_key_len(integ_alg):
        """Return integrity algorithm key length.

        :param integ_alg: Integrity algorithm.
        :type integ_alg: IntegAlg
        :returns: Key length.
        :rtype: int
        """
        return integ_alg.key_len

    @staticmethod
    def get_integ_alg_scapy_name(integ_alg):
        """Return integrity algorithm scapy name.

        :param integ_alg: Integrity algorithm.
        :type integ_alg: IntegAlg
        :returns: Algorithm scapy name.
        :rtype: str
        """
        return integ_alg.scapy_name

    @staticmethod
    def ipsec_proto_esp():
        """Return IPSec protocol ESP.

        :returns: IPsecProto enum ESP object.
        :rtype: IPsecProto
        """
        return int(IPsecProto.ESP)

    @staticmethod
    def ipsec_proto_ah():
        """Return IPSec protocol AH.

        :returns: IPsecProto enum AH object.
        :rtype: IPsecProto
        """
        return int(IPsecProto.SEC_AH)

    @staticmethod
    def vpp_ipsec_select_backend(node, protocol, index=1):
        """Select IPsec backend.

        :param node: VPP node to select IPsec backend on.
        :param protocol: IPsec protocol.
        :param index: Backend index.
        :type node: dict
        :type protocol: IPsecProto
        :type index: int
        :raises RuntimeError: If failed to select IPsec backend or if no API
            reply received.
        """
        cmd = 'ipsec_select_backend'
        err_msg = 'Failed to select IPsec backend on host {host}'.format(
            host=node['host'])
        args = dict(
            protocol=protocol,
            index=index
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_backend_dump(node):
        """Dump IPsec backends.

        :param node: VPP node to dump IPsec backend on.
        :type node: dict
        """
        err_msg = 'Failed to dump IPsec backends on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add('ipsec_backend_dump').get_details(err_msg)

    @staticmethod
    def vpp_ipsec_add_sad_entry(
            node, sad_id, spi, crypto_alg, crypto_key, integ_alg=None,
            integ_key='', tunnel_src=None, tunnel_dst=None):
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
        :type integ_alg: IntegAlg
        :type integ_key: str
        :type tunnel_src: str
        :type tunnel_dst: str
        """
        ckey = dict(
            length=len(crypto_key),
            data=crypto_key
        )
        ikey = dict(
            length=len(integ_key),
            data=integ_key if integ_key else 0
        )

        flags = int(IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE)
        if tunnel_src and tunnel_dst:
            flags = flags | int(IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL)
            src_addr = ip_address(unicode(tunnel_src))
            dst_addr = ip_address(unicode(tunnel_dst))
            if src_addr.version == 6:
                flags = \
                    flags | int(IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL_V6)
        else:
            src_addr = ''
            dst_addr = ''

        cmd = 'ipsec_sad_entry_add_del'
        err_msg = 'Failed to add Security Association Database entry on ' \
                  'host {host}'.format(host=node['host'])
        sad_entry = dict(
            sad_id=int(sad_id),
            spi=int(spi),
            crypto_algorithm=crypto_alg.alg_int_repr,
            crypto_key=ckey,
            integrity_algorithm=integ_alg.alg_int_repr if integ_alg else 0,
            integrity_key=ikey,
            flags=flags,
            tunnel_src=str(src_addr),
            tunnel_dst=str(dst_addr),
            protocol=int(IPsecProto.ESP)
        )
        args = dict(
            is_add=1,
            entry=sad_entry
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_add_sad_entries(
            node, n_entries, sad_id, spi, crypto_alg, crypto_key,
            integ_alg=None, integ_key='', tunnel_src=None, tunnel_dst=None):
        """Create multiple Security Association Database entries on VPP node.

        :param node: VPP node to add SAD entry on.
        :param n_entries: Number of SAD entries to be created.
        :param sad_id: First SAD entry ID. All subsequent SAD entries will have
            id incremented by 1.
        :param spi: Security Parameter Index of first SAD entry. All subsequent
            SAD entries will have spi incremented by 1.
        :param crypto_alg: The encryption algorithm name.
        :param crypto_key: The encryption key string.
        :param integ_alg: The integrity algorithm name.
        :param integ_key: The integrity key string.
        :param tunnel_src: Tunnel header source IPv4 or IPv6 address. If not
            specified ESP transport mode is used.
        :param tunnel_dst: Tunnel header destination IPv4 or IPv6 address. If
            not specified ESP transport mode is used.
        :type node: dict
        :type n_entries: int
        :type sad_id: int
        :type spi: int
        :type crypto_alg: CryptoAlg
        :type crypto_key: str
        :type integ_alg: IntegAlg
        :type integ_key: str
        :type tunnel_src: str
        :type tunnel_dst: str
        """
        if tunnel_src and tunnel_dst:
            src_addr = ip_address(unicode(tunnel_src))
            dst_addr = ip_address(unicode(tunnel_dst))
        else:
            src_addr = ''
            dst_addr = ''

        addr_incr = 1 << (128 - 96) if src_addr.version == 6 \
            else 1 << (32 - 24)

        if int(n_entries) > 10:
            tmp_filename = '/tmp/ipsec_sad_{0}_add_del_entry.script'.\
                format(sad_id)

            with open(tmp_filename, 'w') as tmp_file:
                for i in xrange(n_entries):
                    integ = (
                        'integ-alg {integ_alg} integ-key {integ_key}'.format(
                            integ_alg=integ_alg.alg_name,
                            integ_key=integ_key.encode('hex'))
                        if integ_alg else '')
                    tunnel = (
                        'tunnel-src {laddr} tunnel-dst {raddr}'.format(
                            laddr=src_addr + i * addr_incr,
                            raddr=dst_addr + i * addr_incr)
                        if tunnel_src and tunnel_dst else '')
                    conf = (
                        'exec ipsec sa add {sad_id} esp spi {spi} '
                        'crypto-alg {crypto_alg} crypto-key {crypto_key} '
                        '{integ} {tunnel}\n'.format(
                            sad_id=sad_id + i,
                            spi=spi + i,
                            crypto_alg=crypto_alg.alg_name,
                            crypto_key=crypto_key.encode('hex'),
                            integ=integ,
                            tunnel=tunnel))
                    tmp_file.write(conf)
            vat = VatExecutor()
            vat.execute_script(tmp_filename, node, timeout=300, json_out=False,
                               copy_on_execute=True)
            os.remove(tmp_filename)
            return

        ckey = dict(
            length=len(crypto_key),
            data=crypto_key
        )
        ikey = dict(
            length=len(integ_key),
            data=integ_key if integ_key else 0
        )

        flags = int(IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE)
        if tunnel_src and tunnel_dst:
            flags = flags | int(IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL)
            if src_addr.version == 6:
                flags = flags | int(
                    IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL_V6)

        cmd = 'ipsec_sad_entry_add_del'
        err_msg = 'Failed to add Security Association Database entry on ' \
                  'host {host}'.format(host=node['host'])

        sad_entry = dict(
            sad_id=int(sad_id),
            spi=int(spi),
            crypto_algorithm=crypto_alg.alg_int_repr,
            crypto_key=ckey,
            integrity_algorithm=integ_alg.alg_int_repr if integ_alg else 0,
            integrity_key=ikey,
            flags=flags,
            tunnel_src=str(src_addr),
            tunnel_dst=str(dst_addr),
            protocol=int(IPsecProto.ESP)
        )
        args = dict(
            is_add=1,
            entry=sad_entry
        )
        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(n_entries):
                args['entry']['sad_id'] = int(sad_id) + i
                args['entry']['spi'] = int(spi) + i
                args['entry']['tunnel_src'] = str(src_addr + i * addr_incr) \
                    if tunnel_src and tunnel_dst else src_addr
                args['entry']['tunnel_dst'] = str(dst_addr + i * addr_incr) \
                    if tunnel_src and tunnel_dst else dst_addr
                history = False if 1 < i < n_entries - 1 else True
                papi_exec.add(cmd, history=history, **args)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_set_ip_route(
            node, n_tunnels, tunnel_src, traffic_addr, tunnel_dst, interface,
            raddr_range):
        """Set IP address and route on interface.

        :param node: VPP node to add config on.
        :param n_tunnels: Number of tunnels to create.
        :param tunnel_src: Tunnel header source IPv4 or IPv6 address.
        :param traffic_addr: Traffic destination IP address to route.
        :param tunnel_dst: Tunnel header destination IPv4 or IPv6 address.
        :param interface: Interface key on node 1.
        :param raddr_range: Mask specifying range of Policy selector Remote IP
            addresses. Valid values are from 1 to 32 in case of IPv4 and to 128
            in case of IPv6.
        :type node: dict
        :type n_tunnels: int
        :type tunnel_src: str
        :type traffic_addr: str
        :type tunnel_dst: str
        :type interface: str
        :type raddr_range: int
        """
        laddr = ip_address(unicode(tunnel_src))
        raddr = ip_address(unicode(tunnel_dst))
        taddr = ip_address(unicode(traffic_addr))
        addr_incr = 1 << (128 - raddr_range) if laddr.version == 6 \
            else 1 << (32 - raddr_range)

        if int(n_tunnels) > 10:
            tmp_filename = '/tmp/ipsec_set_ip.script'

            with open(tmp_filename, 'w') as tmp_file:
                for i in xrange(n_tunnels):
                    conf = (
                        'exec set interface ip address {interface} '
                        '{laddr}/{laddr_l}\n'
                        'exec ip route add {taddr}/{taddr_l} via {raddr} '
                        '{interface}\n'.format(
                            interface=Topology.get_interface_name(
                                node, interface),
                            laddr=laddr + i * addr_incr,
                            laddr_l=raddr_range,
                            raddr=raddr + i * addr_incr,
                            taddr=taddr + i,
                            taddr_l=128 if taddr.version == 6 else 32))
                    tmp_file.write(conf)
            vat = VatExecutor()
            vat.execute_script(tmp_filename, node, timeout=300, json_out=False,
                               copy_on_execute=True)
            os.remove(tmp_filename)
            return

        cmd1 = 'sw_interface_add_del_address'
        args1 = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=True,
            del_all=False,
            prefix=None
        )
        cmd2 = 'ip_route_add_del'
        args2 = dict(
            is_add=1,
            is_multipath=0,
            route=None
        )
        err_msg = 'Failed to configure IP addresses and IP routes on ' \
                  'interface {ifc} on host {host}'.\
            format(ifc=interface, host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(n_tunnels):
                args1['prefix'] = IPUtil.create_prefix_object(
                    laddr + i * addr_incr, raddr_range)
                args2['route'] = IPUtil.compose_vpp_route_structure(
                    node,
                    taddr + i,
                    prefix_len=128 if taddr.version == 6 else 32,
                    interface=interface,
                    gateway=raddr + i * addr_incr
                )
                history = False if 1 < i < n_tunnels - 1 else True
                papi_exec.add(cmd1, history=history, **args1).\
                    add(cmd2, history=history, **args2)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_add_spd(node, spd_id):
        """Create Security Policy Database on the VPP node.

        :param node: VPP node to add SPD on.
        :param spd_id: SPD ID.
        :type node: dict
        :type spd_id: int
        """
        cmd = 'ipsec_spd_add_del'
        err_msg = 'Failed to add Security Policy Database on host {host}'.\
            format(host=node['host'])
        args = dict(
            is_add=1,
            spd_id=int(spd_id)
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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
        cmd = 'ipsec_interface_add_del_spd'
        err_msg = 'Failed to add interface {ifc} to Security Policy Database ' \
                  '{spd} on host {host}'.\
            format(ifc=interface, spd=spd_id, host=node['host'])
        args = dict(
            is_add=1,
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            spd_id=int(spd_id)
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_policy_add(
            node, spd_id, priority, action, inbound=True, sa_id=None,
            laddr_range=None, raddr_range=None, proto=None, lport_range=None,
            rport_range=None, is_ipv6=False):
        """Create Security Policy Database entry on the VPP node.

        :param node: VPP node to add SPD entry on.
        :param spd_id: SPD ID to add entry on.
        :param priority: SPD entry priority, higher number = higher priority.
        :param action: Policy action.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param sa_id: SAD entry ID for protect action.
        :param laddr_range: Policy selector local IPv4 or IPv6 address range in
            format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param raddr_range: Policy selector remote IPv4 or IPv6 address range in
            format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param proto: Policy selector next layer protocol number.
        :param lport_range: Policy selector local TCP/UDP port range in format
            <port_start>-<port_end>.
        :param rport_range: Policy selector remote TCP/UDP port range in format
            <port_start>-<port_end>.
        :param is_ipv6: True in case of IPv6 policy when IPv6 address range is
            not defined so it will default to address ::/0, otherwise False.
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
        :type is_ipv6: bool
        """

        if laddr_range is None:
            laddr_range = '::/0' if is_ipv6 else '0.0.0.0/0'

        if raddr_range is None:
            raddr_range = '::/0' if is_ipv6 else '0.0.0.0/0'

        cmd = 'ipsec_spd_entry_add_del'
        err_msg = 'Failed to add entry to Security Policy Database ' \
                  '{spd} on host {host}'.format(spd=spd_id, host=node['host'])

        spd_entry = dict(
            spd_id=int(spd_id),
            priority=int(priority),
            is_outbound=0 if inbound else 1,
            sa_id=int(sa_id) if sa_id else 0,
            policy=action.policy_int_repr,
            protocol=int(proto) if proto else 0,
            remote_address_start=IPUtil.create_ip_address_object(
                ip_network(unicode(raddr_range), strict=False).network_address),
            remote_address_stop=IPUtil.create_ip_address_object(
                ip_network(
                    unicode(raddr_range), strict=False).broadcast_address),
            local_address_start=IPUtil.create_ip_address_object(
                ip_network(
                    unicode(laddr_range), strict=False).network_address),
            local_address_stop=IPUtil.create_ip_address_object(
                ip_network(
                    unicode(laddr_range), strict=False).broadcast_address),
            remote_port_start=int(rport_range.split('-')[0]) if rport_range
            else 0,
            remote_port_stop=int(rport_range.split('-')[1]) if rport_range
            else 65535,
            local_port_start=int(lport_range.split('-')[0]) if lport_range
            else 0,
            local_port_stop=int(lport_range.split('-')[1]) if rport_range
            else 65535
        )
        args = dict(
            is_add=1,
            entry=spd_entry
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_spd_add_entries(
            node, n_entries, spd_id, priority, inbound, sa_id, raddr_ip):
        """Create multiple Security Policy Database entries on the VPP node.

        :param node: VPP node to add SPD entries on.
        :param n_entries: Number of SPD entries to be added.
        :param spd_id: SPD ID to add entries on.
        :param priority: SPD entries priority, higher number = higher priority.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param sa_id: SAD entry ID for first entry. Each subsequent entry will
            SAD entry ID incremented by 1.
        :param raddr_ip: Policy selector remote IPv4 start address for the first
            entry. Remote IPv4 end address will be calculated depending on
            raddr_range parameter. Each subsequent entry will have start address
            next after IPv4 end address of previous entry.
        :type node: dict
        :type n_entries: int
        :type spd_id: int
        :type priority: int
        :type inbound: bool
        :type sa_id: int
        :type raddr_ip: string
        """
        if int(n_entries) > 10:
            tmp_filename = '/tmp/ipsec_spd_{0}_add_del_entry.script'.\
                format(sa_id)

            with open(tmp_filename, 'w') as tmp_file:
                for i in xrange(n_entries):
                    raddr_s = ip_address(unicode(raddr_ip)) + i
                    raddr_e = ip_address(unicode(raddr_ip)) + (i + 1) - 1
                    tunnel = (
                        'exec ipsec policy add spd {spd_id} '
                        'priority {priority} {direction} action protect '
                        'sa {sa_id} remote-ip-range {raddr_s} - {raddr_e} '
                        'local-ip-range 0.0.0.0 - 255.255.255.255\n'.
                        format(
                            spd_id=spd_id,
                            priority=priority,
                            direction='inbound' if inbound else 'outbound',
                            sa_id=sa_id+i,
                            raddr_s=raddr_s,
                            raddr_e=raddr_e))
                    tmp_file.write(tunnel)
            VatExecutor().execute_script(
                tmp_filename, node, timeout=300, json_out=False,
                copy_on_execute=True)
            os.remove(tmp_filename)
            return

        raddr_ip = ip_address(unicode(raddr_ip))
        laddr_range = '::/0' if raddr_ip.version == 6 else '0.0.0.0/0'

        cmd = 'ipsec_spd_entry_add_del'
        err_msg = 'Failed to add entry to Security Policy Database ' \
                  '{spd} on host {host}'.format(spd=spd_id, host=node['host'])

        spd_entry = dict(
            spd_id=int(spd_id),
            priority=int(priority),
            is_outbound=0 if inbound else 1,
            sa_id=int(sa_id) if sa_id else 0,
            policy=IPsecUtil.policy_action_protect().policy_int_repr,
            protocol=0,
            remote_address_start=IPUtil.create_ip_address_object(raddr_ip),
            remote_address_stop=IPUtil.create_ip_address_object(raddr_ip),
            local_address_start=IPUtil.create_ip_address_object(
                ip_network(unicode(laddr_range), strict=False).network_address),
            local_address_stop=IPUtil.create_ip_address_object(
                ip_network(
                    unicode(laddr_range), strict=False).broadcast_address),
            remote_port_start=0,
            remote_port_stop=65535,
            local_port_start=0,
            local_port_stop=65535
        )
        args = dict(
            is_add=1,
            entry=spd_entry
        )

        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(n_entries):
                args['entry']['remote_address_start']['un'] = \
                    IPUtil.union_addr(raddr_ip + i)
                args['entry']['remote_address_stop']['un'] = \
                    IPUtil.union_addr(raddr_ip + i)
                history = False if 1 < i < n_entries - 1 else True
                papi_exec.add(cmd, history=history, **args)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_create_tunnel_interfaces(
            nodes, if1_ip_addr, if2_ip_addr, if1_key, if2_key, n_tunnels,
            crypto_alg, integ_alg, raddr_ip1, raddr_ip2, raddr_range):
        """Create multiple IPsec tunnel interfaces between two VPP nodes.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param if1_ip_addr: VPP node 1 interface IPv4/IPv6 address.
        :param if2_ip_addr: VPP node 2 interface IPv4/IPv6 address.
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 interface key from topology file.
        :param n_tunnels: Number of tunnel interfaces to create.
        :param crypto_alg: The encryption algorithm name.
        :param integ_alg: The integrity algorithm name.
        :param raddr_ip1: Policy selector remote IPv4/IPv6 start address for the
            first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4/IPv6 start address for the
            first tunnel in direction node2->node1.
        :param raddr_range: Mask specifying range of Policy selector Remote
            IPv4/IPv6 addresses. Valid values are from 1 to 32 in case of IPv4
            and to 128 in case of IPv6.
        :type nodes: dict
        :type if1_ip_addr: str
        :type if2_ip_addr: str
        :type if1_key: str
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg
        :type integ_alg: IntegAlg
        :type raddr_ip1: string
        :type raddr_ip2: string
        :type raddr_range: int
        """
        n_tunnels = int(n_tunnels)
        spi_1 = 100000
        spi_2 = 200000
        if1_ip = ip_address(unicode(if1_ip_addr))
        if2_ip = ip_address(unicode(if2_ip_addr))
        raddr_ip1 = ip_address(unicode(raddr_ip1))
        raddr_ip2 = ip_address(unicode(raddr_ip2))
        addr_incr = 1 << (128 - raddr_range) if if1_ip.version == 6 \
            else 1 << (32 - raddr_range)

        if n_tunnels > 10:
            tmp_fn1 = '/tmp/ipsec_create_tunnel_dut1.config'
            tmp_fn2 = '/tmp/ipsec_create_tunnel_dut2.config'
            vat = VatExecutor()
            with open(tmp_fn1, 'w') as tmp_f1, open(tmp_fn2, 'w') as tmp_f2:
                tmp_f1.write(
                    'exec create loopback interface\n'
                    'exec set interface state loop0 up\n'
                    'exec set interface ip address {uifc} {iaddr}/{mask}\n'
                    .format(
                        iaddr=if2_ip - 1,
                        uifc=Topology.get_interface_name(
                            nodes['DUT1'], if1_key),
                        mask=96 if if2_ip.version == 6 else 24))
                tmp_f2.write(
                    'exec set interface ip address {uifc} {iaddr}/{mask}\n'
                    .format(
                        iaddr=if2_ip,
                        uifc=Topology.get_interface_name(
                            nodes['DUT2'], if2_key),
                        mask=96 if if2_ip.version == 6 else 24))
                for i in xrange(n_tunnels):
                    ckey = gen_key(IPsecUtil.get_crypto_alg_key_len(
                        crypto_alg)).encode('hex')
                    if integ_alg:
                        ikey = gen_key(IPsecUtil.get_integ_alg_key_len(
                            integ_alg)).encode('hex')
                        integ = (
                            'integ_alg {integ_alg} '
                            'local_integ_key {local_integ_key} '
                            'remote_integ_key {remote_integ_key} '
                            .format(
                                integ_alg=integ_alg.alg_name,
                                local_integ_key=ikey,
                                remote_integ_key=ikey))
                    else:
                        integ = ''
                    tmp_f1.write(
                        'exec set interface ip address loop0 {laddr}/32\n'
                        'ipsec_tunnel_if_add_del '
                        'local_spi {local_spi} '
                        'remote_spi {remote_spi} '
                        'crypto_alg {crypto_alg} '
                        'local_crypto_key {local_crypto_key} '
                        'remote_crypto_key {remote_crypto_key} '
                        '{integ} '
                        'local_ip {laddr} '
                        'remote_ip {raddr}\n'
                        .format(
                            local_spi=spi_1 + i,
                            remote_spi=spi_2 + i,
                            crypto_alg=crypto_alg.alg_name,
                            local_crypto_key=ckey,
                            remote_crypto_key=ckey,
                            integ=integ,
                            laddr=if1_ip + i * addr_incr,
                            raddr=if2_ip))
                    tmp_f2.write(
                        'ipsec_tunnel_if_add_del '
                        'local_spi {local_spi} '
                        'remote_spi {remote_spi} '
                        'crypto_alg {crypto_alg} '
                        'local_crypto_key {local_crypto_key} '
                        'remote_crypto_key {remote_crypto_key} '
                        '{integ} '
                        'local_ip {laddr} '
                        'remote_ip {raddr}\n'
                        .format(
                            local_spi=spi_2 + i,
                            remote_spi=spi_1 + i,
                            crypto_alg=crypto_alg.alg_name,
                            local_crypto_key=ckey,
                            remote_crypto_key=ckey,
                            integ=integ,
                            laddr=if2_ip,
                            raddr=if1_ip + i * addr_incr))
            vat.execute_script(
                tmp_fn1, nodes['DUT1'], timeout=1800, json_out=False,
                copy_on_execute=True,
                history=False if n_tunnels > 100 else True)
            vat.execute_script(
                tmp_fn2, nodes['DUT2'], timeout=1800, json_out=False,
                copy_on_execute=True,
                history=False if n_tunnels > 100 else True)
            os.remove(tmp_fn1)
            os.remove(tmp_fn2)

            with open(tmp_fn1, 'w') as tmp_f1, open(tmp_fn2, 'w') as tmp_f2:
                tmp_f2.write(
                    'exec ip route add {raddr} via {uifc} {iaddr}\n'
                    .format(
                        raddr=ip_network(unicode(if1_ip_addr+'/8'), False),
                        iaddr=if2_ip - 1,
                        uifc=Topology.get_interface_name(
                            nodes['DUT2'], if2_key)))
                for i in xrange(n_tunnels):
                    tmp_f1.write(
                        'exec set interface unnumbered ipsec{i} use {uifc}\n'
                        'exec set interface state ipsec{i} up\n'
                        'exec ip route add {taddr}/{mask} via ipsec{i}\n'
                        .format(
                            taddr=raddr_ip2 + i,
                            i=i,
                            uifc=Topology.get_interface_name(nodes['DUT1'],
                                                             if1_key),
                            mask=128 if if2_ip.version == 6 else 32))
                    tmp_f2.write(
                        'exec set interface unnumbered ipsec{i} use {uifc}\n'
                        'exec set interface state ipsec{i} up\n'
                        'exec ip route add {taddr}/{mask} via ipsec{i}\n'
                        .format(
                            taddr=raddr_ip1 + i,
                            i=i,
                            uifc=Topology.get_interface_name(nodes['DUT2'],
                                                             if2_key),
                            mask=128 if if2_ip.version == 6 else 32))
            vat.execute_script(
                tmp_fn1, nodes['DUT1'], timeout=1800, json_out=False,
                copy_on_execute=True,
                history=False if n_tunnels > 100 else True)
            vat.execute_script(
                tmp_fn2, nodes['DUT2'], timeout=1800, json_out=False,
                copy_on_execute=True,
                history=False if n_tunnels > 100 else True)
            os.remove(tmp_fn1)
            os.remove(tmp_fn2)
            return

        with PapiSocketExecutor(nodes['DUT1']) as papi_exec:
            # Create loopback interface on DUT1, set it to up state
            cmd1 = 'create_loopback'
            args1 = dict(mac_address=0)
            err_msg = 'Failed to create loopback interface on host {host}'.\
                format(host=nodes['DUT1']['host'])
            loop_sw_if_idx = papi_exec.add(cmd1, **args1).\
                get_sw_if_index(err_msg)
            cmd1 = 'sw_interface_set_flags'
            args1 = dict(
                sw_if_index=loop_sw_if_idx,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value)
            err_msg = 'Failed to set loopback interface state up on host ' \
                      '{host}'.format(host=nodes['DUT1']['host'])
            papi_exec.add(cmd1, **args1).get_reply(err_msg)
            # Set IP address on VPP node 1 interface
            cmd1 = 'sw_interface_add_del_address'
            args1 = dict(
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes['DUT1'], if1_key),
                is_add=True,
                del_all=False,
                prefix=IPUtil.create_prefix_object(
                    if2_ip - 1, 96 if if2_ip.version == 6 else 24)
            )
            err_msg = 'Failed to set IP address on interface {ifc} on host ' \
                      '{host}'.format(ifc=if1_key, host=nodes['DUT1']['host'])
            papi_exec.add(cmd1, **args1).get_reply(err_msg)
            # Configure IPsec tunnel interfaces
            args1 = dict(
                sw_if_index=loop_sw_if_idx,
                is_add=True,
                del_all=False,
                prefix=None
            )
            cmd2 = 'ipsec_tunnel_if_add_del'
            args2 = dict(
                is_add=1,
                local_ip=None,
                remote_ip=None,
                local_spi=0,
                remote_spi=0,
                crypto_alg=crypto_alg.alg_int_repr,
                local_crypto_key_len=0,
                local_crypto_key=None,
                remote_crypto_key_len=0,
                remote_crypto_key=None,
                integ_alg=integ_alg.alg_int_repr if integ_alg else 0,
                local_integ_key_len=0,
                local_integ_key=None,
                remote_integ_key_len=0,
                remote_integ_key=None,
                tx_table_id=0
            )
            err_msg = 'Failed to add IPsec tunnel interfaces on host {host}'.\
                format(host=nodes['DUT1']['host'])
            ipsec_tunnels = list()
            ckeys = list()
            ikeys = list()
            for i in xrange(n_tunnels):
                ckeys.append(
                    gen_key(IPsecUtil.get_crypto_alg_key_len(crypto_alg)))
                if integ_alg:
                    ikeys.append(
                        gen_key(IPsecUtil.get_integ_alg_key_len(integ_alg)))
                args1['prefix'] = IPUtil.create_prefix_object(
                    if1_ip + i * addr_incr, 128 if if1_ip.version == 6 else 32)
                args2['local_spi'] = spi_1 + i
                args2['remote_spi'] = spi_2 + i
                args2['local_ip'] = IPUtil.create_ip_address_object(
                    if1_ip + i * addr_incr)
                args2['remote_ip'] = IPUtil.create_ip_address_object(if2_ip)
                args2['local_crypto_key_len'] = len(ckeys[i])
                args2['local_crypto_key'] = ckeys[i]
                args2['remote_crypto_key_len'] = len(ckeys[i])
                args2['remote_crypto_key'] = ckeys[i]
                if integ_alg:
                    args2['local_integ_key_len'] = len(ikeys[i])
                    args2['local_integ_key'] = ikeys[i]
                    args2['remote_integ_key_len'] = len(ikeys[i])
                    args2['remote_integ_key'] = ikeys[i]
                history = False if 1 < i < n_tunnels - 1 else True
                papi_exec.add(cmd1, history=history, **args1).\
                    add(cmd2, history=history, **args2)
            replies = papi_exec.get_replies(err_msg)
            for reply in replies:
                if 'sw_if_index' in reply:
                    ipsec_tunnels.append(reply["sw_if_index"])
            # Configure IP routes
            cmd1 = 'sw_interface_set_unnumbered'
            args1 = dict(
                is_add=True,
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes['DUT1'], if1_key),
                unnumbered_sw_if_index=0
            )
            cmd2 = 'sw_interface_set_flags'
            args2 = dict(
                sw_if_index=0,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value)
            cmd3 = 'ip_route_add_del'
            args3 = dict(
                is_add=1,
                is_multipath=0,
                route=None
            )
            err_msg = 'Failed to add IP routes on host {host}'.format(
                host=nodes['DUT1']['host'])
            for i in xrange(n_tunnels):
                args1['unnumbered_sw_if_index'] = ipsec_tunnels[i]
                args2['sw_if_index'] = ipsec_tunnels[i]
                args3['route'] = IPUtil.compose_vpp_route_structure(
                    nodes['DUT1'],
                    (raddr_ip2 + i).compressed,
                    prefix_len=128 if raddr_ip2.version == 6 else 32,
                    interface=ipsec_tunnels[i]
                )
                history = False if 1 < i < n_tunnels - 1 else True
                papi_exec.add(cmd1, history=history, **args1).\
                    add(cmd2, history=history, **args2).\
                    add(cmd3, history=history, **args3)
            papi_exec.get_replies(err_msg)

        with PapiSocketExecutor(nodes['DUT2']) as papi_exec:
            # Set IP address on VPP node 2 interface
            cmd1 = 'sw_interface_add_del_address'
            args1 = dict(
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes['DUT2'], if2_key),
                is_add=True,
                del_all=False,
                prefix=IPUtil.create_prefix_object(
                    if2_ip, 96 if if2_ip.version == 6 else 24)
            )
            err_msg = 'Failed to set IP address on interface {ifc} on host ' \
                      '{host}'.format(ifc=if2_key, host=nodes['DUT2']['host'])
            papi_exec.add(cmd1, **args1).get_reply(err_msg)
            # Configure IPsec tunnel interfaces
            cmd2 = 'ipsec_tunnel_if_add_del'
            args2 = dict(
                is_add=1,
                local_ip=IPUtil.create_ip_address_object(if2_ip),
                remote_ip=None,
                local_spi=0,
                remote_spi=0,
                crypto_alg=crypto_alg.alg_int_repr,
                local_crypto_key_len=0,
                local_crypto_key=None,
                remote_crypto_key_len=0,
                remote_crypto_key=None,
                integ_alg=integ_alg.alg_int_repr if integ_alg else 0,
                local_integ_key_len=0,
                local_integ_key=None,
                remote_integ_key_len=0,
                remote_integ_key=None,
                tx_table_id=0
            )
            err_msg = 'Failed to add IPsec tunnel interfaces on host {host}'. \
                format(host=nodes['DUT2']['host'])
            ipsec_tunnels = list()
            for i in xrange(n_tunnels):
                args2['local_spi'] = spi_2 + i
                args2['remote_spi'] = spi_1 + i
                args2['local_ip'] = IPUtil.create_ip_address_object(if2_ip)
                args2['remote_ip'] = IPUtil.create_ip_address_object(
                    if1_ip + i * addr_incr)
                args2['local_crypto_key_len'] = len(ckeys[i])
                args2['local_crypto_key'] = ckeys[i]
                args2['remote_crypto_key_len'] = len(ckeys[i])
                args2['remote_crypto_key'] = ckeys[i]
                if integ_alg:
                    args2['local_integ_key_len'] = len(ikeys[i])
                    args2['local_integ_key'] = ikeys[i]
                    args2['remote_integ_key_len'] = len(ikeys[i])
                    args2['remote_integ_key'] = ikeys[i]
                history = False if 1 < i < n_tunnels - 1 else True
                papi_exec.add(cmd2, history=history, **args2)
            replies = papi_exec.get_replies(err_msg)
            for reply in replies:
                if 'sw_if_index' in reply:
                    ipsec_tunnels.append(reply["sw_if_index"])
            # Configure IP routes
            cmd1 = 'ip_route_add_del'
            route = IPUtil.compose_vpp_route_structure(
                nodes['DUT2'], if1_ip.compressed,
                prefix_len=32 if if1_ip.version == 6 else 8,
                interface=if2_key,
                gateway=(if2_ip - 1).compressed
            )
            args1 = dict(
                is_add=1,
                is_multipath=0,
                route=route
            )
            papi_exec.add(cmd1, **args1)
            cmd1 = 'sw_interface_set_unnumbered'
            args1 = dict(
                is_add=True,
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes['DUT2'], if2_key),
                unnumbered_sw_if_index=0
            )
            cmd2 = 'sw_interface_set_flags'
            args2 = dict(
                sw_if_index=0,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value)
            cmd3 = 'ip_route_add_del'
            args3 = dict(
                is_add=1,
                is_multipath=0,
                route=None
            )
            err_msg = 'Failed to add IP routes on host {host}'.format(
                host=nodes['DUT2']['host'])
            for i in xrange(n_tunnels):
                args1['unnumbered_sw_if_index'] = ipsec_tunnels[i]
                args2['sw_if_index'] = ipsec_tunnels[i]
                args3['route'] = IPUtil.compose_vpp_route_structure(
                    nodes['DUT1'],
                    (raddr_ip1 + i).compressed,
                    prefix_len=128 if raddr_ip1.version == 6 else 32,
                    interface=ipsec_tunnels[i]
                )
                history = False if 1 < i < n_tunnels - 1 else True
                papi_exec.add(cmd1, history=history, **args1). \
                    add(cmd2, history=history, **args2). \
                    add(cmd3, history=history, **args3)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_create_tunnel_interfaces_in_containers(
            nodes, if1_ip_addr, if2_ip_addr, if1_key, if2_key, n_tunnels,
            crypto_alg, integ_alg, raddr_ip1, raddr_ip2, raddr_range,
            n_instances):
        """Create multiple IPsec tunnel interfaces between two VPP nodes.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param if1_ip_addr: VPP node 1 interface IP4 address.
        :param if2_ip_addr: VPP node 2 interface IP4 address.
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 interface key from topology file.
        :param n_tunnels: Number of tunnell interfaces to create.
        :param crypto_alg: The encryption algorithm name.
        :param integ_alg: The integrity algorithm name.
        :param raddr_ip1: Policy selector remote IPv4 start address for the
            first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4 start address for the
            first tunnel in direction node2->node1.
        :param raddr_range: Mask specifying range of Policy selector Remote
            IPv4 addresses. Valid values are from 1 to 32.
        :param n_instances: Number of containers.
        :type nodes: dict
        :type if1_ip_addr: str
        :type if2_ip_addr: str
        :type if1_key: str
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg
        :type integ_alg: IntegAlg
        :type raddr_ip1: string
        :type raddr_ip2: string
        :type raddr_range: int
        :type n_instances: int
        """
        spi_1 = 100000
        spi_2 = 200000
        addr_incr = 1 << (32 - raddr_range)

        dut1_script_file = '/tmp/ipsec_create_tunnel_cnf_dut1.config'

        vat = VatExecutor()

        cnf_scripts = []
        for cnf in range(0, n_instances):
            cnf_script_file = '/tmp/ipsec_create_tunnel_cnf_dut2_'\
                              '{cnf}.config'.format(cnf=cnf + 1)
            cnf_scripts.append(open(cnf_script_file, 'w', buffering=0))
            cnf_scripts[cnf].write(
                'ip route add {raddr} via {mid}\n'
                .format(raddr=ip_network(unicode(if1_ip_addr+'/8'), False),
                        mid='memif1/{cnf}'.format(cnf=cnf+1)))

        with open(dut1_script_file, 'w', buffering=0) as dut1_script:
            for tnl in range(0, n_tunnels):
                tnl_incr = tnl * addr_incr
                cnf = tnl % n_instances
                i = tnl // n_instances
                ckey = gen_key(IPsecUtil.get_crypto_alg_key_len(
                    crypto_alg)).encode('hex')
                integ = ''
                if integ_alg:
                    ikey = gen_key(IPsecUtil.get_integ_alg_key_len(
                        integ_alg)).encode('hex')
                    integ = (
                        'integ-alg {integ_alg} '
                        'local-integ-key {local_integ_key} '
                        'remote-integ-key {remote_integ_key} '
                        .format(
                            integ_alg=integ_alg.alg_name,
                            local_integ_key=ikey,
                            remote_integ_key=ikey))
                # Configure tunnel end point(s) on left side (baremetal VPP)
                dut1_script.write(
                    'exec set interface ip address {uifc} {laddr}/24\n'
                    'exec create ipsec tunnel '
                    'local-ip {laddr} '
                    'local-spi {local_spi} '
                    'remote-ip {raddr}'
                    'remote-spi {remote_spi} '
                    'crypto-alg {crypto_alg} '
                    'local-crypto-key {local_crypto_key} '
                    'remote-crypto-key {remote_crypto_key} '
                    '{integ} \n'
                    'exec set interface unnumbered ipsec{i} use {uifc}\n'
                    'exec set interface state ipsec{i} up\n'
                    'exec ip route add {taddr}/32 via ipsec{i}\n\n'
                    .format(
                        local_spi=spi_1 + tnl,
                        remote_spi=spi_2 + tnl,
                        crypto_alg=crypto_alg.alg_name,
                        local_crypto_key=ckey,
                        remote_crypto_key=ckey,
                        integ=integ,
                        laddr=ip_address(unicode(if1_ip_addr)) + tnl_incr,
                        raddr=ip_address(unicode(if2_ip_addr)) + cnf,
                        taddr=ip_address(unicode(raddr_ip2)) + tnl,
                        i=tnl,
                        uifc=Topology.get_interface_name(nodes['DUT1'],
                                                         if1_key)))

                # Configure tunnel end point(s) on right side (container VPP)
                cnf_scripts[cnf].write(
                    'create ipsec tunnel '
                    'local-ip {laddr} '
                    'local-spi {local_spi} '
                    'remote-ip {raddr} '
                    'remote-spi {remote_spi} '
                    'crypto-alg {crypto_alg} '
                    'local-crypto-key {local_crypto_key} '
                    'remote-crypto-key {remote_crypto_key} '
                    '{integ} \n'
                    'set interface unnumbered ipsec{i} use {uifc}\n'
                    'set interface state ipsec{i} up\n'
                    'ip route add {taddr}/32 via ipsec{i}\n\n'
                    .format(
                        local_spi=spi_2 + tnl,
                        remote_spi=spi_1 + tnl,
                        crypto_alg=crypto_alg.alg_name,
                        local_crypto_key=ckey,
                        remote_crypto_key=ckey,
                        integ=integ,
                        raddr=ip_address(unicode(if1_ip_addr)) + tnl_incr,
                        laddr=ip_address(unicode(if2_ip_addr)) + cnf,
                        taddr=ip_address(unicode(raddr_ip1)) + tnl,
                        i=i,
                        uifc='memif1/{cnf}'.format(cnf=cnf+1)))

        for cnf in range(0, n_instances):
            cnf_scripts[cnf].close()
            cnf_script_file = (
                '/tmp/ipsec_create_tunnel_cnf_dut2_{cnf}.config'.
                format(cnf=cnf + 1))
            scp_node(nodes['DUT2'], cnf_script_file, cnf_script_file)

        vat.execute_script(dut1_script_file, nodes['DUT1'], timeout=3600,
                           json_out=False,
                           copy_on_execute=True, history=False)

    @staticmethod
    def vpp_ipsec_add_multiple_tunnels(
            nodes, interface1, interface2, n_tunnels, crypto_alg, integ_alg,
            tunnel_ip1, tunnel_ip2, raddr_ip1, raddr_ip2, raddr_range):
        """Create multiple IPsec tunnels between two VPP nodes.

        :param nodes: VPP nodes to create tunnels.
        :param interface1: Interface name or sw_if_index on node 1.
        :param interface2: Interface name or sw_if_index on node 2.
        :param n_tunnels: Number of tunnels to create.
        :param crypto_alg: The encryption algorithm name.
        :param integ_alg: The integrity algorithm name.
        :param tunnel_ip1: Tunnel node1 IPv4 address.
        :param tunnel_ip2: Tunnel node2 IPv4 address.
        :param raddr_ip1: Policy selector remote IPv4 start address for the
            first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4 start address for the
            first tunnel in direction node2->node1.
        :param raddr_range: Mask specifying range of Policy selector Remote
            IPv4 addresses. Valid values are from 1 to 32.
        :type nodes: dict
        :type interface1: str or int
        :type interface2: str or int
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg
        :type integ_alg: IntegAlg
        :type tunnel_ip1: str
        :type tunnel_ip2: str
        :type raddr_ip1: string
        :type raddr_ip2: string
        :type raddr_range: int
        """
        spd_id = 1
        p_hi = 100
        p_lo = 10
        sa_id_1 = 100000
        sa_id_2 = 200000
        spi_1 = 300000
        spi_2 = 400000

        crypto_key = gen_key(IPsecUtil.get_crypto_alg_key_len(crypto_alg))
        integ_key = gen_key(IPsecUtil.get_integ_alg_key_len(integ_alg)) \
            if integ_alg else ''

        IPsecUtil.vpp_ipsec_set_ip_route(
            nodes['DUT1'], n_tunnels, tunnel_ip1, raddr_ip2, tunnel_ip2,
            interface1, raddr_range)
        IPsecUtil.vpp_ipsec_set_ip_route(
            nodes['DUT2'], n_tunnels, tunnel_ip2, raddr_ip1, tunnel_ip1,
            interface2, raddr_range)

        IPsecUtil.vpp_ipsec_add_spd(
            nodes['DUT1'], spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(
            nodes['DUT1'], spd_id, interface1)
        IPsecUtil.vpp_ipsec_policy_add(
            nodes['DUT1'], spd_id, p_hi, PolicyAction.BYPASS, inbound=False,
            proto=50, laddr_range='100.0.0.0/8', raddr_range='100.0.0.0/8')
        IPsecUtil.vpp_ipsec_policy_add(
            nodes['DUT1'], spd_id, p_hi, PolicyAction.BYPASS, inbound=True,
            proto=50, laddr_range='100.0.0.0/8', raddr_range='100.0.0.0/8')

        IPsecUtil.vpp_ipsec_add_spd(
            nodes['DUT2'], spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(
            nodes['DUT2'], spd_id, interface2)
        IPsecUtil.vpp_ipsec_policy_add(
            nodes['DUT2'], spd_id, p_hi, PolicyAction.BYPASS, inbound=False,
            proto=50, laddr_range='100.0.0.0/8', raddr_range='100.0.0.0/8')
        IPsecUtil.vpp_ipsec_policy_add(
            nodes['DUT2'], spd_id, p_hi, PolicyAction.BYPASS, inbound=True,
            proto=50, laddr_range='100.0.0.0/8', raddr_range='100.0.0.0/8')

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes['DUT1'], n_tunnels, sa_id_1, spi_1, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip1, tunnel_ip2)

        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes['DUT1'], n_tunnels, spd_id, p_lo, False, sa_id_1, raddr_ip2)

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes['DUT2'], n_tunnels, sa_id_1, spi_1, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip1, tunnel_ip2)

        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes['DUT2'], n_tunnels, spd_id, p_lo, True, sa_id_1, raddr_ip2)

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes['DUT2'], n_tunnels, sa_id_2, spi_2, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip2, tunnel_ip1)

        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes['DUT2'], n_tunnels, spd_id, p_lo, False, sa_id_2, raddr_ip1)

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes['DUT1'], n_tunnels, sa_id_2, spi_2, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip2, tunnel_ip1)

        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes['DUT1'], n_tunnels, spd_id, p_lo, True, sa_id_2, raddr_ip1)

    @staticmethod
    def vpp_ipsec_show(node):
        """Run "show ipsec" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, 'show ipsec')
