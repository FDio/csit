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

"""Linux namespace utilities library."""

from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd, SSH


class Namespaces(object):
    """Linux namespace utilities."""
    def __init__(self):
        self._namespaces = []

    def create_namespace(self, node, namespace_name):
        """
        Create namespace and add the name to the list for later clean-up.
        :param node: Where to create namespace
        :param namespace_name: Name for namespace
        :type node: dict
        :type namespace_name: str
        """
        cmd = ('ip netns add {0}'.format(namespace_name))
        exec_cmd_no_error(node, cmd, sudo=True)
        self._namespaces.append(namespace_name)

    @staticmethod
    def set_int_mac_in_namespace(node, namespace, interface, mac):
        """Set MAC address for interface in namespace.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param interface: Interface in namespace.
        :param mac: MAC to be assigned to interface.
        :type node: dict
        :type namespace: str
        :type interface: str
        :type mac: str
        """
        cmd = 'ip netns exec {} ip link set {} address {}'.format(
            namespace, interface, mac)
        exec_cmd_no_error(node, cmd, sudo=True)

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
        cmd = 'ip link set {0} netns {1}'.format(interface, namespace)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not attach interface, reason:{}'.format(stderr))

    @staticmethod
    def set_int_ip_in_namespace(node, namespace, interface, ip, prefix):
        """Set IP address to interface in namespace.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param interface: Interface in namespace.
        :param ip: IP to be set on interface.
        :param prefix: IP prefix.
        :type node: dict
        :type namespace: str
        :type interface: str
        :type ip: str
        :type prefix: int
        :raises RuntimeError: IP could not be set.
        """
        cmd = 'ip netns exec {} ip addr add {}/{} dev {}'.format(
            namespace, ip, prefix, interface)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not set IP for interface, reason:{}'.format(stderr))

    @staticmethod
    def set_int_state_in_namespace(node, namespace, interface, state="up"):
        """Set interface state up/down.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param interface: Interface in namespace.
        :param state: Interface state. Default is UP.
        :type node: dict
        :type namespace: str
        :type interface: str
        :type state: str
        :raises RuntimeError: IP could not be set.
        """
        cmd = 'ip netns exec {} ip link set {} {}'.format(
            namespace, interface, state)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not set interface state, reason:{}'.format(stderr))

    @staticmethod
    def create_bridge_for_int_in_namespace(
            node, namespace, bridge_name, interfaces):
        """Setup bridge domain and add two interfaces to it.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param bridge_name: Name of the bridge to be created.
        :param interfaces: List of interfaces to add to the namespace.
        :type node: dict
        :type namespace: str
        :type bridge_name: str
        :type interfaces: list
        """
        cmd = 'ip netns exec {} brctl addbr {}'.format(namespace, bridge_name)
        exec_cmd_no_error(node, cmd, sudo=True)

        for interface in interfaces:
            cmd = 'ip netns exec {} brctl addif {} {}'.format(
                namespace, bridge_name, interface)
            exec_cmd_no_error(node, cmd, sudo=True)


        cmd = 'ip netns exec {} ifconfig {} up'.format(namespace, bridge_name)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def int_add_route_in_namespace(node, namespace, ip, prefix, gw):
        """Add route in namespace.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param ip: Route destination IP.
        :param prefix: IP prefix.
        :param gw: Gateway.
        :type node: dict
        :type namespace: str
        :type ip: str
        :type prefix: int
        :type gw: str
        """
        cmd = 'ip netns exec {} ip route add {}/{} via {}'.format(
            namespace, ip, prefix, gw)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_int_arp_in_namespace(node, namespace, interface, ip, mac):
        """Set arp on interface in namespace.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param interface: Interface in namespace.
        :param ip: IP for arp.
        :param mac: MAC address.
        :type node: dict
        :type namespace: str
        :type interface: str
        :type ip: str
        :type mac: str
        """
        cmd = 'ip netns exec {} arp -i {} -s {} {}'.format(
            namespace, interface, ip, mac)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def ping_from_namespace(node, namespace, ip, ping_count=2, timeout=30):
        """Make ping from namespace to IP optionally with ping count or timeout.

        :param node: Node where to execute command.
        :param namespace: Namespace to execute command on.
        :param ip: IP to be set on interface.
        :param ping_count: Number of pings to send.
        :param timeout: Execution timeout.
        :type node: dict
        :type namespace: str
        :type ip: str
        :type ping_count: int
        :type timeout: int
        :raises RuntimeError: Ping was not successful.
        """
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip netns exec {} ping -c{} {}'.format(namespace, ping_count, ip)
        (rc, stdout, stderr) = ssh.exec_command_sudo(cmd, timeout=timeout)
        if rc != 0:
            if '100% packet loss' in stdout:
                raise RuntimeError('Host Unreachable')

    def clean_up_namespaces(self, node):
        """Remove all old namespaces.

        :param node: Node where to execute command.
        :type node: dict
        :raises RuntimeError: Namespaces could not be cleaned properly.
        """
        for namespace in self._namespaces:
            print "Cleaning namespace {}".format(namespace)
            cmd = 'ip netns delete {}'.format(namespace)
            (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
            if rc != 0:
                raise RuntimeError('Could not delete namespace')

