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

"""Linux limit library."""

from resources.libraries.python.ssh import exec_cmd_no_error

__all__ = ["LimitUtil"]


class LimitUtil(object):
    """Class contains methods for getting or setting process resource limits."""

    @staticmethod
    def get_pid_limit(node, pid):
        """Get process resource limits.

        :param node: Node in the topology.
        :param pid: Process ID.
        :type node: dict
        :type pid: int
        """
        command = f"prlimit --noheadings --pid={pid}"
        message = f"Node {node[u'host']} failed to run: {command}"

        exec_cmd_no_error(node, command, sudo=True, message=message)

    @staticmethod
    def set_pid_limit(node, pid, resource, limit):
        """Set process resource limits.

        :param node: Node in the topology.
        :param pid: Process ID.
        :param resource: Resource to set limits.
        :param limit: Limit value.
        :type node: dict
        :type pid: int
        :type resource: str
        :type limit: str
        """
        command = f"prlimit --{resource}={limit} --pid={pid}"
        message = f"Node {node[u'host']} failed to run: {command}"

        exec_cmd_no_error(node, command, sudo=True, message=message)

