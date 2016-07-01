# Copyright (c) 2016 Cisco and/or its affiliates.
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

from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.VatJsonUtil import VatJsonUtil
from resources.libraries.python.topology import Topology


# pylint: disable=too-few-public-methods
class PolicerRateType(Enum):
    """Policer rate types."""
    KBPS = 'kbps'
    PPS = 'pps'

    def __init__(self, string):
        self.string = string


# pylint: disable=invalid-name
class PolicerRoundType(Enum):
    """Policer round types."""
    CLOSEST = 'closest'
    UP = 'up'
    DOWN = 'down'

    def __init__(self, string):
        self.string = string


class PolicerType(Enum):
    """Policer type."""
    P_1R2C = '1r2c'
    P_1R3C = '1r3c'
    P_2R3C_2698 = '2r3c-2698'
    P_2R3C_4115 = '2r3c-4115'
    P_2R3C_MEF5CF1 = '2r3c-mef5cf1'

    def __init__(self, string):
        self.string = string


class PolicerAction(Enum):
    """Policer action."""
    DROP = 'drop'
    TRANSMIT = 'transmit'
    MARK_AND_TRANSMIT = 'mark-and-transmit'

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
# pylint: disable=too-many-public-methods
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

    def policer_set_configuration(self):
        """Configure policer on VPP node.

        ...note:: First set all required parameters.
        """
        node = self._node

        # create policer
        color_aware = ''
        if self._color_aware:
            color_aware = 'color-aware'

        # pylint: disable=no-member
        conform_action = self._conform_action.value

        if PolicerAction.MARK_AND_TRANSMIT == self._conform_action:
            conform_action += ' {0}'.format(self._conform_dscp.string)

        exceed_action = self._exceed_action.value
        if PolicerAction.MARK_AND_TRANSMIT == self._exceed_action:
            exceed_action += ' {0}'.format(self._exceed_dscp.string)

        violate_action = self._violate_action.value
        if PolicerAction.MARK_AND_TRANSMIT == self._violate_action:
            violate_action += ' {0}'.format(self._violate_dscp.string)

        out = VatExecutor.cmd_from_template(node,
                                            "policer/policer_add_3c.vat",
                                            name=self._policer_name,
                                            cir=self._cir,
                                            eir=self._eir,
                                            cb=self._cb,
                                            eb=self._eb,
                                            rate_type=self._rate_type.value,
                                            round_type=self._round_type.value,
                                            p_type=self._policer_type.value,
                                            conform_action=conform_action,
                                            exceed_action=exceed_action,
                                            violate_action=violate_action,
                                            color_aware=color_aware)
        # pylint: enable=no-member

        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add policer {0} failed on {1}'.format(self._policer_name,
                                                           node['host']))

        policer_index = out[0].get('policer_index')

        # create classify table
        ip_version = 'ip4'
        table_type = PolicerClassifyTableType.IP4_TABLE
        direction = 'src'

        if self._classify_match_is_src:
            if 6 == ip_address(unicode(self._classify_match_ip)).version:
                ip_version = 'ip6'
                table_type = PolicerClassifyTableType.IP6_TABLE
        else:
            if 6 == ip_address(unicode(self._classify_match_ip)).version:
                ip_version = 'ip6'
                table_type = PolicerClassifyTableType.IP6_TABLE
            direction = 'dst'

        out = VatExecutor.cmd_from_template(node,
                                            "classify_add_table.vat",
                                            ip_version=ip_version,
                                            direction=direction)

        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add classify table failed on {0}'.format(node['host']))

        new_table_index = out[0].get('new_table_index')
        skip_n_vectors = out[0].get('skip_n_vectors')
        match_n_vectors = out[0].get('match_n_vectors')

        # create classify session
        match = 'l3 {0} {1} {2}'.format(ip_version,
                                        direction,
                                        self._classify_match_ip)

        out = VatExecutor.cmd_from_template(
            node,
            "policer/policer_classify_add_session.vat",
            policer_index=policer_index,
            pre_color=self._classify_precolor.value, # pylint: disable=no-member
            table_index=new_table_index,
            skip_n=skip_n_vectors,
            match_n=match_n_vectors,
            match=match)

        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Add classify session failed on {0}'.format(node['host']))

        # set classify interface
        out = VatExecutor.cmd_from_template(
            node,
            "policer/policer_classify_set_interface.vat",
            sw_if_index=self._sw_if_index,
            table_type=table_type.value, # pylint: disable=no-member
            table_index=new_table_index)

        VatJsonUtil.verify_vat_retval(
            out[0],
            err_msg='Set classify interface failed on {0}'.format(node['host']))

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

    def policer_set_name(self, name):
        """Set policer name.

        :param name: Policer name.
        :type name: str
        """
        self._policer_name = name

    def policer_set_node(self, node):
        """Set node to setup policer on.

        :param node: VPP node.
        :type node: dict
        """
        self._node = node

    def policer_set_cir(self, cir):
        """Set policer CIR.

        :param cir: Committed Information Rate.
        :type cir: int
        """
        self._cir = cir

    def policer_set_eir(self, eir):
        """Set polcier EIR.

        :param eir: Excess Information Rate.
        :type eir: int
        """
        self._eir = eir

    def policer_set_cb(self, cb):
        """Set policer CB.

        :param cb: Committed Burst size.
        :type cb: int
        """
        self._cb = cb

    def policer_set_eb(self, eb):
        """Set policer EB.

        :param eb: Excess Burst size.
        :type eb: int
        """
        self._eb = eb

    def policer_set_rate_type_kbps(self):
        """Set policer rate type to kbps."""
        self._rate_type = PolicerRateType.KBPS

    def policer_set_rate_type_pps(self):
        """Set policer rate type to pps."""
        self._rate_type = PolicerRateType.PPS

    def policer_set_round_type_closest(self):
        """Set policer round type to closest."""
        self._round_type = PolicerRoundType.CLOSEST

    def policer_set_round_type_up(self):
        """Set policer round type to up."""
        self._round_type = PolicerRoundType.UP

    def policer_set_round_type_down(self):
        """Set policer round type to down."""
        self._round_type = PolicerRoundType.DOWN

    def policer_set_type_1r2c(self):
        """Set policer type to 1r2c."""
        self._policer_type = PolicerType.P_1R2C

    def policer_set_type_1r3c(self):
        """Set policer type to 1r3c RFC2697."""
        self._policer_type = PolicerType.P_1R3C

    def policer_set_type_2r3c_2698(self):
        """Set policer type to 2r3c RFC2698."""
        self._policer_type = PolicerType.P_2R3C_2698

    def policer_set_type_2r3c_4115(self):
        """Set policer type to 2r3c RFC4115."""
        self._policer_type = PolicerType.P_2R3C_4115

    def policer_set_type_2r3c_mef5cf1(self):
        """Set policer type to 2r3c MEF5CF1."""
        self._policer_type = PolicerType.P_2R3C_MEF5CF1

    def policer_set_conform_action_drop(self):
        """Set policer conform-action to drop."""
        self._conform_action = PolicerAction.DROP

    def policer_set_conform_action_transmit(self):
        """Set policer conform-action to transmit."""
        self._conform_action = PolicerAction.TRANSMIT

    def policer_set_conform_action_mark_and_transmit(self, dscp):
        """Set policer conform-action to mark-and-transmit.

        :param dscp: DSCP value to mark.
        :type dscp: DSCP
        """
        self._conform_action = PolicerAction.MARK_AND_TRANSMIT
        self._conform_dscp = dscp

    def policer_set_exceed_action_drop(self):
        """Set policer exceed-action to drop."""
        self._exceed_action = PolicerAction.DROP

    def policer_set_exceed_action_transmit(self):
        """Set policer exceed-action to transmit."""
        self._exceed_action = PolicerAction.TRANSMIT

    def policer_set_exceed_action_mark_and_transmit(self, dscp):
        """Set policer exceed-action to mark-and-transmit.

        :param dscp: DSCP value to mark.
        :type dscp: DSCP
        """
        self._exceed_action = PolicerAction.MARK_AND_TRANSMIT
        self._exceed_dscp = dscp

    def policer_set_violate_action_drop(self):
        """Set policer violate-action to drop."""
        self._violate_action = PolicerAction.DROP

    def policer_set_violate_action_transmit(self):
        """Set policer violate-action to transmit."""
        self._violate_action = PolicerAction.TRANSMIT

    def policer_set_violate_action_mark_and_transmit(self, dscp):
        """Set policer violate-action to mark-and-transmit.

        :param dscp: DSCP value to mark.
        :type dscp: DSCP
        """
        self._violate_action = PolicerAction.MARK_AND_TRANSMIT
        self._violate_dscp = dscp

    def policer_enable_color_aware(self):
        """Enable color-aware mode for policer."""
        self._color_aware = True

    def policer_classify_set_precolor_conform(self):
        """Set policer classify pre-color to conform-color."""
        self._classify_precolor = PolicerClassifyPreColor.CONFORM_COLOR

    def policer_classify_set_precolor_exceed(self):
        """Set policer classify pre-color to exceeed-color."""
        self._classify_precolor = PolicerClassifyPreColor.EXCEED_COLOR

    def policer_classify_set_interface(self, interface):
        """Set policer classify interface.

        :param interface: Interface name or sw_if_index.
        :type interface: str or int
        .. note:: First set node with policer_set_node.
        """
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

        :return: DSCP enum CS0 object.
        :rtype: DSCP
        """
        return DSCP.CS0

    @staticmethod
    def dscp_cs1():
        """Return DSCP CS1.

        :return: DSCP enum CS1 object.
        :rtype: DSCP
        """
        return DSCP.CS1

    @staticmethod
    def dscp_cs2():
        """Return DSCP CS2.

        :return: DSCP enum CS2 object.
        :rtype: DSCP
        """
        return DSCP.CS2

    @staticmethod
    def dscp_cs3():
        """Return DSCP CS3.

        :return: DSCP enum CS3 object.
        :rtype: DSCP
        """
        return DSCP.CS3

    @staticmethod
    def dscp_cs4():
        """Return DSCP CS4.

        :return: DSCP enum CS4 object.
        :rtype: DSCP
        """
        return DSCP.CS4

    @staticmethod
    def dscp_cs5():
        """Return DSCP CS5.

        :return: DSCP enum CS5 object.
        :rtype: DSCP
        """
        return DSCP.CS5

    @staticmethod
    def dscp_cs6():
        """Return DSCP CS6.

        :return: DSCP enum CS6 object.
        :rtype: DSCP
        """
        return DSCP.CS6

    @staticmethod
    def dscp_cs7():
        """Return DSCP CS7.

        :return: DSCP enum CS7 object.
        :rtype: DSCP
        """
        return DSCP.CS7

    @staticmethod
    def dscp_ef():
        """Return DSCP EF.

        :return: DSCP enum EF object.
        :rtype: DSCP
        """
        return DSCP.EF

    @staticmethod
    def dscp_af11():
        """Return DSCP AF11.

        :return: DSCP enum AF11 object.
        :rtype: DSCP
        """
        return DSCP.AF11

    @staticmethod
    def dscp_af12():
        """Return DSCP AF12.

        :return: DSCP enum AF12 object.
        :rtype: DSCP
        """
        return DSCP.AF12

    @staticmethod
    def dscp_af13():
        """Return DSCP AF13.

        :return: DSCP enum AF13 object.
        :rtype: DSCP
        """
        return DSCP.AF13

    @staticmethod
    def dscp_af21():
        """Return DSCP AF21.

        :return: DSCP enum AF21 object.
        :rtype: DSCP
        """
        return DSCP.AF21

    @staticmethod
    def dscp_af22():
        """Return DSCP AF22.

        :return: DSCP enum AF22 object.
        :rtype: DSCP
        """
        return DSCP.AF22

    @staticmethod
    def dscp_af23():
        """Return DSCP AF23.

        :return: DSCP enum AF23 object.
        :rtype: DSCP
        """
        return DSCP.AF23

    @staticmethod
    def dscp_af31():
        """Return DSCP AF31.

        :return: DSCP enum AF31 object.
        :rtype: DSCP
        """
        return DSCP.AF31

    @staticmethod
    def dscp_af32():
        """Return DSCP AF32.

        :return: DSCP enum AF32 object.
        :rtype: DSCP
        """
        return DSCP.AF32

    @staticmethod
    def dscp_af33():
        """Return DSCP AF33.

        :return: DSCP enum AF33 object.
        :rtype: DSCP
        """
        return DSCP.AF33

    @staticmethod
    def get_dscp_num_value(dscp):
        """Return DSCP numeric value.

        :param dscp: DSCP enum object.
        :type dscp: DSCP
        :return: DSCP numeric value.
        :rtype: int
        """
        return dscp.num
