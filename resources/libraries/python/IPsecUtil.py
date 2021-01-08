# Copyright (c) 2021 Cisco and/or its affiliates.
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


from enum import Enum, IntEnum
from io import open
from random import choices
from string import (ascii_lowercase, ascii_uppercase)

from ipaddress import ip_network, ip_address

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil, \
    InterfaceStatusFlags
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.IPUtil import IPUtil, IpDscp, MPLS_LABEL_INVALID
from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import scp_node
from resources.libraries.python.topology import Topology


IPSEC_UDP_PORT_NONE = 0xffff


class PolicyAction(Enum):
    """Policy actions."""
    BYPASS = (u"bypass", 0)
    DISCARD = (u"discard", 1)
    PROTECT = (u"protect", 3)

    def __init__(self, policy_name, policy_int_repr):
        self.policy_name = policy_name
        self.policy_int_repr = policy_int_repr


class CryptoAlg(Enum):
    """Encryption algorithms."""
    AES_CBC_128 = (u"aes-cbc-128", 1, u"AES-CBC", 16)
    AES_CBC_256 = (u"aes-cbc-256", 3, u"AES-CBC", 32)
    AES_GCM_128 = (u"aes-gcm-128", 7, u"AES-GCM", 16)
    AES_GCM_256 = (u"aes-gcm-256", 9, u"AES-GCM", 32)

    def __init__(self, alg_name, alg_int_repr, scapy_name, key_len):
        self.alg_name = alg_name
        self.alg_int_repr = alg_int_repr
        self.scapy_name = scapy_name
        self.key_len = key_len


class IntegAlg(Enum):
    """Integrity algorithm."""
    SHA_256_128 = (u"sha-256-128", 4, u"SHA2-256-128", 32)
    SHA_512_256 = (u"sha-512-256", 6, u"SHA2-512-256", 64)

    def __init__(self, alg_name, alg_int_repr, scapy_name, key_len):
        self.alg_name = alg_name
        self.alg_int_repr = alg_int_repr
        self.scapy_name = scapy_name
        self.key_len = key_len


class IPsecProto(IntEnum):
    """IPsec protocol."""
    IPSEC_API_PROTO_ESP = 50
    IPSEC_API_PROTO_AH = 51


class IPsecSadFlags(IntEnum):
    """IPsec Security Association Database flags."""
    IPSEC_API_SAD_FLAG_NONE = 0
    # Enable extended sequence numbers
    IPSEC_API_SAD_FLAG_USE_ESN = 0x01
    # Enable Anti - replay
    IPSEC_API_SAD_FLAG_USE_ANTI_REPLAY = 0x02
    # IPsec tunnel mode if non-zero, else transport mode
    IPSEC_API_SAD_FLAG_IS_TUNNEL = 0x04
    # IPsec tunnel mode is IPv6 if non-zero, else IPv4 tunnel
    # only valid if is_tunnel is non-zero
    IPSEC_API_SAD_FLAG_IS_TUNNEL_V6 = 0x08
    # Enable UDP encapsulation for NAT traversal
    IPSEC_API_SAD_FLAG_UDP_ENCAP = 0x10
    # IPsec SA is or inbound traffic
    IPSEC_API_SAD_FLAG_IS_INBOUND = 0x40


class TunnelEncpaDecapFlags(IntEnum):
    """Flags controlling tunnel behaviour."""
    TUNNEL_API_ENCAP_DECAP_FLAG_NONE = 0
    # at encap, copy the DF bit of the payload into the tunnel header
    TUNNEL_API_ENCAP_DECAP_FLAG_ENCAP_COPY_DF = 1
    # at encap, set the DF bit in the tunnel header
    TUNNEL_API_ENCAP_DECAP_FLAG_ENCAP_SET_DF = 2
    # at encap, copy the DSCP bits of the payload into the tunnel header
    TUNNEL_API_ENCAP_DECAP_FLAG_ENCAP_COPY_DSCP = 4
    # at encap, copy the ECN bit of the payload into the tunnel header
    TUNNEL_API_ENCAP_DECAP_FLAG_ENCAP_COPY_ECN = 8
    # at decap, copy the ECN bit of the tunnel header into the payload
    TUNNEL_API_ENCAP_DECAP_FLAG_ENCAP_SET_ECN = 16


class TunnelMode(IntEnum):
    """Tunnel modes."""
    # point-to-point
    TUNNEL_API_MODE_P2P = 0
    # multi-point
    TUNNEL_API_MODE_MP = 1


class IPsecUtil:
    """IPsec utilities."""

    # We are generating random keys. But fast request generator
    # relies on a sequence on nonequal bytes.
    # In order to prevent error, we make sure the last bit always flips.
    LAST_KEY_BITS = list()
    """List of list of bool.
    The irst index is number of random value within a message,
    we need that beacuse bits should differ between messages,
    not between two fields within a single message.
    The second index enumerates bytes of the fiels.
    The bool is the last used value for the least significant bit.
    """

    @classmethod
    def gen_key(cls, length, index=0):
        """Generate random bytes string as a key.

        As some tests pass the generated keys through Robot variables
        and into bash command line arguments. We take care
        to generate keys consisting of letters only.
        Tests using PAPI only can manipulate keys as they wish,
        as long as the type is bytes, and length is correct.
        Fast scale data generator needs each byte to be different from
        the corresponding byte of the previous (same field of previous message),
        so we flip the least significant bit of each byte.
        To ensure all calls to this method still create only letters,
        we remove 'A', 'Z', 'a' and 'z' from the list of usable letters.
        Index parameter distinguishes fields within a message.
        Basically, generate ckey with 0 (default) and ikey with 1.

        :param length: Length of generated payload.
        :param index: Number of random key within a single message.
        :type length: int
        :type index: int
        :returns: The generated payload.
        :rtype: bytes
        """
        while len(cls.LAST_KEY_BITS) <= index:
            cls.LAST_KEY_BITS.append(list())
        bits = cls.LAST_KEY_BITS[index]
        letters = ascii_lowercase[1:-1] + ascii_uppercase[1:-1]
        key = bytearray(map(ord, choices(letters, k=length)))
        for count, key_byte in enumerate(key):
            if count == len(bits):
                bits.append(bool(key_byte & 1))
            elif bits[count]:
                key[count] &= 0xfe
                bits[count] = False
            else:
                key[count] |= 1
                bits[count] = True
        return bytes(key)

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
        return int(IPsecProto.IPSEC_API_PROTO_ESP)

    @staticmethod
    def ipsec_proto_ah():
        """Return IPSec protocol AH.

        :returns: IPsecProto enum AH object.
        :rtype: IPsecProto
        """
        return int(IPsecProto.IPSEC_API_PROTO_AH)

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
        cmd = u"ipsec_select_backend"
        err_msg = f"Failed to select IPsec backend on host {node[u'host']}"
        args = dict(
            protocol=protocol,
            index=index
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_set_async_mode(node, async_enable=1):
        """Set IPsec async mode on|off.

        :param node: VPP node to set IPsec async mode.
        :param async_enable: Async mode on or off.
        :type node: dict
        :type async_enable: int
        :raises RuntimeError: If failed to set IPsec async mode or if no API
            reply received.
        """
        cmd = u"ipsec_set_async_mode"
        err_msg = f"Failed to set IPsec async mode on host {node[u'host']}"
        args = dict(
            async_enable=async_enable
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_add_sad_entry(
            node, sad_id, spi, crypto_alg, crypto_key, integ_alg=None,
            integ_key=u"", tunnel_src=None, tunnel_dst=None):
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
        if isinstance(crypto_key, str):
            crypto_key = crypto_key.encode(encoding=u"utf-8")
        if isinstance(integ_key, str):
            integ_key = integ_key.encode(encoding=u"utf-8")
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
            src_addr = ip_address(tunnel_src)
            dst_addr = ip_address(tunnel_dst)
            if src_addr.version == 6:
                flags = \
                    flags | int(IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL_V6)
        else:
            src_addr = u""
            dst_addr = u""

        cmd = u"ipsec_sad_entry_add_del"
        err_msg = f"Failed to add Security Association Database entry " \
            f"on host {node[u'host']}"
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
            protocol=int(IPsecProto.IPSEC_API_PROTO_ESP),
            udp_src_port=4500,  # default value in api
            udp_dst_port=4500  # default value in api
        )
        args = dict(
            is_add=True,
            entry=sad_entry
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_add_sad_entries(
            node, n_entries, sad_id, spi, crypto_alg, crypto_key,
            integ_alg=None, integ_key=u"", tunnel_src=None, tunnel_dst=None):
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
        if isinstance(crypto_key, str):
            crypto_key = crypto_key.encode(encoding=u"utf-8")
        if isinstance(integ_key, str):
            integ_key = integ_key.encode(encoding=u"utf-8")
        if tunnel_src and tunnel_dst:
            src_addr = ip_address(tunnel_src)
            dst_addr = ip_address(tunnel_dst)
        else:
            src_addr = u""
            dst_addr = u""

        addr_incr = 1 << (128 - 96) if src_addr.version == 6 \
            else 1 << (32 - 24)

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
                    IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL_V6
                )

        cmd = u"ipsec_sad_entry_add_del"
        err_msg = f"Failed to add Security Association Database entry " \
            f"on host {node[u'host']}"
        args = dict(
            is_add=True,
            entry=dict(
                sad_id=int(sad_id),
                spi=int(spi),
                crypto_algorithm=crypto_alg.alg_int_repr,
                crypto_key=ckey,
                integrity_algorithm=integ_alg.alg_int_repr if integ_alg else 0,
                integrity_key=ikey,
                flags=flags,
                tunnel_src=str(src_addr),
                tunnel_dst=str(dst_addr),
                protocol=int(IPsecProto.IPSEC_API_PROTO_ESP),
                udp_src_port=4500,  # default value in api
                udp_dst_port=4500  # default value in api
            )
        )
        def gen_f():
            for i in range(n_entries):
                args[u"entry"][u"sad_id"] = int(sad_id) + i
                args[u"entry"][u"spi"] = int(spi) + i
                args[u"entry"][u"tunnel_src"] = str(src_addr + i * addr_incr) \
                    if tunnel_src and tunnel_dst else src_addr
                args[u"entry"][u"tunnel_dst"] = str(dst_addr + i * addr_incr) \
                    if tunnel_src and tunnel_dst else dst_addr
                yield args
        PapiSocketExecutor.exec_fast(
            node=node, command_name=cmd, gen_f=gen_f, err_msg=err_msg,
            how_many=n_entries, need_replies=False
        )

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
        tunnel_src = ip_address(tunnel_src)
        tunnel_dst = ip_address(tunnel_dst)
        traffic_addr = ip_address(traffic_addr)
        addr_incr = 1 << (128 - raddr_range) if tunnel_src.version == 6 \
            else 1 << (32 - raddr_range)

        err_msg = f"Failed to configure IP addresses and IP routes " \
            f"on interface {interface} on host {node[u'host']}"
        cmd = u"sw_interface_add_del_address"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=True,
            del_all=False,
            prefix=None
        )
        def gen_address():
            for i in range(n_tunnels):
                args[u"prefix"] = IPUtil.create_prefix_object(
                    tunnel_src + i * addr_incr, raddr_range
                )
                yield args
        PapiSocketExecutor.exec_fast(
            node=node, command_name=cmd, gen_f=gen_address, err_msg=err_msg,
            how_many=n_tunnels, need_replies=False
        )
        cmd = u"ip_route_add_del"
        args = dict(
            is_add=1,
            is_multipath=0,
            route=None
        )
        prefix_len = 128 if traffic_addr.version == 6 else 32
        def gen_route():
            for i in range(n_tunnels):
                args[u"route"] = IPUtil.compose_vpp_route_structure(
                    node, traffic_addr + i, prefix_len=prefix_len,
                    interface=interface, gateway=tunnel_dst + i * addr_incr
                )
                yield args
        PapiSocketExecutor.exec_fast(
            node=node, command_name=cmd, gen_f=gen_route, err_msg=err_msg,
            how_many=n_tunnels, need_replies=False
        )

    @staticmethod
    def vpp_ipsec_add_spd(node, spd_id):
        """Create Security Policy Database on the VPP node.

        :param node: VPP node to add SPD on.
        :param spd_id: SPD ID.
        :type node: dict
        :type spd_id: int
        """
        cmd = u"ipsec_spd_add_del"
        err_msg = f"Failed to add Security Policy Database " \
            f"on host {node[u'host']}"
        args = dict(
            is_add=True,
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
        cmd = u"ipsec_interface_add_del_spd"
        err_msg = f"Failed to add interface {interface} to Security Policy " \
            f"Database {spd_id} on host {node[u'host']}"
        args = dict(
            is_add=True,
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
            laddr_range = u"::/0" if is_ipv6 else u"0.0.0.0/0"

        if raddr_range is None:
            raddr_range = u"::/0" if is_ipv6 else u"0.0.0.0/0"

        cmd = u"ipsec_spd_entry_add_del"
        err_msg = f"Failed to add entry to Security Policy Database {spd_id} " \
            f"on host {node[u'host']}"

        spd_entry = dict(
            spd_id=int(spd_id),
            priority=int(priority),
            is_outbound=not inbound,
            sa_id=int(sa_id) if sa_id else 0,
            policy=action.policy_int_repr,
            protocol=int(proto) if proto else 0,
            remote_address_start=IPAddress.create_ip_address_object(
                ip_network(raddr_range, strict=False).network_address
            ),
            remote_address_stop=IPAddress.create_ip_address_object(
                ip_network(raddr_range, strict=False).broadcast_address
            ),
            local_address_start=IPAddress.create_ip_address_object(
                ip_network(laddr_range, strict=False).network_address
            ),
            local_address_stop=IPAddress.create_ip_address_object(
                ip_network(laddr_range, strict=False).broadcast_address
            ),
            remote_port_start=int(rport_range.split(u"-")[0]) if rport_range
            else 0,
            remote_port_stop=int(rport_range.split(u"-")[1]) if rport_range
            else 65535,
            local_port_start=int(lport_range.split(u"-")[0]) if lport_range
            else 0,
            local_port_stop=int(lport_range.split(u"-")[1]) if rport_range
            else 65535
        )
        args = dict(
            is_add=True,
            entry=spd_entry
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_spd_add_entries(
            node, n_entries, spd_id, priority, inbound, sa_id, raddr_ip,
            raddr_range=0):
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
        :param raddr_range: Required IP addres range.
        :type node: dict
        :type n_entries: int
        :type spd_id: int
        :type priority: int
        :type inbound: bool
        :type sa_id: int
        :type raddr_ip: str
        :type raddr_range: int
        """
        raddr_ip = ip_address(raddr_ip)
        laddr_range = u"::/0" if raddr_ip.version == 6 else u"0.0.0.0/0"

        err_msg = f"Failed to add entry to Security Policy Database " \
            f"'{spd_id} on host {node[u'host']}"
        cmd = u"ipsec_spd_entry_add_del"

        args = dict(
            is_add=True,
            entry=dict(
                spd_id=int(spd_id),
                priority=int(priority),
                is_outbound=not inbound,
                    sa_id=int(sa_id) if sa_id else 0,
                policy=getattr(PolicyAction.PROTECT, u"policy_int_repr"),
                protocol=0,
                remote_address_start=IPAddress.create_ip_address_object(
                    raddr_ip
                ),
                remote_address_stop=IPAddress.create_ip_address_object(
                    raddr_ip
                ),
                local_address_start=IPAddress.create_ip_address_object(
                    ip_network(laddr_range, strict=False).network_address
                ),
                local_address_stop=IPAddress.create_ip_address_object(
                    ip_network(laddr_range, strict=False).broadcast_address
                ),
                remote_port_start=0,
                remote_port_stop=65535,
                local_port_start=0,
                local_port_stop=65535
            )
        )
        def gen_f():
            for i in range(n_entries):
                args[u"entry"][u"remote_address_start"][u"un"] = \
                    IPAddress.union_addr(raddr_ip + (raddr_range + 1) * i)
                args[u"entry"][u"remote_address_stop"][u"un"] = \
                    IPAddress.union_addr(
                        raddr_ip + (raddr_range + 1) * (i + 1) - 1
                    )
                yield args
        PapiSocketExecutor.exec_fast(
            node=node, command_name=cmd, gen_f=gen_f, err_msg=err_msg,
            how_many=n_entries, need_replies=False
        )

    @staticmethod
    def _ipsec_create_loopback_dut1(nodes, tun_ips, if1_key, if2_key):
        """Create loopback interface and set IP address on VPP node 1 interface.
        using PAPI.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param tun_ips: Dictionary with VPP node 1 ipsec tunnel interface
            IPv4/IPv6 address (ip1) and VPP node 2 ipsec tunnel interface
            IPv4/IPv6 address (ip2).
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 / TG node (in case of 2-node topology)
            interface key from topology file.
        :type nodes: dict
        :type tun_ips: dict
        :type if1_key: str
        :type if2_key: str
        """
        node = nodes[u"DUT1"]
        with PapiSocketExecutor(node) as papi_exec:
            # Create loopback interface on DUT1, set it to up state
            cmd = u"create_loopback"
            args = dict(
                mac_address=0
            )
            err_msg = f"Failed to create loopback interface " \
                f"on host {node[u'host']}"
            loop_sw_if_idx = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)
            cmd = u"sw_interface_set_flags"
            args = dict(
                sw_if_index=loop_sw_if_idx,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
            )
            err_msg = f"Failed to set loopback interface state up " \
                f"on host {node[u'host']}"
            papi_exec.add(cmd, **args).get_reply(err_msg)
            # Set IP address on VPP node 1 interface
            cmd = u"sw_interface_add_del_address"
            args = dict(
                sw_if_index=InterfaceUtil.get_interface_index(
                    node, if1_key
                ),
                is_add=True,
                del_all=False,
                prefix=IPUtil.create_prefix_object(
                    tun_ips[u"ip2"] - 1, 96 if tun_ips[u"ip2"].version == 6
                    else 24
                )
            )
            err_msg = f"Failed to set IP address on interface {if1_key} " \
                f"on host {node[u'host']}"
            papi_exec.add(cmd, **args).get_reply(err_msg)
            cmd = u"ip_neighbor_add_del"
            args = dict(
                is_add=1,
                neighbor=dict(
                    sw_if_index=Topology.get_interface_sw_index(
                        node, if1_key
                    ),
                    flags=1,
                    mac_address=str(
                        Topology.get_interface_mac(nodes[u"DUT2"], if2_key)
                        if u"DUT2" in nodes.keys()
                        else Topology.get_interface_mac(
                            nodes[u"TG"], if2_key
                        )
                    ),
                    ip_address=tun_ips[u"ip2"].compressed
                )
            )
            err_msg = f"Failed to add IP neighbor on interface {if1_key}"
            papi_exec.add(cmd, **args).get_reply(err_msg)

            return loop_sw_if_idx

    # TODO: Convert the following into a dataclass when Python 3.7+ is used.
    #
    # A dict is called CreTunIntParam if it contains the following fields:
    #
    # :param nodes: VPP nodes to create tunnel interfaces.
    # :param tun_ips: Dictionary with VPP node 1 ipsec tunnel interface
    #     IPv4/IPv6 address (ip1) and VPP node 2 ipsec tunnel interface
    #     IPv4/IPv6 address (ip2).
    # :param if1_key: VPP node 1 interface key from topology file.
    # :param if2_key: VPP node 2 / TG node (in case of 2-node topology)
    #     interface key from topology file.
    # :param crypto_alg: The encryption algorithm name.
    # :param integ_alg: The integrity algorithm name.
    # :param raddr_ip1: Policy selector remote IPv4/IPv6 start address
    #     for the first tunnel in direction node1->node2.
    # :param raddr_ip2: Policy selector remote IPv4/IPv6 start address
    #     for the first tunnel in direction node2->node1.
    # :param addr_incr: IP / IPv6 address incremental step.
    # :param spi_d: Dictionary with SPIs for VPP node 1 and VPP node 2.
    # :type nodes: dict
    # :type tun_ips: dict
    # :type if1_key: str
    # :type if2_key: str
    # :type crypto_alg: CryptoAlg
    # :type integ_alg: IntegAlg
    # :type raddr_ip1: IPv4Address or IPv6Address
    # :type raddr_ip2: IPv4Address or IPv6Address
    # :type addr_incr: int
    # :type spi_d: dict

    @staticmethod
    def _ipsec_create_tunnel_interfaces_dut1(
            param, n_tunnels, existing_tunnels):
        """Create multiple IPsec tunnel interfaces on DUT1 node.
        :param param: Instance carrying all other required arguments.
        :param n_tunnels: Number of tunnel interfaces
            to be there at the end.
        :param existing_tunnels: Number of tunnel interfaces
            before creation. Useful mainly for reconf tests. Default 0.
        :type arg: CreTunIntParam
        :type n_tunnels: int
        :type existing_tunnels: int
        :returns: List of encryption keys and list of integrity keys.
        :rtype: 2-tuple of list of bytes
        """
        node = param[u"nodes"][u"DUT1"]
        if not existing_tunnels:
            loop_sw_if_idx = IPsecUtil._ipsec_create_loopback_dut1(
                param[u"nodes"], param[u"tun_ips"], param[u"if1_key"],
                param[u"if2_key"]
            )
        else:
            loop_sw_if_idx = InterfaceUtil.vpp_get_interface_sw_index(
                node, u"loop0"
            )
        with PapiSocketExecutor(node) as papi_exec:
            # Configure IP addresses on loop0 interface
            err_msg = u"Failed to add address to loopback."
            cmd = u"sw_interface_add_del_address"
            args = dict(
                sw_if_index=loop_sw_if_idx,
                is_add=True,
                del_all=False,
                prefix=None
            )
            prefix_len = 128 if param[u"tun_ips"][u"ip1"].version == 6 else 32
            def gen_address():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"prefix"] = IPUtil.create_prefix_object(
                        param[u"tun_ips"][u"ip1"] + i * param[u"addr_incr"],
                        prefix_len
                    )
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_address, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Configure IPIP tunnel interfaces
            ipip_tunnels = [None] * existing_tunnels
            err_msg = f"Failed to add IPIP tunnel interfaces on host" \
                f" {node[u'host']}"
            cmd = u"ipip_add_tunnel"
            args = dict(
                tunnel=dict(
                    instance=Constants.BITWISE_NON_ZERO,
                    src=None,
                    dst=IPAddress.create_ip_address_object(
                        param[u"tun_ips"][u"ip2"]
                    ),
                    table_id=0,
                    flags=int(
                        TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                    ),
                    mode=int(TunnelMode.TUNNEL_API_MODE_P2P),
                    dscp=int(IpDscp.IP_API_DSCP_CS0)
                )
            )
            def gen_tunnel():
                for i in range(existing_tunnels, n_tunnels):
                    address = IPAddress.create_ip_address_object(
                        param[u"tun_ips"][u"ip1"] + i * param[u"addr_incr"]
                    )
                    args[u"tunnel"][u"src"] = address
                    yield args
            replies = papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_tunnel, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=True
            )
            ipip_tunnels.extend([reply[u"sw_if_index"] for reply in replies])
            # Configure IPSec SAD entries
            ckeys = [bytes()] * existing_tunnels
            ikeys = [bytes()] * existing_tunnels
            err_msg = f"Failed to add IPsec SAD Tx entries on host" \
                f" {node[u'host']}"
            cmd = u"ipsec_sad_entry_add_del_v2"
            sad_entry = dict(
                sad_id=None,
                spi=None,
                protocol=int(IPsecProto.IPSEC_API_PROTO_ESP),
                crypto_algorithm=param[u"crypto_alg"].alg_int_repr,
                crypto_key=dict(
                    length=0,
                    data=None
                ),
                integrity_algorithm=(
                    param[u"integ_alg"].alg_int_repr
                    if param[u"integ_alg"]
                    else 0
                ),
                integrity_key=dict(
                    length=0,
                    data=None
                ),
                flags=None,
                tunnel_src=0,
                tunnel_dst=0,
                tunnel_flags=int(
                    TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                ),
                dscp=int(IpDscp.IP_API_DSCP_CS0),
                table_id=0,
                salt=0,
                udp_src_port=IPSEC_UDP_PORT_NONE,
                udp_dst_port=IPSEC_UDP_PORT_NONE
            )
            args = dict(
                is_add=True,
                entry=sad_entry
            )
            args[u"entry"][u"flags"] = int(
                IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE
            )
            def gen_sad_tx():
                for i in range(existing_tunnels, n_tunnels):
                    ckeys.append(IPsecUtil.gen_key(
                        IPsecUtil.get_crypto_alg_key_len(param[u"crypto_alg"])
                    ))
                    if param[u"integ_alg"]:
                        ikeys.append(IPsecUtil.gen_key(
                            IPsecUtil.get_integ_alg_key_len(param[u"integ_alg"])
                        ))
                    # SAD entry for outband / tx path
                    args[u"entry"][u"sad_id"] = i
                    args[u"entry"][u"spi"] = param[u"spi_d"][u"spi_1"] + i
                    args[u"entry"][u"crypto_key"][u"length"] = len(ckeys[i])
                    args[u"entry"][u"crypto_key"][u"data"] = ckeys[i]
                    if param[u"integ_alg"]:
                        args[u"entry"][u"integrity_key"][u"length"] = len(
                            ikeys[i]
                        )
                        args[u"entry"][u"integrity_key"][u"data"] = ikeys[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_sad_tx, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            err_msg = f"Failed to add IPsec SAD Rx entries on host" \
                f" {node[u'host']}"
            args[u"entry"][u"flags"] = int(
                IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE |
                IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_INBOUND
            )
            def gen_sad_rx():
                for i in range(existing_tunnels, n_tunnels):
                    # SAD entry for inband / rx path
                    args[u"entry"][u"sad_id"] = 100000 + i
                    args[u"entry"][u"spi"] = param[u"spi_d"][u"spi_2"] + i
                    args[u"entry"][u"crypto_key"][u"length"] = len(ckeys[i])
                    args[u"entry"][u"crypto_key"][u"data"] = ckeys[i]
                    if param[u"integ_alg"]:
                        args[u"entry"][u"integrity_key"][u"length"] = len(
                            ikeys[i]
                        )
                        args[u"entry"][u"integrity_key"][u"data"] = ikeys[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_sad_rx, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Add protection for tunnels with IPSEC
            err_msg = f"Failed to add protection for tunnels with IPSEC " \
                f"on host {node[u'host']}"
            cmd = u"ipsec_tunnel_protect_update"
            args = dict(
                tunnel=dict(
                    sw_if_index=None,
                    nh=dict(
                        address=0,
                        via_label=MPLS_LABEL_INVALID,
                        obj_id=Constants.BITWISE_NON_ZERO
                    ),
                    sa_out=None,
                    n_sa_in=1,
                    sa_in=None
                )
            )
            def gen_prot():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"tunnel"][u"sw_if_index"] = ipip_tunnels[i]
                    args[u"tunnel"][u"sa_out"] = i
                    args[u"tunnel"][u"sa_in"] = [100000 + i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_prot, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )

            # Configure unnumbered interfaces
            err_msg = f"Failed to set unnumbered for tunnels with IPSEC " \
                f"on host {node[u'host']}"
            cmd = u"sw_interface_set_unnumbered"
            args = dict(
                is_add=True,
                sw_if_index=InterfaceUtil.get_interface_index(
                    node, param[u"if1_key"]
                ),
                unnumbered_sw_if_index=0
            )
            def gen_unnum():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"unnumbered_sw_if_index"] = ipip_tunnels[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_unnum, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Set interfaces up
            err_msg = f"Failed to set interface up for tunnels with IPSEC " \
                f"on host {node[u'host']}"
            cmd = u"sw_interface_set_flags"
            args = dict(
                sw_if_index=0,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
            )
            def gen_up():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"sw_if_index"] = ipip_tunnels[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_up, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Configure IP routes
            err_msg = f"Failed to add IP routes on host " \
                f"{node[u'host']}"
            cmd = u"ip_route_add_del"
            args = dict(
                is_add=1,
                is_multipath=0,
                route=None
            )
            prefix_len = 128 if param[u"raddr_ip2"].version == 6 else 32
            def gen_route():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"route"] = IPUtil.compose_vpp_route_structure(
                        node, (param[u"raddr_ip2"] + i).compressed,
                        prefix_len=prefix_len, interface=ipip_tunnels[i]
                    )
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_route, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )

        return ckeys, ikeys

    @staticmethod
    def _ipsec_create_tunnel_interfaces_dut2(
            param, n_tunnels, existing_tunnels, ckeys, ikeys):
        """Create multiple IPsec tunnel interfaces on DUT2 node using PAPI.

        :param param: Instance carrying all other required arguments.
        :param n_tunnels: Number of tunnel interfaces
            to be there at the end.
        :param existing_tunnels: Number of tunnel interfaces
            before creation. Useful mainly for reconf tests. Default 0.
        :param ckeys: List of encryption keys.
        :param ikeys: List of integrity keys.
        :type arg: CreTunIntParam
        :type n_tunnels: int
        :type existing_tunnels: int
        :type ckeys: list
        :type ikeys: list
        """
        node = param[u"nodes"][u"DUT2"]
        with PapiSocketExecutor(node) as papi_exec:
            if not existing_tunnels:
                # Set IP address on VPP node 2 interface
                cmd = u"sw_interface_add_del_address"
                args = dict(
                    sw_if_index=InterfaceUtil.get_interface_index(
                        node, param[u"if2_key"]
                    ),
                    is_add=True,
                    del_all=False,
                    prefix=IPUtil.create_prefix_object(
                        param[u"tun_ips"][u"ip2"],
                        96 if param[u"tun_ips"][u"ip2"].version == 6 else 24
                    )
                )
                err_msg = f"Failed to set IP address on interface " \
                    f"{param[u'if2_key']} on host {node[u'host']}"
                papi_exec.add(cmd, **args).get_reply(err_msg)
            # Configure IPIP tunnel interfaces
            ipip_tunnels = [None] * existing_tunnels
            err_msg = f"Failed to add IPIP tunnel interfaces on host" \
                f" {node[u'host']}"
            cmd = u"ipip_add_tunnel"
            args = dict(
                tunnel=dict(
                    instance=Constants.BITWISE_NON_ZERO,
                    src=IPAddress.create_ip_address_object(
                        param[u"tun_ips"][u"ip2"]
                    ),
                    dst=None,
                    table_id=0,
                    flags=int(
                        TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                    ),
                    mode=int(TunnelMode.TUNNEL_API_MODE_P2P),
                    dscp=int(IpDscp.IP_API_DSCP_CS0)
                )
            )
            def gen_tunnel():
                for i in range(existing_tunnels, n_tunnels):
                    # TODO: Import IPAddress.create_ip_address_object
                    # so local variable is not needed to avoid too long line?
                    address = IPAddress.create_ip_address_object(
                        param[u"tun_ips"][u"ip1"] + i * param[u"addr_incr"]
                    )
                    args[u"tunnel"][u"dst"] = address
                    yield args
            replies = papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_tunnel, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=True
            )
            ipip_tunnels.extend([reply[u"sw_if_index"] for reply in replies])
            # Configure IPSec SAD entries
            err_msg = f"Failed to add IPsec SAD Tx entries on host" \
                f" {node[u'host']}"
            cmd = u"ipsec_sad_entry_add_del_v2"
            sad_entry = dict(
                sad_id=None,
                spi=None,
                protocol=int(IPsecProto.IPSEC_API_PROTO_ESP),
                crypto_algorithm=param[u"crypto_alg"].alg_int_repr,
                crypto_key=dict(
                    length=0,
                    data=None
                ),
                integrity_algorithm=(
                    param[u"integ_alg"].alg_int_repr
                    if param[u"integ_alg"]
                    else 0
                ),
                integrity_key=dict(
                    length=0,
                    data=None
                ),
                flags=None,
                tunnel_src=0,
                tunnel_dst=0,
                tunnel_flags=int(
                    TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                ),
                dscp=int(IpDscp.IP_API_DSCP_CS0),
                table_id=0,
                salt=0,
                udp_src_port=IPSEC_UDP_PORT_NONE,
                udp_dst_port=IPSEC_UDP_PORT_NONE
            )
            args = dict(
                is_add=True,
                entry=sad_entry
            )
            args[u"entry"][u"flags"] = int(
                IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE
            )
            def gen_sad_tx():
                for i in range(existing_tunnels, n_tunnels):
                    ckeys.append(IPsecUtil.gen_key(
                        IPsecUtil.get_crypto_alg_key_len(param[u"crypto_alg"])
                    ))
                    if param[u"integ_alg"]:
                        ikeys.append(IPsecUtil.gen_key(
                            IPsecUtil.get_integ_alg_key_len(param[u"integ_alg"])
                        ))
                    # SAD entry for outband / tx path
                    args[u"entry"][u"sad_id"] = 100000 + i
                    args[u"entry"][u"spi"] = param[u"spi_d"][u"spi_2"] + i
                    args[u"entry"][u"crypto_key"][u"length"] = len(ckeys[i])
                    args[u"entry"][u"crypto_key"][u"data"] = ckeys[i]
                    if param[u"integ_alg"]:
                        args[u"entry"][u"integrity_key"][u"length"] = len(
                            ikeys[i]
                        )
                        args[u"entry"][u"integrity_key"][u"data"] = ikeys[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_sad_tx, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            err_msg = f"Failed to add IPsec SAD Rx entries on host" \
                f" {node[u'host']}"
            args[u"entry"][u"flags"] = int(
                IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE |
                IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_INBOUND
            )
            def gen_sad_rx():
                for i in range(existing_tunnels, n_tunnels):
                    # SAD entry for inband / rx path
                    args[u"entry"][u"sad_id"] = i
                    args[u"entry"][u"spi"] = param[u"spi_d"][u"spi_1"] + i
                    args[u"entry"][u"crypto_key"][u"length"] = len(ckeys[i])
                    args[u"entry"][u"crypto_key"][u"data"] = ckeys[i]
                    if param[u"integ_alg"]:
                        args[u"entry"][u"integrity_key"][u"length"] = len(
                            ikeys[i]
                        )
                        args[u"entry"][u"integrity_key"][u"data"] = ikeys[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_sad_rx, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Add protection for tunnels with IPSEC
            err_msg = f"Failed to add protection for tunnels with IPSEC " \
                f"on host {node[u'host']}"
            cmd = u"ipsec_tunnel_protect_update"
            args = dict(
                tunnel=dict(
                    sw_if_index=None,
                    nh=dict(
                        address=0,
                        via_label=MPLS_LABEL_INVALID,
                        obj_id=Constants.BITWISE_NON_ZERO
                    ),
                    sa_out=None,
                    n_sa_in=1,
                    sa_in=None
                )
            )
            def gen_prot():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"tunnel"][u"sw_if_index"] = ipip_tunnels[i]
                    args[u"tunnel"][u"sa_out"] = 100000 + i
                    args[u"tunnel"][u"sa_in"] = [i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_prot, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )

            if not existing_tunnels:
                # Configure IP route
                err_msg = f"Failed to configure base route with IPSEC " \
                    f"on host {node[u'host']}"
                cmd = u"ip_route_add_del"
                args = dict(
                    is_add=1,
                    is_multipath=0,
                    route=IPUtil.compose_vpp_route_structure(
                        node, param[u"tun_ips"][u"ip1"].compressed,
                        prefix_len=(
                            32
                            if param[u"tun_ips"][u"ip1"].version == 6
                            else 8
                        ),
                        interface=param[u"if2_key"],
                        gateway=(param[u"tun_ips"][u"ip2"] - 1).compressed
                    )
                )
                papi_exec.add(cmd, **args).get_reply(err_msg=err_msg)
            # Configure unnumbered interfaces
            err_msg = f"Failed to set unnumbered for tunnels with IPSEC " \
                f"on host {node[u'host']}"
            cmd = u"sw_interface_set_unnumbered"
            args = dict(
                is_add=True,
                sw_if_index=InterfaceUtil.get_interface_index(
                    node, param[u"if2_key"]
                ),
                unnumbered_sw_if_index=0
            )
            def gen_unnum():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"unnumbered_sw_if_index"] = ipip_tunnels[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_unnum, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Set interfaces up
            err_msg = f"Failed to set interfaces up for tunnels with IPSEC " \
                f"on host {node[u'host']}"
            cmd = u"sw_interface_set_flags"
            args = dict(
                sw_if_index=0,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
            )
            def gen_up():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"sw_if_index"] = ipip_tunnels[i]
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_up, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )
            # Configure IP routes
            err_msg = f"Failed to add IP routes on host {node[u'host']}"
            cmd = u"ip_route_add_del"
            args = dict(
                is_add=1,
                is_multipath=0,
                route=None
            )
            prefix_len = 128 if param[u"raddr_ip1"].version == 6 else 32
            def gen_route():
                for i in range(existing_tunnels, n_tunnels):
                    args[u"route"] = IPUtil.compose_vpp_route_structure(
                        node, (param[u"raddr_ip1"] + i).compressed,
                        prefix_len=prefix_len, interface=ipip_tunnels[i]
                    )
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_route, err_msg=err_msg,
                how_many=n_tunnels - existing_tunnels, need_replies=False
            )

    @staticmethod
    def vpp_ipsec_create_tunnel_interfaces(
            nodes, tun_if1_ip_addr, tun_if2_ip_addr, if1_key, if2_key,
            n_tunnels, crypto_alg, integ_alg, raddr_ip1, raddr_ip2, raddr_range,
            existing_tunnels=0):
        """Create multiple IPsec tunnel interfaces between two VPP nodes.

        For 2-node setups, return keys and SPIs,
        so traffic can be handled on TG side.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param tun_if1_ip_addr: VPP node 1 ipsec tunnel interface IPv4/IPv6
            address.
        :param tun_if2_ip_addr: VPP node 2 ipsec tunnel interface IPv4/IPv6
            address.
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 / TG node (in case of 2-node topology)
            interface key from topology file.
        :param n_tunnels: Number of tunnel interfaces to be there at the end.
        :param crypto_alg: The encryption algorithm name.
        :param integ_alg: The integrity algorithm name.
        :param raddr_ip1: Policy selector remote IPv4/IPv6 start address for the
            first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4/IPv6 start address for the
            first tunnel in direction node2->node1.
        :param raddr_range: Mask specifying range of Policy selector Remote
            IPv4/IPv6 addresses. Valid values are from 1 to 32 in case of IPv4
            and to 128 in case of IPv6.
        :param existing_tunnels: Number of tunnel interfaces before creation.
            Useful mainly for reconf tests. Default 0.
        :type nodes: dict
        :type tun_if1_ip_addr: str
        :type tun_if2_ip_addr: str
        :type if1_key: str
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg
        :type integ_alg: IntegAlg
        :type raddr_ip1: string
        :type raddr_ip2: string
        :type raddr_range: int
        :type existing_tunnels: int
        :returns: First ckey, first ikey, spi_1 and spi_2; Nones if 3-node.
        :rtype: bytes, bytes, int, int
        """
        n_tunnels = int(n_tunnels)
        existing_tunnels = int(existing_tunnels)
        spi_d = dict(
            spi_1=100000,
            spi_2=200000
        )
        tun_ips = dict(
            ip1=ip_address(tun_if1_ip_addr),
            ip2=ip_address(tun_if2_ip_addr)
        )
        raddr_ip1 = ip_address(raddr_ip1)
        raddr_ip2 = ip_address(raddr_ip2)
        addr_incr = 1 << (128 - raddr_range) if tun_ips[u"ip1"].version == 6 \
            else 1 << (32 - raddr_range)

        param = dict(
            nodes=nodes, tun_ips=tun_ips, if1_key=if1_key, if2_key=if2_key,
            crypto_alg=crypto_alg, integ_alg=integ_alg, raddr_ip1=raddr_ip1,
            raddr_ip2=raddr_ip2, addr_incr=addr_incr, spi_d=spi_d
        )
        ckeys, ikeys = IPsecUtil._ipsec_create_tunnel_interfaces_dut1(
            param, n_tunnels, existing_tunnels
        )
        if u"DUT2" not in nodes.keys():
            return ckeys[0], ikeys[0], spi_d[u"spi_1"], spi_d[u"spi_2"]

        IPsecUtil._ipsec_create_tunnel_interfaces_dut2(
            param, n_tunnels, existing_tunnels, ckeys, ikeys
        )

        return None, None, None, None

    @staticmethod
    def _create_ipsec_script_files(dut, instances):
        """Create script files for configuring IPsec in containers

        :param dut: DUT node on which to create the script files
        :param instances: number of containers on DUT node
        :type dut: string
        :type instances: int
        """
        scripts = []
        for cnf in range(0, instances):
            script_filename = (
                f"/tmp/ipsec_create_tunnel_cnf_{dut}_{cnf + 1}.config"
            )
            scripts.append(open(script_filename, 'w'))
        return scripts

    @staticmethod
    def _close_and_copy_ipsec_script_files(
            dut, nodes, instances, scripts):
        """Close created scripts and copy them to containers

        :param dut: DUT node on which to create the script files
        :param nodes: VPP nodes
        :param instances: number of containers on DUT node
        :param scripts: dictionary holding the script files
        :type dut: string
        :type nodes: dict
        :type instances: int
        :type scripts: dict
        """
        for cnf in range(0, instances):
            scripts[cnf].close()
            script_filename = (
                f"/tmp/ipsec_create_tunnel_cnf_{dut}_{cnf + 1}.config"
            )
            scp_node(nodes[dut], script_filename, script_filename)

    @staticmethod
    def vpp_ipsec_create_tunnel_interfaces_in_containers(
            nodes, if1_ip_addr, if2_ip_addr, n_tunnels, crypto_alg, integ_alg,
            raddr_ip1, raddr_ip2, raddr_range, n_instances):
        """Create multiple IPsec tunnel interfaces between two VPP nodes.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param if1_ip_addr: VPP node 1 interface IP4 address.
        :param if2_ip_addr: VPP node 2 interface IP4 address.
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

        dut1_scripts = IPsecUtil._create_ipsec_script_files(
            u"DUT1", n_instances
        )
        dut2_scripts = IPsecUtil._create_ipsec_script_files(
            u"DUT2", n_instances
        )

        for cnf in range(0, n_instances):
            dut1_scripts[cnf].write(
                u"create loopback interface\n"
                u"set interface state loop0 up\n\n"
            )
            dut2_scripts[cnf].write(
                f"ip route add {if1_ip_addr}/8 via "
                f"{ip_address(if2_ip_addr) + cnf + 100} memif1/{cnf + 1}\n\n"
            )

        for tnl in range(0, n_tunnels):
            cnf = tnl % n_instances
            ckey = IPsecUtil.gen_key(
                IPsecUtil.get_crypto_alg_key_len(crypto_alg)
            ).hex()
            integ = u""
            if integ_alg:
                ikey = IPsecUtil.gen_key(
                    IPsecUtil.get_integ_alg_key_len(integ_alg), 1
                ).hex()
                integ = (
                    f"integ-alg {integ_alg.alg_name} "
                    f"local-integ-key {ikey} "
                    f"remote-integ-key {ikey} "
                )
            # Configure tunnel end point(s) on left side
            dut1_scripts[cnf].write(
                u"set interface ip address loop0 "
                f"{ip_address(if1_ip_addr) + tnl * addr_incr}/32\n"
                f"create ipsec tunnel "
                f"local-ip {ip_address(if1_ip_addr) + tnl * addr_incr} "
                f"local-spi {spi_1 + tnl} "
                f"remote-ip {ip_address(if2_ip_addr) + cnf} "
                f"remote-spi {spi_2 + tnl} "
                f"crypto-alg {crypto_alg.alg_name} "
                f"local-crypto-key {ckey} "
                f"remote-crypto-key {ckey} "
                f"instance {tnl // n_instances} "
                f"salt 0x0 "
                f"{integ} \n"
                f"set interface unnumbered ipip{tnl // n_instances} use loop0\n"
                f"set interface state ipip{tnl // n_instances} up\n"
                f"ip route add {ip_address(raddr_ip2)+tnl}/32 "
                f"via ipip{tnl // n_instances}\n\n"
            )
            # Configure tunnel end point(s) on right side
            dut2_scripts[cnf].write(
                f"set ip neighbor memif1/{cnf + 1} "
                f"{ip_address(if1_ip_addr) + tnl * addr_incr} "
                f"02:02:00:00:{17:02X}:{cnf:02X} static\n"
                f"create ipsec tunnel local-ip {ip_address(if2_ip_addr) + cnf} "
                f"local-spi {spi_2 + tnl} "
                f"remote-ip {ip_address(if1_ip_addr) + tnl * addr_incr} "
                f"remote-spi {spi_1 + tnl} "
                f"crypto-alg {crypto_alg.alg_name} "
                f"local-crypto-key {ckey} "
                f"remote-crypto-key {ckey} "
                f"instance {tnl // n_instances} "
                f"salt 0x0 "
                f"{integ}\n"
                f"set interface unnumbered ipip{tnl // n_instances} "
                f"use memif1/{cnf + 1}\n"
                f"set interface state ipip{tnl // n_instances} up\n"
                f"ip route add {ip_address(raddr_ip1) + tnl}/32 "
                f"via ipip{tnl // n_instances}\n\n"
            )

        IPsecUtil._close_and_copy_ipsec_script_files(
            u"DUT1", nodes, n_instances, dut1_scripts)
        IPsecUtil._close_and_copy_ipsec_script_files(
            u"DUT2", nodes, n_instances, dut2_scripts)

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

        crypto_key = IPsecUtil.gen_key(
            IPsecUtil.get_crypto_alg_key_len(crypto_alg)
        )
        integ_key = IPsecUtil.gen_key(
            IPsecUtil.get_integ_alg_key_len(integ_alg), 1
        ) if integ_alg else b""

        IPsecUtil.vpp_ipsec_set_ip_route(
            nodes[u"DUT1"], n_tunnels, tunnel_ip1, raddr_ip2, tunnel_ip2,
            interface1, raddr_range)
        IPsecUtil.vpp_ipsec_set_ip_route(
            nodes[u"DUT2"], n_tunnels, tunnel_ip2, raddr_ip1, tunnel_ip1,
            interface2, raddr_range)

        IPsecUtil.vpp_ipsec_add_spd(nodes[u"DUT1"], spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(nodes[u"DUT1"], spd_id, interface1)
        IPsecUtil.vpp_ipsec_policy_add(
            nodes[u"DUT1"], spd_id, p_hi, PolicyAction.BYPASS, inbound=False,
            proto=50, laddr_range=u"100.0.0.0/8", raddr_range=u"100.0.0.0/8"
        )
        IPsecUtil.vpp_ipsec_policy_add(
            nodes[u"DUT1"], spd_id, p_hi, PolicyAction.BYPASS, inbound=True,
            proto=50, laddr_range=u"100.0.0.0/8", raddr_range=u"100.0.0.0/8"
        )

        IPsecUtil.vpp_ipsec_add_spd(nodes[u"DUT2"], spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(nodes[u"DUT2"], spd_id, interface2)
        IPsecUtil.vpp_ipsec_policy_add(
            nodes[u"DUT2"], spd_id, p_hi, PolicyAction.BYPASS, inbound=False,
            proto=50, laddr_range=u"100.0.0.0/8", raddr_range=u"100.0.0.0/8"
        )
        IPsecUtil.vpp_ipsec_policy_add(
            nodes[u"DUT2"], spd_id, p_hi, PolicyAction.BYPASS, inbound=True,
            proto=50, laddr_range=u"100.0.0.0/8", raddr_range=u"100.0.0.0/8"
        )

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes[u"DUT1"], n_tunnels, sa_id_1, spi_1, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip1, tunnel_ip2
        )
        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes[u"DUT1"], n_tunnels, spd_id, p_lo, False, sa_id_1, raddr_ip2
        )

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes[u"DUT2"], n_tunnels, sa_id_1, spi_1, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip1, tunnel_ip2
        )
        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes[u"DUT2"], n_tunnels, spd_id, p_lo, True, sa_id_1, raddr_ip2
        )

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes[u"DUT2"], n_tunnels, sa_id_2, spi_2, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip2, tunnel_ip1
        )

        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes[u"DUT2"], n_tunnels, spd_id, p_lo, False, sa_id_2, raddr_ip1
        )

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes[u"DUT1"], n_tunnels, sa_id_2, spi_2, crypto_alg, crypto_key,
            integ_alg, integ_key, tunnel_ip2, tunnel_ip1
        )

        IPsecUtil.vpp_ipsec_spd_add_entries(
            nodes[u"DUT1"], n_tunnels, spd_id, p_lo, True, sa_id_2, raddr_ip1
        )

    @staticmethod
    def vpp_ipsec_show(node):
        """Run "show ipsec" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, u"show ipsec")

    @staticmethod
    def show_ipsec_security_association(node):
        """Show IPSec security association.

        :param node: DUT node.
        :type node: dict
        """
        cmds = [
            u"ipsec_sa_v2_dump"
        ]
        PapiSocketExecutor.dump_and_log(node, cmds)
