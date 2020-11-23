# copyright (c) 2020 Intel and/or its affiliates.
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

"""Flow util library."""

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from robot.api import logger
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator


class FlowUtil:
    """flow configuration."""

    @staticmethod
    def vpp_create_ip4_n_tuple_flow(
            node, src_ip, dst_ip, src_port, dst_port,
            proto, action, value=0):
        """Create IP4_N_TUPLE flow.

        :param node: DUT node.
        :param src_ip: source IP4 address.
        :param dst_ip: destination IP4 address.
        :param src_port: source port.
        :param dst_port: destination port.
        :param proto: TCP or UDP.
        :param action: mark, drop or redirect-to-queue.
        :param value: action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :type proto: str
        :type action: str
        :type value: int
        :returns: flow_index.
        :raises ValueError: If the node has an unknown node type.
        """

        if node[u"type"] == NodeType.DUT:
            err_msg = u"Failed to create ip4 ntuple flow on host."

            from vpp_papi import VppEnum
            proto_type = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
            if proto == u"UDP":
                proto_type = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP

            cmd = u"flow_add"
            ip4_tuple_pattern = {
                'src_addr' : {'addr' : src_ip, 'mask' : "255.255.255.255"},
                'dst_addr' : {'addr' : dst_ip, 'mask' : "255.255.255.255"},
                'src_port' : {'port' : src_port, 'mask' : 0xFFFF},
                'dst_port' : {'port' : dst_port, 'mask' : 0xFFFF},
                'protocol' : {'prot' : proto_type}
            }

            if action == u"redirect-to-queue":
                ip4_ntuple_flow_rule = {
                    'type' : VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_N_TUPLE,
                    'actions' : \
                    VppEnum.vl_api_flow_action_t.FLOW_ACTION_REDIRECT_TO_QUEUE,
                    'redirect_queue' : value,
                    'flow' : {'ip4_n_tuple' : ip4_tuple_pattern}
                }
            elif action == u"mark":
                ip4_ntuple_flow_rule = {
                    'type' : VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_N_TUPLE,
                    'actions' : VppEnum.vl_api_flow_action_t.FLOW_ACTION_MARK,
                    'mark_flow_id' : value,
                    'flow' : {'ip4_n_tuple' : ip4_tuple_pattern}
                }
            elif action == u"drop":
                ip4_ntuple_flow_rule = {
                    'type' : VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP4_N_TUPLE,
                    'actions' : VppEnum.vl_api_flow_action_t.FLOW_ACTION_DROP,
                    'flow' : {'ip4_n_tuple' : ip4_tuple_pattern}
                }
            else:
                raise ValueError(u"Action type error")

            args = dict(flow=ip4_ntuple_flow_rule)
            with PapiSocketExecutor(node) as papi_exec:
                reply = papi_exec.add(cmd, **args).get_reply(err_msg)

            return reply[u"flow_index"]
        else:
            raise ValueError(
                f"Node {node[u'host']} has unknown NodeType: '{node[u'type']}'"
            )

    @staticmethod
    def vpp_create_ip6_n_tuple_flow(
            node, src_ip, dst_ip, src_port, dst_port,
            proto, action, value=0):
        """Create IP6-N-TUPLE flow.

        :param node: DUT node.
        :param src_ip: source IP6 address.
        :param dst_ip: destination IP6 address.
        :param src_port: source port.
        :param dst_port: destination port.
        :param proto: TCP or UDP.
        :param action: mark, drop or redirect-to-queue.
        :param value: action value.

        :type node: dict
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :type proto: str
        :type action: str
        :type value: int
        :returns: flow_index.
        :raises ValueError: If the node has an unknown node type.
        """

        if node[u"type"] == NodeType.DUT:
            err_msg = u"Failed to create IP6 ntuple flow on host"

            from vpp_papi import VppEnum
            proto_type = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_TCP
            if proto == u"UDP":
                proto_type = VppEnum.vl_api_ip_proto_t.IP_API_PROTO_UDP

            cmd = u"flow_add"
            ip6_tuple_pattern = {
                'src_addr' : {'addr' : src_ip, \
                    'mask' : "FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
                'dst_addr' : {'addr' : dst_ip, \
                    'mask' : "FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF:FFFF"},
                'src_port' : {'port' : src_port, 'mask' : 0xFFFF},
                'dst_port' : {'port' : dst_port, 'mask' : 0xFFFF},
                'protocol' : {'prot' : proto_type}
            }

            if action == u"redirect-to-queue":
                ip6_ntuple_flow_rule = {
                    'type' : VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP6_N_TUPLE,
                    'actions' : \
                    VppEnum.vl_api_flow_action_t.FLOW_ACTION_REDIRECT_TO_QUEUE,
                    'redirect_queue' : value,
                    'flow' : {'ip6_n_tuple' : ip6_tuple_pattern}
                }
            elif action == u"mark":
                ip6_ntuple_flow_rule = {
                    'type' : VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP6_N_TUPLE,
                    'actions' : VppEnum.vl_api_flow_action_t.FLOW_ACTION_MARK,
                    'mark_flow_id' : value,
                    'flow' : {'ip6_n_tuple' : ip6_tuple_pattern}
                }
            elif action == u"drop":
                ip6_ntuple_flow_rule = {
                    'type' : VppEnum.vl_api_flow_type_t.FLOW_TYPE_IP6_N_TUPLE,
                    'actions' : VppEnum.vl_api_flow_action_t.FLOW_ACTION_DROP,
                    'flow' : {'ip6_n_tuple' : ip6_tuple_pattern}
                }
            else:
                raise ValueError(u"Action type error")

            args = dict(flow=ip6_ntuple_flow_rule)
            with PapiSocketExecutor(node) as papi_exec:
                reply = papi_exec.add(cmd, **args).get_reply(err_msg)

            return reply[u"flow_index"]
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
            err_msg = u"Failed to remove flow on host"
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
    def vpp_flow_verify_action(
            node, action, value,
            src_mac=u"11:22:33:44:55:66", dst_mac=u"11:22:33:44:55:66"):
        """Verify the correctness of the flow action.

        :param node: DUT node.
        :param action: action.
        :param value: action value.
        :param src_mac: source mac address.
        :param dst_mac: destination mac address.

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
