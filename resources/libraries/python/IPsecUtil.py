# Copyright (c) 2024 Cisco and/or its affiliates.
# Copyright (c) 2024 PANTHEON.tech s.r.o.
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
from io import open, TextIOWrapper
from ipaddress import ip_network, ip_address, IPv4Address, IPv6Address
from random import choice
from string import ascii_letters
from typing import Iterable, List, Optional, Sequence, Tuple, Union

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.enum_util import get_enum_instance
from resources.libraries.python.IncrementUtil import ObjIncrement
from resources.libraries.python.InterfaceUtil import (
    InterfaceUtil,
    InterfaceStatusFlags,
)
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.IPUtil import (
    IPUtil,
    IpDscp,
    MPLS_LABEL_INVALID,
    NetworkIncrement,
)
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import scp_node
from resources.libraries.python.topology import Topology, NodeType
from resources.libraries.python.VPPUtil import VPPUtil
from resources.libraries.python.FlowUtil import FlowUtil


IPSEC_UDP_PORT_DEFAULT = 4500
IPSEC_REPLAY_WINDOW_DEFAULT = 64


def gen_key(length: int) -> bytes:
    """Generate random string as a key.

    :param length: Length of generated payload.
    :type length: int
    :returns: The generated payload.
    :rtype: bytes
    """
    return "".join(choice(ascii_letters) for _ in range(length)).encode(
        encoding="utf-8"
    )


# TODO: Introduce a metaclass that adds .find and .InputType automatically?
class IpsecSpdAction(Enum):
    """IPsec SPD actions.

    Mirroring VPP: src/vnet/ipsec/ipsec_types.api enum ipsec_spd_action.
    """

    BYPASS = NONE = ("bypass", 0)
    DISCARD = ("discard", 1)
    RESOLVE = ("resolve", 2)
    PROTECT = ("protect", 3)

    def __init__(self, action_name: str, action_int_repr: int):
        self.action_name = action_name
        self.action_int_repr = action_int_repr

    def __str__(self) -> str:
        return self.action_name

    def __int__(self) -> int:
        return self.action_int_repr


class CryptoAlg(Enum):
    """Encryption algorithms.

    API names and numeric enums from ipsec_types.api (enum ipsec_crypto_alg).

    Lowercase names from ipsec_sa.h (foreach_ipsec_crypto_alg).

    Scapy names are from:
    https://github.com/secdev/scapy/blob/master/scapy/layers/ipsec.py

    Key lengths from crypto.h
    (foreach_crypto_cipher_alg and foreach_crypto_aead_alg).
    """

    NONE = ("none", 0, "none", 0)
    AES_CBC_128 = ("aes-cbc-128", 1, "AES-CBC", 16)
    AES_CBC_192 = ("aes-cbc-192", 2, "AES-CBC", 24)
    AES_CBC_256 = ("aes-cbc-256", 3, "AES-CBC", 32)
    AES_CTR_128 = ("aes-ctr-128", 4, "AES-CTR", 16)
    AES_CTR_192 = ("aes-ctr-192", 5, "AES-CTR", 24)
    AES_CTR_256 = ("aes-ctr-256", 6, "AES-CTR", 32)
    AES_GCM_128 = ("aes-gcm-128", 7, "AES-GCM", 16)
    AES_GCM_192 = ("aes-gcm-192", 8, "AES-GCM", 24)
    AES_GCM_256 = ("aes-gcm-256", 9, "AES-GCM", 32)
    DES_CBC = ("des-cbc", 10, "DES", 7)
    _3DES_CBC = ("3des-cbc", 11, "3DES", 24)
    CHACHA20_POLY1305 = ("chacha20-poly1305", 12, "CHACHA20-POLY1305", 32)
    AES_NULL_GMAC_128 = ("aes-null-gmac-128", 13, "AES-NULL-GMAC", 16)
    AES_NULL_GMAC_192 = ("aes-null-gmac-192", 14, "AES-NULL-GMAC", 24)
    AES_NULL_GMAC_256 = ("aes-null-gmac-256", 15, "AES-NULL-GMAC", 32)

    def __init__(
        self, alg_name: str, alg_int_repr: int, scapy_name: str, key_len: int
    ):
        self.alg_name = alg_name
        self.alg_int_repr = alg_int_repr
        self.scapy_name = scapy_name
        self.key_len = key_len

    # TODO: Investigate if __int__ works with PAPI. It was not enough for "if".
    def __bool__(self):
        """A shorthand to enable "if crypto_alg:" constructs."""
        return self.alg_int_repr != 0


class IntegAlg(Enum):
    """Integrity algorithms.

    API names and numeric enums from ipsec_types.api (enum ipsec_integ_alg).

    Lowercase names from ipsec_sa.h (foreach_ipsec_integ_alg).

    Scapy names are from:
    https://github.com/secdev/scapy/blob/master/scapy/layers/ipsec.py
    Among those, "AES-CMAC-96" may be a mismatch,
    but there is no sha2-related item with "96" in it.

    Key lengths seem to be given double of digest length
    from crypto.h (foreach_crypto_link_async_alg),
    but data there is not complete
    (e.g. it does not distinguish sha-256-96 from sha-256-128).
    The missing values are chosen based on last number (e.g. 192 / 4 = 48).
    """

    NONE = ("none", 0, "none", 0)
    MD5_96 = ("md5-96", 1, "HMAC-MD5-96", 24)
    SHA1_96 = ("sha1-96", 2, "HMAC-SHA1-96", 24)
    SHA_256_96 = ("sha-256-96", 3, "AES-CMAC-96", 24)
    SHA_256_128 = ("sha-256-128", 4, "SHA2-256-128", 32)
    SHA_384_192 = ("sha-384-192", 5, "SHA2-384-192", 48)
    SHA_512_256 = ("sha-512-256", 6, "SHA2-512-256", 64)

    def __init__(
        self, alg_name: str, alg_int_repr: int, scapy_name: str, key_len: int
    ):
        self.alg_name = alg_name
        self.alg_int_repr = alg_int_repr
        self.scapy_name = scapy_name
        self.key_len = key_len

    def __bool__(self):
        """A shorthand to enable "if integ_alg:" constructs."""
        return self.alg_int_repr != 0


# TODO: Base on Enum, so str values can be defined as in alg enums?
class IPsecProto(IntEnum):
    """IPsec protocol.

    Mirroring VPP: src/vnet/ipsec/ipsec_types.api enum ipsec_proto.
    """

    ESP = 50
    AH = 51
    NONE = 255

    def __str__(self) -> str:
        """Return string suitable for CLI commands.

        None is not supported.

        :returns: Lowercase name of the proto.
        :rtype: str
        :raises: ValueError if the numeric value is not recognized.
        """
        num = int(self)
        if num == 50:
            return "esp"
        if num == 51:
            return "ah"
        raise ValueError(f"String form not defined for IPsecProto {num}")


# The rest of enums do not appear outside this file, so no no change needed yet.
class IPsecSadFlags(IntEnum):
    """IPsec Security Association Database flags."""

    IPSEC_API_SAD_FLAG_NONE = NONE = 0
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

    TUNNEL_API_ENCAP_DECAP_FLAG_NONE = NONE = 0
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
    TUNNEL_API_MODE_P2P = NONE = 0
    # multi-point
    TUNNEL_API_MODE_MP = 1


# Derived types for type hints, based on capabilities of get_enum_instance.
IpsecSpdAction.InputType = Union[IpsecSpdAction, str, None]
CryptoAlg.InputType = Union[CryptoAlg, str, None]
IntegAlg.InputType = Union[IntegAlg, str, None]
IPsecProto.InputType = Union[IPsecProto, str, int, None]
# TODO: Introduce a metaclass that adds .find and .InputType automatically?


class IPsecUtil:
    """IPsec utilities."""

    # The following 4 methods are Python one-liners,
    # but they are useful when called as a Robot keyword.

    @staticmethod
    def get_crypto_alg_key_len(crypto_alg: CryptoAlg.InputType) -> int:
        """Return encryption algorithm key length.

        This is a Python one-liner, but useful when called as a Robot keyword.

        :param crypto_alg: Encryption algorithm.
        :type crypto_alg: CryptoAlg.InputType
        :returns: Key length.
        :rtype: int
        """
        return get_enum_instance(CryptoAlg, crypto_alg).key_len

    @staticmethod
    def get_crypto_alg_scapy_name(crypto_alg: CryptoAlg.InputType) -> str:
        """Return encryption algorithm scapy name.

        This is a Python one-liner, but useful when called as a Robot keyword.

        :param crypto_alg: Encryption algorithm.
        :type crypto_alg: CryptoAlg.InputType
        :returns: Algorithm scapy name.
        :rtype: str
        """
        return get_enum_instance(CryptoAlg, crypto_alg).scapy_name

    # The below to keywords differ only by enum type conversion from str.
    @staticmethod
    def get_integ_alg_key_len(integ_alg: IntegAlg.InputType) -> int:
        """Return integrity algorithm key length.

        :param integ_alg: Integrity algorithm.
        :type integ_alg: IntegAlg.InputType
        :returns: Key length.
        :rtype: int
        """
        return get_enum_instance(IntegAlg, integ_alg).key_len

    @staticmethod
    def get_integ_alg_scapy_name(integ_alg: IntegAlg.InputType) -> str:
        """Return integrity algorithm scapy name.

        :param integ_alg: Integrity algorithm.
        :type integ_alg: IntegAlg.InputType
        :returns: Algorithm scapy name.
        :rtype: str
        """
        return get_enum_instance(IntegAlg, integ_alg).scapy_name

    @staticmethod
    def vpp_ipsec_select_backend(
        node: dict, proto: IPsecProto.InputType, index: int = 1
    ) -> None:
        """Select IPsec backend.

        :param node: VPP node to select IPsec backend on.
        :param proto: IPsec protocol.
        :param index: Backend index.
        :type node: dict
        :type proto: IPsecProto.InputType
        :type index: int
        :raises RuntimeError: If failed to select IPsec backend or if no API
            reply received.
        """
        proto = get_enum_instance(IPsecProto, proto)
        cmd = "ipsec_select_backend"
        err_msg = f"Failed to select IPsec backend on host {node['host']}"
        args = dict(protocol=proto, index=index)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_set_async_mode(node: dict, async_enable: int = 1) -> None:
        """Set IPsec async mode on|off.

        Unconditionally, attempt to switch crypto dispatch into polling mode.

        :param node: VPP node to set IPsec async mode.
        :param async_enable: Async mode on or off.
        :type node: dict
        :type async_enable: int
        :raises RuntimeError: If failed to set IPsec async mode or if no API
            reply received.
        """
        with PapiSocketExecutor(node) as papi_exec:
            cmd = "ipsec_set_async_mode"
            err_msg = f"Failed to set IPsec async mode on host {node['host']}"
            args = dict(async_enable=async_enable)
            papi_exec.add(cmd, **args).get_reply(err_msg)
            cmd = "crypto_set_async_dispatch"
            err_msg = "Failed to set dispatch mode."
            args = dict(mode=0, adaptive=False)
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_crypto_sw_scheduler_set_worker(
        node: dict, workers: Iterable[int], crypto_enable: bool = False
    ) -> None:
        """Enable or disable crypto on specific vpp worker threads.

        :param node: VPP node to enable or disable crypto for worker threads.
        :param workers: List of VPP thread numbers.
        :param crypto_enable: Disable or enable crypto work.
        :type node: dict
        :type workers: Iterable[int]
        :type crypto_enable: bool
        :raises RuntimeError: If failed to enable or disable crypto for worker
            thread or if no API reply received.
        """
        for worker in workers:
            cmd = "crypto_sw_scheduler_set_worker"
            err_msg = (
                "Failed to disable/enable crypto for worker thread"
                f" on host {node['host']}"
            )
            args = dict(worker_index=worker - 1, crypto_enable=crypto_enable)
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_crypto_sw_scheduler_set_worker_on_all_duts(
        nodes: dict, crypto_enable: bool = False
    ) -> None:
        """Enable or disable crypto on specific vpp worker threads.

        :param node: VPP node to enable or disable crypto for worker threads.
        :param crypto_enable: Disable or enable crypto work.
        :type node: dict
        :type crypto_enable: bool
        :raises RuntimeError: If failed to enable or disable crypto for worker
            thread or if no API reply received.
        """
        for node_name, node in nodes.items():
            if node["type"] == NodeType.DUT:
                thread_data = VPPUtil.vpp_show_threads(node)
                worker_cnt = len(thread_data) - 1
                if not worker_cnt:
                    return
                worker_ids = list()
                workers = BuiltIn().get_variable_value(
                    f"${{{node_name}_cpu_dp}}"
                )
                for item in thread_data:
                    if str(item.cpu_id) in workers.split(","):
                        worker_ids.append(item.id)

                IPsecUtil.vpp_ipsec_crypto_sw_scheduler_set_worker(
                    node, workers=worker_ids, crypto_enable=crypto_enable
                )

    @staticmethod
    def vpp_ipsec_add_sad_entry(
        node: dict,
        sad_id: int,
        spi: int,
        crypto_alg: CryptoAlg.InputType = None,
        crypto_key: str = "",
        integ_alg: IntegAlg.InputType = None,
        integ_key: str = "",
        tunnel_src: Optional[str] = None,
        tunnel_dst: Optional[str] = None,
    ) -> None:
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
        :type crypto_alg: CryptoAlg.InputType
        :type crypto_key: str
        :type integ_alg: IntegAlg.InputType
        :type integ_key: str
        :type tunnel_src: Optional[str]
        :type tunnel_dst: Optional[str]
        """
        crypto_alg = get_enum_instance(CryptoAlg, crypto_alg)
        integ_alg = get_enum_instance(IntegAlg, integ_alg)
        if isinstance(crypto_key, str):
            crypto_key = crypto_key.encode(encoding="utf-8")
        if isinstance(integ_key, str):
            integ_key = integ_key.encode(encoding="utf-8")
        ckey = dict(length=len(crypto_key), data=crypto_key)
        ikey = dict(length=len(integ_key), data=integ_key if integ_key else 0)

        flags = int(IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE)
        if tunnel_src and tunnel_dst:
            flags = flags | int(IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL)
            src_addr = ip_address(tunnel_src)
            dst_addr = ip_address(tunnel_dst)
            if src_addr.version == 6:
                flags = flags | int(
                    IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL_V6
                )
        else:
            src_addr = ""
            dst_addr = ""

        cmd = "ipsec_sad_entry_add"
        err_msg = (
            "Failed to add Security Association Database entry"
            f" on host {node['host']}"
        )
        sad_entry = dict(
            sad_id=int(sad_id),
            spi=int(spi),
            crypto_algorithm=crypto_alg.alg_int_repr,
            crypto_key=ckey,
            integrity_algorithm=integ_alg.alg_int_repr,
            integrity_key=ikey,
            flags=flags,
            tunnel=dict(
                src=str(src_addr),
                dst=str(dst_addr),
                table_id=0,
                encap_decap_flags=int(
                    TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                ),
                dscp=int(IpDscp.IP_API_DSCP_CS0),
            ),
            protocol=IPsecProto.ESP,
            udp_src_port=IPSEC_UDP_PORT_DEFAULT,
            udp_dst_port=IPSEC_UDP_PORT_DEFAULT,
        )
        args = dict(entry=sad_entry)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_add_sad_entries(
        node: dict,
        n_entries: int,
        sad_id: int,
        spi: int,
        crypto_alg: CryptoAlg.InputType = None,
        crypto_key: str = "",
        integ_alg: IntegAlg.InputType = None,
        integ_key: str = "",
        tunnel_src: Optional[str] = None,
        tunnel_dst: Optional[str] = None,
        tunnel_addr_incr: bool = True,
    ) -> None:
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
        :param tunnel_addr_incr: Enable or disable tunnel IP address
            incremental step.
        :type node: dict
        :type n_entries: int
        :type sad_id: int
        :type spi: int
        :type crypto_alg: CryptoAlg.InputType
        :type crypto_key: str
        :type integ_alg: IntegAlg.InputType
        :type integ_key: str
        :type tunnel_src: Optional[str]
        :type tunnel_dst: Optional[str]
        :type tunnel_addr_incr: bool
        """
        crypto_alg = get_enum_instance(CryptoAlg, crypto_alg)
        integ_alg = get_enum_instance(IntegAlg, integ_alg)
        if isinstance(crypto_key, str):
            crypto_key = crypto_key.encode(encoding="utf-8")
        if isinstance(integ_key, str):
            integ_key = integ_key.encode(encoding="utf-8")
        if tunnel_src and tunnel_dst:
            src_addr = ip_address(tunnel_src)
            dst_addr = ip_address(tunnel_dst)
        else:
            src_addr = ""
            dst_addr = ""

        if tunnel_addr_incr:
            addr_incr = (
                1 << (128 - 96) if src_addr.version == 6 else 1 << (32 - 24)
            )
        else:
            addr_incr = 0

        ckey = dict(length=len(crypto_key), data=crypto_key)
        ikey = dict(length=len(integ_key), data=integ_key if integ_key else 0)

        flags = int(IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE)
        if tunnel_src and tunnel_dst:
            flags = flags | int(IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL)
            if src_addr.version == 6:
                flags = flags | int(
                    IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_TUNNEL_V6
                )

        cmd = "ipsec_sad_entry_add"
        err_msg = (
            "Failed to add Security Association Database entry"
            f" on host {node['host']}"
        )

        sad_entry = dict(
            sad_id=int(sad_id),
            spi=int(spi),
            crypto_algorithm=crypto_alg.alg_int_repr,
            crypto_key=ckey,
            integrity_algorithm=integ_alg.alg_int_repr,
            integrity_key=ikey,
            flags=flags,
            tunnel=dict(
                src=str(src_addr),
                dst=str(dst_addr),
                table_id=0,
                encap_decap_flags=int(
                    TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                ),
                dscp=int(IpDscp.IP_API_DSCP_CS0),
            ),
            protocol=IPsecProto.ESP,
            udp_src_port=IPSEC_UDP_PORT_DEFAULT,
            udp_dst_port=IPSEC_UDP_PORT_DEFAULT,
        )
        args = dict(entry=sad_entry)
        with PapiSocketExecutor(node, is_async=True) as papi_exec:
            for i in range(n_entries):
                args["entry"]["sad_id"] = int(sad_id) + i
                args["entry"]["spi"] = int(spi) + i
                args["entry"]["tunnel"]["src"] = (
                    str(src_addr + i * addr_incr)
                    if tunnel_src and tunnel_dst
                    else src_addr
                )
                args["entry"]["tunnel"]["dst"] = (
                    str(dst_addr + i * addr_incr)
                    if tunnel_src and tunnel_dst
                    else dst_addr
                )
                history = bool(not 1 < i < n_entries - 2)
                papi_exec.add(cmd, history=history, **args)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_set_ip_route(
        node: dict,
        n_tunnels: int,
        tunnel_src: str,
        traffic_addr: str,
        tunnel_dst: str,
        interface: str,
        raddr_range: int,
        dst_mac: Optional[str] = None,
    ) -> None:
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
        :param dst_mac: The MAC address of destination tunnels.
        :type node: dict
        :type n_tunnels: int
        :type tunnel_src: str
        :type traffic_addr: str
        :type tunnel_dst: str
        :type interface: str
        :type raddr_range: int
        :type dst_mac: Optional[str]
        """
        tunnel_src = ip_address(tunnel_src)
        tunnel_dst = ip_address(tunnel_dst)
        traffic_addr = ip_address(traffic_addr)
        tunnel_dst_prefix = 128 if tunnel_dst.version == 6 else 32
        addr_incr = (
            1 << (128 - raddr_range)
            if tunnel_src.version == 6
            else 1 << (32 - raddr_range)
        )

        cmd1 = "sw_interface_add_del_address"
        args1 = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=True,
            del_all=False,
            prefix=None,
        )
        cmd2 = "ip_route_add_del"
        args2 = dict(is_add=1, is_multipath=0, route=None)
        cmd3 = "ip_neighbor_add_del"
        args3 = dict(
            is_add=True,
            neighbor=dict(
                sw_if_index=Topology.get_interface_sw_index(node, interface),
                flags=0,
                mac_address=str(dst_mac),
                ip_address=None,
            ),
        )
        err_msg = (
            "Failed to configure IP addresses, IP routes and"
            f" IP neighbor on interface {interface} on host {node['host']}"
            if dst_mac
            else "Failed to configure IP addresses and IP routes"
            f" on interface {interface} on host {node['host']}"
        )

        with PapiSocketExecutor(node, is_async=True) as papi_exec:
            for i in range(n_tunnels):
                tunnel_dst_addr = tunnel_dst + i * addr_incr
                args1["prefix"] = IPUtil.create_prefix_object(
                    tunnel_src + i * addr_incr, raddr_range
                )
                args2["route"] = IPUtil.compose_vpp_route_structure(
                    node,
                    traffic_addr + i,
                    prefix_len=tunnel_dst_prefix,
                    interface=interface,
                    gateway=tunnel_dst_addr,
                )
                history = bool(not 1 < i < n_tunnels - 2)
                papi_exec.add(cmd1, history=history, **args1)
                papi_exec.add(cmd2, history=history, **args2)

                args2["route"] = IPUtil.compose_vpp_route_structure(
                    node,
                    tunnel_dst_addr,
                    prefix_len=tunnel_dst_prefix,
                    interface=interface,
                    gateway=tunnel_dst_addr,
                )
                papi_exec.add(cmd2, history=history, **args2)

                if dst_mac:
                    args3["neighbor"]["ip_address"] = ip_address(
                        tunnel_dst_addr
                    )
                    papi_exec.add(cmd3, history=history, **args3)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_add_spd(node: dict, spd_id: int) -> None:
        """Create Security Policy Database on the VPP node.

        :param node: VPP node to add SPD on.
        :param spd_id: SPD ID.
        :type node: dict
        :type spd_id: int
        """
        cmd = "ipsec_spd_add_del"
        err_msg = (
            f"Failed to add Security Policy Database on host {node['host']}"
        )
        args = dict(is_add=True, spd_id=int(spd_id))
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_spd_add_if(
        node: dict, spd_id: int, interface: Union[str, int]
    ) -> None:
        """Add interface to the Security Policy Database.

        :param node: VPP node.
        :param spd_id: SPD ID to add interface on.
        :param interface: Interface name or sw_if_index.
        :type node: dict
        :type spd_id: int
        :type interface: str or int
        """
        cmd = "ipsec_interface_add_del_spd"
        err_msg = (
            f"Failed to add interface {interface} to Security Policy"
            f" Database {spd_id} on host {node['host']}"
        )
        args = dict(
            is_add=True,
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            spd_id=int(spd_id),
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ipsec_create_spds_match_nth_entry(
        node: dict,
        dir1_interface: Union[str, int],
        dir2_interface: Union[str, int],
        entry_amount: int,
        local_addr_range: Union[str, IPv4Address, IPv6Address],
        remote_addr_range: Union[str, IPv4Address, IPv6Address],
        action: IpsecSpdAction.InputType = IpsecSpdAction.BYPASS,
        inbound: bool = False,
        bidirectional: bool = True,
    ) -> None:
        """Create one matching SPD entry for inbound or outbound traffic on
        a DUT for each traffic direction and also create entry_amount - 1
        non-matching SPD entries. Create a Security Policy Database on each
        outbound interface where these entries will be configured.
        The matching SPD entry will have the lowest priority, input action and
        will be configured to match the IP flow. The non-matching entries will
        be the same, except with higher priority and non-matching IP flows.

        Action Protect is currently not supported.

        :param node: VPP node to configured the SPDs and their entries.
        :param dir1_interface: The interface in direction 1 where the entries
            will be checked.
        :param dir2_interface: The interface in direction 2 where the entries
            will be checked.
        :param entry_amount: The number of SPD entries to configure. If
            entry_amount == 1, no non-matching entries will be configured.
        :param local_addr_range: Matching local address range in direction 1
            in format IP/prefix or IP/mask. If no mask is provided, it's
            considered to be /32.
        :param remote_addr_range: Matching remote address range in
            direction 1 in format IP/prefix or IP/mask. If no mask is
            provided, it's considered to be /32.
        :param action: IPsec SPD action.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param bidirectional: When True, will create SPDs in both directions
            of traffic. When False, only in one direction.
        :type node: dict
        :type dir1_interface: Union[str, int]
        :type dir2_interface: Union[str, int]
        :type entry_amount: int
        :type local_addr_range:
            Union[str, IPv4Address, IPv6Address]
        :type remote_addr_range:
            Union[str, IPv4Address, IPv6Address]
        :type action: IpsecSpdAction.InputType
        :type inbound: bool
        :type bidirectional: bool
        :raises NotImplementedError: When the action is IpsecSpdAction.PROTECT.
        """
        action = get_enum_instance(IpsecSpdAction, action)
        if action == IpsecSpdAction.PROTECT:
            raise NotImplementedError(
                "IPsec SPD action PROTECT is not supported."
            )

        spd_id_dir1 = 1
        spd_id_dir2 = 2
        matching_priority = 1

        IPsecUtil.vpp_ipsec_add_spd(node, spd_id_dir1)
        IPsecUtil.vpp_ipsec_spd_add_if(node, spd_id_dir1, dir1_interface)
        # matching entry direction 1
        IPsecUtil.vpp_ipsec_add_spd_entry(
            node,
            spd_id_dir1,
            matching_priority,
            action,
            inbound=inbound,
            laddr_range=local_addr_range,
            raddr_range=remote_addr_range,
        )

        if bidirectional:
            IPsecUtil.vpp_ipsec_add_spd(node, spd_id_dir2)
            IPsecUtil.vpp_ipsec_spd_add_if(node, spd_id_dir2, dir2_interface)

            # matching entry direction 2, the address ranges are switched
            IPsecUtil.vpp_ipsec_add_spd_entry(
                node,
                spd_id_dir2,
                matching_priority,
                action,
                inbound=inbound,
                laddr_range=remote_addr_range,
                raddr_range=local_addr_range,
            )

        # non-matching entries
        no_match_entry_amount = entry_amount - 1
        if no_match_entry_amount > 0:
            # create a NetworkIncrement representation of the network,
            # then skip the matching network
            no_match_local_addr_range = NetworkIncrement(
                ip_network(local_addr_range)
            )
            next(no_match_local_addr_range)

            no_match_remote_addr_range = NetworkIncrement(
                ip_network(remote_addr_range)
            )
            next(no_match_remote_addr_range)

            # non-matching entries direction 1
            IPsecUtil.vpp_ipsec_add_spd_entries(
                node,
                no_match_entry_amount,
                spd_id_dir1,
                ObjIncrement(matching_priority + 1, 1),
                action,
                inbound=inbound,
                laddr_range=no_match_local_addr_range,
                raddr_range=no_match_remote_addr_range,
            )

            if bidirectional:
                # reset the networks so that we're using a unified config
                # the address ranges are switched
                no_match_remote_addr_range = NetworkIncrement(
                    ip_network(local_addr_range)
                )
                next(no_match_remote_addr_range)

                no_match_local_addr_range = NetworkIncrement(
                    ip_network(remote_addr_range)
                )
                next(no_match_local_addr_range)
                # non-matching entries direction 2
                IPsecUtil.vpp_ipsec_add_spd_entries(
                    node,
                    no_match_entry_amount,
                    spd_id_dir2,
                    ObjIncrement(matching_priority + 1, 1),
                    action,
                    inbound=inbound,
                    laddr_range=no_match_local_addr_range,
                    raddr_range=no_match_remote_addr_range,
                )

        IPsecUtil.vpp_ipsec_show_all(node)

    @staticmethod
    def _vpp_ipsec_add_spd_entry_internal(
        executor: PapiSocketExecutor,
        spd_id: int,
        priority: int,
        action: IpsecSpdAction.InputType,
        inbound: bool = True,
        sa_id: Optional[int] = None,
        proto: IPsecProto.InputType = None,
        laddr_range: Optional[str] = None,
        raddr_range: Optional[str] = None,
        lport_range: Optional[str] = None,
        rport_range: Optional[str] = None,
        is_ipv6: bool = False,
    ) -> None:
        """Prepare to create Security Policy Database entry on the VPP node.

        This just adds one more command to the executor.
        The call site shall get replies once all entries are added,
        to get speed benefit from async PAPI.

        :param executor: Open PAPI executor (async handling) to add commands to.
        :param spd_id: SPD ID to add entry on.
        :param priority: SPD entry priority, higher number = higher priority.
        :param action: IPsec SPD action.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param sa_id: SAD entry ID for action IpsecSpdAction.PROTECT.
        :param proto: Policy selector next layer protocol number.
        :param laddr_range: Policy selector local IPv4 or IPv6 address range
            in format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param raddr_range: Policy selector remote IPv4 or IPv6 address range
            in format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param lport_range: Policy selector local TCP/UDP port range in format
            <port_start>-<port_end>.
        :param rport_range: Policy selector remote TCP/UDP port range in format
            <port_start>-<port_end>.
        :param is_ipv6: True in case of IPv6 policy when IPv6 address range is
            not defined so it will default to address ::/0, otherwise False.
        :type executor: PapiSocketExecutor
        :type spd_id: int
        :type priority: int
        :type action: IpsecSpdAction.InputType
        :type inbound: bool
        :type sa_id: Optional[int]
        :type proto: IPsecProto.InputType
        :type laddr_range: Optional[str]
        :type raddr_range: Optional[str]
        :type lport_range: Optional[str]
        :type rport_range: Optional[str]
        :type is_ipv6: bool
        """
        action = get_enum_instance(IpsecSpdAction, action)
        proto = get_enum_instance(IPsecProto, proto)
        if laddr_range is None:
            laddr_range = "::/0" if is_ipv6 else "0.0.0.0/0"

        if raddr_range is None:
            raddr_range = "::/0" if is_ipv6 else "0.0.0.0/0"

        local_net = ip_network(laddr_range, strict=False)
        remote_net = ip_network(raddr_range, strict=False)

        cmd = "ipsec_spd_entry_add_del_v2"

        spd_entry = dict(
            spd_id=int(spd_id),
            priority=int(priority),
            is_outbound=not inbound,
            sa_id=int(sa_id) if sa_id else 0,
            policy=int(action),
            protocol=proto,
            remote_address_start=IPAddress.create_ip_address_object(
                remote_net.network_address
            ),
            remote_address_stop=IPAddress.create_ip_address_object(
                remote_net.broadcast_address
            ),
            local_address_start=IPAddress.create_ip_address_object(
                local_net.network_address
            ),
            local_address_stop=IPAddress.create_ip_address_object(
                local_net.broadcast_address
            ),
            remote_port_start=(
                int(rport_range.split("-")[0]) if rport_range else 0
            ),
            remote_port_stop=(
                int(rport_range.split("-")[1]) if rport_range else 65535
            ),
            local_port_start=(
                int(lport_range.split("-")[0]) if lport_range else 0
            ),
            local_port_stop=(
                int(lport_range.split("-")[1]) if rport_range else 65535
            ),
        )
        args = dict(is_add=True, entry=spd_entry)
        executor.add(cmd, **args)

    @staticmethod
    def vpp_ipsec_add_spd_entry(
        node: dict,
        spd_id: int,
        priority: int,
        action: IpsecSpdAction.InputType,
        inbound: bool = True,
        sa_id: Optional[int] = None,
        proto: IPsecProto.InputType = None,
        laddr_range: Optional[str] = None,
        raddr_range: Optional[str] = None,
        lport_range: Optional[str] = None,
        rport_range: Optional[str] = None,
        is_ipv6: bool = False,
    ) -> None:
        """Create Security Policy Database entry on the VPP node.

        :param node: VPP node to add SPD entry on.
        :param spd_id: SPD ID to add entry on.
        :param priority: SPD entry priority, higher number = higher priority.
        :param action: IPsec SPD action.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param sa_id: SAD entry ID for action IpsecSpdAction.PROTECT.
        :param proto: Policy selector next layer protocol number.
        :param laddr_range: Policy selector local IPv4 or IPv6 address range
            in format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param raddr_range: Policy selector remote IPv4 or IPv6 address range
            in format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param lport_range: Policy selector local TCP/UDP port range in format
            <port_start>-<port_end>.
        :param rport_range: Policy selector remote TCP/UDP port range in format
            <port_start>-<port_end>.
        :param is_ipv6: True in case of IPv6 policy when IPv6 address range is
            not defined so it will default to address ::/0, otherwise False.
        :type node: dict
        :type spd_id: int
        :type priority: int
        :type action: IpsecSpdAction.InputType
        :type inbound: bool
        :type sa_id: Optional[int]
        :type proto: IPsecProto.InputType
        :type laddr_range: Optional[str]
        :type raddr_range: Optional[str]
        :type lport_range: Optional[str]
        :type rport_range: Optional[str]
        :type is_ipv6: bool
        """
        action = get_enum_instance(IpsecSpdAction, action)
        proto = get_enum_instance(IPsecProto, proto)
        err_msg = (
            "Failed to add entry to Security Policy Database"
            f" {spd_id} on host {node['host']}"
        )
        with PapiSocketExecutor(node, is_async=True) as papi_exec:
            IPsecUtil._vpp_ipsec_add_spd_entry_internal(
                papi_exec,
                spd_id,
                priority,
                action,
                inbound,
                sa_id,
                proto,
                laddr_range,
                raddr_range,
                lport_range,
                rport_range,
                is_ipv6,
            )
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_add_spd_entries(
        node: dict,
        n_entries: int,
        spd_id: int,
        priority: Optional[ObjIncrement],
        action: IpsecSpdAction.InputType,
        inbound: bool,
        sa_id: Optional[ObjIncrement] = None,
        proto: IPsecProto.InputType = None,
        laddr_range: Optional[NetworkIncrement] = None,
        raddr_range: Optional[NetworkIncrement] = None,
        lport_range: Optional[str] = None,
        rport_range: Optional[str] = None,
        is_ipv6: bool = False,
    ) -> None:
        """Create multiple Security Policy Database entries on the VPP node.

        :param node: VPP node to add SPD entries on.
        :param n_entries: Number of SPD entries to be added.
        :param spd_id: SPD ID to add entries on.
        :param priority: SPD entries priority, higher number = higher priority.
        :param action: IPsec SPD action.
        :param inbound: If True policy is for inbound traffic, otherwise
            outbound.
        :param sa_id: SAD entry ID for action IpsecSpdAction.PROTECT.
        :param proto: Policy selector next layer protocol number.
        :param laddr_range: Policy selector local IPv4 or IPv6 address range
            in format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param raddr_range: Policy selector remote IPv4 or IPv6 address range
            in format IP/prefix or IP/mask. If no mask is provided,
            it's considered to be /32.
        :param lport_range: Policy selector local TCP/UDP port range in format
            <port_start>-<port_end>.
        :param rport_range: Policy selector remote TCP/UDP port range in format
            <port_start>-<port_end>.
        :param is_ipv6: True in case of IPv6 policy when IPv6 address range is
            not defined so it will default to address ::/0, otherwise False.
        :type node: dict
        :type n_entries: int
        :type spd_id: int
        :type priority: Optional[ObjIncrement]
        :type action: IpsecSpdAction.InputType
        :type inbound: bool
        :type sa_id: Optional[ObjIncrement]
        :type proto: IPsecProto.InputType
        :type laddr_range: Optional[NetworkIncrement]
        :type raddr_range: Optional[NetworkIncrement]
        :type lport_range: Optional[str]
        :type rport_range: Optional[str]
        :type is_ipv6: bool
        """
        action = get_enum_instance(IpsecSpdAction, action)
        proto = get_enum_instance(IPsecProto, proto)
        if laddr_range is None:
            laddr_range = "::/0" if is_ipv6 else "0.0.0.0/0"
            laddr_range = NetworkIncrement(ip_network(laddr_range), 0)

        if raddr_range is None:
            raddr_range = "::/0" if is_ipv6 else "0.0.0.0/0"
            raddr_range = NetworkIncrement(ip_network(raddr_range), 0)

        err_msg = (
            "Failed to add entry to Security Policy Database"
            f" {spd_id} on host {node['host']}"
        )
        with PapiSocketExecutor(node, is_async=True) as papi_exec:
            for _ in range(n_entries):
                IPsecUtil._vpp_ipsec_add_spd_entry_internal(
                    papi_exec,
                    spd_id,
                    next(priority),
                    action,
                    inbound,
                    next(sa_id) if sa_id is not None else sa_id,
                    proto,
                    next(laddr_range),
                    next(raddr_range),
                    lport_range,
                    rport_range,
                    is_ipv6,
                )
            papi_exec.get_replies(err_msg)

    @staticmethod
    def _ipsec_create_loopback_dut1_papi(
        nodes: dict, tun_ips: dict, if1_key: str, if2_key: str
    ) -> int:
        """Create loopback interface and set IP address on VPP node 1 interface
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
        :returns: sw_if_idx Of the created loopback interface.
        :rtype: int
        """
        with PapiSocketExecutor(nodes["DUT1"]) as papi_exec:
            # Create loopback interface on DUT1, set it to up state
            cmd = "create_loopback_instance"
            args = dict(
                mac_address=0,
                is_specified=False,
                user_instance=0,
            )
            err_msg = (
                "Failed to create loopback interface"
                f" on host {nodes['DUT1']['host']}"
            )
            papi_exec.add(cmd, **args)
            loop_sw_if_idx = papi_exec.get_sw_if_index(err_msg)
            cmd = "sw_interface_set_flags"
            args = dict(
                sw_if_index=loop_sw_if_idx,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value,
            )
            err_msg = (
                "Failed to set loopback interface state up"
                f" on host {nodes['DUT1']['host']}"
            )
            papi_exec.add(cmd, **args).get_reply(err_msg)
            # Set IP address on VPP node 1 interface
            cmd = "sw_interface_add_del_address"
            args = dict(
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes["DUT1"], if1_key
                ),
                is_add=True,
                del_all=False,
                prefix=IPUtil.create_prefix_object(
                    tun_ips["ip2"] - 1,
                    96 if tun_ips["ip2"].version == 6 else 24,
                ),
            )
            err_msg = (
                f"Failed to set IP address on interface {if1_key}"
                f" on host {nodes['DUT1']['host']}"
            )
            papi_exec.add(cmd, **args).get_reply(err_msg)
            cmd2 = "ip_neighbor_add_del"
            args2 = dict(
                is_add=1,
                neighbor=dict(
                    sw_if_index=Topology.get_interface_sw_index(
                        nodes["DUT1"], if1_key
                    ),
                    flags=1,
                    mac_address=str(
                        Topology.get_interface_mac(nodes["DUT2"], if2_key)
                        if "DUT2" in nodes.keys()
                        else Topology.get_interface_mac(nodes["TG"], if2_key)
                    ),
                    ip_address=tun_ips["ip2"].compressed,
                ),
            )
            err_msg = f"Failed to add IP neighbor on interface {if1_key}"
            papi_exec.add(cmd2, **args2).get_reply(err_msg)

            return loop_sw_if_idx

    @staticmethod
    def _ipsec_create_tunnel_interfaces_dut1_papi(
        nodes: dict,
        tun_ips: dict,
        if1_key: str,
        if2_key: str,
        n_tunnels: int,
        crypto_alg: CryptoAlg.InputType,
        integ_alg: IntegAlg.InputType,
        raddr_ip2: Union[IPv4Address, IPv6Address],
        addr_incr: int,
        spi_d: dict,
        existing_tunnels: int = 0,
        udp_encap: bool = False,
        anti_replay: bool = False,
    ) -> Tuple[List[bytes], List[bytes]]:
        """Create multiple IPsec tunnel interfaces on DUT1 node using PAPI.

        Generate random keys and return them (so DUT2 or TG can decrypt).

        :param nodes: VPP nodes to create tunnel interfaces.
        :param tun_ips: Dictionary with VPP node 1 ipsec tunnel interface
            IPv4/IPv6 address (ip1) and VPP node 2 ipsec tunnel interface
            IPv4/IPv6 address (ip2).
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 / TG node (in case of 2-node topology)
            interface key from topology file.
        :param n_tunnels: Number of tunnel interfaces to be there at the end.
        :param crypto_alg: The encryption algorithm name.
        :param integ_alg: The integrity algorithm name.
        :param raddr_ip2: Policy selector remote IPv4/IPv6 start address for the
            first tunnel in direction node2->node1.
        :param spi_d: Dictionary with SPIs for VPP node 1 and VPP node 2.
        :param addr_incr: IP / IPv6 address incremental step.
        :param existing_tunnels: Number of tunnel interfaces before creation.
            Useful mainly for reconf tests. Default 0.
        :param udp_encap: Whether to apply UDP_ENCAP flag.
        :param anti_replay: Whether to apply USE_ANTI_REPLAY flag.
        :type nodes: dict
        :type tun_ips: dict
        :type if1_key: str
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg.InputType
        :type integ_alg: IntegAlg.InputType
        :type raddr_ip2: Union[IPv4Address, IPv6Address]
        :type addr_incr: int
        :type spi_d: dict
        :type existing_tunnels: int
        :type udp_encap: bool
        :type anti_replay: bool
        :returns: Generated ckeys and ikeys.
        :rtype: List[bytes], List[bytes]
        """
        crypto_alg = get_enum_instance(CryptoAlg, crypto_alg)
        integ_alg = get_enum_instance(IntegAlg, integ_alg)
        if not existing_tunnels:
            loop_sw_if_idx = IPsecUtil._ipsec_create_loopback_dut1_papi(
                nodes, tun_ips, if1_key, if2_key
            )
        else:
            loop_sw_if_idx = InterfaceUtil.vpp_get_interface_sw_index(
                nodes["DUT1"], "loop0"
            )
        with PapiSocketExecutor(nodes["DUT1"], is_async=True) as papi_exec:
            # Configure IP addresses on loop0 interface
            cmd = "sw_interface_add_del_address"
            args = dict(
                sw_if_index=loop_sw_if_idx,
                is_add=True,
                del_all=False,
                prefix=None,
            )
            for i in range(existing_tunnels, n_tunnels):
                args["prefix"] = IPUtil.create_prefix_object(
                    tun_ips["ip1"] + i * addr_incr,
                    128 if tun_ips["ip1"].version == 6 else 32,
                )
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            # Configure IPIP tunnel interfaces
            cmd = "ipip_add_tunnel"
            ipip_tunnel = dict(
                instance=Constants.BITWISE_NON_ZERO,
                src=None,
                dst=None,
                table_id=0,
                flags=int(
                    TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                ),
                mode=int(TunnelMode.TUNNEL_API_MODE_P2P),
                dscp=int(IpDscp.IP_API_DSCP_CS0),
            )
            args = dict(tunnel=ipip_tunnel)
            ipip_tunnels = [None] * existing_tunnels
            for i in range(existing_tunnels, n_tunnels):
                ipip_tunnel["src"] = IPAddress.create_ip_address_object(
                    tun_ips["ip1"] + i * addr_incr
                )
                ipip_tunnel["dst"] = IPAddress.create_ip_address_object(
                    tun_ips["ip2"]
                )
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = (
                "Failed to add IPIP tunnel interfaces on host"
                f" {nodes['DUT1']['host']}"
            )
            ipip_tunnels.extend(
                [
                    reply["sw_if_index"]
                    for reply in papi_exec.get_replies(err_msg)
                    if "sw_if_index" in reply
                ]
            )
            # Configure IPSec SAD entries
            ckeys = [bytes()] * existing_tunnels
            ikeys = [bytes()] * existing_tunnels
            cmd = "ipsec_sad_entry_add"
            c_key = dict(length=0, data=None)
            i_key = dict(length=0, data=None)
            common_flags = IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE
            if udp_encap:
                common_flags |= IPsecSadFlags.IPSEC_API_SAD_FLAG_UDP_ENCAP
            if anti_replay:
                common_flags |= IPsecSadFlags.IPSEC_API_SAD_FLAG_USE_ANTI_REPLAY
            sad_entry = dict(
                sad_id=None,
                spi=None,
                protocol=IPsecProto.ESP,
                crypto_algorithm=crypto_alg.alg_int_repr,
                crypto_key=c_key,
                integrity_algorithm=integ_alg.alg_int_repr,
                integrity_key=i_key,
                flags=common_flags,
                tunnel=dict(
                    src=0,
                    dst=0,
                    table_id=0,
                    encap_decap_flags=int(
                        TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                    ),
                    dscp=int(IpDscp.IP_API_DSCP_CS0),
                ),
                salt=0,
                udp_src_port=IPSEC_UDP_PORT_DEFAULT,
                udp_dst_port=IPSEC_UDP_PORT_DEFAULT,
            )
            args = dict(entry=sad_entry)
            for i in range(existing_tunnels, n_tunnels):
                ckeys.append(gen_key(crypto_alg.key_len))
                ikeys.append(gen_key(integ_alg.key_len))
                # SAD entry for outband / tx path
                sad_entry["sad_id"] = i
                sad_entry["spi"] = spi_d["spi_1"] + i

                sad_entry["crypto_key"]["length"] = len(ckeys[i])
                sad_entry["crypto_key"]["data"] = ckeys[i]
                if integ_alg:
                    sad_entry["integrity_key"]["length"] = len(ikeys[i])
                    sad_entry["integrity_key"]["data"] = ikeys[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            sad_entry["flags"] |= IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_INBOUND
            for i in range(existing_tunnels, n_tunnels):
                # SAD entry for inband / rx path
                sad_entry["sad_id"] = 100000 + i
                sad_entry["spi"] = spi_d["spi_2"] + i

                sad_entry["crypto_key"]["length"] = len(ckeys[i])
                sad_entry["crypto_key"]["data"] = ckeys[i]
                if integ_alg:
                    sad_entry["integrity_key"]["length"] = len(ikeys[i])
                    sad_entry["integrity_key"]["data"] = ikeys[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = (
                "Failed to add IPsec SAD entries on host"
                f" {nodes['DUT1']['host']}"
            )
            papi_exec.get_replies(err_msg)
            # Add protection for tunnels with IPSEC
            cmd = "ipsec_tunnel_protect_update"
            n_hop = dict(
                address=0,
                via_label=MPLS_LABEL_INVALID,
                obj_id=Constants.BITWISE_NON_ZERO,
            )
            ipsec_tunnel_protect = dict(
                sw_if_index=None, nh=n_hop, sa_out=None, n_sa_in=1, sa_in=None
            )
            args = dict(tunnel=ipsec_tunnel_protect)
            for i in range(existing_tunnels, n_tunnels):
                args["tunnel"]["sw_if_index"] = ipip_tunnels[i]
                args["tunnel"]["sa_out"] = i
                args["tunnel"]["sa_in"] = [100000 + i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = (
                "Failed to add protection for tunnels with IPSEC"
                f" on host {nodes['DUT1']['host']}"
            )
            papi_exec.get_replies(err_msg)

            # Configure unnumbered interfaces
            cmd = "sw_interface_set_unnumbered"
            args = dict(
                is_add=True,
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes["DUT1"], if1_key
                ),
                unnumbered_sw_if_index=0,
            )
            for i in range(existing_tunnels, n_tunnels):
                args["unnumbered_sw_if_index"] = ipip_tunnels[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            # Set interfaces up
            cmd = "sw_interface_set_flags"
            args = dict(
                sw_if_index=0,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value,
            )
            for i in range(existing_tunnels, n_tunnels):
                args["sw_if_index"] = ipip_tunnels[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            # Configure IP routes
            cmd = "ip_route_add_del"
            args = dict(is_add=1, is_multipath=0, route=None)
            for i in range(existing_tunnels, n_tunnels):
                args["route"] = IPUtil.compose_vpp_route_structure(
                    nodes["DUT1"],
                    (raddr_ip2 + i).compressed,
                    prefix_len=128 if raddr_ip2.version == 6 else 32,
                    interface=ipip_tunnels[i],
                )
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = f"Failed to add IP routes on host {nodes['DUT1']['host']}"
            papi_exec.get_replies(err_msg)

        return ckeys, ikeys

    @staticmethod
    def _ipsec_create_tunnel_interfaces_dut2_papi(
        nodes: dict,
        tun_ips: dict,
        if2_key: str,
        n_tunnels: int,
        crypto_alg: CryptoAlg.InputType,
        ckeys: Sequence[bytes],
        integ_alg: IntegAlg.InputType,
        ikeys: Sequence[bytes],
        raddr_ip1: Union[IPv4Address, IPv6Address],
        addr_incr: int,
        spi_d: dict,
        existing_tunnels: int = 0,
        udp_encap: bool = False,
        anti_replay: bool = False,
    ) -> None:
        """Create multiple IPsec tunnel interfaces on DUT2 node using PAPI.

        This method accesses keys generated by DUT1 method
        and does not return anything.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param tun_ips: Dictionary with VPP node 1 ipsec tunnel interface
            IPv4/IPv6 address (ip1) and VPP node 2 ipsec tunnel interface
            IPv4/IPv6 address (ip2).
        :param if2_key: VPP node 2 / TG node (in case of 2-node topology)
            interface key from topology file.
        :param n_tunnels: Number of tunnel interfaces to be there at the end.
        :param crypto_alg: The encryption algorithm name.
        :param ckeys: List of encryption keys.
        :param integ_alg: The integrity algorithm name.
        :param ikeys: List of integrity keys.
        :param raddr_ip1: Policy selector remote IPv4/IPv6 start address for the
            first tunnel in direction node1->node2.
        :param spi_d: Dictionary with SPIs for VPP node 1 and VPP node 2.
        :param addr_incr: IP / IPv6 address incremental step.
        :param existing_tunnels: Number of tunnel interfaces before creation.
            Useful mainly for reconf tests. Default 0.
        :param udp_encap: Whether to apply UDP_ENCAP flag.
        :param anti_replay: Whether to apply USE_ANTI_REPLAY flag.
        :type nodes: dict
        :type tun_ips: dict
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg.InputType
        :type ckeys: Sequence[bytes]
        :type integ_alg: IntegAlg.InputType
        :type ikeys: Sequence[bytes]
        :type raddr_ip1: Union[IPv4Address, IPv6Address]
        :type addr_incr: int
        :type spi_d: dict
        :type existing_tunnels: int
        :type udp_encap: bool
        :type anti_replay: bool
        """
        crypto_alg = get_enum_instance(CryptoAlg, crypto_alg)
        integ_alg = get_enum_instance(IntegAlg, integ_alg)
        with PapiSocketExecutor(nodes["DUT2"], is_async=True) as papi_exec:
            if not existing_tunnels:
                # Set IP address on VPP node 2 interface
                cmd = "sw_interface_add_del_address"
                args = dict(
                    sw_if_index=InterfaceUtil.get_interface_index(
                        nodes["DUT2"], if2_key
                    ),
                    is_add=True,
                    del_all=False,
                    prefix=IPUtil.create_prefix_object(
                        tun_ips["ip2"],
                        96 if tun_ips["ip2"].version == 6 else 24,
                    ),
                )
                err_msg = (
                    f"Failed to set IP address on interface {if2_key}"
                    f" on host {nodes['DUT2']['host']}"
                )
                papi_exec.add(cmd, **args).get_replies(err_msg)
            # Configure IPIP tunnel interfaces
            cmd = "ipip_add_tunnel"
            ipip_tunnel = dict(
                instance=Constants.BITWISE_NON_ZERO,
                src=None,
                dst=None,
                table_id=0,
                flags=int(
                    TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                ),
                mode=int(TunnelMode.TUNNEL_API_MODE_P2P),
                dscp=int(IpDscp.IP_API_DSCP_CS0),
            )
            args = dict(tunnel=ipip_tunnel)
            ipip_tunnels = [None] * existing_tunnels
            for i in range(existing_tunnels, n_tunnels):
                ipip_tunnel["src"] = IPAddress.create_ip_address_object(
                    tun_ips["ip2"]
                )
                ipip_tunnel["dst"] = IPAddress.create_ip_address_object(
                    tun_ips["ip1"] + i * addr_incr
                )
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = (
                "Failed to add IPIP tunnel interfaces on host"
                f" {nodes['DUT2']['host']}"
            )
            ipip_tunnels.extend(
                [
                    reply["sw_if_index"]
                    for reply in papi_exec.get_replies(err_msg)
                    if "sw_if_index" in reply
                ]
            )
            # Configure IPSec SAD entries
            cmd = "ipsec_sad_entry_add"
            c_key = dict(length=0, data=None)
            i_key = dict(length=0, data=None)
            common_flags = IPsecSadFlags.IPSEC_API_SAD_FLAG_NONE
            if udp_encap:
                common_flags |= IPsecSadFlags.IPSEC_API_SAD_FLAG_UDP_ENCAP
            if anti_replay:
                common_flags |= IPsecSadFlags.IPSEC_API_SAD_FLAG_USE_ANTI_REPLAY
            sad_entry = dict(
                sad_id=None,
                spi=None,
                protocol=IPsecProto.ESP,
                crypto_algorithm=crypto_alg.alg_int_repr,
                crypto_key=c_key,
                integrity_algorithm=integ_alg.alg_int_repr,
                integrity_key=i_key,
                flags=common_flags,
                tunnel=dict(
                    src=0,
                    dst=0,
                    table_id=0,
                    encap_decap_flags=int(
                        TunnelEncpaDecapFlags.TUNNEL_API_ENCAP_DECAP_FLAG_NONE
                    ),
                    dscp=int(IpDscp.IP_API_DSCP_CS0),
                ),
                salt=0,
                udp_src_port=IPSEC_UDP_PORT_DEFAULT,
                udp_dst_port=IPSEC_UDP_PORT_DEFAULT,
            )
            args = dict(entry=sad_entry)
            for i in range(existing_tunnels, n_tunnels):
                ckeys.append(gen_key(crypto_alg.key_len))
                ikeys.append(gen_key(integ_alg.key_len))
                # SAD entry for outband / tx path
                sad_entry["sad_id"] = 100000 + i
                sad_entry["spi"] = spi_d["spi_2"] + i

                sad_entry["crypto_key"]["length"] = len(ckeys[i])
                sad_entry["crypto_key"]["data"] = ckeys[i]
                if integ_alg:
                    sad_entry["integrity_key"]["length"] = len(ikeys[i])
                    sad_entry["integrity_key"]["data"] = ikeys[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            sad_entry["flags"] |= IPsecSadFlags.IPSEC_API_SAD_FLAG_IS_INBOUND
            for i in range(existing_tunnels, n_tunnels):
                # SAD entry for inband / rx path
                sad_entry["sad_id"] = i
                sad_entry["spi"] = spi_d["spi_1"] + i

                sad_entry["crypto_key"]["length"] = len(ckeys[i])
                sad_entry["crypto_key"]["data"] = ckeys[i]
                if integ_alg:
                    sad_entry["integrity_key"]["length"] = len(ikeys[i])
                    sad_entry["integrity_key"]["data"] = ikeys[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = (
                f"Failed to add IPsec SAD entries on host"
                f" {nodes['DUT2']['host']}"
            )
            papi_exec.get_replies(err_msg)
            # Add protection for tunnels with IPSEC
            cmd = "ipsec_tunnel_protect_update"
            n_hop = dict(
                address=0,
                via_label=MPLS_LABEL_INVALID,
                obj_id=Constants.BITWISE_NON_ZERO,
            )
            ipsec_tunnel_protect = dict(
                sw_if_index=None, nh=n_hop, sa_out=None, n_sa_in=1, sa_in=None
            )
            args = dict(tunnel=ipsec_tunnel_protect)
            for i in range(existing_tunnels, n_tunnels):
                args["tunnel"]["sw_if_index"] = ipip_tunnels[i]
                args["tunnel"]["sa_out"] = 100000 + i
                args["tunnel"]["sa_in"] = [i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = (
                "Failed to add protection for tunnels with IPSEC"
                f" on host {nodes['DUT2']['host']}"
            )
            papi_exec.get_replies(err_msg)

            if not existing_tunnels:
                # Configure IP route
                cmd = "ip_route_add_del"
                route = IPUtil.compose_vpp_route_structure(
                    nodes["DUT2"],
                    tun_ips["ip1"].compressed,
                    prefix_len=32 if tun_ips["ip1"].version == 6 else 8,
                    interface=if2_key,
                    gateway=(tun_ips["ip2"] - 1).compressed,
                )
                args = dict(is_add=1, is_multipath=0, route=route)
                papi_exec.add(cmd, **args)
            # Configure unnumbered interfaces
            cmd = "sw_interface_set_unnumbered"
            args = dict(
                is_add=True,
                sw_if_index=InterfaceUtil.get_interface_index(
                    nodes["DUT2"], if2_key
                ),
                unnumbered_sw_if_index=0,
            )
            for i in range(existing_tunnels, n_tunnels):
                args["unnumbered_sw_if_index"] = ipip_tunnels[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            # Set interfaces up
            cmd = "sw_interface_set_flags"
            args = dict(
                sw_if_index=0,
                flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value,
            )
            for i in range(existing_tunnels, n_tunnels):
                args["sw_if_index"] = ipip_tunnels[i]
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            # Configure IP routes
            cmd = "ip_route_add_del"
            args = dict(is_add=1, is_multipath=0, route=None)
            for i in range(existing_tunnels, n_tunnels):
                args["route"] = IPUtil.compose_vpp_route_structure(
                    nodes["DUT1"],
                    (raddr_ip1 + i).compressed,
                    prefix_len=128 if raddr_ip1.version == 6 else 32,
                    interface=ipip_tunnels[i],
                )
                papi_exec.add(
                    cmd, history=bool(not 1 < i < n_tunnels - 2), **args
                )
            err_msg = f"Failed to add IP routes on host {nodes['DUT2']['host']}"
            papi_exec.get_replies(err_msg)

    @staticmethod
    def vpp_ipsec_create_tunnel_interfaces(
        nodes: dict,
        tun_if1_ip_addr: str,
        tun_if2_ip_addr: str,
        if1_key: str,
        if2_key: str,
        n_tunnels: int,
        crypto_alg: CryptoAlg.InputType,
        integ_alg: IntegAlg.InputType,
        raddr_ip1: str,
        raddr_ip2: str,
        raddr_range: int,
        existing_tunnels: int = 0,
        udp_encap: bool = False,
        anti_replay: bool = False,
        return_keys: bool = False,
    ) -> Optional[Tuple[List[bytes], List[bytes], int, int]]:
        """Create multiple IPsec tunnel interfaces between two VPP nodes.

        Some deployments (e.g. devicetest) need to know the generated keys.
        But other deployments (e.g. scale perf test) would get spammed
        if we returned keys every time.

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
        :param return_keys: Whether generated keys should be returned.
        :param udp_encap: Whether to apply UDP_ENCAP flag.
        :param anti_replay: Whether to apply USE_ANTI_REPLAY flag.
        :type nodes: dict
        :type tun_if1_ip_addr: str
        :type tun_if2_ip_addr: str
        :type if1_key: str
        :type if2_key: str
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg.InputType
        :type integ_alg: IntegAlg.InputType
        :type raddr_ip1: str
        :type raddr_ip2: str
        :type raddr_range: int
        :type existing_tunnels: int
        :type return_keys: bool
        :type udp_encap: bool
        :type anti_replay: bool
        :returns: Ckeys, ikeys, spi_1, spi_2.
        :rtype: Optional[Tuple[List[bytes], List[bytes], int, int]]
        """
        crypto_alg = get_enum_instance(CryptoAlg, crypto_alg)
        integ_alg = get_enum_instance(IntegAlg, integ_alg)
        n_tunnels = int(n_tunnels)
        existing_tunnels = int(existing_tunnels)
        spi_d = dict(spi_1=100000, spi_2=200000)
        tun_ips = dict(
            ip1=ip_address(tun_if1_ip_addr), ip2=ip_address(tun_if2_ip_addr)
        )
        raddr_ip1 = ip_address(raddr_ip1)
        raddr_ip2 = ip_address(raddr_ip2)
        addr_incr = (
            1 << (128 - raddr_range)
            if tun_ips["ip1"].version == 6
            else 1 << (32 - raddr_range)
        )

        ckeys, ikeys = IPsecUtil._ipsec_create_tunnel_interfaces_dut1_papi(
            nodes,
            tun_ips,
            if1_key,
            if2_key,
            n_tunnels,
            crypto_alg,
            integ_alg,
            raddr_ip2,
            addr_incr,
            spi_d,
            existing_tunnels,
            udp_encap,
            anti_replay,
        )
        if "DUT2" in nodes.keys():
            IPsecUtil._ipsec_create_tunnel_interfaces_dut2_papi(
                nodes,
                tun_ips,
                if2_key,
                n_tunnels,
                crypto_alg,
                ckeys,
                integ_alg,
                ikeys,
                raddr_ip1,
                addr_incr,
                spi_d,
                existing_tunnels,
                udp_encap,
                anti_replay,
            )

        if return_keys:
            return ckeys, ikeys, spi_d["spi_1"], spi_d["spi_2"]
        return None

    @staticmethod
    def _create_ipsec_script_files(
        dut: str, instances: int
    ) -> List[TextIOWrapper]:
        """Create script files for configuring IPsec in containers

        :param dut: DUT node on which to create the script files
        :param instances: number of containers on DUT node
        :type dut: str
        :type instances: int
        :returns: Created opened file handles.
        :rtype: List[TextIOWrapper]
        """
        scripts = []
        for cnf in range(0, instances):
            script_filename = (
                f"/tmp/ipsec_create_tunnel_cnf_{dut}_{cnf + 1}.config"
            )
            scripts.append(open(script_filename, "w", encoding="utf-8"))
        return scripts

    @staticmethod
    def _close_and_copy_ipsec_script_files(
        dut: str, nodes: dict, instances: int, scripts: Sequence[TextIOWrapper]
    ) -> None:
        """Close created scripts and copy them to containers

        :param dut: DUT node on which to create the script files
        :param nodes: VPP nodes
        :param instances: number of containers on DUT node
        :param scripts: dictionary holding the script files
        :type dut: str
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
    def vpp_ipsec_add_multiple_tunnels(
        nodes: dict,
        interface1: Union[str, int],
        interface2: Union[str, int],
        n_tunnels: int,
        crypto_alg: CryptoAlg.InputType,
        integ_alg: IntegAlg.InputType,
        tunnel_ip1: str,
        tunnel_ip2: str,
        raddr_ip1: str,
        raddr_ip2: str,
        raddr_range: int,
        tunnel_addr_incr: bool = True,
    ) -> None:
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
        :param tunnel_addr_incr: Enable or disable tunnel IP address
            incremental step.
        :type nodes: dict
        :type interface1: Union[str, int]
        :type interface2: Union[str, int]
        :type n_tunnels: int
        :type crypto_alg: CryptoAlg.InputType
        :type integ_alg: IntegAlg.InputType
        :type tunnel_ip1: str
        :type tunnel_ip2: str
        :type raddr_ip1: str
        :type raddr_ip2: str
        :type raddr_range: int
        :type tunnel_addr_incr: bool
        """
        crypto_alg = get_enum_instance(CryptoAlg, crypto_alg)
        integ_alg = get_enum_instance(IntegAlg, integ_alg)

        spd_id = 1
        p_hi = 100
        p_lo = 10
        sa_id_1 = 100000
        sa_id_2 = 200000
        spi_1 = 300000
        spi_2 = 400000

        crypto_key = gen_key(crypto_alg.key_len).decode()
        integ_key = gen_key(integ_alg.key_len).decode()
        rmac = (
            Topology.get_interface_mac(nodes["DUT2"], interface2)
            if "DUT2" in nodes.keys()
            else Topology.get_interface_mac(nodes["TG"], interface2)
        )
        IPsecUtil.vpp_ipsec_set_ip_route(
            nodes["DUT1"],
            n_tunnels,
            tunnel_ip1,
            raddr_ip2,
            tunnel_ip2,
            interface1,
            raddr_range,
            rmac,
        )

        IPsecUtil.vpp_ipsec_add_spd(nodes["DUT1"], spd_id)
        IPsecUtil.vpp_ipsec_spd_add_if(nodes["DUT1"], spd_id, interface1)

        addr_incr = (
            1 << (128 - 96)
            if ip_address(tunnel_ip1).version == 6
            else 1 << (32 - 24)
        )
        for i in range(n_tunnels // (addr_incr**2) + 1):
            dut1_local_outbound_range = ip_network(
                f"{ip_address(tunnel_ip1) + i*(addr_incr**3)}/8", False
            ).with_prefixlen
            dut1_remote_outbound_range = ip_network(
                f"{ip_address(tunnel_ip2) + i*(addr_incr**3)}/8", False
            ).with_prefixlen

            IPsecUtil.vpp_ipsec_add_spd_entry(
                nodes["DUT1"],
                spd_id,
                p_hi,
                IpsecSpdAction.BYPASS,
                inbound=False,
                proto=IPsecProto.ESP,
                laddr_range=dut1_local_outbound_range,
                raddr_range=dut1_remote_outbound_range,
            )
            IPsecUtil.vpp_ipsec_add_spd_entry(
                nodes["DUT1"],
                spd_id,
                p_hi,
                IpsecSpdAction.BYPASS,
                inbound=True,
                proto=IPsecProto.ESP,
                laddr_range=dut1_remote_outbound_range,
                raddr_range=dut1_local_outbound_range,
            )

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes["DUT1"],
            n_tunnels,
            sa_id_1,
            spi_1,
            crypto_alg,
            crypto_key,
            integ_alg,
            integ_key,
            tunnel_ip1,
            tunnel_ip2,
            tunnel_addr_incr,
        )

        IPsecUtil.vpp_ipsec_add_spd_entries(
            nodes["DUT1"],
            n_tunnels,
            spd_id,
            priority=ObjIncrement(p_lo, 0),
            action=IpsecSpdAction.PROTECT,
            inbound=False,
            sa_id=ObjIncrement(sa_id_1, 1),
            raddr_range=NetworkIncrement(ip_network(raddr_ip2)),
        )

        IPsecUtil.vpp_ipsec_add_sad_entries(
            nodes["DUT1"],
            n_tunnels,
            sa_id_2,
            spi_2,
            crypto_alg,
            crypto_key,
            integ_alg,
            integ_key,
            tunnel_ip2,
            tunnel_ip1,
            tunnel_addr_incr,
        )
        IPsecUtil.vpp_ipsec_add_spd_entries(
            nodes["DUT1"],
            n_tunnels,
            spd_id,
            priority=ObjIncrement(p_lo, 0),
            action=IpsecSpdAction.PROTECT,
            inbound=True,
            sa_id=ObjIncrement(sa_id_2, 1),
            raddr_range=NetworkIncrement(ip_network(raddr_ip1)),
        )

        if "DUT2" in nodes.keys():
            rmac = Topology.get_interface_mac(nodes["DUT1"], interface1)
            IPsecUtil.vpp_ipsec_set_ip_route(
                nodes["DUT2"],
                n_tunnels,
                tunnel_ip2,
                raddr_ip1,
                tunnel_ip1,
                interface2,
                raddr_range,
                rmac,
            )

            IPsecUtil.vpp_ipsec_add_spd(nodes["DUT2"], spd_id)
            IPsecUtil.vpp_ipsec_spd_add_if(nodes["DUT2"], spd_id, interface2)
            for i in range(n_tunnels // (addr_incr**2) + 1):
                dut2_local_outbound_range = ip_network(
                    f"{ip_address(tunnel_ip1) + i*(addr_incr**3)}/8", False
                ).with_prefixlen
                dut2_remote_outbound_range = ip_network(
                    f"{ip_address(tunnel_ip2) + i*(addr_incr**3)}/8", False
                ).with_prefixlen

                IPsecUtil.vpp_ipsec_add_spd_entry(
                    nodes["DUT2"],
                    spd_id,
                    p_hi,
                    IpsecSpdAction.BYPASS,
                    inbound=False,
                    proto=IPsecProto.ESP,
                    laddr_range=dut2_remote_outbound_range,
                    raddr_range=dut2_local_outbound_range,
                )
                IPsecUtil.vpp_ipsec_add_spd_entry(
                    nodes["DUT2"],
                    spd_id,
                    p_hi,
                    IpsecSpdAction.BYPASS,
                    inbound=True,
                    proto=IPsecProto.ESP,
                    laddr_range=dut2_local_outbound_range,
                    raddr_range=dut2_remote_outbound_range,
                )

            IPsecUtil.vpp_ipsec_add_sad_entries(
                nodes["DUT2"],
                n_tunnels,
                sa_id_1,
                spi_1,
                crypto_alg,
                crypto_key,
                integ_alg,
                integ_key,
                tunnel_ip1,
                tunnel_ip2,
                tunnel_addr_incr,
            )
            IPsecUtil.vpp_ipsec_add_spd_entries(
                nodes["DUT2"],
                n_tunnels,
                spd_id,
                priority=ObjIncrement(p_lo, 0),
                action=IpsecSpdAction.PROTECT,
                inbound=True,
                sa_id=ObjIncrement(sa_id_1, 1),
                raddr_range=NetworkIncrement(ip_network(raddr_ip2)),
            )

            IPsecUtil.vpp_ipsec_add_sad_entries(
                nodes["DUT2"],
                n_tunnels,
                sa_id_2,
                spi_2,
                crypto_alg,
                crypto_key,
                integ_alg,
                integ_key,
                tunnel_ip2,
                tunnel_ip1,
                tunnel_addr_incr,
            )
            IPsecUtil.vpp_ipsec_add_spd_entries(
                nodes["DUT2"],
                n_tunnels,
                spd_id,
                priority=ObjIncrement(p_lo, 0),
                action=IpsecSpdAction.PROTECT,
                inbound=False,
                sa_id=ObjIncrement(sa_id_2, 1),
                raddr_range=NetworkIncrement(ip_network(raddr_ip1)),
            )

    @staticmethod
    def vpp_ipsec_show_all(node: dict) -> None:
        """Run "show ipsec all" debug CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, "show ipsec all")

    @staticmethod
    def show_ipsec_security_association(node: dict) -> None:
        """Show IPSec security association.

        :param node: DUT node.
        :type node: dict
        """
        cmd = "ipsec_sa_v5_dump"
        PapiSocketExecutor.dump_and_log(node, [cmd])

    @staticmethod
    def vpp_ipsec_flow_enable_rss(
        node: dict,
        proto: str = "IPSEC_ESP",
        rss_type: str = "esp",
        function: str = "default",
    ) -> int:
        """Ipsec flow enable rss action.

        :param node: DUT node.
        :param proto: The flow protocol.
        :param rss_type: RSS type.
        :param function: RSS function.
        :type node: dict
        :type proto: IPsecProto.InputType
        :type rss_type: str
        :type function: str
        :returns: flow_index.
        :rtype: int
        """
        # The proto argument does not correspond to IPsecProto.
        # The allowed values come from src/vnet/ip/protocols.def
        # and we do not have a good enum for that yet.
        # FlowUtil.FlowType and FlowUtil.FlowProto are close,
        # but not exactly the same.

        # TODO: to be fixed to use full PAPI when it is ready in VPP
        cmd = (
            f"test flow add src-ip any proto {proto} rss function"
            f" {function} rss types {rss_type}"
        )
        stdout = PapiSocketExecutor.run_cli_cmd(node, cmd)
        flow_index = stdout.split()[1]

        return flow_index

    @staticmethod
    def vpp_create_ipsec_flows_on_dut(
        node: dict, n_flows: int, rx_queues: int, spi_start: int, interface: str
    ) -> None:
        """Create mutiple ipsec flows and enable flows onto interface.

        :param node: DUT node.
        :param n_flows: Number of flows to create.
        :param rx_queues: NUmber of RX queues.
        :param spi_start: The start spi.
        :param interface: Name of the interface.

        :type node: dict
        :type n_flows: int
        :type rx_queues: int
        :type spi_start: int
        :type interface: str
        """

        for i in range(0, n_flows):
            rx_queue = i % rx_queues
            spi = spi_start + i
            flow_index = FlowUtil.vpp_create_ip4_ipsec_flow(
                node, "ESP", spi, "redirect-to-queue", value=rx_queue
            )
            FlowUtil.vpp_flow_enable(node, interface, flow_index)
