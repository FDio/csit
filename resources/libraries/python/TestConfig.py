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
        src_ip_start = ip_address(unicode(src_ip_start))
        dst_ip_start = ip_address(unicode(dst_ip_start))
        vni_start = int(vni_start)
        vxlan_if_index = InterfaceUtil.get_interface_index(node, node_vxlan_if)
        vlan_if_index = InterfaceUtil.get_interface_index(node, node_vlan_if)

        params = list()
        for vid in range(0, vxlan_count):
            if vid > 0:
                try:
                    src_ip_start += ip_step
                    dst_ip_start += ip_step
                except AddressValueError:
                    logger.warn("Can't do more iterations - IP address "
                                "limit has been reached.")
                    vxlan_count = vid
                    break
            params.append(dict(
                src_ip=src_ip_start,
                dst_ip=dst_ip_start,
                ip_len=128 if src_ip_start.version == 6 else 32,
                vni=vni_start + vid,
                vlan=vid + 1,
                history=not 1 < vid < vxlan_count))

        if vxlan_count > 10:
            commands = list()
            tmp_fn = '/tmp/create_vxlan_interfaces.config'
            for param in params:
                commands.append(
                    'sw_interface_add_del_address sw_if_index {sw_idx} '
                    '{ip}/{ip_len}\n'.format(
                        sw_idx=vxlan_if_index,
                        ip=param['src_ip'],
                        ip_len=param['ip_len']))
                commands.append(
                    'vxlan_add_del_tunnel src {srcip} dst {dstip} vni {vni}\n'\
                        .format(srcip=param['src_ip'], dstip=param['dst_ip'],
                                vni=param['vni']))
                commands.append(
                    'create_vlan_subif sw_if_index {sw_idx} vlan {vlan}\n'\
                        .format(sw_idx=vlan_if_index, vlan=param['vlan']))
            VatExecutor().write_and_execute_script(node, tmp_fn, commands)
            return vxlan_count

        add_address_args = dict(
            sw_if_index=vxlan_if_index,
            is_add=True,
            del_all=False,
            prefix=None
        )

        add_tunnel_args = dict(
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

        create_vlan_args = dict(
            sw_if_index=vlan_if_index,
            vlan_id=None)

        with PapiSocketExecutor(node) as papi_exec:
            for param in params:
                add_address_args['prefix'] = IPUtil.create_prefix_object(
                    param['src_ip'], param['ip_len'])
                add_tunnel_args['src_address'] = IPUtil.packed(param['src_ip'])
                add_tunnel_args['dst_address'] = IPUtil.packed(param['dst_ip'])
                add_tunnel_args['vni'] = param['vni']
                create_vlan_args['vlan_id'] = param['vlan']
                add_address_args['history'] = param['history']
                add_tunnel_args['history'] = param['history']
                create_vlan_args['history'] = param['history']
                papi_exec.\
                    add('sw_interface_add_del_address', **add_address_args).\
                    add('vxlan_add_del_tunnel', **add_tunnel_args).\
                    add('create_vlan_subif', **create_vlan_args)
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
        if_indexes = {if_data['interface_name']: if_data['sw_if_index']
                      for if_data in InterfaceUtil.vpp_get_interface_data(node)}
        vlan_if_name = Topology.get_interface_name(node, node_vlan_if)

        if_params = list()
        for vid in range(0, vxlan_count):
            vxlan_subif_key = Topology.add_new_port(node, 'vxlan_tunnel')
            vxlan_subif_name = 'vxlan_tunnel{vid}'.format(vid=vid)
            vlan_subif_key = Topology.add_new_port(node, 'vlan_subif')
            vlan_subif_name = '{if_name}.{vlan}'.format(
                if_name=vlan_if_name, vlan=vid + 1)
            vxlan_subif_idx = if_indexes.get(vxlan_subif_name)
            vlan_idx = if_indexes.get(vlan_subif_name)

            Topology.update_interface_sw_if_index(
                node, vxlan_subif_key, vxlan_subif_idx)
            Topology.update_interface_name(
                node, vxlan_subif_key, vxlan_subif_name)
            Topology.update_interface_sw_if_index(
                node, vlan_subif_key, vlan_idx)
            Topology.update_interface_name(
                node, vlan_subif_key, vlan_subif_name)

            history = not 1 < vid < vxlan_count
            if_params.append((vxlan_subif_idx, vlan_idx, history))

        if vxlan_count > 10:
            tmp_fn = '/tmp/put_subinterfaces_up.config'
            commands = list()
            for vxlan_subif_idx, vlan_idx, _ in if_params:
                commands.append(
                    'sw_interface_set_flags sw_if_index {sw_idx} admin-up '
                    'link-up\n'.format(sw_idx=vxlan_subif_idx))
                commands.append(
                    'sw_interface_set_flags sw_if_index {sw_idx} admin-up '
                    'link-up\n'.format(sw_idx=vlan_idx))
            VatExecutor().write_and_execute_script(node, tmp_fn, commands)
            return

        cmd = 'sw_interface_set_flags'
        flags = InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value

        with PapiSocketExecutor(node) as papi_exec:
            for vxlan_subif_idx, vlan_idx, history in if_params:
                papi_exec.add(cmd, history=history, flags=flags,
                              sw_if_index=vxlan_subif_idx)
                papi_exec.add(cmd, history=history, flags=flags,
                              sw_if_index=vlan_idx)
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
        base_args = dict(
            op_node_if_mac=Topology.get_interface_mac(op_node, op_node_if),
            ip_len=128 if dst_ip_addr_start.version == 6 else 32,
            sw_idx_vxlan=Topology.get_interface_sw_index(node, node_vxlan_if))

        params = list()
        for vid in range(0, vxlan_count):
            params.append(dict(
                dst_ip=dst_ip_addr_start + vid * ip_step,
                sw_idx_tun=Topology.get_interface_sw_index(
                    node, 'vxlan_tunnel{vid}'.format(vid=vid)),
                sw_idx_vlan=Topology.get_interface_sw_index(
                    node, 'vlan_subif{vid}'.format(vid=vid)),
                bd_id=bd_id_start + vid,
                history=not 1 < vid < vxlan_count))

        if vxlan_count > 1:
            tmp_fn = '/tmp/configure_routes_and_bridge_domains.config'
            commands = list()
            for param in params:
                commands.append(
                    'ip_neighbor_add_del sw_if_index {sw_idx} dst {ip} '
                    'mac {mac}\n'.format(
                        sw_idx=param['sw_idx_vxlan'],
                        ip=param['dst_ip'],
                        mac=base_args['op_node_if_mac']))
                commands.append(
                    'ip_route_add_del {ip}/{ip_len} count 1 via {ip} '
                    'sw_if_index {sw_idx}\n'.format(
                        ip=param['dst_ip'],
                        ip_len=base_args['ip_len'],
                        sw_idx=base_args['sw_idx_vxlan']))
                commands.append(
                    'sw_interface_set_l2_bridge sw_if_index {sw_idx} '
                    'bd_id {bd_id} shg 0 enable\n'.format(
                        sw_idx=param['sw_idx_tun'],
                        bd_id=param['bd_id']))
                commands.append(
                    'sw_interface_set_l2_bridge sw_if_index {sw_idx} '
                    'bd_id {bd_id} shg 0 enable\n'.format(
                        sw_idx=param['sw_idx_vlan'],
                        bd_id=param['bd_id']))
            VatExecutor().write_and_execute_script(node, tmp_fn, commands)
            return

        add_neighbor_args = dict(
            sw_if_index=base_args['sw_idx_vxlan'],
            flags=0,
            mac_address=base_args['op_node_if_mac'],
            ip_address='')
        add_neighbor_args = dict(
            is_add=1,
            neighbor=add_neighbor_args)

        add_route_args = IPUtil.compose_vpp_route_structure(
            node,
            str(dst_ip_addr_start),
            base_args['ip_len'],
            interface=node_vxlan_if,
            gateway=str(dst_ip_addr_start))
        add_route_args = dict(
            is_add=1,
            is_multipath=0,
            route=add_route_args)

        set_bridge_args = dict(
            rx_sw_if_index=None,
            bd_id=None,
            shg=0,
            port_type=0,
            enable=1)

        with PapiSocketExecutor(node) as papi_exec:
            for param in params:
                add_neighbor_args['neighbor']['ip_address'] = \
                    str(param['dst_ip'])
                add_neighbor_args['history'] = param['history']
                papi_exec.add('ip_neighbor_add_del', **add_neighbor_args)

                add_route_args['route']['prefix']['address']['un'] = \
                    IPUtil.union_addr(param['dst_ip'])
                add_route_args['route']['paths'][0]['nh']['address'] = \
                    IPUtil.union_addr(param['dst_ip'])
                add_route_args['rx_sw_if_index'] = param['sw_idx_tun']
                add_route_args['history'] = param['history']
                papi_exec.add('ip_route_add_del', **add_route_args)

                set_bridge_args['bd_id'] = param['bd_id']
                set_bridge_args['history'] = param['history']
                set_bridge_args['rx_sw_if_index'] = None
                papi_exec.add('sw_interface_set_l2_bridge', **set_bridge_args)

                set_bridge_args['rx_sw_if_index'] = param['sw_idx_vlan']
                papi_exec.add('sw_interface_set_l2_bridge', **set_bridge_args)
            papi_exec.get_replies()
