# Copyright (c) 2018 Cisco and/or its affiliates.
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
from ipaddress import ip_network, ip_address

from enum import Enum

from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatJsonUtil import VatJsonUtil


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
    AES_GCM_128 = ('aes-gcm-128', 'AES-GCM', 20)

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
    AES_GCM_128 = ('aes-gcm-128', 'AES-GCM', 20)

    def __init__(self, alg_name, scapy_name, key_len):
        self.alg_name = alg_name
        self.scapy_name = scapy_name
        self.key_len = key_len


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
    def crypto_alg_aes_cbc_192():
        """Return encryption algorithm aes-cbc-192.

        :returns: CryptoAlg enum AES_CBC_192 objec.
        :rtype: CryptoAlg
        """
        return CryptoAlg.AES_CBC_192

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
    def integ_alg_sha1_96():
        """Return integrity algorithm SHA1-96.

        :returns: IntegAlg enum SHA1_96 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA1_96

    @staticmethod
    def integ_alg_sha_256_128():
        """Return integrity algorithm SHA-256-128.

        :returns: IntegAlg enum SHA_256_128 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_256_128

    @staticmethod
    def integ_alg_sha_384_192():
        """Return integrity algorithm SHA-384-192.

        :returns: IntegAlg enum SHA_384_192 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_384_192

    @staticmethod
    def integ_alg_sha_512_256():
        """Return integrity algorithm SHA-512-256.

        :returns: IntegAlg enum SHA_512_256 object.
        :rtype: IntegAlg
        """
        return IntegAlg.SHA_512_256

    @staticmethod
    def integ_alg_aes_gcm_128():
        """Return integrity algorithm AES-GCM-128.

        :returns: IntegAlg enum AES_GCM_128 object.
        :rtype: IntegAlg
        """
        return IntegAlg.AES_GCM_128

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
    def vpp_ipsec_add_sad_entries(node, n_entries, sad_id, spi, crypto_alg,
                                  crypto_key, integ_alg, integ_key,
                                  tunnel_src=None, tunnel_dst=None):
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
        tmp_filename = '/tmp/ipsec_sad_{0}_add_del_entry.script'.format(sad_id)
        ckey = crypto_key.encode('hex')
        ikey = integ_key.encode('hex')
        tunnel = 'tunnel_src {0} tunnel_dst {1}'.format(tunnel_src, tunnel_dst)\
            if tunnel_src is not None and tunnel_dst is not None else ''

        integ = 'integ_alg {0} integ_key {1}'.format(integ_alg.alg_name, ikey)\
            if crypto_alg.alg_name != 'aes-gcm-128' else ''

        with open(tmp_filename, 'w') as tmp_file:
            for i in range(0, n_entries):
                buf_str = 'ipsec_sad_add_del_entry esp sad_id {0} spi {1} ' \
                          'crypto_alg {2} crypto_key {3} {4} {5}\n'.format(
                              sad_id+i, spi+i, crypto_alg.alg_name, ckey, integ,
                              tunnel)
                tmp_file.write(buf_str)
        vat = VatExecutor()
        vat.execute_script(tmp_filename, node, timeout=300, json_out=False,
                           copy_on_execute=True)
        os.remove(tmp_filename)

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
    def vpp_ipsec_spd_add_entries(node, n_entries, spd_id, priority, inbound,
                                  sa_id, raddr_ip, raddr_range):
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
        :param raddr_range: Mask specifying range of Policy selector Remote IPv4
            addresses. Valid values are from 1 to 32.
        :type node: dict
        :type n_entries: int
        :type spd_id: int
        :type priority: int
        :type inbound: bool
        :type sa_id: int
        :type raddr_ip: string
        :type raddr_range: int
        """
        tmp_filename = '/tmp/ipsec_spd_{0}_add_del_entry.script'.format(sa_id)

        direction = 'inbound' if inbound else 'outbound'
        addr_incr = 1 << (32 - raddr_range)
        addr_ip = int(ip_address(unicode(raddr_ip)))
        start_str = 'ipsec_spd_add_del_entry spd_id {0} priority {1} {2} ' \
                    'action protect sa_id'.format(spd_id, priority, direction)
        with open(tmp_filename, 'w') as tmp_file:
            for i in range(0, n_entries):
                r_ip_s = ip_address(addr_ip + addr_incr * i)
                r_ip_e = ip_address(addr_ip + addr_incr * (i+1) - 1)
                buf_str = '{0} {1} raddr_start {2} raddr_stop {3}\n'.format(
                    start_str, sa_id+i, r_ip_s, r_ip_e)
                tmp_file.write(buf_str)
        vat = VatExecutor()
        vat.execute_script(tmp_filename, node, timeout=300, json_out=False,
                           copy_on_execute=True)
        os.remove(tmp_filename)

    @staticmethod
    def vpp_ipsec_create_tunnel_interfaces(node1, node2, if1_ip_addr,
                                           if2_ip_addr, if1_key, if2_key,
                                           n_tunnels, crypto_alg, crypto_key,
                                           integ_alg, integ_key, raddr_ip1,
                                           raddr_ip2, raddr_range):
        """Create multiple IPsec tunnel interfaces between two VPP nodes.

        :param node1: VPP node 1 to create tunnel interfaces.
        :param node2: VPP node 2 to create tunnel interfaces.
        :param if1_ip_addr: VPP node 1 interface IP4 address.
        :param if2_ip_addr: VPP node 2 interface IP4 address.
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 interface key from topology file.
        :param n_tunnels: Number of tunnell interfaces to create.
        :param crypto_alg: The encryption algorithm name.
        :param crypto_key: The encryption key string.
        :param integ_alg: The integrity algorithm name.
        :param integ_key: The integrity key string.
        :param raddr_ip1: Policy selector remote IPv4 start address for the
            first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4 start address for the
            first tunnel in direction node2->node1.
        :param raddr_range: Mask specifying range of Policy selector Remote IPv4
            addresses. Valid values are from 1 to 32.
        :type node1: dict
        :type node2: dict
        :type if1_ip_addr: str
        :type if2_ip_addr: str
        :type if1_key: str
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg
        :type crypto_key: str
        :type integ_alg: IntegAlg
        :type integ_key: str
        :type raddr_ip1: string
        :type raddr_ip2: string
        :type raddr_range: int
        """
        spi_1 = 10000
        spi_2 = 20000

        raddr_ip1_i = int(ip_address(unicode(raddr_ip1)))
        raddr_ip2_i = int(ip_address(unicode(raddr_ip2)))
        addr_incr = 1 << (32 - raddr_range)

        tmp_fn1 = '/tmp/ipsec_create_tunnel_dut1.config'
        tmp_fn2 = '/tmp/ipsec_create_tunnel_dut2.config'

        ckey = crypto_key.encode('hex')
        ikey = integ_key.encode('hex')

        vat = VatExecutor()
        with open(tmp_fn1, 'w') as tmp_f1, open(tmp_fn2, 'w') as tmp_f2:
            for i in range(0, n_tunnels):
                integ = ''
                if crypto_alg.alg_name != 'aes-gcm-128':
                    integ = 'integ_alg {integ_alg} '\
                            'local_integ_key {local_integ_key} '\
                            'remote_integ_key {remote_integ_key} '\
                            .format(integ_alg=integ_alg.alg_name,
                                    local_integ_key=ikey,
                                    remote_integ_key=ikey)
                dut1_tunnel = 'ipsec_tunnel_if_add_del '\
                              'local_spi {local_spi} '\
                              'remote_spi {remote_spi} '\
                              'crypto_alg {crypto_alg} '\
                              'local_crypto_key {local_crypto_key} '\
                              'remote_crypto_key {remote_crypto_key} '\
                              '{integ} '\
                              'local_ip {local_ip} '\
                              'remote_ip {remote_ip}\n'\
                              .format(local_spi=spi_1+i,
                                      remote_spi=spi_2+i,
                                      crypto_alg=crypto_alg.alg_name,
                                      local_crypto_key=ckey,
                                      remote_crypto_key=ckey,
                                      integ=integ,
                                      local_ip=if1_ip_addr,
                                      remote_ip=if2_ip_addr)
                dut2_tunnel = 'ipsec_tunnel_if_add_del '\
                              'local_spi {local_spi} '\
                              'remote_spi {remote_spi} '\
                              'crypto_alg {crypto_alg} '\
                              'local_crypto_key {local_crypto_key} '\
                              'remote_crypto_key {remote_crypto_key} '\
                              '{integ} '\
                              'local_ip {local_ip} '\
                              'remote_ip {remote_ip}\n'\
                              .format(local_spi=spi_2+i,
                                      remote_spi=spi_1+i,
                                      crypto_alg=crypto_alg.alg_name,
                                      local_crypto_key=ckey,
                                      remote_crypto_key=ckey,
                                      integ=integ,
                                      local_ip=if2_ip_addr,
                                      remote_ip=if1_ip_addr)
                tmp_f1.write(dut1_tunnel)
                tmp_f2.write(dut2_tunnel)
        vat.execute_script(tmp_fn1, node1, timeout=300, json_out=False,
                           copy_on_execute=True)
        vat.execute_script(tmp_fn2, node2, timeout=300, json_out=False,
                           copy_on_execute=True)
        os.remove(tmp_fn1)
        os.remove(tmp_fn2)

        with open(tmp_fn1, 'w') as tmp_f1, open(tmp_fn2, 'w') as tmp_f2:
            for i in range(0, n_tunnels):
                raddr_ip1 = ip_address(raddr_ip1_i + addr_incr*i)
                raddr_ip2 = ip_address(raddr_ip2_i + addr_incr*i)
                dut1_if = Topology.get_interface_name(node1, if1_key)
                dut1 = 'ip_add_del_route {raddr}/{mask} via {addr} ipsec{i}\n'\
                       'exec set interface unnumbered ipsec{i} use {uifc}\n'\
                       'sw_interface_set_flags ipsec{i} admin-up\n'\
                       .format(raddr=raddr_ip2, mask=raddr_range,
                               addr=if2_ip_addr, i=i, uifc=dut1_if)
                dut2_if = Topology.get_interface_name(node2, if2_key)
                dut2 = 'ip_add_del_route {raddr}/{mask} via {addr} ipsec{i}\n'\
                       'exec set interface unnumbered ipsec{i} use {uifc}\n'\
                       'sw_interface_set_flags ipsec{i} admin-up\n'\
                       .format(raddr=raddr_ip1, mask=raddr_range,
                               addr=if1_ip_addr, i=i, uifc=dut2_if)
                tmp_f1.write(dut1)
                tmp_f2.write(dut2)

        vat.execute_script(tmp_fn1, node1, timeout=300, json_out=False,
                           copy_on_execute=True)
        vat.execute_script(tmp_fn2, node2, timeout=300, json_out=False,
                           copy_on_execute=True)
        os.remove(tmp_fn1)
        os.remove(tmp_fn2)

    @staticmethod
    def vpp_ipsec_add_multiple_tunnels(node1, node2, interface1, interface2,
                                       n_tunnels, crypto_alg, crypto_key,
                                       integ_alg, integ_key, tunnel_ip1,
                                       tunnel_ip2, raddr_ip1, raddr_ip2,
                                       raddr_range):
        """Create multiple IPsec tunnels between two VPP nodes.

        :param node1: VPP node 1 to create tunnels.
        :param node2: VPP node 2 to create tunnels.
        :param interface1: Interface name or sw_if_index on node 1.
        :param interface2: Interface name or sw_if_index on node 2.
        :param n_tunnels: Number of tunnels to create.
        :param crypto_alg: The encryption algorithm name.
        :param crypto_key: The encryption key string.
        :param integ_alg: The integrity algorithm name.
        :param integ_key: The integrity key string.
        :param tunnel_ip1: Tunnel node1 IPv4 address.
        :param tunnel_ip2: Tunnel node2 IPv4 address.
        :param raddr_ip1: Policy selector remote IPv4 start address for the
            first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4 start address for the
            first tunnel in direction node2->node1.
        :param raddr_range: Mask specifying range of Policy selector Remote IPv4
            addresses. Valid values are from 1 to 32.
        :type node1: dict
        :type node2: dict
        :type interface1: str or int
        :type interface2: str or int
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg
        :type crypto_key: str
        :type integ_alg: str
        :type integ_key: str
        :type tunnel_ip1: str
        :type tunnel_ip2: str
        :type raddr_ip1: string
        :type raddr_ip2: string
        :type raddr_range: int
        """
        spd_id = 1
        p_hi = 100
        p_lo = 10
        sa_id_1 = 10000
        sa_id_2 = 20000
        spi_1 = 30000
        spi_2 = 40000
        proto = 50

        IPsecUtil.vpp_ipsec_add_spd(node1, spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(node1, spd_id, interface1)
        IPsecUtil.vpp_ipsec_spd_add_entry(node1, spd_id, p_hi,
                                          PolicyAction.BYPASS, inbound=False,
                                          proto=proto)
        IPsecUtil.vpp_ipsec_spd_add_entry(node1, spd_id, p_hi,
                                          PolicyAction.BYPASS, inbound=True,
                                          proto=proto)

        IPsecUtil.vpp_ipsec_add_spd(node2, spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(node2, spd_id, interface2)
        IPsecUtil.vpp_ipsec_spd_add_entry(node2, spd_id, p_hi,
                                          PolicyAction.BYPASS, inbound=False,
                                          proto=proto)
        IPsecUtil.vpp_ipsec_spd_add_entry(node2, spd_id, p_hi,
                                          PolicyAction.BYPASS, inbound=True,
                                          proto=proto)

        IPsecUtil.vpp_ipsec_add_sad_entries(node1, n_tunnels, sa_id_1, spi_1,
                                            crypto_alg, crypto_key, integ_alg,
                                            integ_key, tunnel_ip1, tunnel_ip2)

        IPsecUtil.vpp_ipsec_spd_add_entries(node1, n_tunnels, spd_id, p_lo,
                                            False, sa_id_1, raddr_ip2,
                                            raddr_range)

        IPsecUtil.vpp_ipsec_add_sad_entries(node2, n_tunnels, sa_id_1, spi_1,
                                            crypto_alg, crypto_key, integ_alg,
                                            integ_key, tunnel_ip1, tunnel_ip2)

        IPsecUtil.vpp_ipsec_spd_add_entries(node2, n_tunnels, spd_id, p_lo,
                                            True, sa_id_1, raddr_ip2,
                                            raddr_range)

        IPsecUtil.vpp_ipsec_add_sad_entries(node2, n_tunnels, sa_id_2, spi_2,
                                            crypto_alg, crypto_key, integ_alg,
                                            integ_key, tunnel_ip2, tunnel_ip1)

        IPsecUtil.vpp_ipsec_spd_add_entries(node2, n_tunnels, spd_id, p_lo,
                                            False, sa_id_2, raddr_ip1,
                                            raddr_range)

        IPsecUtil.vpp_ipsec_add_sad_entries(node1, n_tunnels, sa_id_2, spi_2,
                                            crypto_alg, crypto_key, integ_alg,
                                            integ_key, tunnel_ip2, tunnel_ip1)

        IPsecUtil.vpp_ipsec_spd_add_entries(node1, n_tunnels, spd_id, p_lo,
                                            True, sa_id_2, raddr_ip1,
                                            raddr_range)

    @staticmethod
    def vpp_ipsec_show(node):
        """Run "show ipsec" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        VatExecutor().execute_script("ipsec/ipsec_show.vat", node,
                                     json_out=False)
