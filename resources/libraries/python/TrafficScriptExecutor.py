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

"""Traffic script executor library."""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd

__all__ = [u"TrafficScriptExecutor"]


class TrafficScriptExecutor:
    """Traffic script executor utilities."""

    @staticmethod
    def run_traffic_script_on_node(
            script_file_name, node, script_args, timeout=60):
        """Run traffic script on the TG node.

        :param script_file_name: Traffic script name.
        :param node: Node to run traffic script on.
        :param script_args: Traffic scripts arguments.
        :param timeout: Timeout (optional).
        :type script_file_name: str
        :type node: dict
        :type script_args: str
        :type timeout: int
        :raises RuntimeError: ICMP echo Rx timeout.
        :raises RuntimeError: DHCP REQUEST Rx timeout.
        :raises RuntimeError: DHCP DISCOVER Rx timeout.
        :raises RuntimeError: TCP/UDP Rx timeout.
        :raises RuntimeError: ARP reply timeout.
        :raises RuntimeError: Traffic script execution failed.
        """
        cmd = f"cd {Constants.REMOTE_FW_DIR}; virtualenv -p $(which python3) " \
            f"--system-site-packages --never-download env && " \
            f"export PYTHONPATH=${{PWD}}; . ${{PWD}}/env/bin/activate; " \
            f"resources/traffic_scripts/{script_file_name} {script_args}"

        ret_code, stdout, stderr = exec_cmd(
            node, cmd, timeout=timeout, sudo=True
        )
        if ret_code != 0:
            if u"RuntimeError: ICMP echo Rx timeout" in stderr:
                msg = "ICMP echo Rx timeout"
            elif u"RuntimeError: IP packet Rx timeout" in stderr:
                msg = u"IP packet Rx timeout"
            elif u"RuntimeError: DHCP REQUEST Rx timeout" in stderr:
                msg = u"DHCP REQUEST Rx timeout"
            elif u"RuntimeError: DHCP DISCOVER Rx timeout" in stderr:
                msg = u"DHCP DISCOVER Rx timeout"
            elif u"RuntimeError: TCP/UDP Rx timeout" in stderr:
                msg = u"TCP/UDP Rx timeout"
            elif u"Error occurred: ARP reply timeout" in stdout:
                msg = u"ARP reply timeout"
            elif u"RuntimeError: ESP packet Rx timeout" in stderr:
                msg = u"ESP packet Rx timeout"
            else:
                msg = u"Traffic script execution failed"
            raise RuntimeError(msg)

    @staticmethod
    def traffic_script_gen_arg(rx_if, tx_if, src_mac, dst_mac, src_ip, dst_ip):
        """Generate traffic script basic arguments string.

        :param rx_if: Interface that receives traffic.
        :param tx_if: Interface that sends traffic.
        :param src_mac: Source MAC address.
        :param dst_mac: Destination MAC address.
        :param src_ip: Source IP address.
        :param dst_ip: Destination IP address.
        :type rx_if: str
        :type tx_if: str
        :type src_mac: str
        :type dst_mac: str
        :type src_ip: str
        :type dst_ip: str
        :returns: Traffic script arguments string.
        :rtype: str
        """
        args = f"--rx_if {rx_if} --tx_if {tx_if} --src_mac {src_mac} " \
            f"--dst_mac {dst_mac} --src_ip {src_ip} --dst_ip {dst_ip}"
        return args
