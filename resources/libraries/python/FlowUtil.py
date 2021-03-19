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

import time

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

        flow = "ip4_n_tuple"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_N_TUPLE

        if proto == u"TCP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
        elif proto == u"UDP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            'src_addr': {'addr': src_ip, 'mask': "255.255.255.255"},
            'dst_addr': {'addr': dst_ip, 'mask': "255.255.255.255"},
            'src_port': {'port': src_port, 'mask': 0xFFFF},
            'dst_port': {'port': dst_port, 'mask': 0xFFFF},
            'protocol': {'prot': flow_proto}
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

        flow = "ip6_n_tuple"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP6_N_TUPLE

        if proto == u"TCP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
        elif proto == u"UDP":
            flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP
        else:
            raise ValueError(f"proto error: {proto}")

        pattern = {
            'src_addr': {'addr': src_ip, \
                'mask': "FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
            'dst_addr': {'addr': dst_ip, \
                'mask': "FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
            'src_port': {'port': src_port, 'mask': 0xFFFF},
            'dst_port': {'port': dst_port, 'mask': 0xFFFF},
            'protocol': {'prot': flow_proto}
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

        flow = "ip4_gtpu"
        flow_type = VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_GTPU
        flow_proto = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP

        pattern = {
            'src_addr': {'addr': src_ip, 'mask': "255.255.255.255"},
            'dst_addr': {'addr': dst_ip, 'mask': "255.255.255.255"},
            'protocol': {'prot': flow_proto},
            'teid': teid
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
                    'type': flow_type,
                    'actions': VppEnum.vl_api_flow_action_t.FLOW_ACTION_REDIRECT_TO_QUEUE,
                    'redirect_queue': value,
                    'flow': {flow : pattern}
                }
            elif action == u"mark":
                flow_rule = {
                    'type': flow_type,
                    'actions': VppEnum.vl_api_flow_action_t.FLOW_ACTION_MARK,
                    'mark_flow_id': value,
                    'flow': {flow : pattern}
                }
            elif action == u"drop":
                flow_rule = {
                    'type': flow_type,
                    'actions': VppEnum.vl_api_flow_action_t.FLOW_ACTION_DROP,
                    'flow': {flow : pattern}
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

            time.sleep(2)
            FlowUtil.vpp_show_flow_entry(node)

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
            err_msg = u"Failed to enable flow on host"
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
    def vpp_flow_verify_action(
            node, action, value,
            src_mac=u"11:22:33:44:55:66", dst_mac=u"11:22:33:44:55:66"):
        """Verify the correctness of the flow action.

        :param node: DUT node.
        :param action: Action.
        :param value: Action value.
        :param src_mac: Source mac address.
        :param dst_mac: Destination mac address.

        :type node: dict
        :type action: str
        :type value: int
        :type src_mac: str
        :type dst_mac: str
        :returns: Nothing.
        :raises ValueError: Unknown node type or verify error.
        """
        if node[u"type"] == NodeType.DUT:
            err_msg = f"Failed to show trace on host {node[u'host']}"
            cmd = u"vppctl show trace"
            stdout, _ = exec_cmd_no_error(
                node, cmd, sudo=False, message=err_msg, retries=120
            )

            if action == u"drop":
                mac_matched = f"{src_mac} -> {dst_mac}"
                if mac_matched in stdout:
                    raise ValueError(
                        u"The flow packet dropped failed"
                    )
            elif action == u"redirect-to-queue":
                queue_matched = f"queue {value}"
                if queue_matched not in stdout:
                    raise ValueError(
                        u"The flow packet redirected to queue failed"
                    )
            elif action == u"mark":
                if u"PKT_RX_FDIR" not in stdout:
                    raise ValueError(u"The flow packet mark failed")
            else:
                raise ValueError(u"Action type error")
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )
