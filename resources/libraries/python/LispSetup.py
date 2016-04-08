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

from topology import NodeType
from VatExecutor import VatExecutor

class LispGpeIface(object):
    """Class for Lisp gpe interface API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_lisp_gpe_iface_up(node):
        """Set lisp gpe interface up on the VPP node in topology.

        :param node: Node of the test topology.
        :type node: dict
        """

        VatExecutor.cmd_from_template(node,
                                      'lisp_gpe_iface.vat',
                                      state='up')

    @staticmethod
    def vpp_lisp_gpe_iface_down(node):
        """Set lisp gpe interface down on the VPP node in topology.

        :param node: VPP node.
        :type node: dict
        """

        VatExecutor.cmd_from_template(node,
                                      'lisp_gpe_iface.vat',
                                      state='down')

class  LispMapResolver(object):
    """Class for Lisp map resolver API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_mal_resolver(node, map_resolver_ip):
        """Set lisp map resolver on the VPP node in topology.

        :param node: Node of the test topology.
        :param map_resolver_ip: IP address of the map resolver.
        :type node: dict
        :type map_resolver_ip: str
        """

        VatExecutor.cmd_from_template(node,
                                      'add_lisp_map_resolver.vat',
                                      address=map_resolver_ip)
    @staticmethod
    def vpp_del_mal_resolver(node, map_resolver_ip):
        """Unset lisp map resolver on the VPP node in topology.

        :param node: VPP node.
        :param map_resolver_ip: IP address of the map resolver.
        :type node: dict
        :type map_resolver_ip: str
        """

        VatExecutor.cmd_from_template(node,
                                      'del_lisp_map_resolver.vat',
                                      address=map_resolver_ip)

class  LispLocalEid(object):
    """Class for Lisp local eid API."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_add_lisp_local_eid(node, locator_set_name, address, prefix_len):
        """Set lisp eid addres on the VPP node in topology.

        :param node: VPP node.
        :param locator_set_name: Name of the locator_set.
        :param address: Eid IP address.
        :param prefix_len: prefix len of the eid IP address.
        :type node: dict
        :type locator_set_name: str
        :type addres: str
        :type prefix_len: int
        """

        VatExecutor.cmd_from_template(node,
                                      'add_lisp_local_eid.vat',
                                      eid_address=address,
                                      eid_prefix=prefix_len,
                                      locator_name=locator_set_name)

    @staticmethod
    def vpp_del_lisp_local_eid(node, locator_set_name, address, prefix_len):
        """Set lisp eid addres on the VPP node in topology.

        :param node: VPP node.
        :param locator_set_name: Name of the locator_set.
        :param address: Eid IP address.
        :param prefix_len: prefix len of the eid IP address.
        :type node: dict
        :type locator_set_name: str
        :type addres: str
        :type prefix_len: int
        """

        VatExecutor.cmd_from_template(node,
                                      'del_lisp_local_eid.vat',
                                      eid_address=address,
                                      eid_prefix=prefix_len,
                                      locator_name=locator_set_name)

class  LispLocator(object):
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
                                      'add_lisp_locator.vat',
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
                                      'del_lisp_locator.vat',
                                      lisp_name=locator_name,
                                      sw_if_index=sw_if_index,
                                      priority=priority,
                                      weight=weight)

class LispLocatoSet(object):
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
                                      'add_lisp_locator_set.vat',
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
                                      'del_lisp_locator_set.vat',
                                      lisp_name=name)

class LispSetup(object):
    """Lisp setup in topology."""

    def __init__(self):
        pass

    @staticmethod
    def  vpp_set_lisp_locator_set(node, locator_sets):
        """Set lisp locator_sets on VPP node in topology.

        There is 2 way how set lisp locator_set.
        One locator_set can contain multiple locator.
        When we set locator_set we reset the locator for the locator_set.
        So when we want test only add more locator to locator then we use
        "normal" type and then we set locator_set only one.
        When we want test reset the locator we use type "reset" and then
        we set locator_set multiple and reset the locato for locator_set.

        :param node: VPP node.
        :param locator_sets: Dictionary containing information of locator_set.
        :type node: dict
        :type locator_sets: dict
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Lisp locator set, node is not DUT')

        lisp_locator_set = LispLocatoSet()
        lisp_locator = LispLocator()
        for locator_set_type, item in locator_sets.iteritems():
            if locator_set_type == 'normal':
                lsm_set = 1
            elif locator_set_type == 'reset':
                lsm_set = 0
            else:
                raise RuntimeError("Unknow value")

            locator_set_list = []
            for locator_set in item:
                locator_name = locator_set.get('locator-set')
                sw_if_index = locator_set.get('locator')
                priority = locator_set.get('priority')
                weight = locator_set.get('weight')
                if lsm_set == 1:
                    if locator_name not in locator_set_list:
                        locator_set_list.append(locator_name)
                        lisp_locator_set.vpp_add_lisp_locator_set(node,
                                                                  locator_name)
                else:
                    lisp_locator_set.vpp_add_lisp_locator_set(node,
                                                              locator_name)
                lisp_locator.vpp_add_lisp_locator(node,
                                                  locator_name,
                                                  sw_if_index,
                                                  priority,
                                                  weight)

    @staticmethod
    def  vpp_unset_lisp_locator_set(node, locator_sets):
        """Unset lisp locator_sets on VPP node in topology.

        :param node: VPP node.
        :param locator_sets: Dictionary containing information of locator_set.
        :type node: dict
        :type locator_sets: dict
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Lisp locator set, node is not DUT')

        lisp_locator = LispLocator()
        lisp_locator_set = LispLocatoSet()
        for locator_set_type, item in locator_sets.iteritems():
            if locator_set_type == 'normal':
                lsm_set = 1
            elif locator_set_type == 'reset':
                lsm_set = 0
            else:
                raise RuntimeError("Unknow value")

            locator_set_list = []
            for locator_set in item:
                locator_set_name = locator_set.get('locator-set')
                sw_if_index = locator_set.get('locator')
                priority = locator_set.get('priority')
                weight = locator_set.get('weight')
                if lsm_set == 1:
                    if locator_set_name not in locator_set_list:
                        locator_set_list.append(locator_set_name)
                else:
                    lisp_locator.vpp_del_lisp_locator(node,
                                                      locator_set_name,
                                                      sw_if_index,
                                                      priority,
                                                      weight)

        for locator_set_name in locator_set_list:
            lisp_locator_set.vpp_del_lisp_locator_set(node, locator_set_name)

    @staticmethod
    def vpp_set_lisp_eid_table(node, eid_table):
        """Set lisp eid tables on VPP node in topology.

        :param node: VPP node.
        :param eid_table: Dictionary containing information of eid_table.
        :type node: dict
        :type eid_table: dict
        """

        if node['type'] != NodeType.DUT:
            raise ValueError('Lisp locator set, node is not DUT')

        lisp_locator_set = LispLocatoSet()
        lisp_eid = LispLocalEid()
        for eid in eid_table:
            eid_address = eid.get('eid address')
            eid_prefix_len = eid.get('eid prefix len')
            locator_set_name = eid.get('locator-set')
            lisp_locator_set.vpp_add_lisp_locator_set(node, locator_set_name)
            lisp_eid.vpp_add_lisp_local_eid(node,
                                            locator_set_name,
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
            raise Exception('Lisp locator set, node is not DUT')

        locator_set_list = []
        lisp_locator_set = LispLocatoSet()
        lisp_eid = LispLocalEid()
        for eid in eid_table:
            eid_address = eid.get('eid address')
            eid_prefix_len = eid.get('eid prefix len')
            locator_set_name = eid.get('locator-set')
            if locator_set_name not in locator_set_list:
                locator_set_list.append(locator_set_name)

            lisp_eid.vpp_del_lisp_local_eid(node,
                                            locator_set_name,
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
            lisp_map_res.vpp_add_mal_resolver(node, map_ip.get('map resolver'))

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
            lisp_map_res.vpp_del_mal_resolver(node, map_ip.get('map resolver'))

    @staticmethod
    def vpp_lisp_gpe_interface_up(node):
        """Set lisp gpe interface up on VPP node in topology.

        :param node: VPP node.
        :type node: dict
        """

        lgi = LispGpeIface()
        lgi.vpp_lisp_gpe_iface_up(node)

    @staticmethod
    def vpp_lisp_gpe_interface_down(node):
        """Set lisp gpe interface up on VPP node in topology.

        :param node: VPP node.
        :type node: dict
        """

        lgi = LispGpeIface()
        lgi.vpp_lisp_gpe_iface_down(node)
