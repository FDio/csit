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

"""Library to set up Lisp in topology."""

from resources.libraries.python.topology import NodeType
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

        VatExecutor.cmd_from_template(node,
                                      'lisp/lisp_status.vat',
                                      state=state)


class LispRemoteMapping(object):
    """Class for lisp remote mapping API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_remote_mapping(node, vni, deid, deid_prefix, seid,
                                    seid_prefix, rloc):
        """Add lisp remote mapping on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_predix: Destination eid address prefix_len.
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

        VatExecutor.cmd_from_template(node,
                                      'lisp/add_lisp_remote_mapping.vat',
                                      vni=vni,
                                      deid=deid,
                                      deid_prefix=deid_prefix,
                                      seid=seid,
                                      seid_prefix=seid_prefix,
                                      rloc=rloc)

    @staticmethod
    def vpp_del_lisp_remote_mapping(node, vni, deid, deid_prefix, seid,
                                    seid_prefix, rloc):
        """Delete lisp remote mapping on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_predix: Destination eid address prefix_len.
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

        VatExecutor.cmd_from_template(node,
                                      'lisp/del_lisp_remote_mapping.vat',
                                      vni=vni,
                                      deid=deid,
                                      deid_predix=deid_prefix,
                                      seid=seid,
                                      seid_prefix=seid_prefix,
                                      rloc=rloc)


class LispGpeIface(object):
    """Class for Lisp gpe interface API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_lisp_gpe_iface(node, state):
        """Set lisp gpe interface up or down on the VPP node in topology.

        :param node: VPP node.
        :param state: State of the gpe iface, up or down.
        :type node: dict
        :type state: str
        """

        VatExecutor.cmd_from_template(node,
                                      'lisp/lisp_gpe_iface.vat',
                                      state=state)


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

        VatExecutor.cmd_from_template(node,
                                      'lisp/add_lisp_map_resolver.vat',
                                      address=map_resolver_ip)

    @staticmethod
    def vpp_del_map_resolver(node, map_resolver_ip):
        """Unset lisp map resolver on the VPP node in topology.

        :param node: VPP node.
        :param map_resolver_ip: IP address of the map resolver.
        :type node: dict
        :type map_resolver_ip: str
        """

        VatExecutor.cmd_from_template(node,
                                      'lisp/del_lisp_map_resolver.vat',
                                      address=map_resolver_ip)


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

        if prefix_len is not None:
            VatExecutor.cmd_from_template(node,
                                          'lisp/add_lisp_local_eid.vat',
                                          vni=vni,
                                          eid=eid,
                                          eid_prefix=prefix_len,
                                          locator_name=locator_set_name)
        else:
            VatExecutor.cmd_from_template(node,
                                          'lisp/add_lisp_local_eid_mac.vat',
                                          vni=vni,
                                          eid=eid,
                                          locator_name=locator_set_name)

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

        if prefix_len is not None:
            VatExecutor.cmd_from_template(node,
                                          'lisp/del_lisp_local_eid.vat',
                                          vni=vni,
                                          eid=eid,
                                          eid_prefix=prefix_len,
                                          locator_name=locator_set_name)
        else:
            VatExecutor.cmd_from_template(node,
                                          'lisp/del_lisp_local_eid_mac.vat',
                                          vni=vni,
                                          eid=eid,
                                          locator_name=locator_set_name)


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

        VatExecutor.cmd_from_template(node,
                                      'lisp/add_lisp_locator.vat',
                                      lisp_name=locator_name,
                                      sw_if_index=sw_if_index,
                                      priority=priority,
                                      weight=weight)

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

        VatExecutor.cmd_from_template(node,
                                      'lisp/del_lisp_locator.vat',
                                      lisp_name=locator_name,
                                      sw_if_index=sw_if_index,
                                      priority=priority,
                                      weight=weight)


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

        VatExecutor.cmd_from_template(node,
                                      'lisp/add_lisp_locator_set.vat',
                                      lisp_name=name)

    @staticmethod
    def vpp_del_lisp_locator_set(node, name):
        """Del lisp locator_set on VPP.

        :param node: VPP node.
        :param name: VPP locator name.
        :type node: dict
        :type name: str
        """

        VatExecutor.cmd_from_template(node,
                                      'lisp/del_lisp_locator_set.vat',
                                      lisp_name=name)


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

    @staticmethod
    def vpp_lisp_gpe_interface_status(node, state):
        """Set lisp gpe interface status on VPP node in topology.

        :param node: VPP node.
        :param state: State of the gpe iface, up or down
        :type node: dict
        :type state: str
        """

        lgi = LispGpeIface()
        lgi.vpp_lisp_gpe_iface(node, state)
