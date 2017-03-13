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
        :return:
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_set_interfaces.vat',
                    int_in=int_in, int_out=int_out)
                return response[0]
        except (ValueError, IndexError, KeyError):
            raise RuntimeError("Setting of inside and outside interfaces for "
                               "SNAT failed!")

    @staticmethod
    def set_snat_deterministic(node, ip_in, range_in, ip_out, range_out):
        """Set deterministic behaviour of SNAT.

        :param node: DUT node.
        :param ip_in: Inside IP.
        :param range_in: Inside IP range.
        :param ip_out: Outside IP.
        :param range_out: Outside IP range.
        :type node: dict
        :type ip_in: str
        :type range_in: str or int
        :type ip_out: str
        :type range_out: str or int
        :return:
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_set_deterministic.vat',
                    ip_in=ip_in, range_in=range_in,
                    ip_out=ip_out, range_out=range_out)
                return response[0]
        except (ValueError, IndexError, KeyError):
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
        :return:
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'snat/snat_set_workers.vat', lcores=lcores)
                return response[0]
        except (ValueError, IndexError, KeyError):
            raise RuntimeError("Setting of SNAT workers failed!")
