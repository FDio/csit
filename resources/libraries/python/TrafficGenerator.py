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

"""Performance testing traffic generator library."""

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import NodeSubTypeTG
from resources.libraries.python.topology import Topology

__all__ = ['TrafficGenerator']

class TrafficGenerator(object):
    """Traffic Generator"""

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self._result = None
        self._loss = None
        self._sent = None
        self._received = None
        #T-REX interface order mapping
        self._ifaces_reordered = 0

    def initialize_traffic_generator(self, tg_node, tg_if1, tg_if2,
                                     dut1_node, dut1_if1, dut1_if2,
                                     dut2_node, dut2_if1, dut2_if2,
                                     test_type):
        """TG initialization
        :param tg_node: Traffic generator node
        :param tg_if1: TG - name of first interface
        :param tg_if2: TG - name of second interface
        :param dut1_node: DUT1 node
        :param dut1_if1: DUT1 - name of first interface
        :param dut1_if2: DUT1 - name of second interface
        :param dut2_node: DUT2 node
        :param dut2_if1: DUT2 - name of first interface
        :param dut2_if2: DUT2 - name of second interface
        :test_type: 'L2' or 'L3' - src/dst MAC address
        :type tg_node: dict
        :type tg_if1: str
        :type tg_if2: str
        :type dut1_node: dict
        :type dut1_if1: str
        :type dut1_if2: str
        :type dut2_node: dict
        :type dut2_if1: str
        :type dut2_if2: str
        :type test_type: str
        :return: nothing
        """

        trex_path = "/opt/trex-core-1.91"

        topo = Topology()

        if tg_node['type'] != NodeType.TG:
            raise Exception('Node type is not a TG')
        if tg_node['subtype'] == NodeSubTypeTG.TREX:
            ssh = SSH()
            ssh.connect(tg_node)

            if1_pci = topo.get_interface_pci_addr(tg_node, tg_if1)
            if2_pci = topo.get_interface_pci_addr(tg_node, tg_if2)
            if1_mac = topo.get_interface_mac(tg_node, tg_if1)
            if2_mac = topo.get_interface_mac(tg_node, tg_if2)

            if test_type == 'L2':
                if1_adj_mac = if2_mac
                if2_adj_mac = if1_mac
            elif test_type == 'L3':
                if1_adj_mac = topo.get_interface_mac(dut1_node, dut1_if1)
                if2_adj_mac = topo.get_interface_mac(dut2_node, dut2_if2)
            else:
                raise Exception("test_type unknown")

            if min(if1_pci, if2_pci) != if1_pci:
                if1_mac, if2_mac = if2_mac, if1_mac
                if1_pci, if2_pci = if2_pci, if1_pci
                if1_adj_mac, if2_adj_mac = if2_adj_mac, if1_adj_mac
                self._ifaces_reordered = 1

            if1_mac_hex = "0x"+if1_mac.replace(":", ",0x")
            if2_mac_hex = "0x"+if2_mac.replace(":", ",0x")
            if1_adj_mac_hex = "0x"+if1_adj_mac.replace(":", ",0x")
            if2_adj_mac_hex = "0x"+if2_adj_mac.replace(":", ",0x")

            (ret, stdout, stderr) = ssh.exec_command(
                "sudo sh -c 'cat << EOF > /etc/trex_cfg.yaml\n"
                "- port_limit      : 2\n"
                "  version         : 2\n"
                "  interfaces      : [\"{}\",\"{}\"]\n"
                "  port_info       :\n"
                "          - dest_mac        :   [{}]\n"
                "            src_mac         :   [{}]\n"
                "          - dest_mac        :   [{}]\n"
                "            src_mac         :   [{}]\n"
                "EOF'"\
                .format(if1_pci, if2_pci,
                        if1_adj_mac_hex, if1_mac_hex,
                        if2_adj_mac_hex, if2_mac_hex))
            if int(ret) != 0:
                logger.error("failed to create t-rex config: {}"\
                .format(stdout + stderr))
                raise RuntimeError('trex config generation error')

            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c 'cd {0}/scripts/ && "
                "sudo ./trex-cfg'"\
                .format(trex_path))
            if int(ret) != 0:
                logger.error('trex-cfg failed: {0}'.format(stdout + stderr))
                raise RuntimeError('trex-cfg failed')

            (ret, _, _) = ssh.exec_command(
                "sh -c 'cd {0}/scripts/ && "
                "sudo nohup ./t-rex-64 -i -c 4 --iom 0 > /dev/null 2>&1 &'"
                "> /dev/null"\
                .format(trex_path))
            if int(ret) != 0:
                raise RuntimeError('t-rex-64 startup failed')

    @staticmethod
    def teardown_traffic_generator(node):
        """TG teardown
        :param node: Traffic generator node
        :type node: dict
        :return: nothing
        """

        if node['type'] != NodeType.TG:
            raise Exception('Node type is not a TG')
        if node['subtype'] == NodeSubTypeTG.TREX:
            ssh = SSH()
            ssh.connect(node)
            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c 'sudo pkill t-rex'")
            if int(ret) != 0:
                logger.error('pkill t-rex failed: {0}'.format(stdout + stderr))
                raise RuntimeError('pkill t-rex failed')

    def send_traffic_on(self, nodes_info, duration, rate,
                        framesize, traffic_type):
        """Send traffic from all configured interfaces on TG
        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :param duration: Duration of test traffic generation in seconds
        :param rate: Offered load per interface (e.g. 1%, 3gbps, 4mpps, ...)
        :param framesize: Frame size (L2) in Bytes
        :param traffic_type: Traffic profile
        :type nodes_info: dict
        :type duration: str
        :type rate: str
        :type framesize: str
        :type traffic_type: str
        :return: TG output
        :rtype: str
        """

        node = nodes_info["TG"]

        if node['type'] != NodeType.TG:
            raise Exception('Node type is not a TG')

        if node['subtype'] is None:
            raise Exception('TG subtype not defined')

        ssh = SSH()
        ssh.connect(node)

        if node['subtype'] == NodeSubTypeTG.TREX:

            _p0 = 1
            _p1 = 2

            if self._ifaces_reordered != 0:
                _p0, _p1 = _p1, _p0

            if traffic_type in ["3-node-xconnect", "3-node-bridge"]:
                (ret, stdout, stderr) = ssh.exec_command(
                    "sh -c '/tmp/openvpp-testing/resources/tools/t-rex/"
                    "t-rex-stateless.py "
                    "-d {0} -r {1} -s {2} "
                    "--p{3}_src_start_ip 10.10.10.1 "
                    "--p{3}_src_end_ip 10.10.10.254 "
                    "--p{3}_dst_start_ip 20.20.20.1 "
                    "--p{4}_src_start_ip 20.20.20.1 "
                    "--p{4}_src_end_ip 20.20.20.254 "
                    "--p{4}_dst_start_ip 10.10.10.1'".\
                    format(duration, rate, framesize, _p0, _p1),\
                    timeout=int(duration)+60)
            elif traffic_type in ["3-node-IPv4"]:
                (ret, stdout, stderr) = ssh.exec_command(
                    "sh -c '/tmp/openvpp-testing/resources/tools/t-rex/"
                    "t-rex-stateless.py "
                    "-d {0} -r {1} -s {2} "
                    "--p{3}_src_start_ip 10.10.10.2 "
                    "--p{3}_src_end_ip 10.10.10.254 "
                    "--p{3}_dst_start_ip 20.20.20.2 "
                    "--p{4}_src_start_ip 20.20.20.2 "
                    "--p{4}_src_end_ip 20.20.20.254 "
                    "--p{4}_dst_start_ip 10.10.10.2'".\
                    format(duration, rate, framesize, _p0, _p1),\
                    timeout=int(duration)+60)
            else:
                raise NotImplementedError('Unsupported traffic type')

        else:
            raise NotImplementedError("TG subtype not supported")

        logger.trace(ret)
        logger.trace(stdout)
        logger.trace(stderr)

        for line in stdout.splitlines():
            pass

        self._result = line
        logger.info('TrafficGen result: {0}'.format(self._result))

        self._loss = self._result.split(', ')[3].split('=')[1]

        return self._result

    def no_traffic_loss_occured(self):
        """Fail is loss occured in traffic run
        :return: nothing
        """

        if self._loss is None:
            raise Exception('The traffic generation has not been issued')
        if self._loss != '0':
            raise Exception('Traffic loss occured: {0}'.format(self._loss))
