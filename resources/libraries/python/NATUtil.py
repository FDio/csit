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

"""NAT utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiExecutor


class NATUtil(object):
    """This class defines the methods to set NAT."""

    def __init__(self):
        pass

    @staticmethod
    def set_nat44_interfaces(node, int_in, int_out):
        """Set inside and outside interfaces for NAT44.

        nat44_interface_add_del_feature
        nat44_interface_add_del_output_feature

        :param node: DUT node.
        :param int_in: Inside interface.
        :param int_out: Outside interface.
        :type node: dict
        :type int_in: str
        :type int_out: str
        """

        int_in_idx = InterfaceUtil.get_sw_if_index(node, int_in)
        int_out_idx = InterfaceUtil.get_sw_if_index(node, int_out)

        cmd = 'nat44_interface_add_del_feature'

        err_msg = 'Failed to set inside interface {int} for NAT44 on host ' \
                  '{host}'.format(int=int_in, host=node['host'])
        args_in = dict(
            sw_if_index=int_in_idx,
            is_add=True,
            is_inside=True
        )
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

        err_msg = 'Failed to set outside interface {int} for NAT44 on host ' \
                  '{host}'.format(int=int_out, host=node['host'])
        args_in = dict(
            sw_if_index=int_out_idx,
            is_add=True,
            is_inside=False
        )
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

    @staticmethod
    def set_nat44_deterministic(node, ip_in, subnet_in, ip_out, subnet_out):
        """Set deterministic behaviour of NAT44.

        :param node: DUT node.
        :param ip_in: Inside IP.
        :param subnet_in: Inside IP subnet.
        :param ip_out: Outside IP.
        :param subnet_out: Outside IP subnet.
        :type node: dict
        :type ip_in: str
        :type subnet_in: str or int
        :type ip_out: str
        :type subnet_out: str or int
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If setting of deterministic behaviour of NAT44
            fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat44_set_deterministic.vat',
                    ip_in=ip_in, subnet_in=subnet_in,
                    ip_out=ip_out, subnet_out=subnet_out)
                return response
        except:
            raise RuntimeError("Setting of deterministic behaviour of NAT "
                               "failed!")

    @staticmethod
    def show_nat(node):
        """Show the NAT settings.

        :param node: DUT node.
        :type node: dict
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If getting of NAT settings fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat_show_nat.vat')
                return response
        except:
            raise RuntimeError("Getting of NAT settings failed!")
