# copyright (c) 2021 Intel and/or its affiliates.
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

"""Flow Utilities Library."""

from ipaddress import ip_address

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.PapiExecutor import PapiSocketExecutor

class FlowUtil:
    """Utilities for flow configuration."""

    @staticmethod
    def vpp_create_ip4_n_tuple_flow(
            node, src_ip, dst_ip, src_port, dst_port,
            proto, action, value=0):
        """Create IP4_N_TUPLE flow.

        :param node: DUT node.
        :param src_ip: Source IP4 address.
        :param dst_ip: Destination IP4 address.
        :param src_port: Source port.
        :param dst_port: Destination port.
        :param proto: TCP or UDP.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :type proto: str
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip4_n_tuple"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_N_TUPLE

        if proto == u"TCP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
        elif proto == u"UDP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            u'src_addr': {u'addr': src_ip, u'mask': u"255.255.255.255"},
            u'dst_addr': {u'addr': dst_ip, u'mask': u"255.255.255.255"},
            u'src_port': {u'port': src_port, u'mask': 0xFFFF},
            u'dst_port': {u'port': dst_port, u'mask': 0xFFFF},
            u'protocol': {u'prot': flow_proto}
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip6_n_tuple_flow(
            node, src_ip, dst_ip, src_port, dst_port,
            proto, action, value=0):
        """Create IP6_N_TUPLE flow.

        :param node: DUT node.
        :param src_ip: Source IP6 address.
        :param dst_ip: Destination IP6 address.
        :param src_port: Source port.
        :param dst_port: Destination port.
        :param proto: TCP or UDP.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :type proto: str
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip6_n_tuple"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP6_N_TUPLE

        if proto == u"TCP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
        elif proto == u"UDP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            u'src_addr': {u'addr': src_ip, \
                u'mask': u"FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
            u'dst_addr': {u'addr': dst_ip, \
                u'mask': u"FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
            u'src_port': {u'port': src_port, u'mask': 0xFFFF},
            u'dst_port': {u'port': dst_port, u'mask': 0xFFFF},
            u'protocol': {u'prot': flow_proto}
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip4_flow(
            node, src_ip, dst_ip, proto, action, value=0):
        """Create IP4 flow.

        :param node: DUT node.
        :param src_ip: Source IP4 address.
        :param dst_ip: Destination IP4 address.
        :param proto: TCP or UDP.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type proto: str
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip4"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4

        if proto == u"TCP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
        elif proto == u"UDP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            u'src_addr': {u'addr': src_ip, u'mask': u"255.255.255.255"},
            u'dst_addr': {u'addr': dst_ip, u'mask': u"255.255.255.255"},
            u'protocol': {u'prot': flow_proto}
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip6_flow(
            node, src_ip, dst_ip, proto, action, value=0):
        """Create IP6 flow.

        :param node: DUT node.
        :param src_ip: Source IP6 address.
        :param dst_ip: Destination IP6 address.
        :param proto: TCP or UDP.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type proto: str
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip6"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP6

        if proto == u"TCP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
        elif proto == u"UDP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            u'src_addr': {u'addr': src_ip, \
                u'mask': u"FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
            u'dst_addr': {'addr': dst_ip, \
                u'mask': u"FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
            u'protocol': {u'prot': flow_proto}
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip4_gtpu_flow(
            node, src_ip, dst_ip, teid, action, value=0):
        """Create IP4_GTPU flow.

        :param node: DUT node.
        :param src_ip: Source IP4 address.
        :param dst_ip: Destination IP4 address.
        :param teid: Tunnel endpoint identifier.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type teid: int
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip4_gtpu"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_GTPU
        flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP

        pattern = {
            u'src_addr': {u'addr': src_ip, u'mask': u"255.255.255.255"},
            u'dst_addr': {u'addr': dst_ip, u'mask': u"255.255.255.255"},
            u'protocol': {u'prot': flow_proto},
            u'teid': teid
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip4_ipsec_flow(node, proto, spi, action, value=0):
        """Create IP4_IPSEC flow.

        :param node: DUT node.
        :param proto: TCP or UDP.
        :param spi: Security Parameters Index.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type proto: str
        :type spi: int
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        if proto == u"ESP":
            flow = u"ip4_ipsec_esp"
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_ESP
            flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_IPSEC_ESP
        elif proto == u"AH":
            flow = u"ip4_ipsec_ah"
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_AH
            flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_IPSEC_AH
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            u'protocol': {u'prot': flow_proto},
            u'spi': spi
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip4_l2tp_flow(node, session_id, action, value=0):
        """Create IP4_L2TPV3OIP flow.

        :param node: DUT node.
        :param session_id: PPPoE session ID
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type session_id: int
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip4_l2tpv3oip"
        flow_proto = 115    # IP_API_PROTO_L2TP
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_L2TPV3OIP

        pattern = {
            u'protocol': {u'prot': flow_proto},
            u'session_id': session_id
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_create_ip4_vxlan_flow(node, src_ip, dst_ip, vni, action, value=0):
        """Create IP4_VXLAN flow.

        :param node: DUT node.
        :param src_ip: Source IP4 address.
        :param dst_ip: Destination IP4 address.
        :param vni: Virtual network instance.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type vni: int
        :type action: str
        :type value: int
        :returns: flow_index.
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        flow = u"ip4_vxlan"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_VXLAN
        flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP

        pattern = {
            u'src_addr': {u'addr': src_ip, u'mask': u"255.255.255.255"},
            u'dst_addr': {u'addr': dst_ip, u'mask': u"255.255.255.255"},
            u'dst_port': {u'port': 4789, 'mask': 0xFFFF},
            u'protocol': {u'prot': flow_proto},
            u'vni': vni
        }

        flow_index = FlowUtil.vpp_flow_add(node, flow, flow_type,
                pattern, action, value)

        return flow_index

    @staticmethod
    def vpp_flow_add(node, flow, flow_type, pattern, action, value=0):
        """Flow add.

        :param node: DUT node.
        :param flow: Name of flow.
        :param flow_type: Type of flow.
        :param pattern: Pattern of flow.
        :param action: Mark, drop or redirect-to-queue.
        :param value: Action value.

        :type node: dict
        :type node: str
        :type flow_type: str
        :type pattern: dict
        :type action: str
        :type value: int
        :returns: flow_index.
        :rtype: int
        :raises ValueError: If the node has an unknown node type.
        """

        from vpp_papi import VppEnum

        if node[u"type"] == NodeType.DUT:
            cmd = u"flow_add"

            if action == u"redirect-to-queue":
                flow_rule = {
                    u'type': flow_type,
                    u'actions': VppEnum.vl_api_flow_action_t.FLOW_ACTION_REDIRECT_TO_QUEUE,
                    u'redirect_queue': value,
                    u'flow': {flow : pattern}
                }
            elif action == u"mark":
                flow_rule = {
                    u'type': flow_type,
                    u'actions': VppEnum.vl_api_flow_action_t.FLOW_ACTION_MARK,
                    u'mark_flow_id': value,
                    u'flow': {flow : pattern}
                }
            elif action == u"drop":
                flow_rule = {
                    u'type': flow_type,
                    u'actions': VppEnum.vl_api_flow_action_t.FLOW_ACTION_DROP,
                    u'flow': {flow : pattern}
                }
            else:
                raise ValueError(f"Action type error: {action}")

            err_msg = f"Failed to create {flow} flow on host."
            args = dict(flow=flow_rule)
            flow_index = -1
            with PapiSocketExecutor(node) as papi_exec:
                reply = papi_exec.add(cmd, **args).get_reply(err_msg)
                flow_index = reply[u"flow_index"]

            return flow_index
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_flow_enable(node, interface, flow_index=0):
        """Flow enable.

        :param node: DUT node.
        :param interface: Interface sw_if_index.
        :param flow_index: Flow index.

        :type node: dict
        :type interface: int
        :type flow_index: int
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """

        if node[u"type"] == NodeType.DUT:
            err_msg = u"Failed to enable flow on host"
            cmd = u"flow_enable"
            sw_if_index = Topology.get_interface_sw_index(node, interface)
            args = dict(
                flow_index=int(flow_index),
                hw_if_index=int(sw_if_index)
            )
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_flow_disable(node, interface, flow_index=0):
        """Flow disable.

        :param node: DUT node.
        :param interface: Interface sw_if_index.
        :param flow_index: Flow index.

        :type node: dict
        :type interface: int
        :type flow_index: int
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """

        if node[u"type"] == NodeType.DUT:
            err_msg = u"Failed to disable flow on host"
            cmd = u"flow_disable"
            sw_if_index = Topology.get_interface_sw_index(node, interface)
            args = dict(
                flow_index=int(flow_index),
                hw_if_index=int(sw_if_index)
            )
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)

        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_flow_del(node, flow_index=0):
        """Flow delete.

        :param node: DUT node.
        :param flow_index: Flow index.

        :type node: dict
        :type flow_index: int
        :returns: Nothing.
        :raises ValueError: If the node has an unknown node type.
        """

        if node[u"type"] == NodeType.DUT:
            err_msg = u"Failed to delete flow on host"
            cmd = u"flow_del"
            args = dict(
                flow_index=int(flow_index)
            )
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)

        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_show_flow_entry(node):
        """Show flow entry.

        :param node: DUT node.

        :type node: dict
        :returns: flow entry.
        :rtype: str
        :raises ValueError: If the node has an unknown node type.

        """

        if node[u"type"] == NodeType.DUT:
            err_msg = u"Failed to show flow on host"
            cmd = u"vppctl show flow entry"
            stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=False, message=err_msg, retries=120
            )

            return stdout.strip()
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_verify_flow_action(
            node, action, value,
            src_mac=u"11:22:33:44:55:66", dst_mac=u"11:22:33:44:55:66",
            src_ip=None, dst_ip=None):
        """Verify the correctness of the flow action.

        :param node: DUT node.
        :param action: Action.
        :param value: Action value.
        :param src_mac: Source mac address.
        :param dst_mac: Destination mac address.
        :param src_ip: Source IP address.
        :param dst_ip: Destination IP address.

        :type node: dict
        :type action: str
        :type value: int
        :type src_mac: str
        :type dst_mac: str
        :type src_ip: str
        :type dst_ip: str
        :returns: Nothing.
        :raises ValueError: Unknown node type or verify error.
        """
        if node[u"type"] == NodeType.DUT:
            err_msg = f"Failed to show trace on host {node[u'host']}"
            cmd = u"vppctl show trace"
            stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=False, message=err_msg, retries=120
            )

            err_info = f"Verify flow {action} failed"

            if src_ip == None:
                expected_str = f"{src_mac} -> {dst_mac}"
            else:
                src_ip = ip_address(src_ip)
                dst_ip = ip_address(dst_ip)
                expected_str = f"{src_ip} -> {dst_ip}"

            if action == u"drop":
                if expected_str in stdout:
                    raise ValueError(err_info)
            elif action == u"redirect-to-queue":
                if f"queue {value}" not in stdout and f"qid {value}" not in stdout:
                    raise ValueError(err_info)
                if expected_str not in stdout:
                    raise ValueError(err_info)
            elif action == u"mark":
                if u"PKT_RX_FDIR" not in stdout and  u"flow-id 1" not in stdout:
                    raise ValueError(err_info)
                if expected_str not in stdout:
                    raise ValueError(err_info)
            else:
                raise ValueError(f"Action type error: {action}")
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )
