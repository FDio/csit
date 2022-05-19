# Copyright (c) 2022 Intel and/or its affiliates.
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

"""WireGuard utilities library."""

from ipaddress import ip_address
from cryptography.hazmat.primitives.serialization import Encoding, \
    PrivateFormat, PublicFormat, NoEncryption
from cryptography.hazmat.primitives.asymmetric.x25519 import \
    X25519PrivateKey

from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor

class WireGuardUtil:
    """This class defines the methods to set WireGuard."""

    @staticmethod
    def public_key_bytes(k):
        """Return the public key as byte.

        :param k: Generated public key.
        :type: x25519._X25519PublicKey object
        :returns: Public key.
        :rtype: bytes
        """
        return k.public_bytes(Encoding.Raw, PublicFormat.Raw)

    @staticmethod
    def private_key_bytes(k):
        """Return the private key as byte.

        :param k: Generated private key.
        :type: x25519._X25519PrivateKey object
        :returns: Private key.
        :rtype: bytes
        """
        return k.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())

    @staticmethod
    def generate_wireguard_privatekey_and_pubkey():
        """Generate a pair of WireGuard Private key and Public key.

        :returns: A pair of privatekey and publickey
        :rtype: x25519._X25519PublicKey object
        """
        privatekey = X25519PrivateKey.generate()
        pubkey = privatekey.public_key()
        private_key = WireGuardUtil.private_key_bytes(privatekey)
        public_key = WireGuardUtil.public_key_bytes(pubkey)
        return private_key, public_key

    @staticmethod
    def vpp_wireguard_create_interface(
            node, listen_port, wg_src, private_key):
        """Create WireGuard interface.

        :param node: VPP node to add config on.
        :param listen_port: WireGuard interface listen port.
        :param wg_src: WireGuard srouce IPv4.
        :param private_key: WireGuard interface private key
        :type node: dict
        :type listen_port: int
        :type wg_src: str
        :type private_key: bytes
        :returns: Wireguard interface sw_if_index.
        :rtype: int
        """
        cmd = u"wireguard_interface_create"
        err_msg = f"Failed to create wireguard interface" \
            f"on host {node[u'host']}"
        src_ip = ip_address(wg_src)
        args = dict(
            interface=dict(
                port=int(listen_port),
                src_ip=src_ip,
                private_key=private_key,
                generate_key=False
            )
        )
        with PapiSocketExecutor(node) as papi_exec:
            wg_sw_index = \
                papi_exec.add(cmd, **args).get_sw_if_index(err_msg)
            return wg_sw_index

    @staticmethod
    def vpp_wireguard_add_peer(
            node, interface, peer_pubkey, endpoint_ip,
            allowed_ips, n_allowed_ips, dst_port, keepalive_time):
        """Add a peer for WireGuard interface.

        :param node: VPP node to add config on.
        :param interface: WireGuard interface sw_if_index.
        :param peer_pubkey: Public key of wireguard interface peer.
        :param endpoint_ip: Peer source IPv4.
        :param allowed_ips: WireGuard interface allowed ips list.
        :param n_allowed_ips: Number of allowed ips.
        :param dst_port: WireGuard destination port.
        :param keepaliva time: WireGuard persistent keepalive time.
        :type node: dict
        :type interface: int
        :type peer_pubkey: bytes
        :type endpoint_ip: str
        :type allowed_ips: list
        :type n_allowed_ips: int
        :type dst_port: int
        :type keepalive_time: int
        """
        endpoint_ip = ip_address(endpoint_ip)
        wg_name = InterfaceUtil.vpp_get_interface_name(
            node, sw_if_index=interface
        )
        cmd = u"wireguard_peer_add"
        err_msg = f"Failed to add wireguard interface" \
            f"{wg_name} peer on host {node[u'host']}"
        args = dict(
            peer=dict(
                public_key=peer_pubkey,
                port=int(dst_port),
                endpoint=endpoint_ip,
                sw_if_index=interface,
                persistent_keepalive=int(keepalive_time),
                n_allowed_ips=int(n_allowed_ips),
                allowed_ips=allowed_ips
            )
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def _wireguard_create_tunnel_interface_on_dut(
            node, if1_key, if2_mac_addr, src_ip, peer_endpoint_ip,
            peer_allowed_ips, peer_n_allowed_ips, dut_wg_ip, port,
            keepalive_time, dut_private_key, peer_pubkey):
        """Create WireGuard tunnel interface on one DUT node using PAPI.

        :param node: VPP node as DUT to create tunnel interface.
        :param if1_key: VPP node as DUT interface key from topology file.
        :param if2_mac_addr: Vpp node on the other end/ TG node
            (in case of 2-node topology) interface mac address.
        :param src_ip: WireGuard source IPv4 address.
        :param peer_endpoint_ip: Peer source IPv4 address.
        :param peer_allowed_ips: WireGuard peer interface allowed ip list.
        :param peer_n_allowed ips: Number of peer allowed ips.
        :param dut_wg_ip: WireGuard interface ip address on DUT.
        :param port: WireGuard interface listen port or
            Peer interface destination port.
        :param keepalive_time: WireGuard persistent keepalive time.
        :param dut_private_key: WireGuard interface private key of DUT.
        :param peer_pubkey: WireGuard Peer interface public key.
        :type nodes: dict
        :type if1_key: str
        :type if2_mac_addr: str
        :type src_ip: src
        :type peer_endpoint_ip: src
        :type peer_allowed_ips: list
        :type peer_n_allowed_ips: int
        :type dut_wg_ip: src
        :type port: int
        :type keepalive_time: int
        :type dut_private_key: bytes
        :type peer_pubkey: bytes
        """
        #Set IP address on VPP node interface
        IPUtil.vpp_interface_set_ip_address(node, if1_key, src_ip, 24)
        IPUtil.vpp_add_ip_neighbor(
            node, if1_key, peer_endpoint_ip, if2_mac_addr
        )
        #Create Wireguard interface on DUT
        dut_wg_sw_index = WireGuardUtil.vpp_wireguard_create_interface(
            node, port, src_ip, dut_private_key
        )
        #Add wireguard peer
        WireGuardUtil.vpp_wireguard_add_peer(
            node, dut_wg_sw_index, peer_pubkey, peer_endpoint_ip,
            peer_allowed_ips, peer_n_allowed_ips, port, keepalive_time
        )
        #Set wireguard interface up
        InterfaceUtil.set_interface_state(node, dut_wg_sw_index, state=u'up')
        #Set wireguard interface IP address
        cmd = u'sw_interface_add_del_address'
        args = dict(
            sw_if_index=dut_wg_sw_index,
            is_add=True,
            del_all=False,
            prefix=IPUtil.create_prefix_object(ip_address(dut_wg_ip), 24)
        )
        err_msg = f"Failed to set IP address on wg interface " \
            f"on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
        #Set route on VPP node as DUT wg interface
        for allowed_ip in peer_allowed_ips:
            traffic_addr = ip_address(
                allowed_ip[u'address'][u'un'][u'ip4']
            )
            prefix_len = allowed_ip[u'len']
            IPUtil.vpp_route_add(
                node, traffic_addr, prefix_len,
                gateway=(traffic_addr+1).compressed,
                interface=dut_wg_sw_index
            )

    @staticmethod
    def vpp_wireguard_create_tunnel_interface_on_duts(
            nodes, if1_key, if2_key, if1_ip_addr, if2_ip_addr,
            if1_mac_addr, if2_mac_addr, wg_if1_ip_addr, wg_if2_ip_addr,
            n_allowed_ips, port, keepalive_time, raddr_ip1, raddr_ip2):
        """Create WireGuard tunnel interfaces between two VPP nodes.

        :param nodes: VPP nodes to create tunnel interfaces.
        :param if1_key: VPP node 1 interface key from topology file.
        :param if2_key: VPP node 2 / TG node (in case of 2-node topology)
        :param if1_ip_addr: VPP node 1 interface IPv4/IPv6 address.
        :param if2_ip_addr: VPP node 2 / TG node
            (in case of 2-node topology) interface IPv4/IPv6 address.
        :param if1_mac_addr: VPP node1 interface mac address.
        :param if2_mac_addr: VPP node2 interface mac address.
        :param wg_if1_ip_addr: VPP node 1 WireGuard interface IPv4 address.
        :param wg_if2_ip_addr: VPP node 2 WireGuard interface IPv4 address.
        :param allowed_ips: WireGuard interface allowed ip list.
        :param n_allowed_ips: Number of allowed ips.
        :param port: WireGuard interface listen port or
            Peer interface destination port.
        :param keepalive_time: WireGuard persistent keepalive time.
        :param raddr_ip1: Policy selector remote IPv4/IPv6 start address
            for the first tunnel in direction node1->node2.
        :param raddr_ip2: Policy selector remote IPv4/IPv6 start address
            for the first tunnel in direction node2->node1.
        :type nodes: dict
        :type if1_key: str
        :type if2_key: str
        :type if1_ip_addr: str
        :type if2_ip_addr: str
        :type if1_mac_addr: str
        :type if2_mac_addr: str
        :type wg_if1_ip_addr: str
        :type wg_if2_ip_addr: str
        :type allowed_ips: str
        :type n_allowed_ips: int
        :type port: int
        :type keepalive_time: int
        :type raddr_ip1: str
        :type raddr_ip2: str
        """
        dut1_privatekey, dut1_pubkey = \
            WireGuardUtil.generate_wireguard_privatekey_and_pubkey()
        dut2_privatekey, dut2_pubkey = \
            WireGuardUtil.generate_wireguard_privatekey_and_pubkey()
        raddr_ip1 = ip_address(raddr_ip1)
        raddr_ip2 = ip_address(raddr_ip2)
        dut1_allowed_ips = \
            [IPUtil.create_prefix_object(raddr_ip2, 24),]
        dut2_allowed_ips = \
            [IPUtil.create_prefix_object(raddr_ip1, 24),]
        #Configure WireGuard interface on DUT1
        WireGuardUtil._wireguard_create_tunnel_interface_on_dut(
            nodes[u'DUT1'], if1_key, if2_mac_addr, if1_ip_addr, if2_ip_addr,
            dut1_allowed_ips, n_allowed_ips, wg_if1_ip_addr, port,
            keepalive_time, dut1_privatekey, dut2_pubkey
        )
        #Configure WireGuard interface on DUT2
        WireGuardUtil._wireguard_create_tunnel_interface_on_dut(
            nodes[u'DUT2'], if2_key, if1_mac_addr, if2_ip_addr, if1_ip_addr,
            dut2_allowed_ips, n_allowed_ips, wg_if2_ip_addr, port,
            keepalive_time, dut2_privatekey, dut1_pubkey
        )
