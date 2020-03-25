# Copyright (c) 2020 Cisco and/or its affiliates.
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
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor


class TestConfig:
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
            src_ip_start, dst_ip_start, ip_step
        )

        # update topology with VXLAN interfaces and VLAN sub-interfaces data
        # and put interfaces up
        TestConfig.vpp_put_vxlan_and_vlan_interfaces_up(
            node, vxlan_count, node_vlan_if
        )

        # configure bridge domains, ARPs and routes
        TestConfig.vpp_put_vxlan_and_vlan_interfaces_to_bridge_domain(
            node, node_vxlan_if, vxlan_count, op_node, op_node_if, dst_ip_start,
            ip_step, bd_id_start
        )

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
        src_ip_start = ip_address(src_ip_start)
        dst_ip_start = ip_address(dst_ip_start)

        if vxlan_count > 10:
            commands = list()
            for i in range(0, vxlan_count):
                try:
                    src_ip = src_ip_start + i * ip_step
                    dst_ip = dst_ip_start + i * ip_step
                except AddressValueError:
                    logger.warn(
                        u"Can't do more iterations - IP address limit "
                        u"has been reached."
                    )
                    vxlan_count = i
                    break
                commands.append(
                    f"sw_interface_add_del_address sw_if_index "
                    f"{Topology.get_interface_sw_index(node, node_vxlan_if)} "
                    f"{src_ip}/{128 if src_ip.version == 6 else 32}\n"
                )
                commands.append(
                    f"vxlan_add_del_tunnel src {src_ip} dst {dst_ip} "
                    f"vni {vni_start + i}\n"
                )
                commands.append(
                    f"create_vlan_subif sw_if_index "
                    f"{Topology.get_interface_sw_index(node, node_vlan_if)} "
                    f"vlan {i + 1}\n"
                )
            VatExecutor().write_and_execute_script(
                node, u"/tmp/create_vxlan_interfaces.config", commands
            )
            return vxlan_count

        cmd1 = u"sw_interface_add_del_address"
        args1 = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, node_vxlan_if),
            is_add=True,
            del_all=False,
            prefix=None
        )
        cmd2 = u"vxlan_add_del_tunnel"
        args2 = dict(
            is_add=True,
            instance=Constants.BITWISE_NON_ZERO,
            src_address=None,
            dst_address=None,
            mcast_sw_if_index=Constants.BITWISE_NON_ZERO,
            encap_vrf_id=0,
            decap_next_index=Constants.BITWISE_NON_ZERO,
            vni=None
        )
        cmd3 = u"create_vlan_subif"
        args3 = dict(
            sw_if_index=InterfaceUtil.get_interface_index(
                node, node_vlan_if),
            vlan_id=None
        )

        with PapiSocketExecutor(node) as papi_exec:
            for i in range(0, vxlan_count):
                try:
                    src_ip = src_ip_start + i * ip_step
                    dst_ip = dst_ip_start + i * ip_step
                except AddressValueError:
                    logger.warn(
                        u"Can't do more iterations - IP address limit "
                        u"has been reached."
                    )
                    vxlan_count = i
                    break
                args1[u"prefix"] = IPUtil.create_prefix_object(
                    src_ip, 128 if src_ip_start.version == 6 else 32
                )
                args2[u"src_address"] = IPAddress.create_ip_address_object(
                    src_ip
                )
                args2[u"dst_address"] = IPAddress.create_ip_address_object(
                    dst_ip
                )
                args2[u"vni"] = int(vni_start) + i
                args3[u"vlan_id"] = i + 1
                history = bool(not 1 < i < vxlan_count - 1)
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
        if vxlan_count > 10:
            commands = list()
            for i in range(0, vxlan_count):
                vxlan_subif_key = Topology.add_new_port(node, u"vxlan_tunnel")
                vxlan_subif_name = f"vxlan_tunnel{i}"
                founds = dict(vxlan=False, vlan=False)
                vxlan_subif_idx = None
                vlan_subif_key = Topology.add_new_port(node, u"vlan_subif")
                vlan_subif_name = \
                    f"{Topology.get_interface_name(node, node_vlan_if)}.{i + 1}"
                vlan_idx = None
                for data in if_data:
                    if_name = data[u"interface_name"]
                    if not founds[u"vxlan"] and if_name == vxlan_subif_name:
                        vxlan_subif_idx = data[u"sw_if_index"]
                        founds[u"vxlan"] = True
                    elif not founds[u"vlan"] and if_name == vlan_subif_name:
                        vlan_idx = data[u"sw_if_index"]
                        founds[u"vlan"] = True
                    if founds[u"vxlan"] and founds[u"vlan"]:
                        break
                Topology.update_interface_sw_if_index(
                    node, vxlan_subif_key, vxlan_subif_idx)
                Topology.update_interface_name(
                    node, vxlan_subif_key, vxlan_subif_name)
                commands.append(
                    f"sw_interface_set_flags sw_if_index {vxlan_subif_idx} "
                    f"admin-up link-up\n"
                )
                Topology.update_interface_sw_if_index(
                    node, vlan_subif_key, vlan_idx
                )
                Topology.update_interface_name(
                    node, vlan_subif_key, vlan_subif_name
                )
                commands.append(
                    f"sw_interface_set_flags sw_if_index {vlan_idx} admin-up "
                    f"link-up\n"
                )
            VatExecutor().write_and_execute_script(
                node, u"/tmp/put_subinterfaces_up.config", commands
            )
            return

        cmd = u"sw_interface_set_flags"
        args1 = dict(
            sw_if_index=None,
            flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
        )
        args2 = dict(
            sw_if_index=None,
            flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
        )

        with PapiSocketExecutor(node) as papi_exec:
            for i in range(0, vxlan_count):
                vxlan_subif_key = Topology.add_new_port(node, u"vxlan_tunnel")
                vxlan_subif_name = f"vxlan_tunnel{i}"
                founds = dict(vxlan=False, vlan=False)
                vxlan_subif_idx = None
                vlan_subif_key = Topology.add_new_port(node, u"vlan_subif")
                vlan_subif_name = \
                    f"{Topology.get_interface_name(node, node_vlan_if)}.{i+1}"
                vlan_idx = None
                for data in if_data:
                    if not founds[u"vxlan"] \
                            and data[u"interface_name"] == vxlan_subif_name:
                        vxlan_subif_idx = data[u"sw_if_index"]
                        founds[u"vxlan"] = True
                    elif not founds[u"vlan"] \
                            and data[u"interface_name"] == vlan_subif_name:
                        vlan_idx = data[u"sw_if_index"]
                        founds[u"vlan"] = True
                    if founds[u"vxlan"] and founds[u"vlan"]:
                        break
                Topology.update_interface_sw_if_index(
                    node, vxlan_subif_key, vxlan_subif_idx
                )
                Topology.update_interface_name(
                    node, vxlan_subif_key, vxlan_subif_name
                )
                args1[u"sw_if_index"] = vxlan_subif_idx
                Topology.update_interface_sw_if_index(
                    node, vlan_subif_key, vlan_idx
                )
                Topology.update_interface_name(
                    node, vlan_subif_key, vlan_subif_name
                )
                args2[u"sw_if_index"] = vlan_idx
                history = bool(not 1 < i < vxlan_count - 1)
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
        dst_ip_start = ip_address(dst_ip_start)

        if vxlan_count > 1:
            idx_vxlan_if = Topology.get_interface_sw_index(node, node_vxlan_if)
            commands = list()
            for i in range(0, vxlan_count):
                dst_ip = dst_ip_start + i * ip_step
                commands.append(
                    f"exec ip neighbor "
                    f"{Topology.get_interface_name(node, node_vxlan_if)} "
                    f"{dst_ip} "
                    f"{Topology.get_interface_mac(op_node, op_node_if)} static "
                    f"\n"
                )
                commands.append(
                    f"ip_route_add_del "
                    f"{dst_ip}/{128 if dst_ip.version == 6 else 32} count 1 "
                    f"via {dst_ip} sw_if_index {idx_vxlan_if}\n"
                )
                sw_idx_vxlan = Topology.get_interface_sw_index(
                    node, f"vxlan_tunnel{i + 1}"
                )
                commands.append(
                    f"sw_interface_set_l2_bridge sw_if_index {sw_idx_vxlan} "
                    f"bd_id {bd_id_start + i} shg 0 enable\n"
                )
                sw_idx_vlan = Topology.get_interface_sw_index(
                    node, f"vlan_subif{i + 1}"
                )
                commands.append(
                    f"sw_interface_set_l2_bridge sw_if_index {sw_idx_vlan} "
                    f"bd_id {bd_id_start + i} shg 0 enable\n"
                )
            VatExecutor().write_and_execute_script(
                node, u"/tmp/configure_routes_and_bridge_domains.config",
                commands
            )
            return

        cmd1 = u"ip_neighbor_add_del"
        neighbor = dict(
            sw_if_index=Topology.get_interface_sw_index(node, node_vxlan_if),
            flags=0,
            mac_address=Topology.get_interface_mac(op_node, op_node_if),
            ip_address=u""
        )
        args1 = dict(
            is_add=1,
            neighbor=neighbor
        )
        cmd2 = u"ip_route_add_del"
        kwargs = dict(
            interface=node_vxlan_if,
            gateway=str(dst_ip_start)
        )
        route = IPUtil.compose_vpp_route_structure(
            node, str(dst_ip_start),
            128 if dst_ip_start.version == 6 else 32, **kwargs
        )
        args2 = dict(
            is_add=1,
            is_multipath=0,
            route=route
        )
        cmd3 = u"sw_interface_set_l2_bridge"
        args3 = dict(
            rx_sw_if_index=None,
            bd_id=None,
            shg=0,
            port_type=0,
            enable=1
        )
        args4 = dict(
            rx_sw_if_index=None,
            bd_id=None,
            shg=0,
            port_type=0,
            enable=1
        )

        with PapiSocketExecutor(node) as papi_exec:
            for i in range(0, vxlan_count):
                args1[u"neighbor"][u"ip_address"] = \
                    str(dst_ip_start + i * ip_step)
                args2[u"route"][u"prefix"][u"address"][u"un"] = \
                    IPAddress.union_addr(dst_ip_start + i * ip_step)
                args2[u"route"][u"paths"][0][u"nh"][u"address"] = \
                    IPAddress.union_addr(dst_ip_start + i * ip_step)
                args3[u"rx_sw_if_index"] = Topology.get_interface_sw_index(
                    node, f"vxlan_tunnel{i+1}"
                )
                args3[u"bd_id"] = int(bd_id_start+i)
                args4[u"rx_sw_if_index"] = Topology.get_interface_sw_index(
                    node, f"vlan_subif{i+1}"
                )
                args4[u"bd_id"] = int(bd_id_start+i)
                history = bool(not 1 < i < vxlan_count - 1)
                papi_exec.add(cmd1, history=history, **args1). \
                    add(cmd2, history=history, **args2). \
                    add(cmd3, history=history, **args3). \
                    add(cmd3, history=history, **args4)
            papi_exec.get_replies()
