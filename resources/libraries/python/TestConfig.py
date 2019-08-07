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

"""Special test configurations library."""

from ipaddress import ip_address, AddressValueError
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil, \
    InterfaceStatusFlags
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor


class TestConfig(object):
    """Contains special test configurations implemented in python for faster
    execution."""

    @staticmethod
    def vpp_create_multiple_vxlan_ipv4_tunnels(
            node, node_vxlan_if, node_vlan_if, op_node, op_node_if,
            n_tunnels, vni_start, src_ip_start, dst_ip_start, ip_step,
            bd_id_start):
        """Create multiple VXLAN tunnel interfaces and VLAN sub-interfaces on
        VPP node.

        Put each pair of VXLAN tunnel interface and VLAN sub-interface to
        separate bridge-domain.

        :param node: VPP node to create VXLAN tunnel interfaces.
        :param node_vxlan_if: VPP node interface key to create VXLAN tunnel
            interfaces.
        :param node_vlan_if: VPP node interface key to create VLAN
            sub-interface.
        :param op_node: Opposite VPP node for VXLAN tunnel interfaces.
        :param op_node_if: Opposite VPP node interface key for VXLAN tunnel
            interfaces.
        :param n_tunnels: Number of tunnel interfaces to create.
        :param vni_start: VNI start ID.
        :param src_ip_start: VXLAN tunnel source IP address start.
        :param dst_ip_start: VXLAN tunnel destination IP address start.
        :param ip_step: IP address incremental step.
        :param bd_id_start: Bridge-domain ID start.
        :type node: dict
        :type node_vxlan_if: str
        :type node_vlan_if: str
        :type op_node: dict
        :type op_node_if: str
        :type n_tunnels: int
        :type vni_start: int
        :type src_ip_start: str
        :type dst_ip_start: str
        :type ip_step: int
        :type bd_id_start: int
        """
        # configure IPs, create VXLAN interfaces and VLAN sub-interfaces
        vxlan_count = TestConfig.vpp_create_vxlan_and_vlan_interfaces(
            node, node_vxlan_if, node_vlan_if, n_tunnels, vni_start,
            src_ip_start, dst_ip_start, ip_step)

        # update topology with VXLAN interfaces and VLAN sub-interfaces data
        # and put interfaces up
        TestConfig.vpp_put_vxlan_and_vlan_interfaces_up(
            node, vxlan_count, node_vlan_if)

        # configure bridge domains, ARPs and routes
        TestConfig.vpp_put_vxlan_and_vlan_interfaces_to_bridge_domain(
            node, node_vxlan_if, vxlan_count, op_node, op_node_if, dst_ip_start,
            ip_step, bd_id_start)

    @staticmethod
    def vpp_create_vxlan_and_vlan_interfaces(
            node, node_vxlan_if, node_vlan_if, vxlan_count, vni_start,
            src_ip_start, dst_ip_start, ip_step):
        """
        Configure IPs, create VXLAN interfaces and VLAN sub-interfaces on VPP
        node.

        :param node: VPP node.
        :param node_vxlan_if: VPP node interface key to create VXLAN tunnel
            interfaces.
        :param node_vlan_if: VPP node interface key to create VLAN
            sub-interface.
        :param vxlan_count: Number of tunnel interfaces to create.
        :param vni_start: VNI start ID.
        :param src_ip_start: VXLAN tunnel source IP address start.
        :param dst_ip_start: VXLAN tunnel destination IP address start.
        :param ip_step: IP address incremental step.
        :type node: dict
        :type node_vxlan_if: str
        :type node_vlan_if: str
        :type vxlan_count: int
        :type vni_start: int
        :type src_ip_start: str
        :type dst_ip_start: str
        :type ip_step: int
        :returns: Number of created VXLAN interfaces.
        :rtype: int
        """
        src_ip_addr_start = ip_address(unicode(src_ip_start))
        dst_ip_addr_start = ip_address(unicode(dst_ip_start))

        if vxlan_count > 10:
            commands = list()
            tmp_fn = '/tmp/create_vxlan_interfaces.config'
            for i in xrange(0, vxlan_count):
                try:
                    src_ip = src_ip_addr_start + i * ip_step
                    dst_ip = dst_ip_addr_start + i * ip_step
                except AddressValueError:
                    logger.warn("Can't do more iterations - IP address limit "
                                "has been reached.")
                    vxlan_count = i
                    break
                commands.append(
                    'sw_interface_add_del_address sw_if_index {sw_idx} '
                    '{ip}/{ip_len}\n'.format(
                        sw_idx=Topology.get_interface_sw_index(
                            node, node_vxlan_if),
                        ip=src_ip,
                        ip_len=128 if src_ip.version == 6 else 32))
                commands.append(
                    'vxlan_add_del_tunnel src {srcip} dst {dstip} vni {vni}\n'\
                        .format(srcip=src_ip, dstip=dst_ip,
                                vni=vni_start + i))
                commands.append(
                    'create_vlan_subif sw_if_index {sw_idx} vlan {vlan}\n'\
                        .format(sw_idx=Topology.get_interface_sw_index(
                            node, node_vlan_if), vlan=i + 1))
            VatExecutor().write_and_execute_script(node, tmp_fn, commands)
            return vxlan_count

        cmd1 = 'sw_interface_add_del_address'
        args1 = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, node_vxlan_if),
            is_add=True,
            del_all=False,
            prefix=None
        )
        cmd2 = 'vxlan_add_del_tunnel'
        args2 = dict(
            is_add=1,
            is_ipv6=0,
            instance=Constants.BITWISE_NON_ZERO,
            src_address=None,
            dst_address=None,
            mcast_sw_if_index=Constants.BITWISE_NON_ZERO,
            encap_vrf_id=0,
            decap_next_index=Constants.BITWISE_NON_ZERO,
            vni=None
        )
        cmd3 = 'create_vlan_subif'
        args3 = dict(
            sw_if_index=InterfaceUtil.get_interface_index(
                node, node_vlan_if),
            vlan_id=None
        )

        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(0, vxlan_count):
                try:
                    src_ip = src_ip_addr_start + i * ip_step
                    dst_ip = dst_ip_addr_start + i * ip_step
                except AddressValueError:
                    logger.warn("Can't do more iterations - IP address limit "
                                "has been reached.")
                    vxlan_count = i
                    break
                args1['prefix'] = IPUtil.create_prefix_object(
                    src_ip, 128 if src_ip_addr_start.version == 6 else 32)
                args2['src_address'] = getattr(src_ip, 'packed')
                args2['dst_address'] = getattr(dst_ip, 'packed')
                args2['vni'] = int(vni_start) + i
                args3['vlan_id'] = i + 1
                history = False if 1 < i < vxlan_count else True
                papi_exec.add(cmd1, history=history, **args1).\
                    add(cmd2, history=history, **args2).\
                    add(cmd3, history=history, **args3)
            papi_exec.get_replies()

        return vxlan_count

    @staticmethod
    def vpp_put_vxlan_and_vlan_interfaces_up(node, vxlan_count, node_vlan_if):
        """
        Update topology with VXLAN interfaces and VLAN sub-interfaces data
        and put interfaces up.

        :param node: VPP node.
        :param vxlan_count: Number of tunnel interfaces.
        :param node_vlan_if: VPP node interface key where VLAN sub-interfaces
            have been created.
        :type node: dict
        :type vxlan_count: int
        :type node_vlan_if: str
        """
        if_data = InterfaceUtil.vpp_get_interface_data(node)
        vlan_if_name = Topology.get_interface_name(node, node_vlan_if)

        if vxlan_count > 10:
            tmp_fn = '/tmp/put_subinterfaces_up.config'
            commands = list()
            for i in xrange(0, vxlan_count):
                vxlan_subif_key = Topology.add_new_port(node, 'vxlan_tunnel')
                vxlan_subif_name = 'vxlan_tunnel{nr}'.format(nr=i)
                vxlan_found = False
                vxlan_subif_idx = None
                vlan_subif_key = Topology.add_new_port(node, 'vlan_subif')
                vlan_subif_name = '{if_name}.{vlan}'.format(
                    if_name=vlan_if_name, vlan=i + 1)
                vlan_found = False
                vlan_idx = None
                for data in if_data:
                    if_name = data['interface_name']
                    if not vxlan_found and if_name == vxlan_subif_name:
                        vxlan_subif_idx = data['sw_if_index']
                        vxlan_found = True
                    elif not vlan_found and if_name == vlan_subif_name:
                        vlan_idx = data['sw_if_index']
                        vlan_found = True
                    if vxlan_found and vlan_found:
                        break
                Topology.update_interface_sw_if_index(
                    node, vxlan_subif_key, vxlan_subif_idx)
                Topology.update_interface_name(
                    node, vxlan_subif_key, vxlan_subif_name)
                commands.append(
                    'sw_interface_set_flags sw_if_index {sw_idx} admin-up '
                    'link-up\n'.format(sw_idx=vxlan_subif_idx))
                Topology.update_interface_sw_if_index(
                    node, vlan_subif_key, vlan_idx)
                Topology.update_interface_name(
                    node, vlan_subif_key, vlan_subif_name)
                commands.append(
                    'sw_interface_set_flags sw_if_index {sw_idx} admin-up '
                    'link-up\n'.format(sw_idx=vlan_idx))
            VatExecutor().write_and_execute_script(node, tmp_fn, commands)
            return

        cmd = 'sw_interface_set_flags'
        args1 = dict(
            sw_if_index=None,
            flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
        )
        args2 = dict(
            sw_if_index=None,
            flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
        )

        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(0, vxlan_count):
                vxlan_subif_key = Topology.add_new_port(node, 'vxlan_tunnel')
                vxlan_subif_name = 'vxlan_tunnel{nr}'.format(nr=i)
                vxlan_found = False
                vxlan_subif_idx = None
                vlan_subif_key = Topology.add_new_port(node, 'vlan_subif')
                vlan_subif_name = '{if_name}.{vlan}'.format(
                    if_name=vlan_if_name, vlan=i+1)
                vlan_found = False
                vlan_idx = None
                for data in if_data:
                    if not vxlan_found \
                            and data['interface_name'] == vxlan_subif_name:
                        vxlan_subif_idx = data['sw_if_index']
                        vxlan_found = True
                    elif not vlan_found \
                            and data['interface_name'] == vlan_subif_name:
                        vlan_idx = data['sw_if_index']
                        vlan_found = True
                    if vxlan_found and vlan_found:
                        break
                Topology.update_interface_sw_if_index(
                    node, vxlan_subif_key, vxlan_subif_idx)
                Topology.update_interface_name(
                    node, vxlan_subif_key, vxlan_subif_name)
                args1['sw_if_index'] = vxlan_subif_idx
                Topology.update_interface_sw_if_index(
                    node, vlan_subif_key, vlan_idx)
                Topology.update_interface_name(
                    node, vlan_subif_key, vlan_subif_name)
                args2['sw_if_index'] = vlan_idx
                history = False if 1 < i < vxlan_count else True
                papi_exec.add(cmd, history=history, **args1). \
                    add(cmd, history=history, **args2)
                papi_exec.add(cmd, **args1).add(cmd, **args2)
            papi_exec.get_replies()

    @staticmethod
    def vpp_put_vxlan_and_vlan_interfaces_to_bridge_domain(
            node, node_vxlan_if, vxlan_count, op_node, op_node_if, dst_ip_start,
            ip_step, bd_id_start):
        """
        Configure ARPs and routes for VXLAN interfaces and put each pair of
        VXLAN tunnel interface and VLAN sub-interface to separate bridge-domain.

        :param node: VPP node.
        :param node_vxlan_if: VPP node interface key where VXLAN tunnel
            interfaces have been created.
        :param vxlan_count: Number of tunnel interfaces.
        :param op_node: Opposite VPP node for VXLAN tunnel interfaces.
        :param op_node_if: Opposite VPP node interface key for VXLAN tunnel
            interfaces.
        :param dst_ip_start: VXLAN tunnel destination IP address start.
        :param ip_step: IP address incremental step.
        :param bd_id_start: Bridge-domain ID start.
        :type node: dict
        :type node_vxlan_if: str
        :type vxlan_count: int
        :type op_node: dict
        :type op_node_if:
        :type dst_ip_start: str
        :type ip_step: int
        :type bd_id_start: int
        """
        dst_ip_addr_start = ip_address(unicode(dst_ip_start))

        if vxlan_count > 1:
            sw_idx_vxlan = Topology.get_interface_sw_index(node, node_vxlan_if)
            tmp_fn = '/tmp/configure_routes_and_bridge_domains.config'
            commands = list()
            for i in xrange(0, vxlan_count):
                dst_ip = dst_ip_addr_start + i * ip_step
                commands.append(
                    'ip_neighbor_add_del sw_if_index {sw_idx} dst {ip} '
                    'mac {mac}\n'.format(
                        sw_idx=sw_idx_vxlan,
                        ip=dst_ip,
                        mac=Topology.get_interface_mac(op_node, op_node_if)))
                commands.append(
                    'ip_route_add_del {ip}/{ip_len} count 1 via {ip} '
                    'sw_if_index {sw_idx}\n'.format(
                        ip=dst_ip,
                        ip_len=128 if dst_ip.version == 6 else 32,
                        sw_idx=sw_idx_vxlan))
                commands.append(
                    'sw_interface_set_l2_bridge sw_if_index {sw_idx} '
                    'bd_id {bd_id} shg 0 enable\n'.format(
                        sw_idx=Topology.get_interface_sw_index(
                            node, 'vxlan_tunnel{nr}'.format(nr=i + 1)),
                        bd_id=bd_id_start + i))
                commands.append(
                    'sw_interface_set_l2_bridge sw_if_index {sw_idx} '
                    'bd_id {bd_id} shg 0 enable\n'.format(
                        sw_idx=Topology.get_interface_sw_index(
                            node, 'vlan_subif{nr}'.format(nr=i + 1)),
                        bd_id=bd_id_start + i))
            VatExecutor().write_and_execute_script(node, tmp_fn, commands)
            return

        cmd1 = 'ip_neighbor_add_del'
        neighbor = dict(
            sw_if_index=Topology.get_interface_sw_index(node, node_vxlan_if),
            flags=0,
            mac_address=Topology.get_interface_mac(op_node, op_node_if),
            ip_address='')
        args1 = dict(
            is_add=1,
            neighbor=neighbor)
        cmd2 = 'ip_route_add_del'
        kwargs = dict(
            interface=node_vxlan_if,
            gateway=str(dst_ip_addr_start))
        route = IPUtil.compose_vpp_route_structure(
            node,
            str(dst_ip_addr_start),
            128 if dst_ip_addr_start.version == 6 else 32,
            **kwargs)
        args2 = dict(
            is_add=1,
            is_multipath=0,
            route=route)
        cmd3 = 'sw_interface_set_l2_bridge'
        args3 = dict(
            rx_sw_if_index=None,
            bd_id=None,
            shg=0,
            port_type=0,
            enable=1)
        args4 = dict(
            rx_sw_if_index=None,
            bd_id=None,
            shg=0,
            port_type=0,
            enable=1)

        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(0, vxlan_count):
                dst_ip = dst_ip_addr_start + i * ip_step
                args1['neighbor']['ip_address'] = str(dst_ip)
                args2['route']['prefix']['address']['un'] = \
                    IPUtil.union_addr(dst_ip)
                args2['route']['paths'][0]['nh']['address'] = \
                    IPUtil.union_addr(dst_ip)
                args3['rx_sw_if_index'] = Topology.get_interface_sw_index(
                    node, 'vxlan_tunnel{nr}'.format(nr=i+1))
                args3['bd_id'] = int(bd_id_start+i)
                args4['rx_sw_if_index'] = Topology.get_interface_sw_index(
                    node, 'vlan_subif{nr}'.format(nr=i+1))
                args4['bd_id'] = int(bd_id_start+i)
                history = False if 1 < i < vxlan_count else True
                papi_exec.add(cmd1, history=history, **args1). \
                    add(cmd2, history=history, **args2). \
                    add(cmd3, history=history, **args3). \
                    add(cmd3, history=history, **args4)
            papi_exec.get_replies()
