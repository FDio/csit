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

from resources.libraries.python.topology import NodeType
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.L2Util import L2Util

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

        args = dict(is_en=0 if state == 'disable' else 1)

        cmd = 'lisp_enable_disable'
        err_msg = "Failed to set LISP status on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            eid_packed = ip_address(unicode(deid)).packed
            seid_packed = ip_address(unicode(seid)).packed
            eid_len = deid_prefix
            seid_len = seid_prefix
        else:
            eid_type = 2
            eid_packed = L2Util.mac_to_bin(deid)
            seid_packed = L2Util.mac_to_bin(seid)
            eid_len = 0
            seid_len = 0

        rlocs = [dict(is_ip4=1 if ip_address(unicode(rloc)).version == 4 else 0,
                      addr=ip_address(unicode(rloc)).packed)]

        args = dict(is_add=1,
                    is_src_dst=1,
                    vni=int(vni),
                    eid_type=eid_type,
                    eid=eid_packed,
                    eid_len=eid_len,
                    seid=seid_packed,
                    seid_len=seid_len,
                    rloc_num=1,
                    rlocs=rlocs)

        cmd = 'lisp_add_del_remote_mapping'
        err_msg = "Failed to add remote mapping on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        # used only with IPs
        is_mac = False

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            eid_packed = ip_address(unicode(deid)).packed
            seid_packed = ip_address(unicode(seid)).packed
            eid_len = deid_prefix
            seid_len = seid_prefix
        else:
            eid_type = 2
            eid_packed = L2Util.mac_to_bin(deid)
            seid_packed = L2Util.mac_to_bin(seid)
            eid_len = 0
            seid_len = 0

        rlocs = [dict(is_ip4=1 if ip_address(unicode(rloc)).version == 4 else 0,
                      addr=ip_address(unicode(rloc)).packed)]

        args = dict(is_add=0,
                    is_src_dst=1,
                    vni=int(vni),
                    eid_type=eid_type,
                    eid=eid_packed,
                    eid_len=eid_len,
                    seid=seid_packed,
                    seid_len=seid_len,
                    rloc_num=1,
                    rlocs=rlocs)

        cmd = 'lisp_add_del_remote_mapping'
        err_msg = "Failed to delete remote mapping on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            reid = ip_address(unicode(deid)).packed
            leid = ip_address(unicode(seid)).packed
            reid_len = deid_prefix
            leid_len = seid_prefix
        else:
            eid_type = 2
            reid = L2Util.mac_to_bin(deid)
            leid = L2Util.mac_to_bin(seid)
            reid_len = 0
            leid_len = 0

        args = dict(is_add=1,
                    vni=int(vni),
                    eid_type=eid_type,
                    reid=reid,
                    reid_len=reid_len,
                    leid=leid,
                    leid_len=leid_len)

        cmd = 'lisp_add_del_adjacency'
        err_msg = "Failed to add lisp adjacency on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        # used only with IPs
        is_mac = False

        if not is_mac:
            eid_type = 0 if ip_address(unicode(deid)).version == 4 else 1
            reid = ip_address(unicode(deid)).packed
            leid = ip_address(unicode(seid)).packed
            reid_len = deid_prefix
            leid_len = seid_prefix
        else:
            eid_type = 2
            reid = L2Util.mac_to_bin(deid)
            leid = L2Util.mac_to_bin(seid)
            reid_len = 0
            leid_len = 0

        args = dict(is_add=0,
                    vni=int(vni),
                    eid_type=eid_type,
                    reid=reid,
                    reid_len=reid_len,
                    leid=leid,
                    leid_len=leid_len)

        cmd = 'lisp_add_del_adjacency'
        err_msg = "Failed to delete lisp adjacency on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        args = dict(is_en=0 if state == 'disable' else 1)

        cmd = 'gpe_enable_disable'
        err_msg = "Failed to set LISP GPE status on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

class LispGpeForwardEntry(object):
    """The functionality needed for these methods is not implemented in VPP
    (VAT). Bug https://jira.fd.io/browse/VPP-334 was open to cover this issue.

    TODO: Implement when VPP-334 is fixed.
    """

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

        args = dict(is_add=1,
                    is_ipv6=0 if ip_address(unicode(map_resolver_ip)).version \
                                 == 4 else 1,
                    ip_address=ip_address(unicode(map_resolver_ip)).packed)

        cmd = 'lisp_add_del_map_resolver'
        err_msg = "Failed to add map resolver on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_map_resolver(node, map_resolver_ip):
        """Unset lisp map resolver on the VPP node in topology.

        :param node: VPP node.
        :param map_resolver_ip: IP address of the map resolver.
        :type node: dict
        :type map_resolver_ip: str
        """

        args = dict(is_add=0,
                    is_ipv6=0 if ip_address(unicode(map_resolver_ip)).version \
                                 == 4 else 1,
                    ip_address=ip_address(unicode(map_resolver_ip)).packed)

        cmd = 'lisp_add_del_map_resolver'
        err_msg = "Failed to delete map resolver on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        if prefix_len:
            eid_type = 0 if ip_address(unicode(eid)).version == 4 else 1
            eid_packed = ip_address(unicode(eid)).packed
        else:
            eid_type = 2
            eid_packed = L2Util.mac_to_bin(eid)

        args = dict(is_add=1,
                    eid_type=eid_type,
                    eid=eid_packed,
                    prefix_len=prefix_len,
                    locator_set_name=locator_set_name,
                    vni=int(vni))

        cmd = 'lisp_add_del_local_eid'
        err_msg = "Failed to add local eid on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        if prefix_len:
            eid_type = 0 if ip_address(unicode(eid)).version == 4 else 1
            eid_packed = ip_address(unicode(eid)).packed
        else:
            eid_type = 2
            eid_packed = L2Util.mac_to_bin(eid)

        args = dict(is_add=0,
                    eid_type=eid_type,
                    eid=eid_packed,
                    prefix_len=prefix_len,
                    locator_set_name=locator_set_name,
                    vni=int(vni))

        cmd = 'lisp_add_del_local_eid'
        err_msg = "Failed to delete local eid on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        args = dict(is_add=1,
                    locator_set_name=locator_name,
                    sw_if_index=sw_if_index,
                    priority=priority,
                    weight=weight)

        cmd = 'lisp_add_del_locator'
        err_msg = "Failed to add locator on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        args = dict(is_add=0,
                    locator_set_name=locator_name,
                    sw_if_index=sw_if_index,
                    priority=priority,
                    weight=weight)

        cmd = 'lisp_add_del_locator'
        err_msg = "Failed to delete locator on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        args = dict(is_add=1,
                    locator_set_name=name,
                    locator_num=0,
                    locators=[])

        cmd = 'lisp_add_del_locator_set'
        err_msg = "Failed to add locator set on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_lisp_locator_set(node, name):
        """Del lisp locator_set on VPP.

        :param node: VPP node.
        :param name: VPP locator name.
        :type node: dict
        :type name: str
        """

        args = dict(is_add=0,
                    locator_set_name=name,
                    locator_num=0,
                    locators=[])

        cmd = 'lisp_add_del_locator_set'
        err_msg = "Failed to delete locator set on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        lisp_locator = LispLocator()
        lisp_locator_set = LispLocatorSet()
        for locator_set in locator_set_list:
            locator_set_name = locator_set.get('locator-set')
            locator_list = locator_set.get('locator')
            for locator in locator_list:
                sw_if_index = locator.get('locator-index')
                priority = locator.get('priority')
                weight = locator.get('weight')
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

        # adding default mapping vni=0, vrf=0 needs to be skipped
        skip = False

        if bd_id:
            is_l2 = 1
            dp_table = bd_id
        else:
            is_l2 = 0
            dp_table = vrf
            # skip adding default mapping
            if (int(vrf) == 0) and (int(vni) == 0):
                skip = True

        args = dict(is_add=1,
                    vni=int(vni),
                    dp_table=int(dp_table),
                    is_l2=is_l2)

        cmd = 'lisp_eid_table_add_del_map'
        err_msg = "Failed to add eid table map on host {host}".format(
            host=node['host'])

        if not skip:
            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
