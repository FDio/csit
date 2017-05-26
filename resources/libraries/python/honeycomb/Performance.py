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

"""Implementation of keywords for managing Honeycomb notifications."""

from resources.libraries.python.topology import Topology
from resources.libraries.python.ssh import SSH
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class Performance(object):
    def __init__(self):
        pass

    @staticmethod
    def blacklist_interface(node, interface, remove=False):
        """Restore the default driver, configure an IP address
         on the specified interface and set interface up, or remove IP address
         and set interface down.
         Note: When VPP starts, it overrides NIC driver on all interfaces that
         are down and do not have an IP address.

         :param node: VPP node.
         :param interface: Name, link name or sw_if_index of an interface.
         :param remove: Remove interface from blacklist.
         :type node: dict
         :type interface: str or int
         :type remove: bool
         :raises RuntimeError: If the configuration fails.
         """

        interface_key = Topology.convert_interface_reference_to_key(
            node, interface)
        mac = Topology.get_interface_mac(node, interface_key)

        ssh = SSH()
        ssh.connect(node)

        if remove:
            # Get interface name in Linux OS
            cmd = "ifconfig -a | grep \'HWaddr {0}\' | cut -d \' \' -f " \
                  "1".format(mac)
            ret_code, interface, _ = ssh.exec_command_sudo(cmd)
            if ret_code != 0:
                raise RuntimeError("Could not find interface name.")
            # Set interface down and clear IP addresses
            cmd = "sudo ifconfig {0} down && sudo ip addr flush dev {0}".format(
                interface)

        else:
            # Set driver back to default
            InterfaceUtil.set_interface_driver(
                node,
                node["interfaces"][interface_key]["pci-address"],
                node["interfaces"][interface_key]["driver"]
            )

            # Get interface name in Linux OS
            cmd = "ifconfig -a | grep \'HWaddr {0}\' | cut -d \' \' -f " \
                  "1".format(interface)
            ret_code, interface, _ = ssh.exec_command_sudo(cmd)
            if ret_code != 0:
                raise RuntimeError("Could not find interface name.")

            # Set interface up with IP address
            cmd = "sudo ifconfig {0} inet 1.1.1.1/30 && sudo ifup {0}".format(
                interface)

        ret_code, _, _ = ssh.exec_command_sudo(cmd)
        if ret_code != 0:
            raise RuntimeError("Could not configure interface.")
