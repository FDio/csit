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

"""Traffic generator library."""

from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import NodeSubTypeTG
#from resources.libraries.python.topology import Topology

__all__ = ['TrafficGenerator']

class TrafficGenerator(object):
    """Traffic Generator"""

    def __init__(self):
        self._result = None
        self._loss = None
        self._sent = None
        self._received = None

    @staticmethod
    def initialize_traffic_generator(node, interface1, interface2):
        """TG initialization
        :param node: Traffic generator node
        :param interface1: PCI address of first interface
        :param interface2: PCI address of second interface
        :type node: dict
        :type interface1: str
        :type interface2: str
        :return: nothing
        """

        trex_path = "/opt/trex-core-1.91"

        if node['type'] != NodeType.TG:
            raise Exception('Node type is not a TG')
        if node['subtype'] == NodeSubTypeTG.TREX:
            ssh = SSH()
            ssh.connect(node)

            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c 'cd {0}/scripts/ && sudo modprobe uio && "
                "sudo insmod ./ko/src/igb_uio.ko'"\
                .format(trex_path))

            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c 'cd {0}/scripts/ && "
                "sudo nohup ./t-rex-64 -i -c 4 --iom 0 > /dev/null 2>&1 &'"\
                .format(trex_path))

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

    def send_traffic_on(self, nodes_info, duration, rate,
                        framesize, traffic_type):
        """Send traffic from all configured interfaces on TG
        :param nodes_info: Dictionary containing information on all nodes
        in topology.
        :param duration: Duration of test traffic generation in seconds
        :param rate: Percentage of linerate
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

        #tg_port3_src_mac = Topology.get_interface_mac_by_port_key(node, "port3")
        #_, adj_int = Topology.\
        #    get_adjacent_node_and_interface_by_key(nodes_info, node, "port3")
        #tg_port3_dst_mac = adj_int['mac_address']

        #tg_port5_src_mac = Topology.get_interface_mac_by_port_key(node, "port5")
        #_, adj_int = Topology.\
        #    get_adjacent_node_and_interface_by_key(nodes_info, node, "port5")
        #tg_port5_dst_mac = adj_int['mac_address']


        if node['subtype'] == NodeSubTypeTG.TREX:
            if traffic_type in ["3-node-xconnect", "3-node-bridge"]:
                (ret, stdout, stderr) = ssh.exec_command(
                    "sh -c '/tmp/openvpp-testing/resources/tools/t-rex-stateless.py "
                    "-d {0} -r {1}% -s {2} "
                    #"--p1_src_mac 52:00:00:00:00:01 "
                    #"--p1_dst_mac 52:00:00:00:00:02 "
                    "--p1_src_start_ip 10.10.10.1 "
                    #"--p1_src_end_ip 10.10.10.254 "
                    "--p1_dst_start_ip 20.20.20.1 "
                    #"--p1_dst_end_ip 20.20.20.254 "
                    #"--p2_src_mac 52:00:00:00:00:02 "
                    #"--p2_dst_mac 52:00:00:00:00:01 "
                    "--p2_src_start_ip 20.20.20.1 "
                    #"--p2_src_end_ip 20.20.20.254 "
                    "--p2_dst_start_ip 10.10.10.1'".\
                    #"--p2_dst_end_ip 10.10.10.254'".\
                    format(duration, rate, framesize), timeout=int(duration)+60)
            elif traffic_type in ["3-node-IPv4"]:
                (ret, stdout, stderr) = ssh.exec_command(
                    "sh -c '/tmp/openvpp-testing/resources/tools/t-rex-stateless.py "
                    "-d {0} -r {1}% -s {2} "
                    #"--p1_src_mac {3} "
                    #"--p1_dst_mac {4} "
                    "--p1_src_start_ip 10.10.10.2 "
                    #"--p1_src_end_ip 10.10.10.254 "
                    "--p1_dst_start_ip 20.20.20.2 "
                    #"--p1_dst_end_ip 20.20.20.2 "
                    #"--p2_src_mac {5} "
                    #"--p2_dst_mac {6} "
                    "--p2_src_start_ip 20.20.20.2 "
                    #"--p2_src_end_ip 20.20.20.254 "
                    "--p2_dst_start_ip 10.10.10.2'".\
                    #"--p2_dst_end_ip 10.10.10.2'".\
                    format(duration, rate, framesize),\
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
