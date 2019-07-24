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

from enum import Enum
from ipaddress import ip_address
from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


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


class PolicerClassifyPreColor(Enum):
    """Policer classify precolor."""
    CONFORM_COLOR = 'conform-color'
    EXCEED_COLOR = 'exceed-color'


class PolicerClassifyTableType(Enum):
    """Policer classify table type."""
    IP4_TABLE = 'ip4-table'
    IP6_TABLE = 'ip6-table'
    L2_TABLE = 'l2-table'


# pylint: disable=too-many-instance-attributes
class Policer(object):
    """Policer utilities."""

    def __init__(self):
        self._cir = 0
        self._eir = 0
        self._cb = 0
        self._eb = 0
        self._rate_type = None
        self._round_type = None
        self._policer_type = None
        self._conform_action = None
        self._conform_dscp = None
        self._exceed_action = None
        self._exceed_dscp = None
        self._violate_action = None
        self._violate_dscp = None
        self._color_aware = False
        self._classify_match_ip = ''
        self._classify_match_is_src = True
        self._classify_precolor = None
        self._sw_if_index = 0
        self._node = None
        self._policer_name = ''

    def policer_set_configuration(self, node, policer_name, cir,
                                  eir, cb, eb, rate_type, round_type,
                                  policer_type, conform_action_type,
                                  exceed_action_type, violate_action_type,
                                  color_aware, conform_dscp=None,
                                  exceed_dscp=None, violate_dscp=None,
                                  is_add=1):
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

        logger.debug("The dict arguments are {args_in}"
                     .format(args_in=args_in))

        err_msg = 'Add policer {policer_name} Failed'.format(policer_name=args_in['name'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args_in).get_reply(err_msg)

        policer_index = reply['policer_index']

        # create classify table
        direction = 'src' if self._classify_match_is_src else 'dst'

        if ip_address(unicode(self._classify_match_ip)).version == 6:
            ip_version = 'ip6'
            table_type = PolicerClassifyTableType.IP6_TABLE
        else:
            ip_version = 'ip4'
            table_type = PolicerClassifyTableType.IP4_TABLE

        cmd = 'classify_add_del_table'
        args_in = dict(
            ip_version=ip_version,
            direction=direction
        )
        err_msg = 'Add classify table failed on {0}'.format(node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args_in).get_reply(err_msg)

        new_table_index = reply['new_table_index']
        skip_n_vectors = reply['skip_n_vectors']
        match_n_vectors = reply['match_n_vectors']

        # create classify session
        match = 'l3 {0} {1} {2}'.format(ip_version,
                                        direction,
                                        self._classify_match_ip)
        cmd = 'classify_add_del_session'
        args_in = dict(
            policer_index=policer_index,
            pre_color=self._classify_precolor.value,  # pylint:disable=no-member
            table_index=new_table_index,
            skip_n=skip_n_vectors,
            match_n=match_n_vectors,
            match=match
        )
        err_msg = 'Add classify session failed on {0}'.format(node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

        # set classify interface
        cmd = 'policer_classify_set_interface'
        args_in = dict(
            sw_if_index=self._sw_if_index,
            table_type=table_type.value,  # pylint: disable=no-member
            table_index=new_table_index
        )
        err_msg = 'Set classify interface failed on {0}'.format(node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    def policer_clear_settings(self):
        """Clear policer settings."""
        self._classify_match_ip = ''
        self._classify_match_is_src = True
        self._classify_precolor = None
        self._sw_if_index = 0
        self._node = None

    def policer_classify_set_precolor_conform(self):
        """Set policer classify pre-color to conform-color."""
        self._classify_precolor = PolicerClassifyPreColor.CONFORM_COLOR

    def policer_classify_set_precolor_exceed(self):
        """Set policer classify pre-color to exceeed-color."""
        self._classify_precolor = PolicerClassifyPreColor.EXCEED_COLOR

    def policer_classify_set_interface(self, node, interface):
        """Set policer classify interface.

        .. note:: First set node with policer_set_node.

        :param interface: Interface name or sw_if_index.
        :type interface: str or int
        """
        self._node = node
        if isinstance(interface, basestring):
            self._sw_if_index = Topology.get_interface_sw_index(self._node,
                                                                interface)
        else:
            self._sw_if_index = interface

    def policer_classify_set_match_ip(self, ip, is_src=True):
        """Set policer classify match source IP address.

        :param ip: IPv4 or IPv6 address.
        :param is_src: Match src IP if True otherwise match dst IP.
        :type ip: str
        :type is_src: bool
        """
        self._classify_match_ip = ip
        self._classify_match_is_src = is_src
