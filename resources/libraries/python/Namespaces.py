# Copyright (c) 2020 Cisco and/or its affiliates.
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

from copy import deepcopy

from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd


class Namespaces:
    """Linux namespace utilities."""
    __namespaces = []

    @staticmethod
    def create_namespace(node, namespace, delete_before_create=True):
        """Create namespace and add the name to the list for later clean-up.

        :param node: Where to create namespace.
        :param namespace: Name for namespace.
        :param delete_before_create: Delete namespace prior to create
        :type node: dict
        :type namespace: str
        :type delete_before_create: bool
        """
        if delete_before_create:
            Namespaces.delete_namespace(node, namespace)

        cmd = f"ip netns add {namespace}"
        exec_cmd_no_error(node, cmd, sudo=True)
        Namespaces.__namespaces.append(namespace)

    @staticmethod
    def delete_namespace(node, namespace):
        """Delete namespace from the node and list.

        :param node: Where to delete namespace.
        :param namespace: Name for namespace.
        :param delete_before_create: Delete namespace prior to create
        :type node: dict
        :type namespace: str
        :type delete_before_create: bool
        """
        cmd_timeout = 5
        cmd = f"ip netns delete {namespace}"
        (ret_code, _, delete_errmsg) = \
            exec_cmd(node, cmd, timeout=cmd_timeout, sudo=True)
        if ret_code != 0:
            cmd = f"ip netns list {namespace}"
            (stdout, _) = \
                exec_cmd_no_error(node, cmd, timeout=cmd_timeout, sudo=True)
            if stdout == namespace:
                raise RuntimeError(f"Could not delete namespace "
                                   f"({namespace}): {delete_errmsg}")
        try:
            Namespaces.__namespaces.remove(namespace)
        except ValueError:
            pass

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

        ret_code, _, stderr = exec_cmd(node, cmd, timeout=5, sudo=True)
        if ret_code != 0:
            raise RuntimeError(f"Could not attach interface, reason:\n{stderr}")

        cmd = f"ip netns exec {namespace} ip link set {interface} up"

        ret_code, _, stderr = exec_cmd(node, cmd, timeout=5, sudo=True)
        if ret_code != 0:
            raise RuntimeError(
                f"Could not set interface state, reason:\n{stderr}"
            )

    @staticmethod
    def add_default_route_to_namespace(node, namespace, default_route):
        """Add IPv4 default route to interface in namespace.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param default_route: Default route address.
        :type node: dict
        :type namespace: str
        :type default_route: str
        """
        cmd = f"ip netns exec {namespace} ip route add default " \
              f"via {default_route}"
        exec_cmd_no_error(node, cmd, sudo=True)

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

    @staticmethod
    def clean_up_namespaces(node, namespace=None):
        """Delete all old namespaces.

        :param node: Node where to execute command.
        :param namespace: Namespace to delete, if None delete all namespaces
        :type node: dict
        :type namespace: str
        :raises RuntimeError: Namespaces could not be cleaned properly.
        """
        if namespace is not None:
            Namespaces.delete_namespace(node, namespace)
            return

        namespace_copy = deepcopy(Namespaces.__namespaces)
        for namespace_name in namespace_copy:
            Namespaces.delete_namespace(node, namespace_name)
