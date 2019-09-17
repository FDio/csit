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

from socket import htonl
from ipaddress import ip_address
from resources.libraries.python.topology import NodeType
from resources.libraries.python.PapiExecutor import PapiSocketExecutor

def convert_address(ip4_addr=""):
    """Convert address ip4 to ip4 in ip6 format,
       this is VPP loadbalancer specific implement.

    :param ip4_addr: ip4 address(example:"10.10.10.1").
    :type ip4_addr: str
    :returns: 128 bit address.
    :rtype: str
    :raises ValueError: If the node has an unknown node type.
    """
    if ip4_addr == "":
        raise ValueError("Error: ip4_addr is NULL")
    addr4 = list(ip_address(unicode(ip4_addr)).packed)
    addr6 = list(ip_address(unicode("::0")).packed)
    addr6[12] = addr4[0]
    addr6[13] = addr4[1]
    addr6[14] = addr4[2]
    addr6[15] = addr4[3]

    return ''.join(addr6)

class LoadBalancerUtil(object):
    """Basic Loadbalancer parameter configuration"""

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
        if node['type'] == NodeType.DUT:
            ip4_src_addr = ip_address(unicode(kwargs.pop('ip4_src_addr', \
                    '255.255.255.255')))
            ip6_src_addr = ip_address(unicode(kwargs.pop('ip6_src_addr', \
                    'ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff')))
            flow_timeout = kwargs.pop('flow_timeout', 40)
            sticky_buckets_per_core = htonl(kwargs.pop('buckets_per_core', \
                    1024))

            cmd = 'lb_conf'
            err_msg = 'Failed to set lb conf on host {host}'.format(
                host=node['host'])

            args = dict(ip4_src_address=str(ip4_src_addr), \
                    ip6_src_address=str(ip6_src_addr),\
                    sticky_buckets_per_core=sticky_buckets_per_core,\
                    flow_timeout=flow_timeout)

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'
                             .format(node['host'], node['type']))

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
        if node['type'] == NodeType.DUT:
            vip_addr = kwargs.pop('vip_addr', '0.0.0.0')
            protocol = kwargs.pop('protocol', 255)
            port = kwargs.pop('port', 0)
            encap = kwargs.pop('encap', 0)
            dscp = kwargs.pop('dscp', 0)
            srv_type = kwargs.pop('srv_type', 0)
            target_port = kwargs.pop('target_port', 0)
            node_port = kwargs.pop('node_port', 0)
            new_len = kwargs.pop('new_len', 1024)
            is_del = kwargs.pop('is_del', 0)

            cmd = 'lb_add_del_vip'
            err_msg = 'Failed to add vip on host {host}'.format(
                host=node['host'])

            vip_addr = convert_address(str(vip_addr))
            args = dict(pfx={'len': 128, \
                    'address': {'un': {'ip6': vip_addr}, 'af': 1}}, \
                    protocol=protocol, \
                    port=port, \
                    encap=int(encap),\
                    dscp=dscp, \
                    type=srv_type, \
                    target_port=target_port, \
                    node_port=node_port, \
                    new_flows_table_length=int(new_len), \
                    is_del=is_del)

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'
                             .format(node['host'], node['type']))

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
        if node['type'] == NodeType.DUT:
            cmd = 'lb_add_del_as'
            err_msg = 'Failed to add lb as on host {host}'.format(
                host=node['host'])

            vip_addr = kwargs.pop('vip_addr', '0.0.0.0')
            protocol = kwargs.pop('protocol', 255)
            port = kwargs.pop('port', 0)
            as_addr = kwargs.pop('as_addr', '0.0.0.0')
            is_del = kwargs.pop('is_del', 0)
            is_flush = kwargs.pop('is_flush', 0)

            vip_addr = convert_address(str(vip_addr))
            as_addr = convert_address(str(as_addr))
            args = dict(pfx={'len': 128, \
                    'address': {'un': {'ip6': vip_addr}, 'af': 1}},\
                    protocol=protocol,\
                    port=port,\
                    as_address={'un': {'ip6': as_addr}, 'af': 1},\
                    is_del=is_del,\
                    is_flush=is_flush)

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError('Node {} has unknown NodeType: "{}"'
                             .format(node['host'], node['type']))
