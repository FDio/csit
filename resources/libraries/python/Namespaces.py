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

"""Namespace utilities library."""

from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd, SSH


class Namespaces(object):
    """Namespace utilities."""

    @staticmethod
    def set_int_mac_in_namespace(node, namespace, interface, mac):
        cmd = 'ip netns exec {} ip link set {} address {}'.format(namespace, interface, mac)
        exec_cmd_no_error(node,cmd,sudo=True)
    @staticmethod
    def attach_interface_to_namespace(node, namespace, interface):
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip link set {0} netns {1}'.format(interface, namespace)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))
    @staticmethod
    def set_int_ip_in_namespace(node, namespace, interface, ip, prefix):
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip netns exec {0} ip addr add {1}/{2} dev {3}'.format(namespace, ip, prefix, interface)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))

    @staticmethod
    def set_int_state_in_namespace(node, namespace, interface, state="up"):
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip netns exec {0} ip link set {1} {2}'.format(namespace, interface, state)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))

    @staticmethod
    def create_bridge_for_int_in_namespace(node, namespace, bridge_name, interface1, interface2):
        cmd = 'ip netns exec {0} brctl addbr {1}'.format(namespace, bridge_name)
        exec_cmd_no_error(node, cmd, sudo=True)
        cmd = 'ip netns exec {0} brctl addif {1} {2}'.format(namespace, bridge_name, interface1)
        exec_cmd_no_error(node, cmd, sudo=True)
        cmd = 'ip netns exec {0} brctl addif {1} {2}'.format(namespace, bridge_name, interface2)
        exec_cmd_no_error(node, cmd, sudo=True)
        cmd = 'ip netns exec {0} ifconfig {1} up'.format(namespace, bridge_name)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def int_add_route_in_namespace(node, namespace, ip, prefix, gw):
        cmd = 'ip netns exec {} ip route add {}/{} via {}'.format(namespace, ip, prefix, gw)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def clean_up(node):
        ssh = SSH()
        ssh.connect(node)
        print "Clean all namespaces"
        cmd = 'rm -Rf /var/run/netns/ && sudo -S mkdir /var/run/netns'
        (rc, stdout, stderr) = ssh.exec_command_sudo(cmd)
        if rc != 0:
            raise RuntimeError('Could not clean namespaces')
