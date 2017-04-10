# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""SNAT utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal


class SNATUtil(object):
    """This class defines the methods to set SNAT."""

    def __init__(self):
        pass

    @staticmethod
    def set_snat_interfaces(node, int_in, int_out):
        """Set inside and outside interfaces for SNAT.

        :param node: DUT node.
        :param int_in: Inside interface.
        :param int_out: Outside interface.
        :type node: dict
        :type int_in: str
        :type int_out: str
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If setting of inside and outside interfaces for
        SNAT fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_set_interfaces.vat',
                    int_in=int_in, int_out=int_out)
                return response
        except:
            raise RuntimeError("Setting of inside and outside interfaces for "
                               "SNAT failed!")

    @staticmethod
    def set_snat_deterministic(node, ip_in, subnet_in, ip_out, subnet_out):
        """Set deterministic behaviour of SNAT.

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
        :raises RuntimeError: If setting of deterministic behaviour of SNAT
        fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_set_deterministic.vat',
                    ip_in=ip_in, subnet_in=subnet_in,
                    ip_out=ip_out, subnet_out=subnet_out)
                return response
        except:
            raise RuntimeError("Setting of deterministic behaviour of SNAT "
                               "failed!")

    @staticmethod
    def set_snat_workers(node, lcores):
        """Set SNAT workers.

        :param node: DUT node.
        :param lcores: list of cores, format: range e.g. 1-5 or list of ranges
        e.g.: 1-5,18-22.
        :type node: dict
        :type lcores: str
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If setting of SNAT workers fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_set_workers.vat', lcores=lcores)
                return response
        except:
            raise RuntimeError("Setting of SNAT workers failed!")

    @staticmethod
    def show_snat(node):
        """Show the SNAT settings.

        :param node: DUT node.
        :type node: dict
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If getting of SNAT settings fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_show_snat.vat')
                return response
        except:
            raise RuntimeError("Getting of SNAT settings failed!")

    @staticmethod
    def show_snat_deterministic_forward(node, ip_addr):
        """Show forward IP address and port(s).

        :param node: DUT node.
        :param ip_addr: IP address.
        :type node: dict
        :type ip_addr: str
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If command 'exec snat deterministic forward'
        fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_deterministic_forward.vat', ip=ip_addr)
                return response
        except:
            raise RuntimeError("Command 'exec snat deterministic forward {ip}'"
                               " failed!".format(ip=ip_addr))

    @staticmethod
    def show_snat_deterministic_reverse(node, ip_addr, port):
        """Show reverse IP address.

        :param node: DUT node.
        :param ip_addr: IP address.
        :param port: Port.
        :type node: dict
        :type ip_addr: str
        :type port: str or int
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If command 'exec snat deterministic reverse'
        fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_deterministic_reverse.vat',
                    ip=ip_addr, port=port)
                return response
        except:
            raise RuntimeError(
                "Command 'exec snat deterministic reverse {ip}:{port}'"
                " failed!".format(ip=ip_addr, port=port))
