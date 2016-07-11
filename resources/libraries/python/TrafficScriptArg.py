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

"""Traffic scripts argument parser library."""

import argparse


class TrafficScriptArg(object):  # pylint: disable=too-few-public-methods
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
        :return: Argument value.
        :rtype: str
        """
        arg_val = self._args.get(arg_name)
        if arg_val is None:
            raise Exception("Argument '{0}' not found".format(arg_name))

        return arg_val
