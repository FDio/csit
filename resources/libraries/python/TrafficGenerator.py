# Copyright (c) 2018 Cisco and/or its affiliates.
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

from .DropRateSearch import DropRateSearch
from .constants import Constants
from .ssh import SSH
from .topology import NodeType
from .topology import NodeSubTypeTG
from .topology import Topology
from .MLRsearch.AbstractMeasurer import AbstractMeasurer
from .MLRsearch.MultipleLossRatioSearch import MultipleLossRatioSearch
from .MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement

__all__ = ['TGDropRateSearchImpl', 'TrafficGenerator', 'OptimizedSearch']


class TGDropRateSearchImpl(DropRateSearch):
    """Drop Rate Search implementation."""

    def __init__(self):
        super(TGDropRateSearchImpl, self).__init__()

    def measure_loss(self, rate, frame_size, loss_acceptance,
                     loss_acceptance_type, traffic_type, skip_warmup=False):
        """Runs the traffic and evaluate the measured results.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_type: Module name as a traffic type identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param skip_warmup: Start TRex without warmup traffic if true.
        :type rate: float
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_type: str
        :type skip_warmup: bool
        :returns: Drop threshold exceeded? (True/False)
        :rtype: bool
        :raises NotImplementedError: If TG is not supported.
        :raises RuntimeError: If TG is not specified.
        """
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            'resources.libraries.python.TrafficGenerator')

        if tg_instance.node['subtype'] is None:
            raise RuntimeError('TG subtype not defined')
        elif tg_instance.node['subtype'] == NodeSubTypeTG.TREX:
            unit_rate = str(rate) + self.get_rate_type_str()
            if skip_warmup:
                tg_instance.trex_stl_start_remote_exec(self.get_duration(),
                                                       unit_rate, frame_size,
                                                       traffic_type,
                                                       warmup_time=0.0)
            else:
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


class TrafficGenerator(AbstractMeasurer):
    """Traffic Generator.

    FIXME: Describe API."""

    # TODO: Decrease friction between various search and rate provider APIs.
    # FIXME: Remove "trex" from lines which could work with other TGs.

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
        # Parameters not given by measure().
        self.frame_size = None
        self.traffic_type = None
        self.warmup_time = None

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
        :param test_type: 'L2', 'L3' or 'L7' - OSI Layer testing type.
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
        :raises RuntimeError: In case of issue during initialization.
        """
        if tg_node['type'] != NodeType.TG:
            raise RuntimeError('Node type is not a TG')
        self._node = tg_node

        if tg_node['subtype'] == NodeSubTypeTG.TREX:
            ssh = SSH()
            ssh.connect(tg_node)

            (ret, _, _) = ssh.exec_command(
                "sudo -E sh -c '{0}/resources/tools/trex/"
                "trex_installer.sh {1}'".format(Constants.REMOTE_FW_DIR,
                                                Constants.TREX_INSTALL_VERSION),
                timeout=1800)
            if int(ret) != 0:
                raise RuntimeError('TRex installation failed.')

            if1_pci = Topology().get_interface_pci_addr(tg_node, tg_if1)
            if2_pci = Topology().get_interface_pci_addr(tg_node, tg_if2)
            if1_addr = Topology().get_interface_mac(tg_node, tg_if1)
            if2_addr = Topology().get_interface_mac(tg_node, tg_if2)

            if test_type == 'L2':
                if1_adj_addr = if2_addr
                if2_adj_addr = if1_addr
            elif test_type == 'L3':
                if1_adj_addr = Topology().get_interface_mac(tg_if1_adj_node,
                                                            tg_if1_adj_if)
                if2_adj_addr = Topology().get_interface_mac(tg_if2_adj_node,
                                                            tg_if2_adj_if)
            elif test_type == 'L7':
                if1_addr = Topology().get_interface_ip4(tg_node, tg_if1)
                if2_addr = Topology().get_interface_ip4(tg_node, tg_if2)
                if1_adj_addr = Topology().get_interface_ip4(tg_if1_adj_node,
                                                            tg_if1_adj_if)
                if2_adj_addr = Topology().get_interface_ip4(tg_if2_adj_node,
                                                            tg_if2_adj_if)
            else:
                raise ValueError("Unknown Test Type")

            # in case of switched environment we can override MAC addresses
            if tg_if1_dst_mac is not None and tg_if2_dst_mac is not None:
                if1_adj_addr = tg_if1_dst_mac
                if2_adj_addr = tg_if2_dst_mac

            if min(if1_pci, if2_pci) != if1_pci:
                if1_pci, if2_pci = if2_pci, if1_pci
                if1_addr, if2_addr = if2_addr, if1_addr
                if1_adj_addr, if2_adj_addr = if2_adj_addr, if1_adj_addr
                self._ifaces_reordered = True

            if test_type == 'L2' or test_type == 'L3':
                (ret, _, _) = ssh.exec_command(
                    "sudo sh -c 'cat << EOF > /etc/trex_cfg.yaml\n"
                    "- port_limit: 2\n"
                    "  version: 2\n"
                    "  interfaces: [\"{0}\",\"{1}\"]\n"
                    "  port_info:\n"
                    "      - dest_mac: [{2}]\n"
                    "        src_mac: [{3}]\n"
                    "      - dest_mac: [{4}]\n"
                    "        src_mac: [{5}]\n"
                    "EOF'"\
                    .format(if1_pci, if2_pci,
                            "0x"+if1_adj_addr.replace(":", ",0x"),
                            "0x"+if1_addr.replace(":", ",0x"),
                            "0x"+if2_adj_addr.replace(":", ",0x"),
                            "0x"+if2_addr.replace(":", ",0x")))
            elif test_type == 'L7':
                (ret, _, _) = ssh.exec_command(
                    "sudo sh -c 'cat << EOF > /etc/trex_cfg.yaml\n"
                    "- port_limit: 2\n"
                    "  version: 2\n"
                    "  interfaces: [\"{0}\",\"{1}\"]\n"
                    "  port_info:\n"
                    "      - ip: [{2}]\n"
                    "        default_gw: [{3}]\n"
                    "      - ip: [{4}]\n"
                    "        default_gw: [{5}]\n"
                    "EOF'"\
                    .format(if1_pci, if2_pci,
                            if1_addr, if1_adj_addr,
                            if2_addr, if2_adj_addr))
            else:
                raise ValueError("Unknown Test Type")
            if int(ret) != 0:
                raise RuntimeError('TRex config generation error')

            for _ in range(0, 3):
                # kill TRex only if it is already running
                ssh.exec_command(
                    "sh -c 'pgrep t-rex && sudo pkill t-rex && sleep 3'")

                # configure TRex
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'cd {0}/scripts/ && sudo ./trex-cfg'"\
                    .format(Constants.TREX_INSTALL_DIR))
                if int(ret) != 0:
                    raise RuntimeError('trex-cfg failed')

                # start TRex
                if test_type == 'L2' or test_type == 'L3':
                    (ret, _, _) = ssh.exec_command(
                        "sh -c 'cd {0}/scripts/ && "
                        "sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /tmp/trex.log "
                        "2>&1 &' > /dev/null"\
                        .format(Constants.TREX_INSTALL_DIR))
                elif test_type == 'L7':
                    (ret, _, _) = ssh.exec_command(
                        "sh -c 'cd {0}/scripts/ && "
                        "sudo nohup ./t-rex-64 --astf -i -c 7 --iom 0 > "
                        "/tmp/trex.log 2>&1 &' > /dev/null"\
                        .format(Constants.TREX_INSTALL_DIR))
                else:
                    raise ValueError("Unknown Test Type")
                if int(ret) != 0:
                    ssh.exec_command("sh -c 'cat /tmp/trex.log'")
                    raise RuntimeError('t-rex-64 startup failed')

                # get TRex server info
                (ret, _, _) = ssh.exec_command(
                    "sh -c 'sleep 3; "
                    "{0}/resources/tools/trex/trex_server_info.py'"\
                    .format(Constants.REMOTE_FW_DIR),
                    timeout=120)
                if int(ret) == 0:
                    # If we get info TRex is running
                    return
            # after max retries TRex is still not responding to API
            # critical error occurred
            raise RuntimeError('t-rex-64 startup failed')

    @staticmethod
    def is_trex_running(node):
        """Check if TRex is running using pidof.

        :param node: Traffic generator node.
        :type node: dict
        :returns: True if TRex is running otherwise False.
        :rtype: bool
        :raises RuntimeError: If node type is not a TG.
        """
        if node['type'] != NodeType.TG:
            raise RuntimeError('Node type is not a TG')

        ssh = SSH()
        ssh.connect(node)
        ret, _, _ = ssh.exec_command_sudo("pidof t-rex")
        return bool(int(ret) == 0)

    @staticmethod
    def teardown_traffic_generator(node):
        """TG teardown.

        :param node: Traffic generator node.
        :type node: dict
        :returns: nothing
        :raises RuntimeError: If node type is not a TG,
            or if TRex teardown fails.
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

        :param node: TRex generator node.
        :type node: dict
        :returns: Nothing
        :raises RuntimeError: If stop traffic script fails.
        """
        ssh = SSH()
        ssh.connect(node)

        (ret, _, _) = ssh.exec_command(
            "sh -c '{}/resources/tools/trex/"
            "trex_stateless_stop.py'".format(Constants.REMOTE_FW_DIR))

        if int(ret) != 0:
            raise RuntimeError('TRex stateless runtime error')

    def trex_stl_start_remote_exec(self, duration, rate, framesize,
                                   traffic_type, async_call=False,
                                   latency=True, warmup_time=5.0):
        """Execute script on remote node over ssh to start traffic.

        :param duration: Time expresed in seconds for how long to send traffic.
        :param rate: Traffic rate expressed with units (pps, %)
        :param framesize: L2 frame size to send (without padding and IPG).
        :param traffic_type: Module name as a traffic type identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param async_call: If enabled then don't wait for all incomming trafic.
        :param latency: With latency measurement.
        :param warmup_time: Warmup time period.
        :type duration: float
        :type rate: str
        :type framesize: str
        :type traffic_type: str
        :type async_call: bool
        :type latency: bool
        :type warmup_time: float
        :returns: Nothing
        :raises RuntimeError: In case of TG driver issue.
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
            timeout=float(duration) + 60)

        if int(ret) != 0:
            raise RuntimeError('TRex stateless runtime error')
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
        :raises RuntimeError: If TG is not set.
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
        :param traffic_type: Module name as a traffic type identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param warmup_time: Warmup phase in seconds.
        :param async_call: Async mode.
        :param latency: With latency measurement.
        :type duration: str
        :type rate: str
        :type framesize: str
        :type traffic_type: str
        :type warmup_time: float
        :type async_call: bool
        :type latency: bool
        :returns: TG output.
        :rtype: str
        :raises RuntimeError: If TG is not set, or if node is not TG,
            or if subtype is not specified.
        :raises NotImplementedError: If TG is not supported.
        """

        node = self._node
        if node is None:
            raise RuntimeError("TG is not set")

        if node['type'] != NodeType.TG:
            raise RuntimeError('Node type is not a TG')

        if node['subtype'] is None:
            raise RuntimeError('TG subtype not defined')
        elif node['subtype'] == NodeSubTypeTG.TREX:
            self.trex_stl_start_remote_exec(duration, rate, framesize,
                                            traffic_type, async_call, latency,
                                            warmup_time=warmup_time)
        else:
            raise NotImplementedError("TG subtype not supported")

        return self._result

    def no_traffic_loss_occurred(self):
        """Fail if loss occurred in traffic run.

        :returns: nothing
        :raises Exception: If loss occured.
        """
        if self._loss is None:
            raise RuntimeError('The traffic generation has not been issued')
        if self._loss != '0':
            raise RuntimeError('Traffic loss occurred: {0}'.format(self._loss))

    def fail_if_no_traffic_forwarded(self):
        """Fail if no traffic forwarded.

        :returns: nothing
        :raises Exception: If no traffic forwarded.
        """
        if self._received is None:
            raise RuntimeError('The traffic generation has not been issued')
        if self._received == '0':
            raise RuntimeError('No traffic forwarded')

    def partial_traffic_loss_accepted(self, loss_acceptance,
                                      loss_acceptance_type):
        """Fail if loss is higher then accepted in traffic run.

        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :returns: nothing
        :raises Exception: If loss is above acceptance criteria.
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

    def set_rate_provider_defaults(self, frame_size, traffic_type,
                                   warmup_time=0.0):
        """Store values accessed by measure().

        :param frame_size: Frame size identifier or value [B].
        :param traffic_type: Module name as a traffic type identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param warmup_time: Traffic duration before measurement starts [s].
        :type frame_size: str or int
        :type traffic_type: str
        :type warmup_time: float
        """
        self.frame_size = frame_size
        self.traffic_type = str(traffic_type)
        self.warmup_time = float(warmup_time)

    def measure(self, duration, transmit_rate):
        """Run bi-directional measurement, parse and return results.

        :param duration: Trial duration [s].
        :param transmit_rate: Target bidirectional transmit rate [pps].
        :type duration: float
        :type transmit_rate: float
        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        :raises RuntimeError: If TG is not set, or if node is not TG,
            or if subtype is not specified.
        :raises NotImplementedError: If TG is not supported.
        """
        duration = float(duration)
        transmit_rate = float(transmit_rate)
        # Trex needs target Tr per stream, but reports aggregate Tx and Dx.
        unit_rate = str(transmit_rate / 2.0) + "pps"
        self.send_traffic_on_tg(
            duration, unit_rate, self.frame_size, self.traffic_type,
            self.warmup_time, latency=True)
        transmit_count = int(self.get_sent())
        loss_count = int(self.get_loss())
        measurement = ReceiveRateMeasurement(
            duration, transmit_rate, transmit_count, loss_count)
        measurement.latency = self.get_latency_int()
        return measurement


class OptimizedSearch(object):
    """Class to be imported as Robot Library, containing a single keyword."""

    @staticmethod
    def perform_optimized_ndrpdr_search(
            frame_size, traffic_type, minimum_transmit_rate,
            maximum_transmit_rate, packet_loss_ratio=0.005,
            final_relative_width=0.005, final_trial_duration=30.0,
            initial_trial_duration=1.0, number_of_intermediate_phases=2,
            timeout=720.0, doublings=1):
        """Setup initialized TG, perform optimized search, return intervals.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_type: Module name as a traffic type identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param minimum_transmit_rate: Minimal bidirectional
            target transmit rate [pps].
        :param maximum_transmit_rate: Maximal bidirectional
            target transmit rate [pps].
        :param packet_loss_ratio: Fraction of packets lost, for PDR [1].
        :param final_relative_width: Final lower bound transmit rate
            cannot be more distant that this multiple of upper bound [1].
        :param final_trial_duration: Trial duration for the final phase [s].
        :param initial_trial_duration: Trial duration for the initial phase
            and also for the first intermediate phase [s].
        :param number_of_intermediate_phases: Number of intermediate phases
            to perform before the final phase [1].
        :param timeout: The search will fail itself when not finished
            before this overall time [s].
        :param doublings: How many doublings to do in external search step.
            Default 1 is suitable for fairly stable tests,
            less stable tests might get better overal duration with 2 or more.
        :type frame_size: str or int
        :type traffic_type: str
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type packet_loss_ratio: float
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type doublings: int
        :returns: Structure containing narrowed down NDR and PDR intervals
            and their measurements.
        :rtype: NdrPdrResult
        :raises RuntimeError: If total duration is larger than timeout.
        """
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            'resources.libraries.python.TrafficGenerator')
        tg_instance.set_rate_provider_defaults(frame_size, traffic_type)
        algorithm = MultipleLossRatioSearch(
            measurer=tg_instance, final_trial_duration=final_trial_duration,
            final_relative_width=final_relative_width,
            number_of_intermediate_phases=number_of_intermediate_phases,
            initial_trial_duration=initial_trial_duration, timeout=timeout)
        result = algorithm.narrow_down_ndr_and_pdr(
            minimum_transmit_rate, maximum_transmit_rate, packet_loss_ratio)
        return result
