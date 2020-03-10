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

"""Performance testing traffic generator library."""

import time

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from .Constants import Constants
from .CpuUtils import CpuUtils
from .DropRateSearch import DropRateSearch
from .MLRsearch.AbstractMeasurer import AbstractMeasurer
from .MLRsearch.MultipleLossRatioSearch import MultipleLossRatioSearch
from .MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement
from .PLRsearch.PLRsearch import PLRsearch
from .OptionString import OptionString
from .ssh import exec_cmd_no_error, exec_cmd
from .topology import NodeType
from .topology import NodeSubTypeTG
from .topology import Topology

__all__ = [u"TGDropRateSearchImpl", u"TrafficGenerator", u"OptimizedSearch"]


def check_subtype(node):
    """Return supported subtype of given node, or raise an exception.

    Currently only one subtype is supported,
    but we want our code to be ready for other ones.

    :param node: Topology node to check. Can be None.
    :type node: dict or NoneType
    :returns: Subtype detected.
    :rtype: NodeSubTypeTG
    :raises RuntimeError: If node is not supported, message explains how.
    """
    if node.get(u"type") is None:
        msg = u"Node type is not defined"
    elif node['type'] != NodeType.TG:
        msg = f"Node type is {node[u'type']!r}, not a TG"
    elif node.get(u"subtype") is None:
        msg = u"TG subtype is not defined"
    elif node[u"subtype"] != NodeSubTypeTG.TREX:
        msg = f"TG subtype {node[u'subtype']!r} is not supported"
    else:
        return NodeSubTypeTG.TREX
    raise RuntimeError(msg)


class TGDropRateSearchImpl(DropRateSearch):
    """Drop Rate Search implementation."""

    # def __init__(self):
    #     super(TGDropRateSearchImpl, self).__init__()

    def measure_loss(
            self, rate, frame_size, loss_acceptance, loss_acceptance_type,
            traffic_profile, skip_warmup=False):
        """Runs the traffic and evaluate the measured results.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param skip_warmup: Start TRex without warmup traffic if true.
        :type rate: float
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_profile: str
        :type skip_warmup: bool
        :returns: Drop threshold exceeded? (True/False)
        :rtype: bool
        :raises NotImplementedError: If TG is not supported.
        :raises RuntimeError: If TG is not specified.
        """
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        subtype = check_subtype(tg_instance.node)
        if subtype == NodeSubTypeTG.TREX:
            unit_rate = str(rate) + self.get_rate_type_str()
            if skip_warmup:
                tg_instance.trex_stl_start_remote_exec(
                    self.get_duration(), unit_rate, frame_size, traffic_profile,
                    warmup_time=0.0
                )
            else:
                tg_instance.trex_stl_start_remote_exec(
                    self.get_duration(), unit_rate, frame_size, traffic_profile
                )
            loss = tg_instance.get_loss()
            sent = tg_instance.get_sent()
            if self.loss_acceptance_type_is_percentage():
                loss = (float(loss) / float(sent)) * 100
            logger.trace(
                f"comparing: {loss} < {loss_acceptance} {loss_acceptance_type}"
            )
            return float(loss) <= float(loss_acceptance)
        return False

    def get_latency(self):
        """Returns min/avg/max latency.

        :returns: Latency stats.
        :rtype: list
        """
        tg_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        return tg_instance.get_latency_int()


# TODO: Pylint says too-many-instance-attributes.
# A fix is developed in https://gerrit.fd.io/r/c/csit/+/22221
class TrafficGenerator(AbstractMeasurer):
    """Traffic Generator.

    FIXME: Describe API."""

    # TODO: Decrease friction between various search and rate provider APIs.
    # TODO: Remove "trex" from lines which could work with other TGs.

    # Use one instance of TrafficGenerator for all tests in test suite
    ROBOT_LIBRARY_SCOPE = u"TEST SUITE"

    def __init__(self):
        # TODO: Number of fields will be reduced with CSIT-1378.
        self._node = None
        # T-REX interface order mapping
        self._ifaces_reordered = False
        # Result holding fields, to be removed.
        self._result = None
        self._loss = None
        self._sent = None
        self._latency = None
        self._received = None
        # Measurement input fields, needed for async stop result.
        self._start_time = None
        self._rate = None
        # Other input parameters, not knowable from measure() signature.
        self.frame_size = None
        self.traffic_profile = None
        self.warmup_time = None
        self.traffic_directions = None
        # Transient data needed for async measurements.
        self._xstats = (None, None)
        # TODO: Rename "xstats" to something opaque, so TRex is not privileged?

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

    # TODO: pylint says disable=too-many-locals.
    # A fix is developed in https://gerrit.fd.io/r/c/csit/+/22221
    def initialize_traffic_generator(
            self, tg_node, tg_if1, tg_if2, tg_if1_adj_node, tg_if1_adj_if,
            tg_if2_adj_node, tg_if2_adj_if, osi_layer, tg_if1_dst_mac=None,
            tg_if2_dst_mac=None):
        """TG initialization.

        TODO: Document why do we need (and how do we use) _ifaces_reordered.

        :param tg_node: Traffic generator node.
        :param tg_if1: TG - name of first interface.
        :param tg_if2: TG - name of second interface.
        :param tg_if1_adj_node: TG if1 adjecent node.
        :param tg_if1_adj_if: TG if1 adjecent interface.
        :param tg_if2_adj_node: TG if2 adjecent node.
        :param tg_if2_adj_if: TG if2 adjecent interface.
        :param osi_layer: 'L2', 'L3' or 'L7' - OSI Layer testing type.
        :param tg_if1_dst_mac: Interface 1 destination MAC address.
        :param tg_if2_dst_mac: Interface 2 destination MAC address.
        :type tg_node: dict
        :type tg_if1: str
        :type tg_if2: str
        :type tg_if1_adj_node: dict
        :type tg_if1_adj_if: str
        :type tg_if2_adj_node: dict
        :type tg_if2_adj_if: str
        :type osi_layer: str
        :type tg_if1_dst_mac: str
        :type tg_if2_dst_mac: str
        :returns: nothing
        :raises RuntimeError: In case of issue during initialization.
        """
        subtype = check_subtype(tg_node)
        if subtype == NodeSubTypeTG.TREX:
            self._node = tg_node

            if1_pci = Topology().get_interface_pci_addr(self._node, tg_if1)
            if2_pci = Topology().get_interface_pci_addr(self._node, tg_if2)
            if1_addr = Topology().get_interface_mac(self._node, tg_if1)
            if2_addr = Topology().get_interface_mac(self._node, tg_if2)

            if osi_layer == u"L2":
                if1_adj_addr = if2_addr
                if2_adj_addr = if1_addr
            elif osi_layer == u"L3":
                if1_adj_addr = Topology().get_interface_mac(
                    tg_if1_adj_node, tg_if1_adj_if
                )
                if2_adj_addr = Topology().get_interface_mac(
                    tg_if2_adj_node, tg_if2_adj_if
                )
            elif osi_layer == u"L7":
                if1_addr = Topology().get_interface_ip4(self._node, tg_if1)
                if2_addr = Topology().get_interface_ip4(self._node, tg_if2)
                if1_adj_addr = Topology().get_interface_ip4(
                    tg_if1_adj_node, tg_if1_adj_if
                )
                if2_adj_addr = Topology().get_interface_ip4(
                    tg_if2_adj_node, tg_if2_adj_if
                )
            else:
                raise ValueError(u"Unknown Test Type")

            # in case of switched environment we can override MAC addresses
            if tg_if1_dst_mac is not None and tg_if2_dst_mac is not None:
                if1_adj_addr = tg_if1_dst_mac
                if2_adj_addr = tg_if2_dst_mac

            if min(if1_pci, if2_pci) != if1_pci:
                if1_pci, if2_pci = if2_pci, if1_pci
                if1_addr, if2_addr = if2_addr, if1_addr
                if1_adj_addr, if2_adj_addr = if2_adj_addr, if1_adj_addr
                self._ifaces_reordered = True

            master_thread_id, latency_thread_id, socket, threads = \
                CpuUtils.get_affinity_trex(
                    self._node, tg_if1, tg_if2,
                    tg_dtc=Constants.TREX_CORE_COUNT)

            trex_config = \
                    f"- version: 2\n"\
                    f"  c: {len(threads)}\n"\
                    f"  limit_memory: {Constants.TREX_LIMIT_MEMORY}\n"\
                    f"  interfaces: [\"{if1_pci}\",\"{if2_pci}\"]\n"

            if Constants.CLOUD_ENVIRONMENT == u"azure":
                trex_config += \
                    f"  ext_dpdk_opt: "\
                           f"[\"--vdev=net_vdev_netvsc0,iface=eth1\", "\
                           f"\"--vdev=net_vdev_netvsc1,iface=eth2\"]\n"\
                    f"  interfaces_vdevs : [\"net_failsafe_vsc0\", "\
                           f"\"net_failsafe_vsc1\"]\n"

            if osi_layer in (u"L2", u"L3"):
                dst_mac0 = f"0x{if1_adj_addr.replace(u':', u',0x')}"
                src_mac0 = f"0x{if1_addr.replace(u':', u',0x')}"
                dst_mac1 = f"0x{if2_adj_addr.replace(u':', u',0x')}"
                src_mac1 = f"0x{if2_addr.replace(u':', u',0x')}"
                trex_config += \
                    f"  port_info:\n"\
                    f"      - dest_mac: [{dst_mac0}]\n"\
                    f"        src_mac: [{src_mac0}]\n"\
                    f"      - dest_mac: [{dst_mac1}]\n"\
                    f"        src_mac: [{src_mac1}]\n"

            elif osi_layer == u"L7":
                trex_config += \
                    f"  port_info:\n"\
                    f"      - ip: [{if1_addr}]\n"\
                    f"        default_gw: [{if1_adj_addr}]\n"\
                    f"      - ip: [{if2_addr}]\n"\
                    f"        default_gw: [{if2_adj_addr}]\n"
            else:
                raise ValueError(u"Unknown Test Type!")

            trex_config += \
                f"  platform :\n"\
                f"      master_thread_id: {master_thread_id}\n"\
                f"      latency_thread_id: {latency_thread_id}\n"\
                f"      dual_if:\n"\
                f"          - socket: {socket}\n"\
                f"            threads: {threads}\n"\

            exec_cmd_no_error(self._node,
                f"sh -c 'cat << EOF > /etc/trex_cfg.yaml\n"
                f"{trex_config}"
                f"EOF'", sudo=True,
                message=u"TRex config generation!"
            )
            TrafficGenerator.startup_trex(
                self._node, osi_layer, subtype=subtype
            )

    @staticmethod
    def startup_trex(tg_node, osi_layer, subtype=None):
        """Startup sequence for the TRex traffic generator.

        :param tg_node: Traffic generator node.
        :param osi_layer: 'L2', 'L3' or 'L7' - OSI Layer testing type.
        :param subtype: Traffic generator sub-type.
        :type tg_node: dict
        :type osi_layer: str
        :type subtype: NodeSubTypeTG
        :raises RuntimeError: If node subtype is not a TREX or startup failed.
        """
        if not subtype:
            subtype = check_subtype(tg_node)
        if subtype == NodeSubTypeTG.TREX:
            for _ in range(0, 3):
                # Kill TRex only if it is already running.
                cmd = u"sh -c \"pgrep t-rex && pkill t-rex && sleep 3 || true\""
                exec_cmd_no_error(
                    tg_node, cmd, sudo=True, message=u"Kill TRex failed!"
                )

                # Configure TRex.
                ports = ''
                for port in tg_node[u"interfaces"].values():
                    ports += f" {port.get(u'pci_address')}"

                cmd = f"sh -c \"cd {Constants.TREX_INSTALL_DIR}/scripts/ && " \
                    f"./dpdk_nic_bind.py -u {ports} || true\""
                exec_cmd_no_error(
                    tg_node, cmd, sudo=True,
                    message=u"Unbind PCI ports from driver failed!"
                )

                # Start TRex.
                cd_cmd = f"cd '{Constants.TREX_INSTALL_DIR}/scripts/'"
                trex_cmd = OptionString([u"nohup", u"./t-rex-64"])
                trex_cmd.add(u"-i")
                trex_cmd.add(u"--prefix $(hostname)")
                trex_cmd.add(u"--hdrh")
                trex_cmd.add(u"--no-scapy-server")
                trex_cmd.add_if(u"--astf", osi_layer == u"L7")
                # OptionString does not create double space if extra is empty.
                trex_cmd.add(f"{Constants.TREX_EXTRA_CMDLINE}")
                inner_command = f"{cd_cmd} && {trex_cmd} > /tmp/trex.log 2>&1 &"
                cmd = f"sh -c \"{inner_command}\" > /dev/null"
                try:
                    exec_cmd_no_error(tg_node, cmd, sudo=True)
                except RuntimeError:
                    cmd = u"sh -c \"cat /tmp/trex.log\""
                    exec_cmd_no_error(
                        tg_node, cmd, sudo=True,
                        message=u"Get TRex logs failed!"
                    )
                    raise RuntimeError(u"Start TRex failed!")

                # Test if TRex starts successfully.
                cmd = f"sh -c \"{Constants.REMOTE_FW_DIR}/resources/tools/" \
                    f"trex/trex_server_info.py\""
                try:
                    exec_cmd_no_error(
                        tg_node, cmd, sudo=True,
                        message=u"Test TRex failed!", retries=20
                    )
                except RuntimeError:
                    continue
                return
            # After max retries TRex is still not responding to API critical
            # error occurred.
            exec_cmd(tg_node, u"cat /tmp/trex.log", sudo=True)
            raise RuntimeError(u"Start TRex failed after multiple retries!")

    @staticmethod
    def is_trex_running(node):
        """Check if TRex is running using pidof.

        :param node: Traffic generator node.
        :type node: dict
        :returns: True if TRex is running otherwise False.
        :rtype: bool
        :raises RuntimeError: If node type is not a TG.
        """
        ret, _, _ = exec_cmd(node, u"pgrep t-rex", sudo=True)
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
        subtype = check_subtype(node)
        if subtype == NodeSubTypeTG.TREX:
            exec_cmd_no_error(
                node,
                u"sh -c "
                u"\"if pgrep t-rex; then sudo pkill t-rex && sleep 3; fi\"",
                sudo=False,
                message=u"pkill t-rex failed"
            )

    def _parse_traffic_results(self, stdout):
        """Parse stdout of scripts into fields of self.

        Block of code to reuse, by sync start, or stop after async.
        TODO: Is the output TG subtype dependent?

        :param stdout: Text containing the standard output.
        :type stdout: str
        """
        # last line from console output
        line = stdout.splitlines()[-1]
        self._result = line
        logger.info(f"TrafficGen result: {self._result}")
        self._received = self._result.split(u", ")[1].split(u"=", 1)[1]
        self._sent = self._result.split(u", ")[2].split(u"=", 1)[1]
        self._loss = self._result.split(u", ")[3].split(u"=", 1)[1]
        self._latency = list()
        self._latency.append(self._result.split(u", ")[4].split(u"=", 1)[1])
        self._latency.append(self._result.split(u", ")[5].split(u"=", 1)[1])

    def trex_stl_stop_remote_exec(self, node):
        """Execute script on remote node over ssh to stop running traffic.

        Internal state is updated with measurement results.

        :param node: TRex generator node.
        :type node: dict
        :raises RuntimeError: If stop traffic script fails.
        """
        # No need to check subtype, we know it is TREX.
        x_args = u""
        for index, value in enumerate(self._xstats):
            if value is not None:
                # Nested quoting is fun.
                value = value.replace(u"'", u"\"")
                x_args += f" --xstat{index}='\"'\"'{value}'\"'\"'"
        stdout, _ = exec_cmd_no_error(
            node, f"sh -c '{Constants.REMOTE_FW_DIR}/resources/tools/trex/"
            f"trex_stateless_stop.py{x_args}'",
            message=u"TRex stateless runtime error"
        )
        self._parse_traffic_results(stdout)

    def trex_stl_start_remote_exec(
            self, duration, rate, frame_size, traffic_profile, async_call=False,
            latency=True, warmup_time=5.0, traffic_directions=2, tx_port=0,
            rx_port=1, ip_profile=None):
        """Execute script on remote node over ssh to start traffic.

        In sync mode, measurement results are stored internally.
        In async mode, initial data including xstats are stored internally.

        :param duration: Time expresed in seconds for how long to send traffic.
        :param rate: Traffic rate expressed with units (pps, %)
        :param frame_size: L2 frame size to send (without padding and IPG).
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param async_call: If enabled then don't wait for all incomming trafic.
        :param latency: With latency measurement.
        :param warmup_time: Warmup time period.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param tx_port: Traffic generator transmit port for first flow.
            Default: 0
        :param rx_port: Traffic generator receive port for first flow.
            Default: 1
        :param ip_profile: IP profile for traffic profile.
            Default: none
        :type duration: float
        :type rate: str
        :type frame_size: str
        :type traffic_profile: str
        :type async_call: bool
        :type latency: bool
        :type warmup_time: float
        :type traffic_directions: int
        :type tx_port: int
        :type rx_port: int
        :raises RuntimeError: In case of TG driver issue.
        """
        # No need to check subtype, we know it is TREX.
        reorder = self._ifaces_reordered  # Just to make the next line fit.
        p_0, p_1 = (rx_port, tx_port) if reorder else (tx_port, rx_port)

        if not isinstance(duration, (float, int)):
            duration = float(duration)
        if not isinstance(warmup_time, (float, int)):
            warmup_time = float(warmup_time)
        command = f"sh -c \"" \
            f"{Constants.REMOTE_FW_DIR}/resources/tools/trex/" \
            f"trex_stateless_profile.py " \
            f"--profile {Constants.REMOTE_FW_DIR}/resources/" \
            f"traffic_profiles/trex/{traffic_profile}.py " \
            f"--duration {duration!r} --frame_size {frame_size} " \
            f"--rate {rate!r} --warmup_time {warmup_time!r} " \
            f"--port_0 {p_0} --port_1 {p_1} " \
            f"--traffic_directions {traffic_directions}"
        if ip_profile:
            command += f" --ip_profile {ip_profile}"
        if async_call:
            command += u" --async_start"
        if latency:
            command += u" --latency"
        if Constants.TREX_SEND_FORCE:
            command += u" --force"
        command += u"\""

        stdout, _ = exec_cmd_no_error(
            self._node, command, timeout=float(duration) + 60,
            message=u"TRex stateless runtime error"
        )

        self.traffic_directions = traffic_directions
        if async_call:
            # no result
            self._start_time = time.time()
            self._rate = float(rate[:-3]) if u"pps" in rate else float(rate)
            self._received = None
            self._sent = None
            self._loss = None
            self._latency = None
            xstats = [None, None]
            index = 0
            for line in stdout.splitlines():
                if f"Xstats snapshot {index}: " in line:
                    xstats[index] = line[19:]
                    index += 1
                if index == 2:
                    break
            self._xstats = tuple(xstats)
        else:
            self._parse_traffic_results(stdout)
            self._start_time = None
            self._rate = None

    def stop_traffic_on_tg(self):
        """Stop all traffic on TG.

        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        :raises RuntimeError: If TG is not set.
        """
        subtype = check_subtype(self._node)
        if subtype == NodeSubTypeTG.TREX:
            self.trex_stl_stop_remote_exec(self._node)
        return self.get_measurement_result()

    def send_traffic_on_tg(
            self, duration, rate, frame_size, traffic_profile, warmup_time=5,
            async_call=False, latency=True, traffic_directions=2, tx_port=0,
            rx_port=1, ip_profile=None):
        """Send traffic from all configured interfaces on TG.

        In async mode, xstats is stored internally,
        to enable getting correct result when stopping the traffic.
        In both modes, stdout is returned,
        but _parse_traffic_results only works in sync output.

        Note that bidirectional traffic also contains flows
        transmitted from rx_port and received in tx_port.
        But some tests use asymmetric traffic, so those arguments are relevant.

        Also note that traffic generator uses DPDK driver which might
        reorder port numbers based on wiring and PCI numbering.
        This method handles that, so argument values are invariant,
        but you can see swapped valued in debug logs.

        TODO: Is it better to have less descriptive argument names
        just to make them less probable to be viewed as misleading or confusing?
        See https://gerrit.fd.io/r/#/c/17625/11/resources/libraries/python\
        /TrafficGenerator.py@406

        :param duration: Duration of test traffic generation in seconds.
        :param rate: Offered load per interface (e.g. 1%, 3gbps, 4mpps, ...).
        :param frame_size: Frame size (L2) in Bytes.
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param warmup_time: Warmup phase in seconds.
        :param async_call: Async mode.
        :param latency: With latency measurement.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param tx_port: Traffic generator transmit port for first flow.
            Default: 0
        :param rx_port: Traffic generator receive port for first flow.
            Default: 1
        :param ip_profile: IP profile for traffic profile.
            Default: none
        :type duration: str
        :type rate: str
        :type frame_size: str
        :type traffic_profile: str
        :type warmup_time: float
        :type async_call: bool
        :type latency: bool
        :type traffic_directions: int
        :type tx_port: int
        :type rx_port: int
        :type ip_profile: str
        :returns: TG output.
        :rtype: str
        :raises RuntimeError: If TG is not set, or if node is not TG,
            or if subtype is not specified.
        :raises NotImplementedError: If TG is not supported.
        """
        subtype = check_subtype(self._node)
        if subtype == NodeSubTypeTG.TREX:
            self.trex_stl_start_remote_exec(
                duration, rate, frame_size, traffic_profile, async_call,
                latency, warmup_time, traffic_directions, tx_port, rx_port,
                ip_profile
            )

        return self._result

    def no_traffic_loss_occurred(self):
        """Fail if loss occurred in traffic run.

        :returns: nothing
        :raises Exception: If loss occured.
        """
        if self._loss is None:
            raise RuntimeError(u"The traffic generation has not been issued")
        if self._loss != u"0":
            raise RuntimeError(f"Traffic loss occurred: {self._loss}")

    def fail_if_no_traffic_forwarded(self):
        """Fail if no traffic forwarded.

        :returns: nothing
        :raises Exception: If no traffic forwarded.
        """
        if self._received is None:
            raise RuntimeError(u"The traffic generation has not been issued")
        if self._received == u"0":
            raise RuntimeError(u"No traffic forwarded")

    def partial_traffic_loss_accepted(
            self, loss_acceptance, loss_acceptance_type):
        """Fail if loss is higher then accepted in traffic run.

        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :returns: nothing
        :raises Exception: If loss is above acceptance criteria.
        """
        if self._loss is None:
            raise Exception(u"The traffic generation has not been issued")

        if loss_acceptance_type == u"percentage":
            loss = (float(self._loss) / float(self._sent)) * 100
        elif loss_acceptance_type == u"frames":
            loss = float(self._loss)
        else:
            raise Exception(u"Loss acceptance type not supported")

        if loss > float(loss_acceptance):
            raise Exception(
                f"Traffic loss {loss} above loss acceptance: {loss_acceptance}"
            )

    def set_rate_provider_defaults(
            self, frame_size, traffic_profile, warmup_time=0.0,
            traffic_directions=2, ip_profile=None):
        """Store values accessed by measure().

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param warmup_time: Traffic duration before measurement starts [s].
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param ip_profile: IP profile for traffic profile.
        :type frame_size: str or int
        :type traffic_profile: str
        :type warmup_time: float
        :type traffic_directions: int
        :type ip_profile: str
        """
        self.frame_size = frame_size
        self.traffic_profile = str(traffic_profile)
        self.warmup_time = float(warmup_time)
        self.traffic_directions = traffic_directions
        self.ip_profile = ip_profile

    def get_measurement_result(self, duration=None, transmit_rate=None):
        """Return the result of last measurement as ReceiveRateMeasurement.

        Separate function, as measurements can end either by time
        or by explicit call, this is the common block at the end.

        TODO: Fail on running or already reported measurement.

        :param duration: Measurement duration [s] if known beforehand.
            For explicitly stopped measurement it is estimated.
        :param transmit_rate: Target aggregate transmit rate [pps].
            If not given, computed assuming it was bidirectional.
        :type duration: float or NoneType
        :type transmit_rate: float or NoneType
        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        """
        if duration is None:
            duration = time.time() - self._start_time
            self._start_time = None
        if transmit_rate is None:
            transmit_rate = self._rate * self.traffic_directions
        transmit_count = int(self.get_sent())
        loss_count = int(self.get_loss())
        measurement = ReceiveRateMeasurement(
            duration, transmit_rate, transmit_count, loss_count
        )
        measurement.latency = self.get_latency_int()
        return measurement

    def measure(self, duration, transmit_rate):
        """Run trial measurement, parse and return aggregate results.

        Aggregate means sum over traffic directions.

        :param duration: Trial duration [s].
        :param transmit_rate: Target aggregate transmit rate [pps].
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
        # TG needs target Tr per stream, but reports aggregate Tx and Dx.
        unit_rate_int = transmit_rate / float(self.traffic_directions)
        unit_rate_str = str(unit_rate_int) + u"pps"
        self.send_traffic_on_tg(
            duration, unit_rate_str, self.frame_size, self.traffic_profile,
            warmup_time=self.warmup_time, latency=True,
            traffic_directions=self.traffic_directions,
            ip_profile=self.ip_profile
        )
        return self.get_measurement_result(duration, transmit_rate)


class OptimizedSearch:
    """Class to be imported as Robot Library, containing search keywords.

    Aside of setting up measurer and forwarding arguments,
    the main business is to translate min/max rate from unidir to aggregate.
    """

    @staticmethod
    def perform_optimized_ndrpdr_search(
            frame_size, traffic_profile, minimum_transmit_rate,
            maximum_transmit_rate, packet_loss_ratio=0.005,
            final_relative_width=0.005, final_trial_duration=30.0,
            initial_trial_duration=1.0, number_of_intermediate_phases=2,
            timeout=720.0, doublings=1, traffic_directions=2,
            ip_profile=None):
        """Setup initialized TG, perform optimized search, return intervals.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param minimum_transmit_rate: Minimal uni-directional
            target transmit rate [pps].
        :param maximum_transmit_rate: Maximal uni-directional
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
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param ip_profile: IP profile for traffic profile.
        :type frame_size: str or int
        :type traffic_profile: str
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type packet_loss_ratio: float
        :type final_relative_width: float
        :type final_trial_duration: float
        :type initial_trial_duration: float
        :type number_of_intermediate_phases: int
        :type timeout: float
        :type doublings: int
        :type traffic_directions: int
        :type ip_profile: str
        :returns: Structure containing narrowed down NDR and PDR intervals
            and their measurements.
        :rtype: NdrPdrResult
        :raises RuntimeError: If total duration is larger than timeout.
        """
        minimum_transmit_rate *= traffic_directions
        maximum_transmit_rate *= traffic_directions
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        tg_instance.set_rate_provider_defaults(
            frame_size, traffic_profile, traffic_directions=traffic_directions,
            ip_profile=ip_profile)
        algorithm = MultipleLossRatioSearch(
            measurer=tg_instance, final_trial_duration=final_trial_duration,
            final_relative_width=final_relative_width,
            number_of_intermediate_phases=number_of_intermediate_phases,
            initial_trial_duration=initial_trial_duration, timeout=timeout,
            doublings=doublings
        )
        result = algorithm.narrow_down_ndr_and_pdr(
            minimum_transmit_rate, maximum_transmit_rate, packet_loss_ratio
        )
        return result

    @staticmethod
    def perform_soak_search(
            frame_size, traffic_profile, minimum_transmit_rate,
            maximum_transmit_rate, plr_target=1e-7, tdpt=0.1,
            initial_count=50, timeout=1800.0, trace_enabled=False,
            traffic_directions=2):
        """Setup initialized TG, perform soak search, return avg and stdev.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param minimum_transmit_rate: Minimal uni-directional
            target transmit rate [pps].
        :param maximum_transmit_rate: Maximal uni-directional
            target transmit rate [pps].
        :param plr_target: Fraction of packets lost to achieve [1].
        :param tdpt: Trial duration per trial.
            The algorithm linearly increases trial duration with trial number,
            this is the increment between succesive trials, in seconds.
        :param initial_count: Offset to apply before the first trial.
            For example initial_count=50 makes first trial to be 51*tdpt long.
            This is needed because initial "search" phase of integrator
            takes significant time even without any trial results.
        :param timeout: The search will stop after this overall time [s].
        :param trace_enabled: True if trace enabled else False.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :type frame_size: str or int
        :type traffic_profile: str
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type plr_target: float
        :type initial_count: int
        :type timeout: float
        :type trace_enabled: bool
        :type traffic_directions: int
        :returns: Average and stdev of estimated aggregate rate giving PLR.
        :rtype: 2-tuple of float
        """
        minimum_transmit_rate *= traffic_directions
        maximum_transmit_rate *= traffic_directions
        tg_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        tg_instance.set_rate_provider_defaults(
            frame_size, traffic_profile, traffic_directions=traffic_directions)
        algorithm = PLRsearch(
            measurer=tg_instance, trial_duration_per_trial=tdpt,
            packet_loss_ratio_target=plr_target,
            trial_number_offset=initial_count, timeout=timeout,
            trace_enabled=trace_enabled
        )
        result = algorithm.search(minimum_transmit_rate, maximum_transmit_rate)
        return result
