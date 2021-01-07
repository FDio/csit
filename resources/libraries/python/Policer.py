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

"""Policer utilities library."""

from enum import IntEnum

from resources.libraries.python.Constants import Constants
from resources.libraries.python.IPUtil import IpDscp
from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class PolicerRateType(IntEnum):
    """Policer rate types."""
    KBPS = 0
    PPS = 1
    INVALID = 2


class PolicerRoundType(IntEnum):
    """Policer round types."""
    ROUND_TO_CLOSEST = 0
    ROUND_TO_UP = 1
    ROUND_TO_DOWN = 2
    ROUND_INVALID = 3


class PolicerType(IntEnum):
    """Policer type."""
    TYPE_1R2C = 0
    TYPE_1R3C_RFC_2697 = 1
    TYPE_2R3C_RFC_2698 = 2
    TYPE_2R3C_RFC_4115 = 3
    TYPE_2R3C_RFC_MEF5CF1 = 4
    TYPE_MAX = 5


class PolicerAction(IntEnum):
    """Policer action."""
    DROP = 0
    TRANSMIT = 1
    MARK_AND_TRANSMIT = 2


class PolicerPreColor(IntEnum):
    """Policer Pre-color."""
    CONFORM_COLOR = 0
    EXCEED_COLOR = 1
    VIOLATE_COLOR = 2


class Policer:
    """Policer utilities."""

    # TODO: Pylint says too-many-arguments and too-many-locals.
    # It is right, we should refactor the code
    # and group similar arguments together (into documented classes).
    # Note that even the call from Robot Framework
    # is not very readable with this many arguments.
    @staticmethod
    def policer_set_configuration(
            node, policer_name, cir, eir, cbs, ebs, rate_type, round_type,
            policer_type, conform_action_type, exceed_action_type,
            violate_action_type, color_aware, is_add=True, conform_dscp=None,
            exceed_dscp=None, violate_dscp=None):
        """Configure policer on VPP node.

        :param node: VPP node.
        :param policer_name: Name of the policer.
        :param cir: Committed information rate.
        :param eir: Excess (or Peak) information rate.
        :param cbs: Committed burst size.
        :param ebs: Excess (or Peak) burst size.
        :param rate_type: Rate type.
        :param round_type: Round type.
        :param policer_type: Policer algorithm.
        :param conform_action_type: Conform action type.
        :param exceed_action_type: Exceed action type.
        :param violate_action_type: Violate action type.
        :param color_aware: Color-blind (cb) or color-aware (ca).
        :param is_add: Add policer if True, else delete.
        :param conform_dscp: DSCP for conform mark_and_transmit action.
        :param exceed_dscp: DSCP for exceed mark_and_transmit action.
        :param violate_dscp: DSCP for vilate mark_and_transmit action.
        :type node: dict
        :type policer_name: str
        :type cir: int
        :type eir: int
        :type cbs: int
        :type ebs: int
        :type rate_type: str
        :type round_type: str
        :type policer_type: str
        :type conform_action_type: str
        :type exceed_action_type: str
        :type violate_action_type: str
        :type color_aware: str
        :type is_add: bool
        :type conform_dscp: str
        :type exceed_dscp: str
        :type violate_dscp: str
        """
        conform_action = dict(
            type=getattr(PolicerAction, conform_action_type.upper()).value,
            dscp=Policer.get_dscp_num_value(conform_dscp) if
            conform_action_type.upper() == PolicerAction.MARK_AND_TRANSMIT.name
            else 0
        )
        exceed_action = dict(
            type=getattr(PolicerAction, exceed_action_type.upper()).value,
            dscp=Policer.get_dscp_num_value(exceed_dscp) if
            exceed_action_type.upper() == PolicerAction.MARK_AND_TRANSMIT.name
            else 0
        )
        violate_action = dict(
            type=getattr(PolicerAction, violate_action_type.upper()).value,
            dscp=Policer.get_dscp_num_value(violate_dscp) if
            violate_action_type.upper() == PolicerAction.MARK_AND_TRANSMIT.name
            else 0
        )

        cmd = u"policer_add_del"
        args = dict(
            is_add=is_add,
            name=str(policer_name),
            cir=int(cir),
            eir=int(eir),
            cb=int(cbs),
            eb=int(ebs),
            rate_type=getattr(PolicerRateType, rate_type.upper()).value,
            round_type=getattr(
                PolicerRoundType, f"ROUND_TO_{round_type.upper()}"
            ).value,
            type=getattr(PolicerType, f"TYPE_{policer_type.upper()}").value,
            conform_action=conform_action,
            exceed_action=exceed_action,
            violate_action=violate_action,
            color_aware=bool(color_aware == u"'ca'")
        )
        err_msg = f"Failed to configure policer {policer_name} " \
            f"on host {node['host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return reply[u"policer_index"]

    @staticmethod
    def policer_classify_set_interface(
            node, interface, ip4_table_index=Constants.BITWISE_NON_ZERO,
            ip6_table_index=Constants.BITWISE_NON_ZERO,
            l2_table_index=Constants.BITWISE_NON_ZERO, is_add=True):
        """Set/unset policer classify interface.

        :param node: VPP node.
        :param interface: Interface name or sw_if_index to set/unset policer
            classify.
        :param ip4_table_index: IP4 classify table index (~0 to skip).
            (Default value = ~0)
        :param ip6_table_index: IP6 classify table index (~0 to skip).
            (Default value = ~0)
        :param l2_table_index: L2 classify table index (~0 to skip).
            (Default value = ~0)
        :param is_add: Set if True, else unset.
        :type node: dict
        :type interface: str or int
        :type ip4_table_index: int
        :type ip6_table_index: int
        :type l2_table_index: int
        :type is_add: bool
        """
        if isinstance(interface, str):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        cmd = u"policer_classify_set_interface"
        args = dict(
            is_add=is_add,
            sw_if_index=int(sw_if_index),
            ip4_table_index=int(ip4_table_index),
            ip6_table_index=int(ip6_table_index),
            l2_table_index=int(l2_table_index)
        )
        err_msg = f"Failed to set/unset policer classify interface " \
            f"{interface} on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def policer_classify_get_precolor(precolor):
        """Return policer pre-color numeric value.

        :param precolor: Policer pre-color name.
        :type precolor: str
        :returns: Policer pre-color numeric value.
        :rtype: int
        """
        return getattr(PolicerPreColor, precolor.upper()).value

    @staticmethod
    def get_dscp_num_value(dscp):
        """Return DSCP numeric value.

        :param dscp: DSCP name.
        :type dscp: str
        :returns: DSCP numeric value.
        :rtype: int
        """
        return getattr(IpDscp, f"IP_API_DSCP_{dscp.upper()}").value
