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

    def __init__(self, string):
        self.string = string


# pylint: disable=invalid-name
class PolicerRoundType(Enum):
    """Policer round types."""
    CLOSEST = 0
    UP = 1
    DOWN = 2

    def __init__(self, string):
        self.string = string


class PolicerType(Enum):
    """Policer type."""
    P_1R2C = 0
    P_1R3C = 1
    P_2R3C_2698 = 2
    P_2R3C_4115 = 3
    P_2R3C_MEF5CF1 = 4

    def __init__(self, string):
        self.string = string


class PolicerAction(Enum):
    """Policer action."""
    DROP = 0
    TRANSMIT = 1
    MARK_AND_TRANSMIT = 2

    def __init__(self, string):
        self.string = string


class DSCP(Enum):
    """DSCP for mark-and-transmit action."""
    CS0 = ('CS0', 0)
    CS1 = ('CS1', 8)
    CS2 = ('CS2', 16)
    CS3 = ('CS3', 24)
    CS4 = ('CS4', 32)
    CS5 = ('CS5', 40)
    CS6 = ('CS6', 48)
    CS7 = ('CS7', 56)
    AF11 = ('AF11', 10)
    AF12 = ('AF12', 12)
    AF13 = ('AF13', 14)
    AF21 = ('AF21', 18)
    AF22 = ('AF22', 20)
    AF23 = ('AF23', 22)
    AF31 = ('AF31', 26)
    AF32 = ('AF32', 28)
    AF33 = ('AF33', 30)
    EF = ('EF', 46)

    def __init__(self, string, num):
        self.string = string
        self.num = num


class PolicerClassifyPreColor(Enum):
    """Policer classify precolor."""
    CONFORM_COLOR = 'conform-color'
    EXCEED_COLOR = 'exceed-color'

    def __init__(self, string):
        self.string = string


class PolicerClassifyTableType(Enum):
    """Policer classify table type."""
    IP4_TABLE = 'ip4-table'
    IP6_TABLE = 'ip6-table'
    L2_TABLE = 'l2-table'

    def __init__(self, string):
        self.string = string


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
        if rate_type == 'pps':
            rate_type = int(PolicerRateType.PPS.value)
        else:
            rate_type = int(PolicerRateType.KBPS.value)

        # Setting of Policer Round Type.
        if round_type == 'Closest':
            round_type = int(PolicerRoundType.CLOSEST.value)
        elif round_type == 'Up':
            round_type = int(PolicerRoundType.UP.value)
        else:
            round_type = int(PolicerRoundType.DOWN.value)

        # Setting of Policer Type.
        if policer_type == '1R2C':
            policer_type = int(PolicerType.P_1R2C.value)
        elif policer_type == '1R3C':
            policer_type = int(PolicerType.P_1R3C.value)
        elif policer_type == '2R3C 2698':
            policer_type = int(PolicerType.P_2R3C_2698.value)
        elif policer_type == '2R3C 4115':
            policer_type = int(PolicerType.P_2R3C_4115.value)
        else:
            policer_type = int(PolicerType.P_2R3C_MEF5CF1.value)

        # Setting of Policer Conform-Action
        if conform_action_type == 'Drop':
            conform_action_type = int(PolicerAction.DROP.value)
        elif conform_action_type == 'Transmit':
            conform_action_type = int(PolicerAction.TRANSMIT.value)
        else:
            conform_action_type = int(PolicerAction.MARK_AND_TRANSMIT.value)

        # Setting of Policer Exceed-Action
        if exceed_action_type == 'Drop':
            exceed_action_type = int(PolicerAction.DROP.value)
        elif exceed_action_type == 'Transmit':
            exceed_action_type = int(PolicerAction.TRANSMIT.value)
        else:
            exceed_action_type = int(PolicerAction.MARK_AND_TRANSMIT.value)

        # Setting of Policer Violate-Action
        if violate_action_type == 'Drop':
            violate_action_type = int(PolicerAction.DROP.value)
        elif violate_action_type == 'Transmit':
            violate_action_type = int(PolicerAction.TRANSMIT.value)
        else:
            violate_action_type = int(PolicerAction.MARK_AND_TRANSMIT.value)

        # Setting of Color Aware
        color_aware = 1 if color_aware else 0

        # Setting of Conform DSCP
        if conform_dscp == 'DSCP CS0':
            conform_dscp = int(DSCP.CS0.value[1])
        elif conform_dscp == 'DSCP CS1':
            conform_dscp = int(DSCP.CS1.value[1])
        elif conform_dscp == 'DSCP CS2':
            conform_dscp = int(DSCP.CS2.value[1])
        elif conform_dscp == 'DSCP CS3':
            conform_dscp = int(DSCP.CS3.value[1])
        elif conform_dscp == 'DSCP CS4':
            conform_dscp = int(DSCP.CS4.value[1])
        elif conform_dscp == 'DSCP CS5':
            conform_dscp = int(DSCP.CS5.value[1])
        elif conform_dscp == 'DSCP CS6':
            conform_dscp = int(DSCP.CS6.value[1])
        elif conform_dscp == 'DSCP CS7':
            conform_dscp = int(DSCP.CS7.value[1])
        elif conform_dscp == 'DSCP AF11':
            conform_dscp = int(DSCP.AF11.value[1])
        elif conform_dscp == 'DSCP AF12':
            conform_dscp = int(DSCP.AF12.value[1])
        elif conform_dscp == 'DSCP AF13':
            conform_dscp = int(DSCP.AF13.value[1])
        elif conform_dscp == 'DSCP AF21':
            conform_dscp = int(DSCP.AF21.value[1])
        elif conform_dscp == 'DSCP AF22':
            conform_dscp = int(DSCP.AF22.value[1])
        elif conform_dscp == 'DSCP AF23':
            conform_dscp = int(DSCP.AF23.value[1])
        elif conform_dscp == 'DSCP AF31':
            conform_dscp = int(DSCP.AF31.value[1])
        elif conform_dscp == 'DSCP AF32':
            conform_dscp = int(DSCP.AF32.value[1])
        else:
            conform_dscp = int(DSCP.AF33.value[1])

        # Setting of Exceed DSCP
        if exceed_dscp == 'DSCP CS0':
            exceed_dscp = int(DSCP.CS0.value[1])
        elif exceed_dscp == 'DSCP CS1':
            exceed_dscp = int(DSCP.CS1.value[1])
        elif exceed_dscp == 'DSCP CS2':
            exceed_dscp = int(DSCP.CS2.value[1])
        elif exceed_dscp == 'DSCP CS3':
            exceed_dscp = int(DSCP.CS3.value[1])
        elif exceed_dscp == 'DSCP CS4':
            exceed_dscp = int(DSCP.CS4.value[1])
        elif exceed_dscp == 'DSCP CS5':
            exceed_dscp = int(DSCP.CS5.value[1])
        elif exceed_dscp == 'DSCP CS6':
            exceed_dscp = int(DSCP.CS6.value[1])
        elif exceed_dscp == 'DSCP CS7':
            exceed_dscp = int(DSCP.CS7.value[1])
        elif exceed_dscp == 'DSCP AF11':
            exceed_dscp = int(DSCP.AF11.value[1])
        elif exceed_dscp == 'DSCP AF12':
            exceed_dscp = int(DSCP.AF12.value[1])
        elif exceed_dscp == 'DSCP AF13':
            exceed_dscp = int(DSCP.AF13.value[1])
        elif exceed_dscp == 'DSCP AF21':
            exceed_dscp = int(DSCP.AF21.value[1])
        elif exceed_dscp == 'DSCP AF22':
            exceed_dscp = int(DSCP.AF22.value[1])
        elif exceed_dscp == 'DSCP AF23':
            exceed_dscp = int(DSCP.AF23.value[1])
        elif exceed_dscp == 'DSCP AF31':
            exceed_dscp = int(DSCP.AF31.value[1])
        elif exceed_dscp == 'DSCP AF32':
            exceed_dscp = int(DSCP.AF32.value[1])
        else:
            exceed_dscp = int(DSCP.AF33.value[1])

        # Setting of Violate DSCP
        if violate_dscp == 'DSCP CS0':
            violate_dscp = int(DSCP.CS0.value[1])
        elif violate_dscp == 'DSCP CS1':
            violate_dscp = int(DSCP.CS1.value[1])
        elif violate_dscp == 'DSCP CS2':
            violate_dscp = int(DSCP.CS2.value[1])
        elif violate_dscp == 'DSCP CS3':
            violate_dscp = int(DSCP.CS3.value[1])
        elif violate_dscp == 'DSCP CS4':
            violate_dscp = int(DSCP.CS4.value[1])
        elif violate_dscp == 'DSCP CS5':
            violate_dscp = int(DSCP.CS5.value[1])
        elif violate_dscp == 'DSCP CS6':
            violate_dscp = int(DSCP.CS6.value[1])
        elif violate_dscp == 'DSCP CS7':
            violate_dscp = int(DSCP.CS7.value[1])
        elif violate_dscp == 'DSCP AF11':
            violate_dscp = int(DSCP.AF11.value[1])
        elif violate_dscp == 'DSCP AF12':
            violate_dscp = int(DSCP.AF12.value[1])
        elif violate_dscp == 'DSCP AF13':
            violate_dscp = int(DSCP.AF13.value[1])
        elif violate_dscp == 'DSCP AF21':
            violate_dscp = int(DSCP.AF21.value[1])
        elif violate_dscp == 'DSCP AF22':
            violate_dscp = int(DSCP.AF22.value[1])
        elif violate_dscp == 'DSCP AF23':
            violate_dscp = int(DSCP.AF23.value[1])
        elif violate_dscp == 'DSCP AF31':
            violate_dscp = int(DSCP.AF31.value[1])
        elif violate_dscp == 'DSCP AF32':
            violate_dscp = int(DSCP.AF32.value[1])
        else:
            violate_dscp = int(DSCP.AF33.value[1])

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

    def policer_enable_color_aware(self):
        """Enable color-aware mode for policer."""
        self._color_aware = True

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

    @staticmethod
    def dscp_cs0():
        """Return DSCP CS0.

        :returns: DSCP enum CS0 object.
        :rtype: DSCP
        """
        return DSCP.CS0

    @staticmethod
    def dscp_cs1():
        """Return DSCP CS1.

        :returns: DSCP enum CS1 object.
        :rtype: DSCP
        """
        return DSCP.CS1

    @staticmethod
    def dscp_cs2():
        """Return DSCP CS2.

        :returns: DSCP enum CS2 object.
        :rtype: DSCP
        """
        return DSCP.CS2

    @staticmethod
    def dscp_cs3():
        """Return DSCP CS3.

        :returns: DSCP enum CS3 object.
        :rtype: DSCP
        """
        return DSCP.CS3

    @staticmethod
    def dscp_cs4():
        """Return DSCP CS4.

        :returns: DSCP enum CS4 object.
        :rtype: DSCP
        """
        return DSCP.CS4

    @staticmethod
    def dscp_cs5():
        """Return DSCP CS5.

        :returns: DSCP enum CS5 object.
        :rtype: DSCP
        """
        return DSCP.CS5

    @staticmethod
    def dscp_cs6():
        """Return DSCP CS6.

        :returns: DSCP enum CS6 object.
        :rtype: DSCP
        """
        return DSCP.CS6

    @staticmethod
    def dscp_cs7():
        """Return DSCP CS7.

        :returns: DSCP enum CS7 object.
        :rtype: DSCP
        """
        return DSCP.CS7

    @staticmethod
    def dscp_ef():
        """Return DSCP EF.

        :returns: DSCP enum EF object.
        :rtype: DSCP
        """
        return DSCP.EF

    @staticmethod
    def dscp_af11():
        """Return DSCP AF11.

        :returns: DSCP enum AF11 object.
        :rtype: DSCP
        """
        return DSCP.AF11

    @staticmethod
    def dscp_af12():
        """Return DSCP AF12.

        :returns: DSCP enum AF12 object.
        :rtype: DSCP
        """
        return DSCP.AF12

    @staticmethod
    def dscp_af13():
        """Return DSCP AF13.

        :returns: DSCP enum AF13 object.
        :rtype: DSCP
        """
        return DSCP.AF13

    @staticmethod
    def dscp_af21():
        """Return DSCP AF21.

        :returns: DSCP enum AF21 object.
        :rtype: DSCP
        """
        return DSCP.AF21

    @staticmethod
    def dscp_af22():
        """Return DSCP AF22.

        :returns: DSCP enum AF22 object.
        :rtype: DSCP
        """
        return DSCP.AF22

    @staticmethod
    def dscp_af23():
        """Return DSCP AF23.

        :returns: DSCP enum AF23 object.
        :rtype: DSCP
        """
        return DSCP.AF23

    @staticmethod
    def dscp_af31():
        """Return DSCP AF31.

        :returns: DSCP enum AF31 object.
        :rtype: DSCP
        """
        return DSCP.AF31

    @staticmethod
    def dscp_af32():
        """Return DSCP AF32.

        :returns: DSCP enum AF32 object.
        :rtype: DSCP
        """
        return DSCP.AF32

    @staticmethod
    def dscp_af33():
        """Return DSCP AF33.

        :returns: DSCP enum AF33 object.
        :rtype: DSCP
        """
        return DSCP.AF33

    @staticmethod
    def get_dscp_num_value(dscp):
        """Return DSCP numeric value.

        :param dscp: DSCP enum object.
        :type dscp: DSCP
        :returns: DSCP numeric value.
        :rtype: int
        """
        return dscp.num
