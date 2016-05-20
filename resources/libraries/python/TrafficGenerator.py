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
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.constants import Constants
from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import NodeSubTypeTG
from resources.libraries.python.topology import Topology
from resources.libraries.python.DropRateSearch import DropRateSearch

__all__ = ['TrafficGenerator', 'TGDropRateSearchImpl']


class TGDropRateSearchImpl(DropRateSearch):
    """Drop Rate Search implementation."""

    def __init__(self):
        super(TGDropRateSearchImpl, self).__init__()

    def measure_loss(self, rate, frame_size, loss_acceptance,
                     loss_acceptance_type, traffic_type):

        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            'resources.libraries.python.TrafficGenerator')

        if tg_instance._node['subtype'] is None:
            raise Exception('TG subtype not defined')
        elif tg_instance._node['subtype'] == NodeSubTypeTG.TREX:
            unit_rate = str(rate) + self.get_rate_type_str()
            tg_instance.trex_stl_start_remote_exec(self.get_duration(),
                                                   unit_rate, frame_size,
                                                   traffic_type)
            # Get latency stats from stream
            self._latency_stats = tg_instance.get_latency()

            loss = tg_instance.get_loss()
            sent = tg_instance.get_sent()
            if self.loss_acceptance_type_is_percentage():
                loss = (float(loss) / float(sent)) * 100

            # TODO: getters for tg_instance
            logger.trace("comparing: {} < {} {}".format(loss,
                                                        loss_acceptance,
                                                        loss_acceptance_type))
            if float(loss) > float(loss_acceptance):
                return False
            else:
                return True
        else:
            raise NotImplementedError("TG subtype not supported")


class TrafficGenerator(object):
    """Traffic Generator."""

    # use one instance of TrafficGenerator for all tests in test suite
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self._result = None
        self._loss = None
        self._sent = None
        self._latency = None
        self._received = None
        self._node = None
        # T-REX interface order mapping
        self._ifaces_reordered = 0

    def get_loss(self):
        """Return number of lost packets.

        :return: Number of lost packets.
        :rtype: str
        """
        return self._loss

    def get_sent(self):
        """Return number of sent packets.

        :return: Number of sent packets.
        :rtype: str
        """
        return self._sent

    def get_received(self):
        """Return number of received packets.

        :return: Number of received packets.
        :rtype: str
        """
        return self._received

    def get_latency(self):
        """Return min/avg/max latency.

        :return: Latency stats.
        :rtype: list
        """
        return self._latency

    #pylint: disable=too-many-arguments, too-many-locals
    def initialize_traffic_generator(self, tg_node, tg_if1, tg_if2,
                                     tg_if1_adj_node, tg_if1_adj_if,
                                     tg_if2_adj_node, tg_if2_adj_if,
                                     test_type):
        """TG initialization.

        :param tg_node: Traffic generator node.
        :param tg_if1: TG - name of first interface.
        :param tg_if2: TG - name of second interface.
        :param tg_if1_adj_node: TG if1 adjecent node.
        :param tg_if1_adj_if: TG if1 adjecent interface.
        :param tg_if2_adj_node: TG if2 adjecent node.
        :param tg_if2_adj_if: TG if2 adjecent interface.
        :test_type: 'L2' or 'L3' - src/dst MAC address.
        :type tg_node: dict
        :type tg_if1: str
        :type tg_if2: str
        :type tg_if1_adj_node: dict
        :type tg_if1_adj_if: str
        :type tg_if2_adj_node: dict
        :type tg_if2_adj_if: str
        :type test_type: str
        :return: nothing
        """

        topo = Topology()

        if tg_node['type'] != NodeType.TG:
            raise Exception('Node type is not a TG')
        self._node = tg_node

        if tg_node['subtype'] == NodeSubTypeTG.TREX:
            trex_path = "/opt/trex-core-2.03"

            ssh = SSH()
            ssh.connect(tg_node)

            (ret, stdout, stderr) = ssh.exec_command(
                "sudo sh -c '{}/resources/tools/t-rex/"
                "t-rex-installer.sh'".format(Constants.REMOTE_FW_DIR),
                timeout=1800)
            if int(ret) != 0:
                logger.error('trex installation failed: {0}'.format(
                    stdout + stderr))
                raise RuntimeError('Installation of TG failed')

            if1_pci = topo.get_interface_pci_addr(tg_node, tg_if1)
            if2_pci = topo.get_interface_pci_addr(tg_node, tg_if2)
            if1_mac = topo.get_interface_mac(tg_node, tg_if1)
            if2_mac = topo.get_interface_mac(tg_node, tg_if2)

            if test_type == 'L2':
                if1_adj_mac = if2_mac
                if2_adj_mac = if1_mac
            elif test_type == 'L3':
                if1_adj_mac = topo.get_interface_mac(tg_if1_adj_node,
                                                     tg_if1_adj_if)
                if2_adj_mac = topo.get_interface_mac(tg_if2_adj_node,
                                                     tg_if2_adj_if)
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
                "  port_bandwidth_gb : 10\n"
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
                "sh -c 'cd {0}/scripts/ && sudo ./trex-cfg'".format(trex_path))
            if int(ret) != 0:
                logger.error('trex-cfg failed: {0}'.format(stdout + stderr))
                raise RuntimeError('trex-cfg failed')

            max_startup_retries = 3
            while max_startup_retries > 0:
                # kill T-rex only if it is already running
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'pgrep t-rex && sudo pkill t-rex'")

                # start T-rex
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'cd {0}/scripts/ && "
                    "sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /dev/null 2>&1 &'"
                    "> /dev/null"\
                    .format(trex_path))
                if int(ret) != 0:
                    raise RuntimeError('t-rex-64 startup failed')

                # get T-rex server info
                (ret, _, _) = ssh.exec_command(
                    "sh -c '{0}/resources/tools/t-rex/t-rex-server-info.py'"\
                    .format(Constants.REMOTE_FW_DIR),
                    timeout=120)
                if int(ret) == 0:
                    # If we get info T-rex is running
                    return
                # try again
                max_startup_retries -= 1
            # after max retries T-rex is still not responding to API
            # critical error occured
            raise RuntimeError('t-rex-64 startup failed')


    @staticmethod
    def teardown_traffic_generator(node):
        """TG teardown.

        :param node: Traffic generator node.
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

    @staticmethod
    def trex_stl_stop_remote_exec(node):
        """Execute script on remote node over ssh to stop running traffic.

        :param node: T-REX generator node.
        :type node: dict
        :return: Nothing
        """
        ssh = SSH()
        ssh.connect(node)

        (ret, stdout, stderr) = ssh.exec_command(
            "sh -c '{}/resources/tools/t-rex/"
            "t-rex-stateless-stop.py'".format(Constants.REMOTE_FW_DIR))
        logger.trace(ret)
        logger.trace(stdout)
        logger.trace(stderr)

        if int(ret) != 0:
            raise RuntimeError('T-rex stateless runtime error')

    def trex_stl_start_remote_exec(self, duration, rate, framesize,
                                   traffic_type, async_call=False,
                                   latency=True, warmup_time=5):
        """Execute script on remote node over ssh to start traffic.

        :param duration: Time expresed in seconds for how long to send traffic.
        :param rate: Traffic rate expressed with units (pps, %)
        :param framesize: L2 frame size to send (without padding and IPG).
        :param traffic_type: Traffic profile.
        :param async_call: If enabled then don't wait for all incomming trafic.
        :param latency: With latency measurement.
        :param warmup_time: Warmup time period.
        :type duration: int
        :type rate: str
        :type framesize: int
        :type traffic_type: str
        :type async_call: bool
        :type latency: bool
        :type warmup_time: int
        :return: Nothing
        """
        ssh = SSH()
        ssh.connect(self._node)

        _p0 = 1
        _p1 = 2
        _async = ""
        _latency = ""

        if async_call:
            _async = "--async"
        if latency:
            _latency = "--latency"
        if self._ifaces_reordered != 0:
            _p0, _p1 = _p1, _p0

        if traffic_type in ["3-node-xconnect", "3-node-bridge"]:
            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c '{0}/resources/tools/t-rex/t-rex-stateless.py "
                "--duration={1} -r {2} -s {3} "
                "--p{4}_src_start_ip 10.10.10.1 "
                "--p{4}_src_end_ip 10.10.10.254 "
                "--p{4}_dst_start_ip 20.20.20.1 "
                "--p{5}_src_start_ip 20.20.20.1 "
                "--p{5}_src_end_ip 20.20.20.254 "
                "--p{5}_dst_start_ip 10.10.10.1 "
                "{6} {7} --warmup_time={8}'".format(Constants.REMOTE_FW_DIR,
                                                    duration, rate, framesize,
                                                    _p0, _p1, _async, _latency,
                                                    warmup_time),
                timeout=int(duration)+60)
        elif traffic_type in ["3-node-IPv4"]:
            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c '{0}/resources/tools/t-rex/t-rex-stateless.py "
                "--duration={1} -r {2} -s {3} "
                "--p{4}_src_start_ip 10.10.10.2 "
                "--p{4}_src_end_ip 10.10.10.254 "
                "--p{4}_dst_start_ip 20.20.20.2 "
                "--p{5}_src_start_ip 20.20.20.2 "
                "--p{5}_src_end_ip 20.20.20.254 "
                "--p{5}_dst_start_ip 10.10.10.2 "
                "{6} {7} --warmup_time={8}'".format(Constants.REMOTE_FW_DIR,
                                                    duration, rate, framesize,
                                                    _p0, _p1, _async, _latency,
                                                    warmup_time),
                timeout=int(duration)+60)
        elif traffic_type in ["3-node-IPv6"]:
            (ret, stdout, stderr) = ssh.exec_command(
                "sh -c '{0}/resources/tools/t-rex/t-rex-stateless.py "
                "--duration={1} -r {2} -s {3} -6 "
                "--p{4}_src_start_ip 2001:1::2 "
                "--p{4}_src_end_ip 2001:1::FE "
                "--p{4}_dst_start_ip 2001:2::2 "
                "--p{5}_src_start_ip 2001:2::2 "
                "--p{5}_src_end_ip 2001:2::FE "
                "--p{5}_dst_start_ip 2001:1::2 "
                "{6} {7} --warmup_time={8}'".format(Constants.REMOTE_FW_DIR,
                                                    duration, rate, framesize,
                                                    _p0, _p1, _async, _latency,
                                                    warmup_time),
                timeout=int(duration)+60)
        else:
            raise NotImplementedError('Unsupported traffic type')

        logger.trace(ret)
        logger.trace(stdout)
        logger.trace(stderr)

        if int(ret) != 0:
            raise RuntimeError('T-rex stateless runtime error')
        elif async_call:
            #no result
            self._received = None
            self._sent = None
            self._loss = None
            self._latency = None
        else:
            # last line from console output
            line = stdout.splitlines()[-1]

            self._result = line
            logger.info('TrafficGen result: {0}'.format(self._result))

            self._received = self._result.split(', ')[1].split('=')[1]
            self._sent = self._result.split(', ')[2].split('=')[1]
            self._loss = self._result.split(', ')[3].split('=')[1]
            self._latency = []
            self._latency.append(self._result.split(', ')[4].split('=')[1])
            self._latency.append(self._result.split(', ')[5].split('=')[1])

    def stop_traffic_on_tg(self):
        """Stop all traffic on TG

        :return: Nothing
        """
        if self._node is None:
            raise RuntimeError("TG is not set")
        if self._node['subtype'] == NodeSubTypeTG.TREX:
            self.trex_stl_stop_remote_exec(self._node)

    def send_traffic_on_tg(self, duration, rate, framesize,
                           traffic_type, warmup_time=5, async_call=False,
                           latency=True):
        """Send traffic from all configured interfaces on TG.

        :param duration: Duration of test traffic generation in seconds.
        :param rate: Offered load per interface (e.g. 1%, 3gbps, 4mpps, ...).
        :param framesize: Frame size (L2) in Bytes.
        :param traffic_type: Traffic profile.
        :param latency: With latency measurement.
        :type duration: str
        :type rate: str
        :type framesize: str
        :type traffic_type: str
        :type latency: bool
        :return: TG output.
        :rtype: str
        """

        node = self._node
        if node is None:
            raise RuntimeError("TG is not set")

        if node['type'] != NodeType.TG:
            raise Exception('Node type is not a TG')

        if node['subtype'] is None:
            raise Exception('TG subtype not defined')
        elif node['subtype'] == NodeSubTypeTG.TREX:
            self.trex_stl_start_remote_exec(duration, rate, framesize,
                                            traffic_type, async_call, latency,
                                            warmup_time=warmup_time)
        else:
            raise NotImplementedError("TG subtype not supported")

        return self._result

    def no_traffic_loss_occurred(self):
        """Fail if loss occurred in traffic run.

        :return: nothing
        """
        if self._loss is None:
            raise Exception('The traffic generation has not been issued')
        if self._loss != '0':
            raise Exception('Traffic loss occurred: {0}'.format(self._loss))

    def partial_traffic_loss_accepted(self, loss_acceptance,
                                      loss_acceptance_type):
        """Fail if loss is higher then accepted in traffic run.

        :return: nothing
        """
        if self._loss is None:
            raise Exception('The traffic generation has not been issued')

        if loss_acceptance_type == 'percentage':
            loss = (float(self._loss) / float(self._sent)) * 100
        elif loss_acceptance_type == 'frames':
            loss = float(self._loss)
        else:
            raise Exception('Loss acceptance type not supported')

        if loss > float(loss_acceptance):
            raise Exception("Traffic loss {} above loss acceptance: {}".format(
                loss, loss_acceptance))
