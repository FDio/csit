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
        """Runs the traffic and evaluate the measured results.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_type: Traffic profile ([2,3]-node-L[2,3], ...).
        :type rate: int
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_type: str
        :returns: Drop threshold exceeded? (True/False)
        :rtype: bool
        :raises: NotImplementedError if TG is not supported.
        :raises: RuntimeError if TG is not specified.
        """
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            'resources.libraries.python.TrafficGenerator')

        if tg_instance.node['subtype'] is None:
            raise RuntimeError('TG subtype not defined')
        elif tg_instance.node['subtype'] == NodeSubTypeTG.TREX:
            unit_rate = str(rate) + self.get_rate_type_str()
            tg_instance.trex_stl_start_remote_exec(self.get_duration(),
                                                   unit_rate, frame_size,
                                                   traffic_type)
            loss = tg_instance.get_loss()
            sent = tg_instance.get_sent()
            if self.loss_acceptance_type_is_percentage():
                loss = (float(loss) / float(sent)) * 100

            logger.trace("comparing: {} < {} {}".format(loss,
                                                        loss_acceptance,
                                                        loss_acceptance_type))
            if float(loss) > float(loss_acceptance):
                return False
            else:
                return True
        else:
            raise NotImplementedError("TG subtype not supported")

    def get_latency(self):
        """Returns min/avg/max latency.

        :returns: Latency stats.
        :rtype: list
        """
        tg_instance = BuiltIn().get_library_instance(
            'resources.libraries.python.TrafficGenerator')
        return tg_instance.get_latency_int()


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
        self._ifaces_reordered = False

    @property
    def node(self):
        """Getter.

        :returns: Traffic generator node.
        :rtype: dict
        """
        return self._node

    def get_loss(self):
        """Return number of lost packets.

        :returns: Number of lost packets.
        :rtype: str
        """
        return self._loss

    def get_sent(self):
        """Return number of sent packets.

        :returns: Number of sent packets.
        :rtype: str
        """
        return self._sent

    def get_received(self):
        """Return number of received packets.

        :returns: Number of received packets.
        :rtype: str
        """
        return self._received

    def get_latency_int(self):
        """Return rounded min/avg/max latency.

        :returns: Latency stats.
        :rtype: list
        """
        return self._latency

    def initialize_traffic_generator(self, tg_node, tg_if1, tg_if2,
                                     tg_if1_adj_node, tg_if1_adj_if,
                                     tg_if2_adj_node, tg_if2_adj_if,
                                     test_type,
                                     tg_if1_dst_mac=None, tg_if2_dst_mac=None):
        """TG initialization.

        :param tg_node: Traffic generator node.
        :param tg_if1: TG - name of first interface.
        :param tg_if2: TG - name of second interface.
        :param tg_if1_adj_node: TG if1 adjecent node.
        :param tg_if1_adj_if: TG if1 adjecent interface.
        :param tg_if2_adj_node: TG if2 adjecent node.
        :param tg_if2_adj_if: TG if2 adjecent interface.
        :param test_type: 'L2' or 'L3' - src/dst MAC address.
        :param tg_if1_dst_mac: Interface 1 destination MAC address.
        :param tg_if2_dst_mac: Interface 2 destination MAC address.
        :type tg_node: dict
        :type tg_if1: str
        :type tg_if2: str
        :type tg_if1_adj_node: dict
        :type tg_if1_adj_if: str
        :type tg_if2_adj_node: dict
        :type tg_if2_adj_if: str
        :type test_type: str
        :type tg_if1_dst_mac: str
        :type tg_if2_dst_mac: str
        :returns: nothing
        :raises: RuntimeError in case of issue during initialization.
        """

        topo = Topology()

        if tg_node['type'] != NodeType.TG:
            raise RuntimeError('Node type is not a TG')
        self._node = tg_node

        if tg_node['subtype'] == NodeSubTypeTG.TREX:
            trex_path = "/opt/trex-core-2.34"

            ssh = SSH()
            ssh.connect(tg_node)

            (ret, _, _) = ssh.exec_command(
                "sudo -E sh -c '{}/resources/tools/trex/"
                "trex_installer.sh'".format(Constants.REMOTE_FW_DIR),
                timeout=1800)
            if int(ret) != 0:
                raise RuntimeError('TRex installation failed.')

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
                raise ValueError("test_type unknown")

            if tg_if1_dst_mac is not None and tg_if2_dst_mac is not None:
                if1_adj_mac = tg_if1_dst_mac
                if2_adj_mac = tg_if2_dst_mac

            if min(if1_pci, if2_pci) != if1_pci:
                if1_mac, if2_mac = if2_mac, if1_mac
                if1_pci, if2_pci = if2_pci, if1_pci
                if1_adj_mac, if2_adj_mac = if2_adj_mac, if1_adj_mac
                self._ifaces_reordered = True

            if1_mac_hex = "0x"+if1_mac.replace(":", ",0x")
            if2_mac_hex = "0x"+if2_mac.replace(":", ",0x")
            if1_adj_mac_hex = "0x"+if1_adj_mac.replace(":", ",0x")
            if2_adj_mac_hex = "0x"+if2_adj_mac.replace(":", ",0x")

            (ret, _, _) = ssh.exec_command(
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
                raise RuntimeError('trex config generation error')

            max_startup_retries = 3
            while max_startup_retries > 0:
                # kill T-rex only if it is already running
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'pgrep t-rex && sudo pkill t-rex && sleep 3'")

                # configure T-rex
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'cd {0}/scripts/ && sudo ./trex-cfg'"\
                    .format(trex_path))
                if int(ret) != 0:
                    raise RuntimeError('trex-cfg failed')

                # start T-rex
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'cd {0}/scripts/ && "
                    "sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /tmp/trex.log "
                    "2>&1 &' > /dev/null"\
                    .format(trex_path))
                if int(ret) != 0:
                    ssh.exec_command("sh -c 'cat /tmp/trex.log'")
                    raise RuntimeError('t-rex-64 startup failed')

                # get T-rex server info
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'sleep 3; "
                    "{0}/resources/tools/trex/trex_server_info.py'"\
                    .format(Constants.REMOTE_FW_DIR),
                    timeout=120)
                if int(ret) == 0:
                    # If we get info T-rex is running
                    return
                # try again
                max_startup_retries -= 1
            # after max retries T-rex is still not responding to API
            # critical error occurred
            raise RuntimeError('t-rex-64 startup failed')

    @staticmethod
    def teardown_traffic_generator(node):
        """TG teardown.

        :param node: Traffic generator node.
        :type node: dict
        :returns: nothing
        :raises: RuntimeError if T-rex teardown failed.
        :raises: RuntimeError if node type is not a TG.
        """
        if node['type'] != NodeType.TG:
            raise RuntimeError('Node type is not a TG')
        if node['subtype'] == NodeSubTypeTG.TREX:
            ssh = SSH()
            ssh.connect(node)
            (ret, _, _) = ssh.exec_command(
                "sh -c 'sudo pkill t-rex && sleep 3'")
            if int(ret) != 0:
                raise RuntimeError('pkill t-rex failed')

    @staticmethod
    def trex_stl_stop_remote_exec(node):
        """Execute script on remote node over ssh to stop running traffic.

        :param node: T-REX generator node.
        :type node: dict
        :returns: Nothing
        :raises: RuntimeError if stop traffic script fails.
        """
        ssh = SSH()
        ssh.connect(node)

        (ret, _, _) = ssh.exec_command(
            "sh -c '{}/resources/tools/trex/"
            "trex_stateless_stop.py'".format(Constants.REMOTE_FW_DIR))

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
        :type framesize: str
        :type traffic_type: str
        :type async_call: bool
        :type latency: bool
        :type warmup_time: int
        :returns: Nothing
        :raises: RuntimeError in case of TG driver issue.
        """
        ssh = SSH()
        ssh.connect(self._node)

        _async = "--async" if async_call else ""
        _latency = "--latency" if latency else ""
        _p0, _p1 = (2, 1) if self._ifaces_reordered else (1, 2)

        profile_path = ("{0}/resources/traffic_profiles/trex/"
                        "{1}.py".format(Constants.REMOTE_FW_DIR,
                                        traffic_type))
        (ret, stdout, _) = ssh.exec_command(
            "sh -c "
            "'{0}/resources/tools/trex/trex_stateless_profile.py "
            "--profile {1} "
            "--duration {2} "
            "--frame_size {3} "
            "--rate {4} "
            "--warmup_time {5} "
            "--port_0 {6} "
            "--port_1 {7} "
            "{8} "   # --async
            "{9}'".  # --latency
            format(Constants.REMOTE_FW_DIR, profile_path, duration, framesize,
                   rate, warmup_time, _p0 - 1, _p1 - 1, _async, _latency),
            timeout=int(duration) + 60)

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
        """Stop all traffic on TG.

        :returns: Nothing
        :raises: RuntimeError if TG is not set.
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
        :param warmup_time: Warmup phase in seconds.
        :param async_call: Async mode.
        :param latency: With latency measurement.
        :type duration: str
        :type rate: str
        :type framesize: str
        :type traffic_type: str
        :type warmup_time: int
        :type async_call: bool
        :type latency: bool
        :returns: TG output.
        :rtype: str
        :raises: RuntimeError if TG is not set.
        :raises: RuntimeError if node is not TG or subtype is not specified.
        :raises: NotImplementedError if TG is not supported.
        """

        node = self._node
        if node is None:
            raise RuntimeError("TG is not set")

        if node['type'] != NodeType.TG:
            raise RuntimeError('Node type is not a TG')

        if node['subtype'] is None:
            raise RuntimeError('TG subtype not defined')
        elif node['subtype'] == NodeSubTypeTG.TREX:
            self.trex_stl_start_remote_exec(int(duration), rate, framesize,
                                            traffic_type, async_call, latency,
                                            warmup_time=warmup_time)
        else:
            raise NotImplementedError("TG subtype not supported")

        return self._result

    def no_traffic_loss_occurred(self):
        """Fail if loss occurred in traffic run.

        :returns: nothing
        :raises: Exception if loss occured.
        """
        if self._loss is None:
            raise Exception('The traffic generation has not been issued')
        if self._loss != '0':
            raise Exception('Traffic loss occurred: {0}'.format(self._loss))

    def partial_traffic_loss_accepted(self, loss_acceptance,
                                      loss_acceptance_type):
        """Fail if loss is higher then accepted in traffic run.

        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :returns: nothing
        :raises: Exception if loss is above acceptance criteria.
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
