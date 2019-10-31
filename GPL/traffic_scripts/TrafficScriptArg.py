# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""Traffic scripts argument parser library."""

import argparse


class TrafficScriptArg(object):
    """Traffic scripts argument parser.

    Parse arguments for traffic script. Default has two arguments '--tx_if'
    and '--rx_if'. You can provide more arguments. All arguments have string
    representation of the value. You can add also optional arguments. Default
    value for optional arguments is empty string.

    :param more_args: List of additional arguments (optional).
    :param opt_args: List of optional arguments (optional).
    :type more_args: list
    :type opt_args: list

    :Example:

    >>> from TrafficScriptArg import TrafficScriptArg
    >>> args = TrafficScriptArg(['src_mac', 'dst_mac', 'src_ip', 'dst_ip'])
    """

    def __init__(self, more_args=None, opt_args=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("--tx_if", help="interface that sends traffic")
        parser.add_argument("--rx_if", help="interface that receives traffic")

        if more_args is not None:
            for arg in more_args:
                arg_name = '--{0}'.format(arg)
                parser.add_argument(arg_name)

        if opt_args is not None:
            for arg in opt_args:
                arg_name = '--{0}'.format(arg)
                parser.add_argument(arg_name, nargs='?', default='')

        self._parser = parser
        self._args = vars(parser.parse_args())

    def get_arg(self, arg_name):
        """Get argument value.

        :param arg_name: Argument name.
        :type arg_name: str
        :returns: Argument value.
        :rtype: str
        """
        arg_val = self._args.get(arg_name)
        if arg_val is None:
            raise Exception("Argument '{0}' not found".format(arg_name))

        return arg_val
