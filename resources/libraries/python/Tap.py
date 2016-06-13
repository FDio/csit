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

"""Tap utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class Tap(object):
    """Tap utilities."""

    @staticmethod
    def add_tap_interface(node, tap_name, mac=None):
        """Add tap interface with name and optionally with MAC.

        :param node: Node to add tap on.
        :param tap_name: Tap interface name for linux tap.
        :param mac: Optional MAC address for VPP tap.
        :type node: dict
        :type tap_name: str
        :type mac: str
        :return: Returns a interface index.
        :rtype: int
        """
        command = 'connect'
        if mac is not None:
            args = 'tapname {} mac {}'.format(tap_name, mac)
        else:
            args = 'tapname {}'.format(tap_name)
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template('tap.vat',
                                                           tap_command=command,
                                                           tap_arguments=args)
            interface = resp[0]['sw_if_index']
            return interface

    @staticmethod
    def modify_tap_interface(node, if_index, tap_name, mac=None):
        """Modify tap interface like linux interface name or VPP MAC.

        :param node: Node to modify tap on.
        :param if_index: Index of tap interface to be modified.
        :param tap_name: Tap interface name for linux tap.
        :param mac: Optional MAC address for VPP tap.
        :type node: dict
        :type if_index: int
        :type tap_name: str
        :type mac: str
        :return: Returns a interface index.
        :rtype: int
        """
        command = 'modify'
        if mac is not None:
            args = 'sw_if_index {} tapname {} mac {}'.format(
                if_index, tap_name, mac)
        else:
            args = 'sw_if_index {} tapname {}'.format(if_index, tap_name)
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template('tap.vat',
                                                           tap_command=command,
                                                           tap_arguments=args)
            interface = resp[0]['sw_if_index']
            return interface

    @staticmethod
    def delete_tap_interface(node, if_index):
        """Delete tap interface.

        :param node: Node to delete tap on.
        :param if_index: Index of tap interface to be deleted.
        :type node: dict
        :type if_index: int
        :raises RuntimeError: Deletion was not successful.
        """
        command = 'delete'
        args = 'sw_if_index {}'.format(if_index)
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template('tap.vat',
                                                           tap_command=command,
                                                           tap_arguments=args)
            if int(resp[0]['retval']) != 0:
                raise RuntimeError(
                    'Could not remove tap interface: {}'.format(resp))

    @staticmethod
    def check_tap_present(node, tap_name):
        """Check whether specific tap interface exists.

        :param node: Node to check tap on.
        :param tap_name: Tap interface name for linux tap.
        :type node: dict
        :type tap_name: str
        :raises RuntimeError: Specified interface was not found.
        """
        tap_if = InterfaceUtil.tap_dump(node, tap_name)
        if len(tap_if) == 0:
            raise RuntimeError(
                'Tap interface :{} does not exist'.format(tap_name))
