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

"""Traffic script executor library."""

from robot.api import logger

from resources.libraries.python.constants import Constants
from resources.libraries.python.ssh import SSH

__all__ = ['TrafficScriptExecutor']


class TrafficScriptExecutor(object):
    """Traffic script executor utilities."""

    @staticmethod
    def _escape(string):
        """Escape quotation mark and dollar mark for shell command.

        :param string: String to escape.
        :type string: str
        :return: Escaped string.
        :rtype: str
        """
        return string.replace('"', '\\"').replace("$", "\\$")

    @staticmethod
    def run_traffic_script_on_node(script_file_name, node, script_args,
                                   timeout=60):
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
        :raises RuntimeError: DHCP DISCOVER timeout.
        :raises RuntimeError: TCP/UDP Rx timeout.
        :raises RuntimeError: ARP reply timeout.
        :raises RuntimeError: Traffic script execution failed.
        """
        logger.trace("{}".format(timeout))
        ssh = SSH()
        ssh.connect(node)
        cmd = ("cd {}; virtualenv --system-site-packages env && " +
               "export PYTHONPATH=${{PWD}}; " +
               ". ${{PWD}}/env/bin/activate; " +
               "resources/traffic_scripts/{} {}") \
                  .format(Constants.REMOTE_FW_DIR, script_file_name,
                          script_args)
        (ret_code, stdout, stderr) = ssh.exec_command_sudo(
            'sh -c "{}"'.format(TrafficScriptExecutor._escape(cmd)),
            timeout=timeout)
        logger.debug("stdout: {}".format(stdout))
        logger.debug("stderr: {}".format(stderr))
        logger.debug("ret_code: {}".format(ret_code))
        if ret_code != 0:
            if "RuntimeError: ICMP echo Rx timeout" in stderr:
                raise RuntimeError("ICMP echo Rx timeout")
            elif "RuntimeError: DHCP REQUEST Rx timeout" in stderr:
                raise RuntimeError("DHCP REQUEST Rx timeout")
            elif "RuntimeError: DHCP DISCOVER Rx timeout" in stderr:
                raise RuntimeError("DHCP DISCOVER Rx timeout")
            elif "RuntimeError: TCP/UDP Rx timeout" in stderr:
                raise RuntimeError("TCP/UDP Rx timeout")
            elif "Error occurred: ARP reply timeout" in stdout:
                raise RuntimeError("ARP reply timeout")
            else:
                raise RuntimeError("Traffic script execution failed")

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
        :return: Traffic script arguments string.
        :rtype: str
        """
        args = ('--rx_if {0} --tx_if {1} --src_mac {2} --dst_mac {3} --src_ip'
                ' {4} --dst_ip {5}').format(rx_if, tx_if, src_mac, dst_mac,
                                            src_ip, dst_ip)
        return args
