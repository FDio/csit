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

"""Lisp utilities library."""

from resources.libraries.python.parsers.JsonParser import JsonParser
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor


class LispUtil(object):
    """Implements keywords for Lisp tests."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_show_lisp_state(node):
        """Get lisp state from VPP node.

        :param node: VPP node.
        :type node: dict
        :return: Lisp gpe state.
        :rtype: list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('lisp/show_lisp_status.vat',
                                    node)
        return JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def vpp_show_lisp_locator_set(node):
        """Get lisp locator_set from VPP node.

        :param node: VPP node.
        :type node: dict
        :return: Lisp locator_set data as python list.
        :rtype: list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('lisp/show_lisp_locator_set.vat', node)
        return JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def vpp_show_lisp_local_eid_table(node):
        """Get lisp local eid table from VPP node.

        :param node: VPP node.
        :type node: dict
        :return: Lisp eid table as python list.
        :rtype: list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('lisp/show_lisp_local_eid_table.vat', node)
        return JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def vpp_show_lisp_map_resolver(node):
        """Get lisp map resolver from VPP node.

        :param node: VPP node.
        :type node: dict
        :return: Lisp map resolver as python list.
        :rtype: list
        """

        vat = VatExecutor()
        vat.execute_script_json_out('lisp/show_lisp_map_resolver.vat', node)
        return JsonParser().parse_data(vat.get_script_stdout())

    @staticmethod
    def lisp_should_be_equal(lisp_val1, lisp_val2):
        """Fail if the lisp values are not equal.

        :param lisp_val1: First lisp value.
        :param lisp_val2: Second lisp value.
        :type lisp_val1: list
        :type lisp_val2: list
        """

        len1 = len(lisp_val1)
        len2 = len(lisp_val2)
        if len1 != len2:
            raise RuntimeError('Values are not same. '
                               'Value 1 {} \n'
                               'Value 2 {}.'.format(lisp_val1,
                                                    lisp_val2))

        for tmp in lisp_val1:
            if tmp not in lisp_val2:
                raise RuntimeError('Value {} is not find in vpp:\n'
                                   '{}'.format(tmp, lisp_val2))

    def lisp_locator_s_should_be_equal(self, locator_set1, locator_set2):
        """Fail if the lisp values are not equal.

        :param locator_set1: Generate lisp value.
        :param locator_set2: Lisp value from VPP.
        :type locator_set1: list
        :type locator_set2: list
        """

        # Remove duplicate value which is not set in vpp node.
        locator_set_list = []
        tmp_list = list(locator_set1)
        while len(tmp_list):
            locator_set = tmp_list.pop(0)
            locator_set_name = locator_set.get('locator-set')
            for tmp_loc_set in tmp_list:
                tmp_loc_set_name = tmp_loc_set.get('locator-set')
                if locator_set_name == tmp_loc_set_name:
                    locator_set = tmp_loc_set
                    tmp_list.remove(tmp_loc_set)
            locator_set_list.append(locator_set)

        for locator_set in locator_set2:
            if 'locator-set-index' in locator_set:
                del locator_set['locator-set-index']

        self.lisp_should_be_equal(locator_set_list, locator_set2)

    @staticmethod
    def generate_unique_lisp_locator_set_data(node, locator_set_number):
        """Generate a list of lisp locator_set we want set to VPP and
        then check if it is set correctly. All locator_sets are unique.

        :param node: VPP node.
        :param locator_set_number: Generate n locator_set.
        :type node: dict
        :type locator_set_number: str
        :return: list of lisp locator_set.
        :rtype: list
        """

        topo = Topology()

        locator_set_list = []
        i = 0
        for num in range(0, int(locator_set_number)):
            locator_list = []
            for interface in node['interfaces'].values():
                link = interface.get('link')
                i += 1
                if link is None:
                    continue

                if_name = topo.get_interface_by_link_name(node, link)
                sw_if_index = topo.get_interface_sw_index(node, if_name)
                if if_name is not None:
                    locator = {'locator-index': sw_if_index,
                               'priority': i,
                               'weight': i}
                    locator_list.append(locator)

            l_name = 'ls{0}'.format(num)
            locator_set = {'locator-set': l_name,
                           'locator': locator_list}
            locator_set_list.append(locator_set)

        return locator_set_list

    @staticmethod
    def generate_duplicate_lisp_locator_set_data(node, locator_set_number):
        """Generate a list of lisp locator_set we want set to VPP and
        then check if it is set correctly. Some locator_sets are duplicated.

        :param node: VPP node.
        :param locator_set_number: Generate n locator_set.
        :type node: dict
        :type locator_set_number: str
        :return: list of lisp locator_set.
        :rtype: list
        """

        topo = Topology()
        locator_set_list = []
        i = 0
        for num in range(0, int(locator_set_number)):
            locator_list = []
            for interface in node['interfaces'].values():
                link = interface.get('link')
                i += 1
                if link is None:
                    continue

                if_name = topo.get_interface_by_link_name(node, link)
                sw_if_index = topo.get_interface_sw_index(node, if_name)
                if if_name is not None:
                    l_name = 'ls{0}'.format(num)
                    locator = {'locator-index': sw_if_index,
                               'priority': i,
                               'weight': i}
                    locator_list.append(locator)
                    locator_set = {'locator-set': l_name,
                                   'locator': locator_list}
                    locator_set_list.append(locator_set)

        return locator_set_list

    def lisp_is_empty(self, lisp_params):
        """Check if the input param are empty.

        :param lisp_params: Should be empty list.
        :type lisp_params: list
        """

        self.lisp_should_be_equal([], lisp_params)
