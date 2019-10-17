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

from resources.libraries.python.ssh import exec_cmd_no_error


class IPv6Management(object):
    """Utilities for managing IPv6 contol-plane interfaces."""

    @staticmethod
    def get_interface_name_by_mac(node, mac):
        """Get the name of an interface using its MAC address.

        :param node: Node in topology.
        :param mac: MAC address.
        :type node: dict
        :type mac: str
        :returns: Name of the interface.
        :rtype: str
        :raises RuntimeError: If no interface is found.
        """

        cmd = " | ".join([
            "fgrep -ls '{0}' /sys/class/net/*/address".format(mac),
            "awk -F '/' '{print $5}'"
        ])

        message = "No interface found using the specified MAC address."
        # TODO: other modules in this package raise HoneycombError
        stdout, _ = exec_cmd_no_error(node, cmd, message=message)
        return stdout.strip()

    @staticmethod
    def clear_interface_configuration(node, interface):
        """Remove all configured IP addresses from the specified interface
         and set it into down state.

         :param node: Node in topology.
         :param interface: Name of an interface on the node.
         :type node: dict
         :type interface: str
         :raises RuntimeError: If the configuration could not be cleared.
         """

        cmd = " && ".join([
            "ip addr flush dev {interface}".format(interface=interface),
            "ip link set dev {interface} down".format(interface=interface)
        ])

        message = "Could not clear interface configuration."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

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
        :raises RuntimeError: If the configuration fails.
        """
        # Enable IPv6 for only the specified interface
        cmd = "sysctl net.ipv6.conf.{0}.disable_ipv6=0".format(interface)
        message = "Could not enable IPv6 on interface."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

        # Configure IPv6 address on the interface
        cmd = "ip address add {address}/{prefix} dev {interface}".format(
            interface=interface,
            address=address,
            prefix=prefix)
        message = "Could not configure IP address on interface."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

        # Set the interface up
        cmd = "ip link set {interface} up".format(interface=interface)
        message = "Could not change the interface to 'up' state."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

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
        :raises RuntimeError: If tunnel creation is not successful.
        """

        cmd = "nohup socat TCP4-LISTEN:{src_port},fork,su=nobody " \
              "TCP6:[{dst_ip}]:{dst_port} $@ > " \
              "/tmp/socat.log 2>&1 &".format(
                  src_port=src_port,
                  dst_ip=dst_ip,
                  dst_port=dst_port)
        message = "Could not configure tunnel."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)
