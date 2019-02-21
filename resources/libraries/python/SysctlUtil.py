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

"""Linux sysctl library."""

from resources.libraries.python.ssh import exec_cmd_no_error

__all__ = ["SysctlUtil"]


class SysctlUtil(object):
    """Class contains methods for getting or setting sysctl settings."""

    @staticmethod
    def get_sysctl_value(node, key):
        """Get sysctl key.

        :param node: Node in the topology.
        :param key: Key that will be set.
        :type node: dict
        :type key: str
        """
        command = 'sysctl {key}'.format(key=key)

        message = 'Node {host} failed to run: {command}'.\
            format(host=node['host'], command=command)

        exec_cmd_no_error(node, command, sudo=True, message=message)

    @staticmethod
    def set_sysctl_value(node, key, value):
        """Set sysctl key to specific value.

        :param node: Node in the topology.
        :param key: Key that will be set.
        :param value: Value to set.
        :type node: dict
        :type key: str
        :type value: str
        """
        command = 'sysctl -w {key}={value}'.format(key=key, value=value)

        message = 'Node {host} failed to run: {command}'.\
            format(host=node['host'], command=command)

        exec_cmd_no_error(node, command, sudo=True, message=message)

