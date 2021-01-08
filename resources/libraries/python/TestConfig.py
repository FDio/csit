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

"""Special test configurations library.

TODO: Add support for remote_vpp_socket optional argument.
"""

from ipaddress import ip_address

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil, \
    InterfaceStatusFlags
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


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
        err_msg = u"Error creating vlan/vxlan interfaces."

        # TODO: Bring back the code to detect IP address overflows
        #       which alse decreases vxlan_count.

        with PapiSocketExecutor(node) as papi_exec:
            cmd = u"sw_interface_add_del_address"
            args = dict(
                sw_if_index=InterfaceUtil.get_interface_index(
                    node, node_vxlan_if
                ),
                is_add=True,
                del_all=False,
                prefix=None
            )
            def gen_address():
                for count in range(vxlan_count):
                    src_ip = src_ip_start + count * ip_step
                    args[u"prefix"] = IPUtil.create_prefix_object(
                        src_ip, 128 if src_ip_start.version == 6 else 32
                    )
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_address, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )

            cmd = u"vxlan_add_del_tunnel"
            args = dict(
                is_add=True,
                instance=Constants.BITWISE_NON_ZERO,
                src_address=None,
                dst_address=None,
                mcast_sw_if_index=Constants.BITWISE_NON_ZERO,
                encap_vrf_id=0,
                decap_next_index=Constants.BITWISE_NON_ZERO,
                vni=None
            )
            def gen_vxlan():
                for count in range(vxlan_count):
                    src_ip = src_ip_start + count * ip_step
                    dst_ip = dst_ip_start + count * ip_step
                    args[u"src_address"] = IPAddress.create_ip_address_object(
                        src_ip
                    )
                    args[u"dst_address"] = IPAddress.create_ip_address_object(
                        dst_ip
                    )
                    args[u"vni"] = int(vni_start) + count
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_vxlan, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )

            cmd = u"create_vlan_subif"
            args = dict(
                sw_if_index=InterfaceUtil.get_interface_index(
                    node, node_vlan_if),
                vlan_id=None
            )
            def gen_vlan():
                for count in range(vxlan_count):
                    args[u"vlan_id"] = count + 1
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_vlan, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )

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
        vlan_superif_name = Topology.get_interface_name(node, node_vlan_if)

        # First phase builds data structures.
        # This has to be done outside args generator,
        # as that that skips repetitive cycles.
        for count in range(vxlan_count):
            vxlan_subif_key = Topology.add_new_port(node, u"vxlan_tunnel")
            vxlan_subif_name = f"vxlan_tunnel{count}"
            founds = dict(vxlan=False, vlan=False)
            vxlan_subif_index = None
            vlan_subif_key = Topology.add_new_port(node, u"vlan_subif")
            vlan_subif_name = f"{vlan_superif_name}.{count + 1}"
            vlan_index = None
            for data in if_data:
                if not founds[u"vxlan"] \
                        and data[u"interface_name"] == vxlan_subif_name:
                    vxlan_subif_index = data[u"sw_if_index"]
                    founds[u"vxlan"] = True
                elif not founds[u"vlan"] \
                        and data[u"interface_name"] == vlan_subif_name:
                    vlan_index = data[u"sw_if_index"]
                    founds[u"vlan"] = True
                if founds[u"vxlan"] and founds[u"vlan"]:
                    break
            Topology.update_interface_sw_if_index(
                node, vxlan_subif_key, vxlan_subif_index
            )
            Topology.update_interface_name(
                node, vxlan_subif_key, vxlan_subif_name
            )
            Topology.update_interface_sw_if_index(
                node, vlan_subif_key, vlan_index
            )
            Topology.update_interface_name(
                node, vlan_subif_key, vlan_subif_name
            )

        cmd = u"sw_interface_set_flags"
        args = dict(
            sw_if_index=None,
            flags=InterfaceStatusFlags.IF_STATUS_API_FLAG_ADMIN_UP.value
        )
        err_msg = u"Error putting vlan/vxlan interfaces up."

        with PapiSocketExecutor(node) as papi_exec:
            def gen_vxlan():
                for count in range(vxlan_count):
                    vxlan_subif_name = f"vxlan_tunnel{count}"
                    vxlan_subif_key = Topology.get_interface_by_name(
                        node, vxlan_subif_name
                    )
                    vxlan_subif_index = Topology.get_interface_sw_index(
                        node, vxlan_subif_key
                    )
                    args[u"sw_if_index"] = vxlan_subif_index
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_vxlan, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )
            def gen_vlan():
                for count in range(vxlan_count):
                    vlan_subif_name = f"{vlan_superif_name}.{count + 1}"
                    vlan_subif_key = Topology.get_interface_by_name(
                        node, vlan_subif_name
                    )
                    vlan_subif_index = Topology.get_interface_sw_index(
                        node, vlan_subif_key
                    )
                    args[u"sw_if_index"] = vlan_subif_index
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_vlan, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )

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

        err_msg = u"Error adding vlan/vxlan interfaces to bridge domain."

        with PapiSocketExecutor(node) as papi_exec:
            cmd = u"ip_neighbor_add_del"
            neighbor = dict(
                sw_if_index=Topology.get_interface_sw_index(
                    node, node_vxlan_if
                ),
                flags=0,
                mac_address=Topology.get_interface_mac(op_node, op_node_if),
                ip_address=u""
            )
            args = dict(
                is_add=1,
                neighbor=neighbor
            )
            def gen_neighbor():
                for count in range(vxlan_count):
                    args[u"neighbor"][u"ip_address"] = \
                        str(dst_ip_start + count * ip_step)
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_neighbor, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )

            cmd = u"ip_route_add_del"
            kwargs = dict(
                interface=node_vxlan_if,
                gateway=str(dst_ip_start)
            )
            route = IPUtil.compose_vpp_route_structure(
                node, str(dst_ip_start),
                128 if dst_ip_start.version == 6 else 32, **kwargs
            )
            args = dict(
                is_add=1,
                is_multipath=0,
                route=route
            )
            def gen_route():
                for count in range(vxlan_count):
                    args[u"route"][u"prefix"][u"address"][u"un"] = \
                        IPAddress.union_addr(dst_ip_start + count * ip_step)
                    args[u"route"][u"paths"][0][u"nh"][u"address"] = \
                        IPAddress.union_addr(dst_ip_start + count * ip_step)
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_route, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )

            cmd = u"sw_interface_set_l2_bridge"
            args = dict(
                rx_sw_if_index=None,
                bd_id=None,
                shg=0,
                port_type=0,
                enable=1
            )
            def gen_vxlan():
                for count in range(vxlan_count):
                    args[u"rx_sw_if_index"] = Topology.get_interface_sw_index(
                        node, f"vxlan_tunnel{count+1}"
                    )
                    args[u"bd_id"] = int(bd_id_start + count)
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_vxlan, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )
            def gen_vlan():
                for count in range(vxlan_count):
                    args[u"rx_sw_if_index"] = Topology.get_interface_sw_index(
                        node, f"vlan_subif{count+1}"
                    )
                    args[u"bd_id"] = int(bd_id_start + count)
                    yield args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_vlan, err_msg=err_msg,
                how_many=vxlan_count, need_replies=False
            )
