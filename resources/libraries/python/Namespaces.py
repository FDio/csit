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

"""Linux namespace utilities library."""

from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd


class Namespaces(object):
    """Linux namespace utilities."""
    def __init__(self):
        self._namespaces = []

    def create_namespace(self, node, namespace_name):
        """Create namespace and add the name to the list for later clean-up.

        :param node: Where to create namespace.
        :param namespace_name: Name for namespace.
        :type node: dict
        :type namespace_name: str
        """
        cmd = f"p netns add {namespace_name}"

        exec_cmd_no_error(node, cmd, sudo=True)
        self._namespaces.append(namespace_name)

    @staticmethod
    def attach_interface_to_namespace(node, namespace, interface):
        """Attach specific interface to namespace.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param interface: Interface in namespace.
        :type node: dict
        :type namespace: str
        :type interface: str
        :raises RuntimeError: Interface could not be attached.
        """
        cmd = f"ip link set {interface} netns {namespace}"

        (ret_code, _, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if ret_code != 0:
            raise RuntimeError(f"Could not attach interface, reason:\n{stderr}")

        cmd = f"ip netns exec {namespace} ip link set {interface} up"

        (ret_code, _, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if ret_code != 0:
            raise RuntimeError(
                f"Could not set interface state, reason:\n{stderr}"
            )

    @staticmethod
    def create_bridge_for_int_in_namespace(
            node, namespace, bridge_name, *interfaces):
        """Setup bridge domain and add interfaces to it.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param bridge_name: Name of the bridge to be created.
        :param interfaces: List of interfaces to add to the namespace.
        :type node: dict
        :type namespace: str
        :type bridge_name: str
        :type interfaces: list
        """
        cmd = f"ip netns exec {namespace} brctl addbr {bridge_name}"
        exec_cmd_no_error(node, cmd, sudo=True)

        for interface in interfaces:
            cmd = f"ip netns exec {namespace} brctl addif {bridge_name} " \
                f"{interface}"
            exec_cmd_no_error(node, cmd, sudo=True)

        cmd = f"ip netns exec {namespace} ip link set dev {bridge_name} up"
        exec_cmd_no_error(node, cmd, sudo=True)

    def clean_up_namespaces(self, node):
        """Remove all old namespaces.

        :param node: Node where to execute command.
        :type node: dict
        :raises RuntimeError: Namespaces could not be cleaned properly.
        """
        for namespace in self._namespaces:
            print(f"Cleaning namespace {namespace}")
            cmd = f"ip netns delete {namespace}"
            (ret_code, _, _) = exec_cmd(node, cmd, timeout=5, sudo=True)
            if ret_code != 0:
                raise RuntimeError(u"Could not delete namespace")
