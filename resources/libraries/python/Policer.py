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

"""Policer utilities library."""

from enum import IntEnum

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
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
    ROUND_TO_INVALID = 3


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


class DSCP(IntEnum):
    """DSCP for mark-and-transmit action."""
    D_CS0 = 0
    D_CS1 = 8
    D_CS2 = 16
    D_CS3 = 24
    D_CS4 = 32
    D_vCS5 = 40
    D_CS6 = 48
    D_CS7 = 56
    D_AF11 = 10
    D_AF12 = 12
    D_AF13 = 14
    D_AF21 = 18
    D_AF22 = 20
    D_AF23 = 22
    D_AF31 = 26
    D_AF32 = 28
    D_AF33 = 30
    D_EF = 46


class Policer(object):
    """Policer utilities."""

    # pylint: disable=too-many-arguments, too-many-locals
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
        cmd = 'policer_add_del'
        args = dict(
            is_add=int(is_add),
            name=str(policer_name),
            cir=int(cir),
            eir=int(eir),
            cb=int(cbs),
            eb=int(ebs),
            rate_type=getattr(PolicerRateType, rate_type.upper()).value,
            round_type=getattr(
                PolicerRoundType, 'ROUND_TO_{rt}'.format(
                    rt=round_type.upper())).value,
            type=getattr(PolicerType, 'TYPE_{pt}'.format(
                pt=policer_type.upper())).value,
            conform_action_type=getattr(
                PolicerAction, conform_action_type.upper()).value,
            conform_dscp=getattr(DSCP, 'D_{dscp}'.format(
                dscp=conform_dscp.upper())).value
            if
            conform_action_type.upper() == PolicerAction.MARK_AND_TRANSMIT.name
            else 0,
            exceed_action_type=getattr(
                PolicerAction, exceed_action_type.upper()).value,
            exceed_dscp=getattr(DSCP, 'D_{dscp}'.format(
                dscp=exceed_dscp.upper())).value
            if
            exceed_action_type.upper() == PolicerAction.MARK_AND_TRANSMIT.name
            else 0,
            violate_action_type=getattr(
                PolicerAction, violate_action_type.upper()).value,
            violate_dscp=getattr(DSCP, 'D_{dscp}'.format(
                dscp=violate_dscp.upper())).value
            if
            violate_action_type.upper() == PolicerAction.MARK_AND_TRANSMIT.name
            else 0,
            color_aware=1 if color_aware == ""'ca'"" else 0
        )
        err_msg = 'Failed to configure policer {pn} on host {host}'.format(
            pn=policer_name, host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return reply['policer_index']

    @staticmethod
    def policer_classify_set_interface(
            node, interface, ip4_table_index=0xFFFFFFFF,
            ip6_table_index=0xFFFFFFFF, l2_table_index=0xFFFFFFFF, is_add=1):
        """Set/unset policer classify interface.

        :param node: VPP node.
        :param interface: Interface name or sw_if_index to set/unset policer
            classify.
        :param ip4_table_index: IP4 classify table index (0xFFFFFFFF to skip).
            (Default value = 0xFFFFFFFF)
        :param ip6_table_index: IP6 classify table index (0xFFFFFFFF to skip).
            (Default value = 0xFFFFFFFF)
        :param l2_table_index: L2 classify table index (0xFFFFFFFF to skip).
            (Default value = 0xFFFFFFFF)
        :param is_add: Set if non-zero, else unset.
        :type node: dict
        :type interface: str or int
        :type ip4_table_index: int
        :type ip6_table_index: int
        :type l2_table_index: int
        """
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        cmd = 'policer_classify_set_interface'

        args = dict(
            is_add=int(is_add),
            sw_if_index=sw_if_index,
            ip4_table_index=int(ip4_table_index),
            ip6_table_index=int(ip6_table_index),
            l2_table_index=int(l2_table_index)
        )
        err_msg = 'Failed to set/unset policer classify interface {ifc} ' \
                  'on host {host}'.format(ifc=interface, host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def get_dscp_num_value(dscp):
        """Return DSCP numeric value.

        :param dscp: DSCP name.
        :type dscp: str
        :returns: DSCP numeric value.
        :rtype: int
        """
        return getattr(DSCP, 'D_{dscp}'.format(dscp=dscp.upper())).value
