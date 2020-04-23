# Copyright (c) 2019 Intel and/or its affiliates.
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

"""Loadbalancer util library."""

from ipaddress import ip_address
from socket import htonl

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor


class LoadBalancerUtil:
    """Basic Loadbalancer parameter configuration."""

    @staticmethod
    def vpp_lb_conf(node, **kwargs):
        """Config global parameters for loadbalancer.

        :param node: Node where the interface is.
        :param kwargs: Optional key-value arguments:

            ip4_src_addr: IPv4 address to be used as source for IPv4 traffic.
                          (str)
            ip6_src_addr: IPv6 address to be used as source for IPv6 traffic.
                          (str)
            flow_timeout: Time in seconds after which, if no packet is received
                          for a given flow, the flow is removed from the
                          established flow table. (int)
            buckets_per_core: Number of buckets *per worker thread* in the
                              established flow table (int)

        :type node: dict
        :type kwargs: dict
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """
        if node[u"type"] == NodeType.DUT:
            ip4_src_addr = ip_address(
                kwargs.pop(u"ip4_src_addr", u"255.255.255.255")
            )
            ip6_src_addr = ip_address(
                kwargs.pop(
                    u"ip6_src_addr", u"ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff"
                )
            )
            flow_timeout = kwargs.pop(u"flow_timeout", 40)
            sticky_buckets_per_core = kwargs.pop(u"buckets_per_core", 1024)

            cmd = u"lb_conf"
            err_msg = f"Failed to set lb conf on host {node[u'host']}"
            args = dict(
                ip4_src_address=str(ip4_src_addr),
                ip6_src_address=str(ip6_src_addr),
                sticky_buckets_per_core=sticky_buckets_per_core,
                flow_timeout=flow_timeout
            )

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_lb_add_del_vip(node, **kwargs):
        """Config vip for loadbalancer.

        :param node: Node where the interface is.
        :param kwargs: Optional key-value arguments:

            vip_addr: IPv4 address to be used as source for IPv4 traffic. (str)
            protocol: tcp or udp. (int)
            port: destination port. (int)
            encap: encap is ip4 GRE(0) or ip6 (1GRE) or L3DSR(2) or NAT4(3) or
                   NAT6(4). (int)
            dscp: dscp bit corresponding to VIP
            type: service type
            target_port: Pod's port corresponding to specific service
            node_port: Node's port
            new_len: Size of the new connections flow table used
                     for this VIP
            is_del: 1 if the VIP should be removed otherwise 0.

        :type node: dict
        :type kwargs: dict
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """
        if node[u"type"] == NodeType.DUT:
            vip_addr = kwargs.pop(u"vip_addr", "0.0.0.0")
            protocol = kwargs.pop(u"protocol", 255)
            port = kwargs.pop(u"port", 0)
            encap = kwargs.pop(u"encap", 0)
            dscp = kwargs.pop(u"dscp", 0)
            srv_type = kwargs.pop(u"srv_type", 0)
            target_port = kwargs.pop(u"target_port", 0)
            node_port = kwargs.pop(u"node_port", 0)
            new_len = kwargs.pop(u"new_len", 1024)
            is_del = kwargs.pop(u"is_del", 0)

            cmd = u"lb_add_del_vip"
            err_msg = f"Failed to add vip on host {node[u'host']}"

            vip_addr = ip_address(vip_addr).packed
            args = dict(
                pfx={
                    u"len": 128,
                    u"address": {u"un": {u"ip4": vip_addr}, u"af": 0}
                },
                protocol=protocol,
                port=port,
                encap=htonl(encap),
                dscp=dscp,
                type=srv_type,
                target_port=target_port,
                node_port=node_port,
                new_flows_table_length=int(new_len),
                is_del=is_del
            )

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_lb_add_del_as(node, **kwargs):
        """Config AS for Loadbalancer.

        :param node: Node where the interface is.
        :param kwargs: Optional key-value arguments:

            vip_addr: IPv4 address to be used as source for IPv4 traffic. (str)
            protocol: tcp or udp. (int)
            port: destination port. (int)
            as_addr: The application server address. (str)
            is_del: 1 if the VIP should be removed otherwise 0. (int)
            is_flush: 1 if the sessions related to this AS should be flushed
                      otherwise 0. (int)

        :type node: dict
        :type kwargs: dict
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """
        if node[u"type"] == NodeType.DUT:
            cmd = u"lb_add_del_as"
            err_msg = f"Failed to add lb as on host {node[u'host']}"

            vip_addr = kwargs.pop(u"vip_addr", "0.0.0.0")
            protocol = kwargs.pop(u"protocol", 255)
            port = kwargs.pop(u"port", 0)
            as_addr = kwargs.pop(u"as_addr", u"0.0.0.0")
            is_del = kwargs.pop(u"is_del", 0)
            is_flush = kwargs.pop(u"is_flush", 0)

            vip_addr = ip_address(vip_addr).packed
            as_addr = ip_address(as_addr).packed

            args = dict(
                pfx={
                    u"len": 128,
                    u"address": {u"un": {u"ip4": vip_addr}, u"af": 0}
                },
                protocol=protocol,
                port=port,
                as_address={u"un": {u"ip4": as_addr}, u"af": 0},
                is_del=is_del,
                is_flush=is_flush
            )

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_lb_add_del_intf_nat4(node, **kwargs):
        """Enable/disable NAT4 feature on the interface.

        :param node: Node where the interface is.
        :param kwargs: Optional key-value arguments:

            is_add: true if add, false if delete. (bool)
            interface: software index of the interface. (int)

        :type node: dict
        :type kwargs: dict
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """
        if node[u"type"] == NodeType.DUT:
            cmd = u"lb_add_del_intf_nat4"
            err_msg = f"Failed to add interface nat4 on host {node[u'host']}"

            is_add = kwargs.pop(u"is_add", True)
            interface = kwargs.pop(u"interface", 0)
            sw_if_index = Topology.get_interface_sw_index(node, interface)
            args = dict(
                is_add=is_add,
                sw_if_index=sw_if_index
            )

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )
