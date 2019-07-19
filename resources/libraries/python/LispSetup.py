# Copyright (c) 2016-2019 Cisco and/or its affiliates.
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

"""Library to set up Lisp in topology."""

from ipaddress import ip_address
from robot.api import logger

from resources.libraries.python.topology import NodeType
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.VatExecutor import VatExecutor


class LispStatus(object):
    """Class for lisp API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_lisp_enable_disable(node, state):
        """Enable/Disable lisp in the VPP node in topology.

        :param node: Node of the test topology.
        :param state: State of the lisp, enable or disable.
        :type node: dict
        :type state: str
        """
# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-ip4base-func.robot
#         /csit/tests/vpp/func/ip4_tunnels/lisp/api-crud-lisp-func.robot

        args = dict(is_en=0 if state == 'disable' else 1)

        cmd = 'lisp_enable_disable'
        err_msg = "Failed to set LISP status on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

#        VatExecutor.cmd_from_template(node,
#                                      'lisp/lisp_status.vat',
#                                      state=state)


class LispRemoteMapping(object):
    """Class for lisp remote mapping API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_remote_mapping(node, vni, deid, deid_prefix, seid,
                                    seid_prefix, rloc, is_mac=False):
        """Add lisp remote mapping on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :param rloc: Receiver locator.
        :param is_mac: Set to True if the deid/seid is MAC address.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        :type rloc: str
        :type is_mac: bool
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-l2bdbasemaclrn-func.robot

        # _(lisp_add_del_remote_mapping, "add|del vni <vni> eid <dest-eid> " \
        #         22158
        # "[seid <seid>] " \
        #         22159
        # "rloc <locator> p <prio> " \
        #         22160
        # "w <weight> [rloc <loc> ... ] " \
        #         22161
        # "action <action> [del-all]")

        # u8
        # is_add
        # u8
        # is_src_dst
        # u8
        # del_all
        # u32
        # vni
        # u8
        # action
        # u8
        # eid_type
        # u8
        # eid[16]
        # u8
        # eid_len
        # u8
        # seid[16]
        # u8
        # seid_len
        # u32
        # rloc_num
        # vl_api_remote_locator_t
        # rlocs[rloc_num]

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            eid_packed = ip_address(unicode(deid)).packed
            seid_packed = ip_address(unicode(seid)).packed
            eid_len = deid_prefix
            seid_len = seid_prefix
        else:
            eid_type = 2
            eid_packed = deid.replace(':', '')
            seid_packed = seid.replace(':', '')
            eid_len = 0
            seid_len = 0

        rlocs = [dict(is_ip4=1 if ip_address(unicode(rloc)).version == 4 else 0,
                     addr=ip_address(unicode(rloc)).packed)]

        args = dict(is_add=1,
                    is_src_dst=1,
                    vni=vni,
                    eid_type=eid_type,
                    eid=eid_packed,
                    eid_len=eid_len,
                    seid=seid_packed,
                    seid_len=seid_len,
                    rloc_num=1,
                    rlocs=rlocs)

        logger.info(args)

        cmd = 'lisp_add_del_remote_mapping'
        err_msg = "Failed to add remote mapping on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # if is_mac:
        #     deid_prefix = ''
        #     seid_prefix = ''
        # else:
        #     deid_prefix = '/{}'.format(deid_prefix)
        #     seid_prefix = '/{}'.format(seid_prefix)
        # VatExecutor.cmd_from_template(node,
        #                               'lisp/add_lisp_remote_mapping.vat',
        #                               vni=vni,
        #                               deid=deid,
        #                               deid_prefix=deid_prefix,
        #                               seid=seid,
        #                               seid_prefix=seid_prefix,
        #                               rloc=rloc)

    @staticmethod
    def vpp_del_lisp_remote_mapping(node, vni, deid, deid_prefix, seid,
                                    seid_prefix, rloc):
        """Delete lisp remote mapping on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :param rloc: Receiver locator.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        :type rloc: str
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lispgpe-ip6base-func.robot

        is_mac = False

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            eid_packed = ip_address(unicode(deid)).packed
            seid_packed = ip_address(unicode(seid)).packed
            eid_len = deid_prefix
            seid_len = seid_prefix
        else:
            eid_type = 2
            eid_packed = deid.replace(':', '')
            seid_packed = seid.replace(':', '')
            eid_len = 0
            seid_len = 0

        rlocs = [dict(is_ip4=1 if ip_address(unicode(rloc)).version == 4 else 0,
                     addr=ip_address(unicode(rloc)).packed)]

        args = dict(is_add=0,
                    is_src_dst=1,
                    vni=vni,
                    eid_type=eid_type,
                    eid=eid_packed,
                    eid_len=eid_len,
                    seid=seid_packed,
                    seid_len=seid_len,
                    rloc_num=1,
                    rlocs=rlocs)

        logger.info(args)

        cmd = 'lisp_add_del_remote_mapping'
        err_msg = "Failed to delete remote mapping on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)


        # VatExecutor.cmd_from_template(node,
        #                               'lisp/del_lisp_remote_mapping.vat',
        #                               vni=vni,
        #                               deid=deid,
        #                               deid_prefix=deid_prefix,
        #                               seid=seid,
        #                               seid_prefix=seid_prefix,
        #                               rloc=rloc)


class LispAdjacency(object):
    """Class for lisp adjacency API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_adjacency(node, vni, deid, deid_prefix, seid,
                               seid_prefix, is_mac=False):
        """Add lisp adjacency on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :param is_mac: Set to True if the deid/seid is MAC address.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        :type is_mac: bool
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-ip4base-func.robot

        # u8
        # is_add
        #
        # u32
        # vni
        #
        # u8
        # eid_type
        #
        # u8
        # reid[16]
        #
        # u8
        # leid[16]
        #
        # u8
        # reid_len
        #
        # u8
        # leid_len

        # _(lisp_add_del_adjacency, "add|del vni <vni> reid <remote-eid> leid " \
        #         22163
        # "<local-eid>")

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            reid = ip_address(unicode(deid)).packed
            leid = ip_address(unicode(seid)).packed
            reid_len = deid_prefix
            leid_len = seid_prefix
        else:
            eid_type = 2
            reid = deid.replace(':', '')
            leid = seid.replace(':', '')
            reid_len = 0
            leid_len = 0

        args = dict(is_add=1,
                    vni=vni,
                    eid_type=eid_type,
                    reid=reid,
                    reid_len=reid_len,
                    leid=leid,
                    leid_len=leid_len)

        logger.info(args)

        cmd = 'lisp_add_del_adjacency'
        err_msg = "Failed to add lisp adjacency on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # if is_mac:
        #     deid_prefix = ''
        #     seid_prefix = ''
        # else:
        #     deid_prefix = '/{}'.format(deid_prefix)
        #     seid_prefix = '/{}'.format(seid_prefix)
        # VatExecutor.cmd_from_template(node,
        #                               'lisp/add_lisp_adjacency.vat',
        #                               vni=vni,
        #                               deid=deid,
        #                               deid_prefix=deid_prefix,
        #                               seid=seid,
        #                               seid_prefix=seid_prefix)

    @staticmethod
    def vpp_del_lisp_adjacency(node, vni, deid, deid_prefix, seid,
                               seid_prefix):
        """Delete lisp adjacency on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lispgpe-ip6base-func.robot

        is_mac = False

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            reid = ip_address(unicode(deid)).packed
            leid = ip_address(unicode(seid)).packed
            reid_len = deid_prefix
            leid_len = seid_prefix
        else:
            eid_type = 2
            reid = deid.replace(':', '')
            leid = seid.replace(':', '')
            reid_len = 0
            leid_len = 0

        args = dict(is_add=0,
                    vni=vni,
                    eid_type=eid_type,
                    reid=reid,
                    reid_len=reid_len,
                    leid=leid,
                    leid_len=leid_len)

        logger.info(args)

        cmd = 'lisp_add_del_adjacency'
        err_msg = "Failed to delete lisp adjacency on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # VatExecutor.cmd_from_template(node,
        #                               'lisp/del_lisp_adjacency.vat',
        #                               vni=vni,
        #                               deid=deid,
        #                               deid_prefix=deid_prefix,
        #                               seid=seid,
        #                               seid_prefix=seid_prefix)


class LispGpeStatus(object):
    """Clas for LISP GPE status manipulation."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_lisp_gpe_enable_disable(node, state):
        """Change the state of LISP GPE - enable or disable.

        :param node: VPP node.
        :param state: Requested state - enable or disable.
        :type node: dict
        :type state: str
        """
# used in /csit/tests/honeycomb/func/mgmt-cfg-lispgpe-apihc-apivat-func.robot
#         /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lispgpe-ip4base-func.robot
#         /csit/tests/vpp/perf/crypto/10ge2p1x710-ethip4ipsectptlispgpe-ip4base-aes128cbc-hmac256sha-ndrpdr.robot

        args = dict(is_en=0 if state == 'disable' else 1)

        cmd = 'gpe_enable_disable'
        err_msg = "Failed to set LISP GPE status on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)


#        VatExecutor.cmd_from_template(node, 'lisp/lisp_gpe_status.vat',
#                                      state=state)


# class LispGpeIface(object):
#     """Class for Lisp gpe interface API."""
#
#     def __init__(self):
#         pass
#
#     @staticmethod
#     def vpp_lisp_gpe_iface(node, state):
#         """Set lisp gpe interface up or down on the VPP node in topology.
#
#         :param node: VPP node.
#         :param state: State of the gpe iface, up or down.
#         :type node: dict
#         :type state: str
#         """
#
# # not used in robot, used in lispsetup class
#
#         VatExecutor.cmd_from_template(node, 'lisp/lisp_gpe_iface.vat',
#                                       state=state)
#

class LispGpeForwardEntry(object):
    """The functionality needed for these methods is not implemented in VPP
    (VAT). Bug https://jira.fd.io/browse/VPP-334 was open to cover this issue.

    TODO: Implement when VPP-334 is fixed.
    """

# not used

    def __init__(self):
        pass

    @staticmethod
    def add_lisp_gpe_forward_entry(node, *args):
        """Not implemented"""
        # TODO: Implement when VPP-334 is fixed.
        pass

    @staticmethod
    def del_lisp_gpe_forward_entry(node, *args):
        """Not implemented"""
        # TODO: Implement when VPP-334 is fixed.
        pass


class LispMapResolver(object):
    """Class for Lisp map resolver API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_map_resolver(node, map_resolver_ip):
        """Set lisp map resolver on the VPP node in topology.

        :param node: VPP node.
        :param map_resolver_ip: IP address of the map resolver.
        :type node: dict
        :type map_resolver_ip: str
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-l2bdbasemaclrn-func.robot

        args = dict(is_add=1,
                    is_ipv6=0 if ip_address(unicode(map_resolver_ip)).version == 4 else 1,
                    ip_address=ip_address(unicode(map_resolver_ip)).packed)

        cmd = 'lisp_add_del_map_resolver'
        err_msg = "Failed to add map resolver on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)


#        VatExecutor.cmd_from_template(node,
#                                      'lisp/add_lisp_map_resolver.vat',
#                                      address=map_resolver_ip)

    @staticmethod
    def vpp_del_map_resolver(node, map_resolver_ip):
        """Unset lisp map resolver on the VPP node in topology.

        :param node: VPP node.
        :param map_resolver_ip: IP address of the map resolver.
        :type node: dict
        :type map_resolver_ip: str
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/api-crud-lisp-func.robot

        args = dict(is_add=0,
                    is_ipv6=0 if ip_address(unicode(map_resolver_ip)).version == 4 else 1,
                    ip_address=ip_address(unicode(map_resolver_ip)).packed)

        cmd = 'lisp_add_del_map_resolver'
        err_msg = "Failed to delete map resolver on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

#        VatExecutor.cmd_from_template(node,
#                                      'lisp/del_lisp_map_resolver.vat',
#                                      address=map_resolver_ip)


class LispLocalEid(object):
    """Class for Lisp local eid API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_local_eid(node, locator_set_name, vni, eid,
                               prefix_len=None):
        """Set lisp eid address on the VPP node in topology.

        :param node: VPP node.
        :param locator_set_name: Name of the locator_set.
        :param vni: vni value.
        :param eid: Eid value.
        :param prefix_len: prefix len if the eid is IP address.
        :type node: dict
        :type locator_set_name: str
        :type vni: int
        :type eid: str
        :type prefix_len: int
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-ip4base-func.robot

        # u8
        # is_add
        #
        # u8
        # eid_type
        #
        # u8
        # eid[16]
        #
        # u8
        # prefix_len
        #
        # u8
        # locator_set_name[64]
        #
        # u32
        # vni
        #
        # u16
        # key_id
        #
        # u8
        # key[64]

        # 2148
        # _(lisp_add_del_local_eid, "vni <vni> eid " \
        #         22149
        # "<ipv4|ipv6>/<prefix> | <L2 address> " \
        #         22150
        # "locator-set <locator_name> [del]" \
        #         22151
        # "[key-id sha1|sha256 secret-key <secret-key>]")
        #

        if prefix_len:
            eid_type =  0 if ip_address(unicode(eid)).version == 4 else 1
            eid_packed = ip_address(unicode(eid)).packed
        else:
            eid_type = 2
            eid_packed = eid.replace(':', '')

        args = dict(is_add=1,
                    eid_type=eid_type,
                    eid=eid_packed,
                    prefix_len=prefix_len,
                    locator_set_name=locator_set_name,
                    vni=vni)

        logger.info(args)

        cmd = 'lisp_add_del_local_eid'
        err_msg = "Failed to add local eid on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # if prefix_len is not None:
        #     VatExecutor.cmd_from_template(node,
        #                                   'lisp/add_lisp_local_eid.vat',
        #                                   vni=vni,
        #                                   eid=eid,
        #                                   eid_prefix=prefix_len,
        #                                   locator_name=locator_set_name)
        # else:
        #     VatExecutor.cmd_from_template(node,
        #                                   'lisp/add_lisp_local_eid_mac.vat',
        #                                   vni=vni,
        #                                   eid=eid,
        #                                   locator_name=locator_set_name)

    @staticmethod
    def vpp_del_lisp_local_eid(node, locator_set_name, vni, eid,
                               prefix_len=None):
        """Set lisp eid addres on the VPP node in topology.

        :param node: VPP node.
        :param locator_set_name: Name of the locator_set.
        :param vni: vni value.
        :param eid: Eid value.
        :param prefix_len: prefix len if the eid is IP address.
        :type node: dict
        :type locator_set_name: str
        :type vni: int
        :type eid: str
        :type prefix_len: int
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/api-crud-lisp-func.robot

        if prefix_len:
            eid_type =  0 if ip_address(unicode(eid)).version == 4 else 1
            eid_packed = ip_address(unicode(eid)).packed
        else:
            eid_type = 2
            eid_packed = eid.replace(':', '')

        args = dict(is_add=0,
                    eid_type=eid_type,
                    eid=eid_packed,
                    prefix_len=prefix_len,
                    locator_set_name=locator_set_name,
                    vni=vni)

        logger.info(args)

        cmd = 'lisp_add_del_local_eid'
        err_msg = "Failed to add local eid on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # if prefix_len is not None:
        #     VatExecutor.cmd_from_template(node,
        #                                   'lisp/del_lisp_local_eid.vat',
        #                                   vni=vni,
        #                                   eid=eid,
        #                                   eid_prefix=prefix_len,
        #                                   locator_name=locator_set_name)
        # else:
        #     VatExecutor.cmd_from_template(node,
        #                                   'lisp/del_lisp_local_eid_mac.vat',
        #                                   vni=vni,
        #                                   eid=eid,
        #                                   locator_name=locator_set_name)


class LispLocator(object):
    """Class for the Lisp Locator API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_locator(node, locator_name, sw_if_index, priority, weight):
        """Set lisp locator on the VPP node in topology.

        :param node: VPP node.
        :param locator_name: Name of the locator_set.
        :param sw_if_index: sw_if_index if the interface.
        :param priority: priority of the locator.
        :param weight: weight of the locator.
        :type node: dict
        :type locator_name: str
        :type sw_if_index: int
        :type priority: int
        :type weight: int
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-l2bdbasemaclrn-func.robot
#         Data
#         Fields

#         u8
#         is_add
#
#         u8
#         locator_set_name[64]
#
#         u32
#         sw_if_index
#
#         u8
#         priority
#
#         u8
#         weight

        args = dict(is_add=1,
                    locator_set_name=locator_name,
                    sw_if_index=sw_if_index,
                    priority=priority,
                    weight=weight)

        cmd = 'lisp_add_del_locator'
        err_msg = "Failed to add locator on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # VatExecutor.cmd_from_template(node,
        #                               'lisp/add_lisp_locator.vat',
        #                               lisp_name=locator_name,
        #                               sw_if_index=sw_if_index,
        #                               priority=priority,
        #                               weight=weight)

    @staticmethod
    def vpp_del_lisp_locator(node, locator_name, sw_if_index, priority, weight):
        """Unset lisp locator on the VPP node in topology.

        :param node: VPP node.
        :param locator_name: Name of the locator_set.
        :param sw_if_index: sw_if_index if the interface.
        :param priority: priority of the locator.
        :param weight: weight of the locator.
        :type node: dict
        :type locator_name: str
        :type sw_if_index: int
        :type priority: int
        :type weight: int
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/api-crud-lisp-func.robot

        args = dict(is_add=0,
                    locator_set_name=locator_name,
                    sw_if_index=sw_if_index,
                    priority=priority,
                    weight=weight)

        cmd = 'lisp_add_del_locator'
        err_msg = "Failed to delete locator on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # VatExecutor.cmd_from_template(node,
        #                               'lisp/del_lisp_locator.vat',
        #                               lisp_name=locator_name,
        #                               sw_if_index=sw_if_index,
        #                               priority=priority,
        #                               weight=weight)


class LispLocatorSet(object):
    """Class for Lisp Locator Set API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_locator_set(node, name):
        """Add lisp locator_set on VPP.

        :param node: VPP node.
        :param name: VPP locator name.
        :type node: dict
        :type name: str
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-l2bdbasemaclrn-func.robot

        args = dict(is_add=1,
                    locator_set_name=name,
                    locator_num=0,
                    locators=[])

        cmd = 'lisp_add_del_locator_set'
        err_msg = "Failed to add locator set on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)


       # VatExecutor.cmd_from_template(node,
       #                               'lisp/add_lisp_locator_set.vat',
       #                               lisp_name=name)

    @staticmethod
    def vpp_del_lisp_locator_set(node, name):
        """Del lisp locator_set on VPP.

        :param node: VPP node.
        :param name: VPP locator name.
        :type node: dict
        :type name: str
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/api-crud-lisp-func.robot

        args = dict(is_add=0,
                    locator_set_name=name,
                    locator_num=0,
                    locators=[])

        cmd = 'lisp_add_del_locator_set'
        err_msg = "Failed to delete locator set on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        # VatExecutor.cmd_from_template(node,
        #                               'lisp/del_lisp_locator_set.vat',
        #                               lisp_name=name)


class LispSetup(object):
    """Lisp setup in topology."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_set_lisp_locator_set(node, locator_set_list):
        """Set lisp locator_sets on VPP node in topology.

        :param node: VPP node.
        :param locator_set_list: List of locator_set.
        :type node: dict
        :type locator_set_list: list
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Node is not DUT')

        logger.info(locator_set_list)

        lisp_locator = LispLocator()
        lisp_locator_set = LispLocatorSet()
        for locator_set in locator_set_list:
            locator_set_name = locator_set.get('locator-set')
            locator_list = locator_set.get('locator')
            lisp_locator_set.vpp_add_lisp_locator_set(node,
                                                      locator_set_name)
            for locator in locator_list:
                sw_if_index = locator.get('locator-index')
                priority = locator.get('priority')
                weight = locator.get('weight')
                logger.info(node)
                logger.info(locator_set_name)
                logger.info(sw_if_index)
                logger.info(priority)
                logger.info(weight)
                lisp_locator.vpp_add_lisp_locator(node,
                                                  locator_set_name,
                                                  sw_if_index,
                                                  priority,
                                                  weight)

    @staticmethod
    def vpp_unset_lisp_locator_set(node, locator_set_list):
        """Unset lisp locator_sets on VPP node in topology.

        :param node: VPP node.
        :param locator_set_list: List of locator_set.
        :type node: dict
        :type locator_set_list: list
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Lisp locator set, node is not DUT')

        logger.info(locator_set_list)

        lisp_locator = LispLocator()
        lisp_locator_set = LispLocatorSet()
        for locator_set in locator_set_list:
            locator_set_name = locator_set.get('locator-set')
            locator_list = locator_set.get('locator')
            for locator in locator_list:
                sw_if_index = locator.get('locator-index')
                priority = locator.get('priority')
                weight = locator.get('weight')
                logger.info(node)
                logger.info(locator_set_name)
                logger.info(sw_if_index)
                logger.info(priority)
                logger.info(weight)
                lisp_locator.vpp_del_lisp_locator(node,
                                                  locator_set_name,
                                                  sw_if_index,
                                                  priority,
                                                  weight)

            lisp_locator_set.vpp_del_lisp_locator_set(node,
                                                      locator_set_name)

    @staticmethod
    def vpp_set_lisp_eid_table(node, eid_table):
        """Set lisp eid tables on VPP node in topology.

        :param node: VPP node.
        :param eid_table: Dictionary containing information of eid_table.
        :type node: dict
        :type eid_table: dict
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Node is not DUT')

        lisp_locator_set = LispLocatorSet()
        lisp_eid = LispLocalEid()
        for eid in eid_table:
            vni = eid.get('vni')
            eid_address = eid.get('eid')
            eid_prefix_len = eid.get('eid-prefix-len')
            locator_set_name = eid.get('locator-set')
            lisp_locator_set.vpp_add_lisp_locator_set(node, locator_set_name)
            lisp_eid.vpp_add_lisp_local_eid(node,
                                            locator_set_name,
                                            vni,
                                            eid_address,
                                            eid_prefix_len)

    @staticmethod
    def vpp_unset_lisp_eid_table(node, eid_table):
        """Unset lisp eid tables on VPP node in topology.

        :param node: VPP node.
        :param eid_table: Dictionary containing information of eid_table.
        :type node: dict
        :type eid_table: dict
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Node is not DUT')

        locator_set_list = []
        lisp_locator_set = LispLocatorSet()
        lisp_eid = LispLocalEid()
        for eid in eid_table:
            vni = eid.get('vni')
            eid_address = eid.get('eid')
            eid_prefix_len = eid.get('eid-prefix-len')
            locator_set_name = eid.get('locator-set')
            if locator_set_name not in locator_set_list:
                locator_set_list.append(locator_set_name)

            lisp_eid.vpp_del_lisp_local_eid(node,
                                            locator_set_name,
                                            vni,
                                            eid_address,
                                            eid_prefix_len)

        for locator_set_name in locator_set_list:
            lisp_locator_set.vpp_del_lisp_locator_set(node, locator_set_name)

    @staticmethod
    def vpp_set_lisp_map_resolver(node, map_resolver):
        """Set lisp map resolvers on VPP node in topology.

        :param node: VPP node.
        :param map_resolver: Dictionary containing information of map resolver.
        :type node: dict
        :type map_resolver: dict
        """

        lisp_map_res = LispMapResolver()
        for map_ip in map_resolver:
            lisp_map_res.vpp_add_map_resolver(node, map_ip.get('map resolver'))

    @staticmethod
    def vpp_unset_lisp_map_resolver(node, map_resolver):
        """Unset lisp map resolvers on VPP node in topology.

        :param node: VPP node.
        :param map_resolver: Dictionary containing information of map resolver.
        :type node: dict
        :type map_resolver: dict
        """

        lisp_map_res = LispMapResolver()
        for map_ip in map_resolver:
            lisp_map_res.vpp_del_map_resolver(node, map_ip.get('map resolver'))

    # @staticmethod
    # def vpp_lisp_gpe_interface_status(node, state):
    #     """Set lisp gpe interface status on VPP node in topology.
    #
    #     :param node: VPP node.
    #     :param state: State of the gpe iface, up or down
    #     :type node: dict
    #     :type state: str
    #     """
    #
    #     lgi = LispGpeIface()
    #     lgi.vpp_lisp_gpe_iface(node, state)


class LispEidTableMap(object):
    """
    Class for EID table map.
    """

    @staticmethod
    def vpp_lisp_eid_table_mapping(node, vni, bd_id=None, vrf=None):
        """
        Map LISP VNI to either bridge domain ID, or VRF ID.

        :param node: VPP node.
        :param vni: Lisp VNI.
        :param bd_id: Bridge domain ID.
        :param vrf: VRF id.
        :type node: dict
        :type vni: int
        :type bd_id: int
        :type vrf: int
        """

# used in /csit/tests/vpp/func/ip4_tunnels/lisp/eth2p-ethip4lisp-l2bdbasemaclrn-func.robot

        # Data
        # Fields
        #
        # u8
        # is_add
        #
        # u32
        # vni
        #
        # u32
        # dp_table
        #
        # u8
        # is_l2

        if bd_id:
            is_l2 = 1
            dp_table = bd_id
        else:
            is_l2 = 0
            dp_table = vrf

        args = dict(is_add=1,
                    vni=int(vni),
                    dp_table=int(dp_table),
                    is_l2=is_l2)

        logger.info(args)

        cmd = 'lisp_eid_table_add_del_map'
        err_msg = "Failed to add eid table map on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)



        # if bd_id:
        #     bd_or_vrf = 'bd_index {}'.format(bd_id)
        # else:
        #     bd_or_vrf = 'vrf {}'.format(vrf)
        # VatExecutor.cmd_from_template(node,
        #                               'lisp/lisp_eid_table_add_del_map.vat',
        #                               vni=vni,
        #                               bd_or_vrf=bd_or_vrf)
