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
                                  color_aware, conform_dscp=None,
                                  exceed_dscp=None, violate_dscp=None, is_add=1):

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

    def build_ip_mask(self, proto='', src_ip='', dst_ip='', src_port='',
                      dst_port=''):
        """Build IP ACL mask data in hexstring format.

        :param proto: Protocol number <0-ff>.
        :param src_ip: Source ip address <0-ffffffff>.
        :param dst_ip: Destination ip address <0-ffffffff>.
        :param src_port: Source port number <0-ffff>.
        :param str dst_port: Destination port number <0-ffff>.
        :type proto: str
        :type src_ip: str
        :type dst_ip: str
        :type src_port: str
        :type dst_port:src
        :returns: IP mask in hexstring format.
        :rtype: str
        """
        if dst_port:
            end = 48
        elif src_port:
            end = 44
        elif dst_ip:
            end = 40
        elif src_ip:
            end = 32
        else:
            end = 20

        return ('{!s:0>20}{!s:0>12}{!s:0>8}{!s:0>4}{!s:0>4}'.format(
            proto, src_ip, dst_ip, src_port, dst_port))[0:end]

    def build_ip6_mask(self, next_hdr='', src_ip='', dst_ip='', src_port='',
                       dst_port=''):
        """Build IPv6 ACL mask data in hexstring format.

        :param next_hdr: Next header number <0-ff>.
        :param src_ip: Source ip address <0-ffffffff>.
        :param dst_ip: Destination ip address <0-ffffffff>.
        :param src_port: Source port number <0-ffff>.
        :param dst_port: Destination port number <0-ffff>.
        :type next_hdr: str
        :type src_ip: str
        :type dst_ip: str
        :type src_port: str
        :type dst_port: str
        :returns: IPv6 ACL mask in hexstring format.
        :rtype: str
        """
        if dst_port:
            end = 88
        elif src_port:
            end = 84
        elif dst_ip:
            end = 80
        elif src_ip:
            end = 48
        else:
            end = 14

        return ('{!s:0>14}{!s:0>34}{!s:0>32}{!s:0>4}{!s:0>4}'.format(
            next_hdr, src_ip, dst_ip, src_port, dst_port))[0:end]

    def vpp_create_classify_table_l3(self, node, ip_version, direction, ip_addr):
        """Create classify table for IP address filtering.

        :param node: VPP node to create classify table.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param ip_addr: IPv4 or Ipv6 (depending on the parameter 'ip_version')
            address.
        :type node: dict
        :type ip_version: str
        :type direction: str
        :type ip_addr: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        :raises ValueError: If the parameters 'ip_version' or 'direction' have
            incorrect values.
        """
        mask_f = dict(
            ip4=self.build_ip_mask,
            ip6=self.build_ip6_mask
        )
        if ip_version == "ip4" or ip_version == "ip6":
            ip_addr = binascii.hexlify(ip_address(unicode(ip_addr)).packed)
        else:
            raise ValueError("IP version {ver} is not supported.".
                             format(ver=ip_version))

        if direction == "src":
            mask = mask_f[ip_version](src_ip=ip_addr)
        elif direction == "dst":
            mask = mask_f[ip_version](dst_ip=ip_addr)
        else:
            raise ValueError("Direction {dir} is not supported.".
                             format(dir=direction))
        return self.create_classify_add_del_table(
            node,
            is_add=1,
            mask=binascii.unhexlify(mask),
            match_n_vectors=(len(mask) - 1) // 32 + 1
        )

    def create_classify_add_del_table(self, node, is_add, mask, match_n_vectors=1,
                                      table_index=0xFFFFFFFF, nbuckets=2,
                                      memory_size=2097152, skip_n_vectors=0,
                                      next_table_index=0xFFFFFFFF,
                                      miss_next_index=0xFFFFFFFF, current_data_flag=0,
                                      current_data_offset=0):
        """Add or delete a classify table.

        :param node: VPP node to create classify table.
        :param is_add: If 1 the table is added, if 0 the table is deleted.
        :param mask: ACL mask in hexstring format.
        :param match_n_vectors: Number of vectors to match (Default value = 1).
        :param table_index: Index of the classify table.
            (Default value = 0xFFFFFFFF)
        :param nbuckets: Number of buckets when adding a table.
            (Default value = 2)
        :param memory_size: Memory size when adding a table.
            (Default value = 2097152)
        :param skip_n_vectors: Number of skip vectors (Default value = 0).
        :param next_table_index: Index of next table.
            (Default value = 0xFFFFFFFF)
        :param miss_next_index: Index of miss table.
            (Default value = 0xFFFFFFFF)
        :param current_data_flag: Option to use current node's packet payload
            as the starting point from where packets are classified.
            This option is only valid for L2/L3 input ACL for now.
            0: by default, classify data from the buffer's start location
            1: classify packets from VPP node's current data pointer.
        :param current_data_offset: A signed value to shift the start location
            of the packet to be classified.
            For example, if input IP ACL node is used, L2 header's first byte
            can be accessible by configuring current_data_offset to -14
            if there is no vlan tag.
            This is valid only if current_data_flag is set to 1.
            (Default value = 0)
        :type node: dict
        :type is_add: int
        :type mask: str
        :type match_n_vectors: int
        :type table_index: int
        :type nbuckets: int
        :type memory_size: int
        :type skip_n_vectors: int
        :type next_table_index: int
        :type miss_next_index: int
        :type current_data_flag: int
        :type current_data_offset: int
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        """
        mask_len = ((len(mask) - 1) / 16 + 1) * 16
        mask = mask + '\0' * (mask_len - len(mask))

        args = dict(
            is_add=is_add,
            table_index=table_index,
            nbuckets=nbuckets,
            memory_size=memory_size,
            skip_n_vectors=skip_n_vectors,
            match_n_vectors=match_n_vectors,
            next_table_index=next_table_index,
            miss_next_index=miss_next_index,
            current_data_flag=current_data_flag,
            current_data_offset=current_data_offset,
            mask_len=mask_len,
            mask=mask
        )

        cmd = 'classify_add_del_table'
        err_msg = "Failed to create a classify table on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)
        return int(reply["new_table_index"]), int(reply["skip_n_vectors"]),\
            int(reply["match_n_vectors"])

    def create_classify_add_del_session(self, node, is_add, table_index, match,
                                        opaque_index=0xFFFFFFFF,
                                        hit_next_index=0xFFFFFFFF, advance=0,
                                        action=0, metadata=0):
        """Add or delete a classify session.

        :param node: VPP node to create classify session.
        :param is_add: If 1 the session is added, if 0 the session is deleted.
        :param table_index: Index of the table to add/del the session.
        :param match: For add, match value for session, required, needs to
            include bytes in front with length of skip_n_vectors of target table
            times sizeof (u32x4) (values of those bytes will be ignored).
        :param opaque_index: For add, opaque_index of new session.
            (Default value = 0xFFFFFFFF)
        :param hit_next_index: For add, hit_next_index of new session.
            (Default value = 0xFFFFFFFF)
        :param advance: For add, advance value for session. (Default value = 0)
        :param action: 0: No action (by default) metadata is not used.
            1: Classified IP packets will be looked up from the specified ipv4
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            2: Classified IP packets will be looked up from the specified ipv6
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            3: Classified packet will be steered to source routig policy of
               given index (in metadata).
               This is only valid for IPv6 packets redirected to a source
               routing node.
        :param metadata: Valid only if action != 0
            VRF id if action is 1 or 2. SR policy index if action is 3.
            (Default value = 0)
        :type node: dict
        :type is_add: int
        :type table_index: int
        :type match: str
        :type opaque_index: int
        :type hit_next_index: int
        :type advance: int
        :type action: int
        :type metadata: int
        """

        match_len = ((len(match) - 1) / 16 + 1) * 16
        match = match + '\0' * (match_len - len(match))
        args = dict(
            is_add=is_add,
            table_index=int(table_index),
            hit_next_index=hit_next_index,
            opaque_index=opaque_index,
            advance=int(advance),
            action=action,
            metadata=metadata,
            match_len=match_len,
            match=match
        )
        logger.debug(args)
        cmd = 'classify_add_del_session'
        err_msg = "Failed to create a classify session on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    def build_ip_match(self, proto=0, src_ip='', dst_ip='', src_port=0, dst_port=0):
        """Build IP ACL match data in hexstring format.

        :param proto: Protocol number with valid option "x".
        :param src_ip: Source ip address with format of "x.x.x.x".
        :param dst_ip: Destination ip address with format of "x.x.x.x".
        :param src_port: Source port number "x".
        :param dst_port: Destination port number "x".
        :type proto: int
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :returns: IP ACL match data in hexstring format.
        :rtype: str
        """
        if src_ip:
            src_ip = binascii.hexlify(ip_address(unicode(src_ip)).packed)
        if dst_ip:
            dst_ip = binascii.hexlify(ip_address(unicode(dst_ip)).packed)
        if dst_port:
            end = 48
        elif src_port:
            end = 44
        elif dst_ip:
            end = 40
        elif src_ip:
            end = 32
        else:
            end = 20

        return ('{!s:0>20}{!s:0>12}{!s:0>8}{!s:0>4}{!s:0>4}'.format(
            hex(proto)[2:], src_ip, dst_ip, hex(src_port)[2:],
            hex(dst_port)[2:]))[0:end]

    def build_ip6_match(self, next_hdr=0, src_ip='', dst_ip='', src_port=0,
                        dst_port=0):
        """Build IPv6 ACL match data in hexstring format.

        :param next_hdr: Next header number with valid option "x".
        :param src_ip: Source ip6 address with format of "xxxx:xxxx::xxxx".
        :param dst_ip: Destination ip6 address with format of
            "xxxx:xxxx::xxxx".
        :param src_port: Source port number "x".
        :param dst_port: Destination port number "x".
        :type next_hdr: int
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :returns: IPv6 ACL match data in hexstring format.
        :rtype: str
        """
        if src_ip:
            src_ip = binascii.hexlify(ip_address(unicode(src_ip)).packed)
        if dst_ip:
            dst_ip = binascii.hexlify(ip_address(unicode(dst_ip)).packed)
        if dst_port:
            end = 88
        elif src_port:
            end = 84
        elif dst_ip:
            end = 80
        elif src_ip:
            end = 48
        else:
            end = 14

        return ('{!s:0>14}{!s:0>34}{!s:0>32}{!s:0>4}{!s:0>4}'.format(
            hex(next_hdr)[2:], src_ip, dst_ip, hex(src_port)[2:],
            hex(dst_port)[2:]))[0:end]

    # Configure Classify Session
    def vpp_configure_classify_session_l3(self, node, acl_method, table_index,
                                          ip_version, direction, address):
        """Configuration of classify session for IP address filtering.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param address: IPv4 or IPv6 address.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type ip_version: str
        :type direction: str
        :type address: str
        :raises ValueError: If the parameter 'direction' has incorrect value.
        """
        match_f = dict(
            ip4=self.build_ip_match,
            ip6=self.build_ip6_match
        )
        if direction == "src":
            match = match_f[ip_version](src_ip=address)
        elif direction == "dst":
            match = match_f[ip_version](dst_ip=address)
        else:
            raise ValueError("Direction {dir} is not supported.".
                             format(dir=direction))
        action = dict(
            permit=0,
            deny=1
        )
        self.create_classify_add_del_session(
            node,
            is_add=1,
            table_index=table_index,
            match=binascii.unhexlify(match),
            action=action[acl_method])

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
        logger.debug("The dictonary arguments are {args_in}"
                     .format(args_in=args_in))
        err_msg = 'Policer Classify Set Interface Failed'
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args_in).get_reply(err_msg)
