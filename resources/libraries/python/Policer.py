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

import binascii
import re

from ipaddress import ip_address
from enum import Enum
from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.Classify import Classify

class PolicerRateType(Enum):
    """Policer rate types."""
    KBPS = 0
    PPS = 1


# pylint: disable=invalid-name
class PolicerRoundType(Enum):
    """Policer round types."""
    CLOSEST = 0
    UP = 1
    DOWN = 2


class PolicerType(Enum):
    """Policer type."""
    P_1R2C = 0
    P_1R3C = 1
    P_2R3C_2698 = 2
    P_2R3C_4115 = 3
    P_2R3C_MEF5CF1 = 4


class PolicerAction(Enum):
    """Policer action."""
    DROP = 0
    TRANSMIT = 1
    MARK_AND_TRANSMIT = 2


class DSCP(Enum):
    """DSCP for mark-and-transmit action."""
    CS0 = 0
    CS1 = 8
    CS2 = 16
    CS3 = 24
    CS4 = 32
    CS5 = 40
    CS6 = 48
    CS7 = 56
    AF11 = 10
    AF12 = 12
    AF13 = 14
    AF21 = 18
    AF22 = 20
    AF23 = 22
    AF31 = 26
    AF32 = 28
    AF33 = 30
    EF = 46

# pylint: disable=too-many-instance-attributes
class Policer(object):

    """Policer utilities."""

    def __init__(self):
        self._color_aware = False
        self._classify_precolor = None
        self._sw_if_index = 0
        self._node = None

    def policer_set_configuration(self, node, interface, policer_name, cir,
                                  eir, cb, eb, rate_type, round_type,
                                  policer_type, conform_action_type,
                                  exceed_action_type, violate_action_type,
                                  color_aware, ip_version, direction, ip_addr,
                                  is_add=1, conform_dscp=None,
                                  exceed_dscp=None, violate_dscp=None):

        """Configure policer on VPP node.
        ...note:: First set all required parameters.
        """
        node = node
        # Setting of Policer Rate Type.
        rate_type = rate_type.upper()
        rate_type = getattr(PolicerRateType, rate_type).value

        # Setting of Policer Round Type.
        round_type = round_type.upper()
        round_type = getattr(PolicerRoundType, round_type).value

        # Setting of Policer Type.
        policer_type = "P_" + policer_type.upper().replace(" ", "_")
        policer_type = getattr(PolicerType, policer_type).value

        # Setting of Policer Conform-Action
        conform_action_type = conform_action_type.upper().replace(" ", "_")
        conform_action_type = getattr(PolicerAction, conform_action_type).value

        # Setting of Policer Exceed-Action
        exceed_action_type = exceed_action_type.upper().replace(" ", "_")
        exceed_action_type = getattr(PolicerAction, exceed_action_type).value

        # Setting of Policer Violate-Action
        violate_action_type = violate_action_type.upper().replace(" ", "_")
        violate_action_type = getattr(PolicerAction, violate_action_type).value

        # Setting of Color Aware
        color_aware = 1 if color_aware else 0

        # Setting of Conform DSCP
        if conform_dscp is None:
            conform_dscp = None
        else:
            conform_dscp = conform_dscp.upper()
            conform_dscp = getattr(DSCP, conform_dscp).value

        # Setting of Exceed DSCP
        if exceed_dscp is None:
            exceed_dscp = None
        else:
            exceed_dscp = exceed_dscp.upper()
            exceed_dscp = getattr(DSCP, exceed_dscp).value

        # Setting of Violate DSCP
        if violate_dscp is None:
            violate_dscp = None
        else:
            violate_dscp = violate_dscp.upper()
            violate_dscp = getattr(DSCP, violate_dscp).value

        cmd = 'policer_add_del'
        args_in = dict(
            is_add=int(is_add),
            name=policer_name.encode("utf-8"),
            cir=int(cir),
            eir=int(eir),
            cb=int(cb),
            eb=int(eb),
            rate_type=rate_type,
            round_type=round_type,
            type=policer_type,
            conform_action_type=conform_action_type,
            exceed_action_type=exceed_action_type,
            violate_action_type=violate_action_type,
            color_aware=color_aware
        )

        if PolicerAction.MARK_AND_TRANSMIT.value == conform_action_type:
            args_in['conform_dscp'] = conform_dscp

        if PolicerAction.MARK_AND_TRANSMIT.value == exceed_action_type:
            args_in['exceed_dscp'] = exceed_dscp

        if PolicerAction.MARK_AND_TRANSMIT.value == violate_action_type:
            args_in['violate_dscp'] = violate_dscp

        err_msg = 'Add policer {policer_name} Failed'.format(policer_name=args_in['name'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args_in).get_reply(err_msg)
        policer_index = reply['policer_index']

        (table_index, skip_n_vectors, match_n_vectors) = Classify.vpp_creates_classify_table_l3(node, ip_version, direction, ip_addr)
        Classify.vpp_configures_classify_session_l3(node, 'permit', table_index, ip_version, direction, ip_addr)
        return table_index

    # Policer Classify Set Interface
    def policer_classify_set_interface(self, node, interface, ip4_table_index=0xFFFFFFFF,
                                       ip6_table_index=0xFFFFFFFF, l2_table_index=0xFFFFFFFF, is_add=1):
        cmd = 'policer_classify_set_interface'
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface
        args_in = dict(
            is_add=int(is_add),
            sw_if_index=sw_if_index,
            ip4_table_index=int(ip4_table_index),
            ip6_table_index=int(ip6_table_index),
            l2_table_index=int(l2_table_index)
        )
        err_msg = 'Policer Classify Set Interface Failed'
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args_in).get_reply(err_msg)

    def get_dscp_num_value(self, dscp_value):
        """Return DSCP numeric value.
        :param dscp: DSCP enum object.
        :type dscp: DSCP
        :returns: DSCP numeric value.
        :rtype: int
        """
        return getattr(DSCP, dscp_value).value
