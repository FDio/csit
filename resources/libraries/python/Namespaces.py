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

from resources.libraries.python.ssh import exec_cmd, SSH


class Namespaces(object):
    """Namespace utilities."""

    @staticmethod
    def attach_interface_to_namespace(node, interface, namespace):
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip link set {0} netns {1}'.format(interface, namespace)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))
    @staticmethod
    def set_int_ip_for_namespace(node, namespace, interface, ip, prefix):
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip netns exec {0} ip addr add {1}/{2} dev {3}'.format(namespace, ip, prefix, interface)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))

    @staticmethod
    def set_int_state_for_namespace(node, namespace, interface, state="up"):
        ssh = SSH()
        ssh.connect(node)
        cmd = 'ip netns exec {0} ip link set {1} {2}'.format(namespace, interface, state)
        (rc, stdout, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not..., reason:{0}'.format(stderr))
