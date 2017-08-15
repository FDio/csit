# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""Keywords used for setup and testing of Honeycomb's control-plane interface
using IPv6.
"""

from resources.libraries.python.ssh import SSH


class IPv6Management(object):
    """Utilities for managing IPv6 contol-plane interfaces."""

    def __init__(self):
        pass

    @staticmethod
    def get_interface_name_by_mac(node, mac):
        """Get the name of an interface from ifconfig using its MAC address.

        :param node: Node in topology.
        :param mac: MAC address.
        :type node: dict
        :type mac: str
        """

        cmd = " | ".join([
            "sudo ifconfig -a",
            "grep {0}".format(mac),
            "awk '{print $1}'"
        ])

        ssh = SSH()
        ssh.connect(node)
        ret_code, stdout, _ = ssh.exec_command(cmd)

        if ret_code == 0:
            return stdout.strip()
        else:
            raise RuntimeError("No interface found using the specified MAC "
                               "address.")

    @staticmethod
    def bind_interface_driver(node, pci, old_driver, new_driver):
        """Bind the specified network interface to a new driver.

        :param node: Node in topology.
        :param pci: PCI address of the interface.
        :param old_driver: Name of the driver currently being used.
        :param new_driver: Name of the driver to bind to.
        :type node: dict
        :type pci: str
        :type old_driver: str
        :type new_driver: str
        """

        ssh = SSH()
        ssh.connect(node)
        # Unbind from old driver
        cmd = "sh -c 'echo {pci} > " \
              "/sys/bus/pci/drivers/{old_driver}/unbind'".format(
                pci=pci, old_driver=old_driver)
        ssh.exec_command_sudo(cmd)
        # Bind to new driver
        cmd = "sh -c 'echo {pci} > " \
              "/sys/bus/pci/drivers/{new_driver}/bind'".format(
                pci=pci, new_driver=new_driver)
        ssh.exec_command_sudo(cmd)

    @staticmethod
    def clear_interface_configuration(node, interface):
        """Remove all configured IP addresses from the specified interface
         and set it into down state.

         :param node: Node in topology.
         :param interface: Name of an interface on the node.
         :type node: dict
         :type interface: str
         """

        cmd = " | ".join([
            "sudo ip addr flush dev {interface}".format(interface=interface),
            "sudo ifconfig {interface} down".format(interface=interface)
        ])

        ssh = SSH()
        ssh.connect(node)
        _, stdout, _ = ssh.exec_command(cmd)

    @staticmethod
    def set_management_interface_address(node, interface, address, prefix):
        """Configure an IP address on the specified interface.

        :param node: Node in topology.
        :param interface: Name of an interface on the node.
        :param address: IP address to configure.
        :param prefix: IP network prefix.
        :type node: dict
        :type interface: str
        :type address: str
        :type prefix: int
        """

        cmd = "sudo ifconfig {interface} add {address}/{prefix} up".format(
            interface=interface,
            address=address,
            prefix=prefix
        )

        ssh = SSH()
        ssh.connect(node)
        ssh.exec_command(cmd)

    @staticmethod
    def configure_control_interface_tunnel(node, src_port, dst_ip, dst_port):
        """Configure a tunnel on the specified node, tunelling any IPv4 traffic
        from one port to the specified address.

        :param node: Node in topology.
        :param src_port: Port to tunnel traffic from.
        :param dst_ip: IP address to tunnel traffic to.
        :param dst_port: Port to tunnel traffic to.
        :type node: dict
        :type src_port: int
        :type dst_ip: str
        :type dst_port: int
        """

        cmd = "nohup socat TCP4-LISTEN:{src_port},fork,su=nobody " \
              "TCP6:[{dst_ip}]:{dst_port} $@ > " \
              "/tmp/socat.log 2>&1 &".format(
                src_port=src_port,
                dst_ip=dst_ip,
                dst_port=dst_port
                )

        ssh = SSH()
        ssh.connect(node)
        ssh.exec_command_sudo(cmd)
