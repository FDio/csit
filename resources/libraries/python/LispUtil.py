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

""" TODO """

from resources.libraries.python.parsers.JsonParser import JsonParser
from topology import Topology
from VatExecutor import VatExecutor

class LispUtil():
    """Implements keywords for Lisp tests."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_show_lisp_locator_set(node):
        """Get lisp locator_set from VPP node

        :param node: VPP node
        :type node: dict
        return: Lisp locator_set data as python list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('show_lisp_locator_set.vat', node)
        return JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def vpp_show_lisp_local_eid_table(node):
        """Get lisp local eid table from VPP node

        :param node: VPP node
        :type node: dict
        return: Lisp eid table as python list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('show_lisp_local_eid_table.vat', node)
        return  JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def vpp_show_lisp_map_resolver(node):
        """Get lisp map resolver from VPP node

        :param node: VPP node
        :type node: dict
        return: Lisp map resolver as python list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('show_lisp_map_resolver.vat', node)
        return  JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def compare_lisp(lisp_val1, lisp_val2):
        """compare_lisp

        :param lisp_val1: list of values which want compare
        :param lisp_val2: list of values which want compare
        :type lisp_val1: list
        :type lisp_val2: list
        """

        len1 = len(lisp_val1)
        len2 = len(lisp_val2)
        if len1 != len2:
            raise Exception('Values are not same. '
                            'Value 1 {} \n'
                            'Value 2 {}.'.format(lisp_val1,
                                                 lisp_val2))

        for tmp in lisp_val1:
            if tmp not in lisp_val2:
                raise Exception('Value {} is not find in vpp:\n'
                                '{}'.format(tmp, lisp_val2))

    def compare_lisp_locator_set(self, locator_set1, locator_set2):
        """Comapare lisp locator_set

        :param node: VPP node
        :param locator_set1: list of locator_set we want compare
        :param locator_set2: list of locator_set we want compare
        :type node: dict
        :type locator_set1: dict
        :type locator_set2: list
        """

        reset_list = []
        locator_set_list = []
        for locator_set_type, item in locator_set1.iteritems():
            if locator_set_type == 'normal':
                self.compare_lisp(item, locator_set2)
            elif locator_set_type == 'reset':
                for locator_list in reversed(item):
                    name = locator_list.get('locator-set')
                    if name not in locator_set_list:
                        reset_list.insert(0, locator_list)
                        locator_set_list.append(name)
                self.compare_lisp(reset_list, locator_set2)
            else:
                raise Exception("Unknow value")

    @staticmethod
    def get_lisp_locator_set_test_values(node):
        """Get a list of lisp locator_set we want set to VPP and
        then check if is set correct
        Use type "normal" when we set locator_set only one

        :param node: VPP node
        :type node: dict
        return: dict of lisp locator_set
        """

        topo = Topology()

        locator_set_list = []
        i = 0
        for interface in node['interfaces'].values():
            link = interface.get('link')
            i += 1
            if link is None:
                continue

            if_name = topo.get_interface_by_link_name(node, link)
            sw_if_index = topo.get_interface_sw_index(node, if_name)
            if if_name is not None:
                locator_set = {'locator-set': 'ls1',
                               'locator': sw_if_index,
                               'priority': 1,
                               'weight': 1}
                locator_set_list.append(locator_set)

                locator_set = {'locator-set': 'ls2',
                               'locator': sw_if_index,
                               'priority': 6 + i,
                               'weight': 9 + i}
                locator_set_list.append(locator_set)

        loc_type = {'normal':locator_set_list}
        return loc_type

    @staticmethod
    def get_lisp_locator_set_reset_test_values(node):
        """Get a list of lisp locator_set we want set to VPP and
        then check if is set correct
        Use type "reset", where we set multiple time locator_set
        and test reset the locator

        :param node: VPP node
        :type node: dict
        return: dict of lisp locator_set
        """

        topo = Topology()

        locator_set_list = []
        for interface in node['interfaces'].values():
            link = interface.get('link')
            if link is None:
                continue

            if_name = topo.get_interface_by_link_name(node, link)
            sw_if_index = topo.get_interface_sw_index(node, if_name)
            if if_name is not None:
                locator_set = {'locator-set': 'ls1',
                               'locator': sw_if_index,
                               'priority': 1,
                               'weight': 1}
                locator_set_list.append(locator_set)

                locator_set = {'locator-set': 'ls2',
                               'locator': sw_if_index,
                               'priority': 6,
                               'weight': 9}
                locator_set_list.append(locator_set)

        loc_type = {'reset':locator_set_list}
        return loc_type

    @staticmethod
    def get_lisp_local_eid_test_value():
        """Get a list of lisp local eid we want set to VPP and
        then check if is set correct

        return: list of lisp local eid
        """

        eid_table = [{'eid address': '192.168.0.1',
                      'eid prefix len': 24,
                      'locator-set': 'ls1'},
                     {'eid address': '192.168.9.1',
                      'eid prefix len': 24,
                      'locator-set': 'ls1'},
                     {'eid address': '10::1',
                      'eid prefix len': 32,
                      'locator-set': 'ls2'},
                     {'eid address': '11::1',
                      'eid prefix len': 84,
                      'locator-set': 'ls2'}]

        return  eid_table

    @staticmethod
    def get_lisp_map_resolver():
        """Get a list of lisp map resolvers we want set to VPP and
        then check if is set correct

        return: list of lisp map resolver
        """

        map_resolver = [{'map resolver':'192.168.10.100'},
                        {'map resolver':'192.168.0.100'},
                        {'map resolver':'12::9'}]

        return  map_resolver

    @staticmethod
    def get_locator_empty_list():
        """Get dist which contain empty list. We need it for test
        del locator_set

        return: dict which contain empty list, for lisp locator_set
        """

        empty_list = {'normal':[], 'reset':[]}

        return  empty_list

    @staticmethod
    def get_empty_list():
        """Get empty list

        return: empty list
        """

        return  []
