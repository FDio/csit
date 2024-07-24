# Copyright (c) 2024 Cisco and/or its affiliates.
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

import math
import time

from typing import Callable, List, Optional, Union

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from .Constants import Constants
from .DropRateSearch import DropRateSearch
from .MLRsearch import (
    AbstractMeasurer, Config, GoalResult, MeasurementResult,
    MultipleLossRatioSearch, SearchGoal,
)
from .PLRsearch.PLRsearch import PLRsearch
from .OptionString import OptionString
from .ssh import exec_cmd_no_error, exec_cmd
from .topology import NodeType
from .topology import NodeSubTypeTG
from .topology import Topology
from .TRexConfigGenerator import TrexConfig
from .DUTSetup import DUTSetup as DS

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
    elif node[u"type"] != NodeType.TG:
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
            traffic_profile):
        """Runs the traffic and evaluate the measured results.

        :param rate: Offered traffic load.
        :param frame_size: Size of frame.
        :param loss_acceptance: Permitted drop ratio or frames count.
        :param loss_acceptance_type: Type of permitted loss.
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :type rate: float
        :type frame_size: str
        :type loss_acceptance: float
        :type loss_acceptance_type: LossAcceptanceType
        :type traffic_profile: str
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


class TrexMode:
    """Defines mode of T-Rex traffic generator."""
    # Advanced stateful mode
    ASTF = u"ASTF"
    # Stateless mode
    STL = u"STL"


class TrafficGenerator(AbstractMeasurer):
    """Traffic Generator."""

    # Use one instance of TrafficGenerator for all tests in test suite
    ROBOT_LIBRARY_SCOPE = u"TEST SUITE"

    def __init__(self):
        self._node = None
        self._mode = None
        # TG interface order mapping
        self._ifaces_reordered = False
        self._ifaces = []
        # Result holding fields, to be removed.
        self._result = None
        self._loss = None
        self._sent = None
        self._latency = None
        self._received = None
        self._approximated_rate = None
        self._approximated_duration = None
        self._l7_data = None
        # Measurement input fields, needed for async stop result.
        self._start_time = None
        self._stop_time = None
        self._rate = None
        self._target_duration = None
        self._duration = None
        # Other input parameters, not knowable from measure() signature.
        self.frame_size = None
        self.traffic_profile = None
        self.traffic_directions = None
        self.negative_loss = None
        self.use_latency = None
        self.ppta = None
        self.resetter = None
        self.transaction_scale = None
        self.transaction_duration = None
        self.sleep_till_duration = None
        self.transaction_type = None
        self.duration_limit = None
        self.ramp_up_start = None
        self.ramp_up_stop = None
        self.ramp_up_rate = None
        self.ramp_up_duration = None
        self.state_timeout = None
        # Transient data needed for async measurements.
        self._xstats = []

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

    def get_approximated_rate(self):
        """Return approximated rate computed as ratio of transmitted packets
        over duration of trial.

        :returns: Approximated rate.
        :rtype: str
        """
        return self._approximated_rate

    def get_l7_data(self):
        """Return L7 data.

        :returns: Number of received packets.
        :rtype: dict
        """
        return self._l7_data

    def check_mode(self, expected_mode):
        """Check TG mode.

        :param expected_mode: Expected traffic generator mode.
        :type expected_mode: object
        :raises RuntimeError: In case of unexpected TG mode.
        """
        if self._mode == expected_mode:
            return
        raise RuntimeError(
            f"{self._node[u'subtype']} not running in {expected_mode} mode!"
        )

    @staticmethod
    def get_tg_type(tg_node):
        """Log and return the installed traffic generator type.

        :param tg_node: Node from topology file.
        :type tg_node: dict
        :returns: Traffic generator type string.
        :rtype: str
        :raises RuntimeError: If command returns nonzero return code.
        """
        return str(check_subtype(tg_node))

    @staticmethod
    def get_tg_version(tg_node):
        """Log and return the installed traffic generator version.

        :param tg_node: Node from topology file.
        :type tg_node: dict
        :returns: Traffic generator version string.
        :rtype: str
        :raises RuntimeError: If command returns nonzero return code.
        """
        subtype = check_subtype(tg_node)
        if subtype == NodeSubTypeTG.TREX:
            command = f"cat {Constants.TREX_INSTALL_DIR}/VERSION"
            message = u"Get T-Rex version failed!"
            stdout, _ = exec_cmd_no_error(tg_node, command, message=message)
            return stdout.strip()
        return "none"

    def initialize_traffic_generator(self, osi_layer, pfs=2):
        """TG initialization.

        :param osi_layer: 'L2', 'L3' or 'L7' - OSI Layer testing type.
        :param pfs: Number of physical interfaces to configure.
        :type osi_layer: str
        :type pfs: int
        :raises ValueError: If OSI layer is unknown.
        """
        if osi_layer not in ("L2", "L3", "L7"):
            raise ValueError("Unknown OSI layer!")

        topology = BuiltIn().get_variable_value("&{topology_info}")
        self._node = topology["TG"]
        subtype = check_subtype(self._node)

        if subtype == NodeSubTypeTG.TREX:
            trex_topology = list()
            self._mode = TrexMode.ASTF if osi_layer == "L7" else TrexMode.STL

            for link in range(1, pfs, 2):
                tg_if1_adj_addr = topology[f"TG_pf{link+1}_mac"][0]
                tg_if2_adj_addr = topology[f"TG_pf{link}_mac"][0]
                if osi_layer in ("L3", "L7") and "DUT1" in topology.keys():
                    ifl = BuiltIn().get_variable_value("${int}")
                    last = topology["duts_count"]
                    tg_if1_adj_addr = Topology().get_interface_mac(
                        topology["DUT1"],
                        BuiltIn().get_variable_value(
                            f"${{DUT1_{ifl}{link}}}[0]"
                        )
                    )
                    tg_if2_adj_addr = Topology().get_interface_mac(
                        topology[f"DUT{last}"],
                        BuiltIn().get_variable_value(
                            f"${{DUT{last}_{ifl}{link+1}}}[0]"
                        )
                    )

                if1_pci = topology[f"TG_pf{link}_pci"][0]
                if2_pci = topology[f"TG_pf{link+1}_pci"][0]
                if min(if1_pci, if2_pci) != if1_pci:
                    self._ifaces.append(str(link))
                    self._ifaces.append(str(link-1))
                    trex_topology.append(
                        dict(
                            interface=topology[f"TG_pf{link+1}"][0],
                            dst_mac=tg_if2_adj_addr
                        )
                    )
                    trex_topology.append(
                        dict(
                            interface=topology[f"TG_pf{link}"][0],
                            dst_mac=tg_if1_adj_addr
                        )
                    )
                else:
                    self._ifaces.append(str(link-1))
                    self._ifaces.append(str(link))
                    trex_topology.append(
                        dict(
                            interface=topology[f"TG_pf{link}"][0],
                            dst_mac=tg_if1_adj_addr
                        )
                    )
                    trex_topology.append(
                        dict(
                            interface=topology[f"TG_pf{link+1}"][0],
                            dst_mac=tg_if2_adj_addr
                        )
                    )

            TrexConfig.add_startup_configuration(
                self._node, trex_topology
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
        :raises RuntimeError: If T-Rex startup failed.
        :raises ValueError: If OSI layer is not supported.
        """
        if not subtype:
            subtype = check_subtype(tg_node)
        if subtype == NodeSubTypeTG.TREX:
            for _ in range(0, 3):
                # Kill TRex only if it is already running.
                cmd = "sh -c \"pgrep t-rex && pkill t-rex && sleep 3 || true\""
                exec_cmd_no_error(
                    tg_node, cmd, sudo=True, message="Kill TRex failed!"
                )

                # Prepare interfaces for TRex.
                tg_port_drv = Constants.TREX_PORT_DRIVER
                mlx_driver = ""
                for port in tg_node["interfaces"].values():
                    if "Mellanox" in port.get("model"):
                        mlx_driver = port.get("driver")
                        pci_addr = port.get("pci_address")
                        cur_driver = DS.get_pci_dev_driver(tg_node, pci_addr)
                        if cur_driver == mlx_driver:
                            pass
                        elif not cur_driver:
                            DS.pci_driver_bind(tg_node, pci_addr, mlx_driver)
                        else:
                            DS.pci_driver_unbind(tg_node, pci_addr)
                            DS.pci_driver_bind(tg_node, pci_addr, mlx_driver)
                    else:
                        pci_addr = port.get("pci_address")
                        cur_driver = DS.get_pci_dev_driver(tg_node, pci_addr)
                        if cur_driver:
                            DS.pci_driver_unbind(tg_node, pci_addr)
                        DS.pci_driver_bind(tg_node, pci_addr, tg_port_drv)

                # Start TRex.
                cd_cmd = f"cd '{Constants.TREX_INSTALL_DIR}/scripts/'"
                trex_cmd = OptionString(["nohup", "./t-rex-64"])
                trex_cmd.add("-i")
                trex_cmd.add("--prefix $(hostname)")
                trex_cmd.add("--hdrh")
                trex_cmd.add("--no-scapy-server")
                trex_cmd.add_if("--astf", osi_layer == "L7")
                # OptionString does not create double space if extra is empty.
                trex_cmd.add(f"{Constants.TREX_EXTRA_CMDLINE}")
                inner_command = f"{cd_cmd} && {trex_cmd} > /tmp/trex.log 2>&1 &"
                cmd = f"sh -c \"{inner_command}\" > /dev/null"
                try:
                    exec_cmd_no_error(tg_node, cmd, sudo=True)
                except RuntimeError:
                    cmd = "sh -c \"cat /tmp/trex.log\""
                    exec_cmd_no_error(
                        tg_node, cmd, sudo=True,
                        message="Get TRex logs failed!"
                    )
                    raise RuntimeError("Start TRex failed!")

                # Test T-Rex API responsiveness.
                cmd = f"python3 {Constants.REMOTE_FW_DIR}/GPL/tools/trex/"
                if osi_layer in ("L2", "L3"):
                    cmd += "trex_stl_assert.py"
                elif osi_layer == "L7":
                    cmd += "trex_astf_assert.py"
                else:
                    raise ValueError("Unknown OSI layer!")
                try:
                    exec_cmd_no_error(
                        tg_node, cmd, sudo=True,
                        message="T-Rex API is not responding!", retries=20
                    )
                except RuntimeError:
                    continue
                return
            # After max retries TRex is still not responding to API critical
            # error occurred.
            exec_cmd(tg_node, "cat /tmp/trex.log", sudo=True)
            raise RuntimeError("Start T-Rex failed after multiple retries!")

    @staticmethod
    def is_trex_running(node):
        """Check if T-Rex is running using pidof.

        :param node: Traffic generator node.
        :type node: dict
        :returns: True if T-Rex is running otherwise False.
        :rtype: bool
        """
        ret, _, _ = exec_cmd(node, "pgrep t-rex", sudo=True)
        return bool(int(ret) == 0)

    @staticmethod
    def teardown_traffic_generator(node):
        """TG teardown.

        :param node: Traffic generator node.
        :type node: dict
        :returns: nothing
        :raises RuntimeError: If node type is not a TG,
            or if T-Rex teardown fails.
        """
        subtype = check_subtype(node)
        if subtype == NodeSubTypeTG.TREX:
            exec_cmd_no_error(
                node,
                u"sh -c "
                u"\"if pgrep t-rex; then sudo pkill t-rex && sleep 3; fi\"",
                sudo=False,
                message=u"T-Rex kill failed!"
            )

    def trex_astf_stop_remote_exec(self, node):
        """Execute T-Rex ASTF script on remote node over ssh to stop running
        traffic.

        Internal state is updated with measurement results.

        :param node: T-Rex generator node.
        :type node: dict
        :raises RuntimeError: If stop traffic script fails.
        """
        command_line = OptionString().add("python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/GPL/tools/trex"
        command_line.add(f"'{dirname}/trex_astf_stop.py'")
        command_line.add("--xstat")
        for value in self._xstats:
            if value is not None:
                value = value.replace("'", "\"")
                command_line.add(f"'{value}'")
        stdout, _ = exec_cmd_no_error(
            node, command_line,
            message="T-Rex ASTF runtime error!"
        )
        self._parse_traffic_results(stdout)

    def trex_stl_stop_remote_exec(self, node):
        """Execute T-Rex STL script on remote node over ssh to stop running
        traffic.

        Internal state is updated with measurement results.

        :param node: T-Rex generator node.
        :type node: dict
        :raises RuntimeError: If stop traffic script fails.
        """
        command_line = OptionString().add("python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/GPL/tools/trex"
        command_line.add(f"'{dirname}/trex_stl_stop.py'")
        command_line.add("--xstat")
        for value in self._xstats:
            if value is not None:
                value = value.replace("'", "\"")
                command_line.add(f"'{value}'")
        stdout, _ = exec_cmd_no_error(
            node, command_line,
            message="T-Rex STL runtime error!", include_reason=True
        )
        self._parse_traffic_results(stdout)

    def stop_traffic_on_tg(self):
        """Stop all traffic on TG.

        :returns: Structure containing the result of the measurement.
        :rtype: MeasurementResult
        :raises ValueError: If TG traffic profile is not supported.
        """
        subtype = check_subtype(self._node)
        if subtype != NodeSubTypeTG.TREX:
            raise ValueError(f"Unsupported TG subtype: {subtype!r}")
        if u"trex-astf" in self.traffic_profile:
            self.trex_astf_stop_remote_exec(self._node)
        elif u"trex-stl" in self.traffic_profile:
            self.trex_stl_stop_remote_exec(self._node)
        else:
            raise ValueError(u"Unsupported T-Rex traffic profile!")
        self._stop_time = time.monotonic()

        return self._get_measurement_result()

    def _compute_duration(self, duration, multiplier):
        """Compute duration for profile driver.

        The final result is influenced by transaction scale and duration limit.
        It is assumed a higher level function has already set those on self.
        The duration argument is the target value from search point of view,
        before the overrides are applied here.

        Minus one (signalling async traffic start) is kept.

        Completeness flag is also included. Duration limited or async trials
        are not considered complete for ramp-up purposes.

        :param duration: Time expressed in seconds for how long to send traffic.
        :param multiplier: Traffic rate in transactions per second.
        :type duration: float
        :type multiplier: float
        :returns: New duration and whether it was a complete ramp-up candidate.
        :rtype: float, bool
        """
        if duration < 0.0:
            # Keep the async -1.
            return duration, False
        computed_duration = duration
        if self.transaction_scale:
            computed_duration = self.transaction_scale / multiplier
            # Log the computed duration,
            # so we can compare with what telemetry suggests
            # the real duration was.
            logger.debug(f"Expected duration {computed_duration}")
        if not self.duration_limit:
            return computed_duration, True
        limited_duration = min(computed_duration, self.duration_limit)
        return limited_duration, (limited_duration == computed_duration)

    def trex_astf_start_remote_exec(
            self, duration, multiplier, async_call=False):
        """Execute T-Rex ASTF script on remote node over ssh to start running
        traffic.

        In sync mode, measurement results are stored internally.
        In async mode, initial data including xstats are stored internally.

        This method contains the logic to compute duration as maximum time
        if transaction_scale is nonzero.
        The transaction_scale argument defines (limits) how many transactions
        will be started in total. As that amount of transaction can take
        considerable time (sometimes due to explicit delays in the profile),
        the real time a trial needs to finish is computed here. For now,
        in that case the duration argument is ignored, assuming it comes
        from ASTF-unaware search algorithm. The overall time a single
        transaction needs is given in parameter transaction_duration,
        it includes both explicit delays and implicit time it takes
        to transfer data (or whatever the transaction does).

        Currently it is observed TRex does not start the ASTF traffic
        immediately, an ad-hoc constant is added to the computed duration
        to compensate for that.

        If transaction_scale is zero, duration is not recomputed.
        It is assumed the subsequent result parsing gets the real duration
        if the traffic stops sooner for any reason.

        Currently, it is assumed traffic profile defines a single transaction.
        To avoid heavy logic here, the input rate is expected to be in
        transactions per second, as that directly translates to TRex multiplier,
        (assuming the profile does not override the default cps value of one).

        :param duration: Time expressed in seconds for how long to send traffic.
        :param multiplier: Traffic rate in transactions per second.
        :param async_call: If enabled then don't wait for all incoming traffic.
        :type duration: float
        :type multiplier: int
        :type async_call: bool
        :raises RuntimeError: In case of T-Rex driver issue.
        """
        self.check_mode(TrexMode.ASTF)
        p_0, p_1 = (1, 0) if self._ifaces_reordered else (0, 1)
        if not isinstance(duration, (float, int)):
            duration = float(duration)

        computed_duration, _ = self._compute_duration(duration, multiplier)

        command_line = OptionString().add(u"python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/GPL/tools/trex"
        command_line.add(f"'{dirname}/trex_astf_profile.py'")
        command_line.change_prefix(u"--")
        dirname = f"{Constants.REMOTE_FW_DIR}/GPL/traffic_profiles/trex"
        command_line.add_with_value(
            u"profile", f"'{dirname}/{self.traffic_profile}.py'"
        )
        command_line.add_with_value(u"duration", f"{computed_duration!r}")
        command_line.add_with_value(u"frame_size", self.frame_size)
        command_line.add_with_value(
            u"n_data_frames", Constants.ASTF_N_DATA_FRAMES
        )
        command_line.add_with_value(u"multiplier", multiplier)
        command_line.add_with_value(u"port_0", p_0)
        command_line.add_with_value(u"port_1", p_1)
        command_line.add_with_value(
            u"traffic_directions", self.traffic_directions
        )
        command_line.add_if(u"async_start", async_call)
        command_line.add_if(u"latency", self.use_latency)
        command_line.add_if(u"force", Constants.TREX_SEND_FORCE)
        command_line.add_with_value(
            u"delay", Constants.PERF_TRIAL_ASTF_DELAY
        )

        self._start_time = time.monotonic()
        self._rate = multiplier
        stdout, _ = exec_cmd_no_error(
            self._node, command_line, timeout=computed_duration + 10.0,
            message=u"T-Rex ASTF runtime error!"
        )

        if async_call:
            # no result
            self._target_duration = None
            self._duration = None
            self._received = None
            self._sent = None
            self._loss = None
            self._latency = None
            xstats = []
            self._l7_data = dict()
            self._l7_data[u"client"] = dict()
            self._l7_data[u"client"][u"active_flows"] = None
            self._l7_data[u"client"][u"established_flows"] = None
            self._l7_data[u"client"][u"traffic_duration"] = None
            self._l7_data[u"server"] = dict()
            self._l7_data[u"server"][u"active_flows"] = None
            self._l7_data[u"server"][u"established_flows"] = None
            self._l7_data[u"server"][u"traffic_duration"] = None
            if u"udp" in self.traffic_profile:
                self._l7_data[u"client"][u"udp"] = dict()
                self._l7_data[u"client"][u"udp"][u"connects"] = None
                self._l7_data[u"client"][u"udp"][u"closed_flows"] = None
                self._l7_data[u"client"][u"udp"][u"err_cwf"] = None
                self._l7_data[u"server"][u"udp"] = dict()
                self._l7_data[u"server"][u"udp"][u"accepted_flows"] = None
                self._l7_data[u"server"][u"udp"][u"closed_flows"] = None
            elif u"tcp" in self.traffic_profile:
                self._l7_data[u"client"][u"tcp"] = dict()
                self._l7_data[u"client"][u"tcp"][u"initiated_flows"] = None
                self._l7_data[u"client"][u"tcp"][u"connects"] = None
                self._l7_data[u"client"][u"tcp"][u"closed_flows"] = None
                self._l7_data[u"client"][u"tcp"][u"connattempt"] = None
                self._l7_data[u"server"][u"tcp"] = dict()
                self._l7_data[u"server"][u"tcp"][u"accepted_flows"] = None
                self._l7_data[u"server"][u"tcp"][u"connects"] = None
                self._l7_data[u"server"][u"tcp"][u"closed_flows"] = None
            else:
                logger.warn(u"Unsupported T-Rex ASTF traffic profile!")
            index = 0
            for line in stdout.splitlines():
                if f"Xstats snapshot {index}: " in line:
                    xstats.append(line[19:])
                    index += 1
            self._xstats = tuple(xstats)
        else:
            self._target_duration = duration
            self._duration = computed_duration
            self._parse_traffic_results(stdout)

    def trex_stl_start_remote_exec(self, duration, rate, async_call=False):
        """Execute T-Rex STL script on remote node over ssh to start running
        traffic.

        In sync mode, measurement results are stored internally.
        In async mode, initial data including xstats are stored internally.

        Mode-unaware code (e.g. in search algorithms) works with transactions.
        To keep the logic simple, multiplier is set to that value.
        As bidirectional traffic profiles send packets in both directions,
        they are treated as transactions with two packets (one per direction).

        :param duration: Time expressed in seconds for how long to send traffic.
        :param rate: Traffic rate in transactions per second.
        :param async_call: If enabled then don't wait for all incoming traffic.
        :type duration: float
        :type rate: str
        :type async_call: bool
        :raises RuntimeError: In case of T-Rex driver issue.
        """
        self.check_mode(TrexMode.STL)
        if not isinstance(duration, (float, int)):
            duration = float(duration)

        duration, _ = self._compute_duration(duration=duration, multiplier=rate)

        command_line = OptionString().add("python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/GPL/tools/trex"
        command_line.add(f"'{dirname}/trex_stl_profile.py'")
        command_line.change_prefix("--")
        dirname = f"{Constants.REMOTE_FW_DIR}/GPL/traffic_profiles/trex"
        command_line.add_with_value(
            "profile", f"'{dirname}/{self.traffic_profile}.py'"
        )
        command_line.add_with_value("duration", f"{duration!r}")
        command_line.add_with_value("frame_size", self.frame_size)
        command_line.add_with_value("rate", f"{rate!r}")
        command_line.add_with_value("ports", " ".join(self._ifaces))
        command_line.add_with_value(
            "traffic_directions", self.traffic_directions
        )
        command_line.add_if("async_start", async_call)
        command_line.add_if("latency", self.use_latency)
        command_line.add_if("force", Constants.TREX_SEND_FORCE)
        command_line.add_with_value("delay", Constants.PERF_TRIAL_STL_DELAY)

        self._start_time = time.monotonic()
        self._rate = float(rate[:-3]) if "pps" in rate else float(rate)
        stdout, _ = exec_cmd_no_error(
            self._node, command_line, timeout=int(duration) + 60,
            message="T-Rex STL runtime error", include_reason=True
        )

        if async_call:
            # no result
            self._target_duration = None
            self._duration = None
            self._received = None
            self._sent = None
            self._loss = None
            self._latency = None

            xstats = []
            index = 0
            for line in stdout.splitlines():
                if f"Xstats snapshot {index}: " in line:
                    xstats.append(line[19:])
                    index += 1
            self._xstats = tuple(xstats)
        else:
            self._target_duration = duration
            self._duration = duration
            self._parse_traffic_results(stdout)

    def send_traffic_on_tg(
            self,
            duration,
            rate,
            frame_size,
            traffic_profile,
            async_call=False,
            ppta=1,
            traffic_directions=2,
            transaction_duration=0.0,
            transaction_scale=0,
            transaction_type=u"packet",
            duration_limit=0.0,
            use_latency=False,
            ramp_up_rate=None,
            ramp_up_duration=None,
            state_timeout=240.0,
            ramp_up_only=False,
        ):
        """Send traffic from all configured interfaces on TG.

        In async mode, xstats is stored internally,
        to enable getting correct result when stopping the traffic.
        In both modes, stdout is returned,
        but _parse_traffic_results only works in sync output.

        Note that traffic generator uses DPDK driver which might
        reorder port numbers based on wiring and PCI numbering.
        This method handles that, so argument values are invariant,
        but you can see swapped valued in debug logs.

        When transaction_scale is specified, the duration value is ignored
        and the needed time is computed. For cases where this results in
        to too long measurement (e.g. teardown trial with small rate),
        duration_limit is applied (of non-zero), so the trial is stopped sooner.

        Bidirectional STL profiles are treated as transactions with two packets.

        The return value is None for async.

        :param duration: Duration of test traffic generation in seconds.
        :param rate: Traffic rate in transactions per second.
        :param frame_size: Frame size (L2) in Bytes.
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :param async_call: Async mode.
        :param ppta: Packets per transaction, aggregated over directions.
            Needed for udp_pps which does not have a good transaction counter,
            so we need to compute expected number of packets.
            Default: 1.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param transaction_duration: Total expected time to close transaction.
        :param transaction_scale: Number of transactions to perform.
            0 (default) means unlimited.
        :param transaction_type: An identifier specifying which counters
            and formulas to use when computing attempted and failed
            transactions. Default: "packet".
        :param duration_limit: Zero or maximum limit for computed (or given)
            duration.
        :param use_latency: Whether to measure latency during the trial.
            Default: False.
        :param ramp_up_rate: Rate to use in ramp-up trials [pps].
        :param ramp_up_duration: Duration of ramp-up trials [s].
        :param state_timeout: Time of life of DUT state [s].
        :param ramp_up_only: If true, do not perform main trial measurement.
        :type duration: float
        :type rate: float
        :type frame_size: str
        :type traffic_profile: str
        :type async_call: bool
        :type ppta: int
        :type traffic_directions: int
        :type transaction_duration: float
        :type transaction_scale: int
        :type transaction_type: str
        :type duration_limit: float
        :type use_latency: bool
        :type ramp_up_rate: float
        :type ramp_up_duration: float
        :type state_timeout: float
        :type ramp_up_only: bool
        :returns: TG results.
        :rtype: MeasurementResult or None
        :raises ValueError: If TG traffic profile is not supported.
        """
        self.set_rate_provider_defaults(
            frame_size=frame_size,
            traffic_profile=traffic_profile,
            ppta=ppta,
            traffic_directions=traffic_directions,
            transaction_duration=transaction_duration,
            transaction_scale=transaction_scale,
            transaction_type=transaction_type,
            duration_limit=duration_limit,
            use_latency=use_latency,
            ramp_up_rate=ramp_up_rate,
            ramp_up_duration=ramp_up_duration,
            state_timeout=state_timeout,
        )
        return self._send_traffic_on_tg_with_ramp_up(
            duration=duration,
            rate=rate,
            async_call=async_call,
            ramp_up_only=ramp_up_only,
        )

    def _send_traffic_on_tg_internal(
            self, duration, rate, async_call=False):
        """Send traffic from all configured interfaces on TG.

        This is an internal function, it assumes set_rate_provider_defaults
        has been called to remember most values.
        The reason why need to remember various values is that
        the traffic can be asynchronous, and parsing needs those values.
        The reason why this is is a separate function from the one
        which calls set_rate_provider_defaults is that some search algorithms
        need to specify their own values, and we do not want the measure call
        to overwrite them with defaults.

        This function is used both for automated ramp-up trials
        and for explicitly called trials.

        :param duration: Duration of test traffic generation in seconds.
        :param rate: Traffic rate in transactions per second.
        :param async_call: Async mode.
        :type duration: float
        :type rate: float
        :type async_call: bool
        :returns: TG results.
        :rtype: MeasurementResult or None
        :raises ValueError: If TG traffic profile is not supported.
        """
        subtype = check_subtype(self._node)
        if subtype == NodeSubTypeTG.TREX:
            if u"trex-astf" in self.traffic_profile:
                self.trex_astf_start_remote_exec(
                    duration, float(rate), async_call
                )
            elif u"trex-stl" in self.traffic_profile:
                unit_rate_str = str(rate) + u"pps"
                self.trex_stl_start_remote_exec(
                    duration, unit_rate_str, async_call
                )
            else:
                raise ValueError(u"Unsupported T-Rex traffic profile!")

        return None if async_call else self._get_measurement_result()

    def _send_traffic_on_tg_with_ramp_up(
            self, duration, rate, async_call=False, ramp_up_only=False):
        """Send traffic from all interfaces on TG, maybe after ramp-up.

        This is an internal function, it assumes set_rate_provider_defaults
        has been called to remember most values.
        The reason why need to remember various values is that
        the traffic can be asynchronous, and parsing needs those values.
        The reason why this is a separate function from the one
        which calls set_rate_provider_defaults is that some search algorithms
        need to specify their own values, and we do not want the measure call
        to overwrite them with defaults.

        If ramp-up tracking is detected, a computation is performed,
        and if state timeout is near, trial at ramp-up rate and duration
        is inserted before the main trial measurement.

        The ramp_up_only parameter forces a ramp-up without immediate
        trial measurement, which is useful in case self remembers
        a previous ramp-up trial that belongs to a different test (phase).

        Return None if trial is async or ramp-up only.

        :param duration: Duration of test traffic generation in seconds.
        :param rate: Traffic rate in transactions per second.
        :param async_call: Async mode.
        :param ramp_up_only: If true, do not perform main trial measurement.
        :type duration: float
        :type rate: float
        :type async_call: bool
        :type ramp_up_only: bool
        :returns: TG results.
        :rtype: MeasurementResult or None
        :raises ValueError: If TG traffic profile is not supported.
        """
        complete = False
        if self.ramp_up_rate:
            # Figure out whether we need to insert a ramp-up trial.
            if ramp_up_only or self.ramp_up_start is None:
                # We never ramped up yet (at least not in this test case).
                ramp_up_needed = True
            else:
                # We ramped up before, but maybe it was too long ago.
                # Adding a constant overhead to be safe.
                time_now = time.monotonic() + 1.0
                computed_duration, complete = self._compute_duration(
                    duration=duration,
                    multiplier=rate,
                )
                # There are two conditions for inserting ramp-up.
                # If early sessions are expiring already,
                # or if late sessions are to expire before measurement is over.
                ramp_up_start_delay = time_now - self.ramp_up_start
                ramp_up_stop_delay = time_now - self.ramp_up_stop
                ramp_up_stop_delay += computed_duration
                bigger_delay = max(ramp_up_start_delay, ramp_up_stop_delay)
                # Final boolean decision.
                ramp_up_needed = (bigger_delay >= self.state_timeout)
            if ramp_up_needed:
                logger.debug(
                    u"State may time out during next real trial, "
                    u"inserting a ramp-up trial."
                )
                self.ramp_up_start = time.monotonic()
                self._send_traffic_on_tg_internal(
                    duration=self.ramp_up_duration,
                    rate=self.ramp_up_rate,
                    async_call=async_call,
                )
                self.ramp_up_stop = time.monotonic()
                logger.debug(u"Ramp-up done.")
            else:
                logger.debug(
                    u"State will probably not time out during next real trial, "
                    u"no ramp-up trial needed just yet."
                )
        if ramp_up_only:
            return None
        trial_start = time.monotonic()
        result = self._send_traffic_on_tg_internal(
            duration=duration,
            rate=rate,
            async_call=async_call,
        )
        trial_end = time.monotonic()
        if self.ramp_up_rate:
            # Optimization: No loss acts as a good ramp-up, if it was complete.
            if complete and result is not None and result.loss_ratio == 0.0:
                logger.debug(u"Good trial acts as a ramp-up")
                self.ramp_up_start = trial_start
                self.ramp_up_stop = trial_end
            else:
                logger.debug(u"Loss or incomplete, does not act as a ramp-up.")
        return result

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
        if self._received == 0:
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

    def _parse_traffic_results(self, stdout):
        """Parse stdout of scripts into fields of self.

        Block of code to reuse, by sync start, or stop after async.

        :param stdout: Text containing the standard output.
        :type stdout: str
        """
        subtype = check_subtype(self._node)
        if subtype == NodeSubTypeTG.TREX:
            # Last line from console output
            line = stdout.splitlines()[-1]
            results = line.split(u";")
            if results[-1] in (u" ", u""):
                results.pop(-1)
            self._result = dict()
            for result in results:
                key, value = result.split(u"=", maxsplit=1)
                self._result[key.strip()] = value
            logger.info(f"TrafficGen results:\n{self._result}")
            self._received = int(self._result.get(u"total_received"), 0)
            self._sent = int(self._result.get(u"total_sent", 0))
            self._loss = int(self._result.get(u"frame_loss", 0))
            self._approximated_duration = \
                self._result.get(u"approximated_duration", 0.0)
            if u"manual" not in str(self._approximated_duration):
                self._approximated_duration = float(self._approximated_duration)
            self._latency = list()
            self._latency.append(self._result.get(u"latency_stream_0(usec)"))
            self._latency.append(self._result.get(u"latency_stream_1(usec)"))
            if self._mode == TrexMode.ASTF:
                self._l7_data = dict()
                self._l7_data[u"client"] = dict()
                self._l7_data[u"client"][u"sent"] = \
                    int(self._result.get(u"client_sent", 0))
                self._l7_data[u"client"][u"received"] = \
                    int(self._result.get(u"client_received", 0))
                self._l7_data[u"client"][u"active_flows"] = \
                    int(self._result.get(u"client_active_flows", 0))
                self._l7_data[u"client"][u"established_flows"] = \
                    int(self._result.get(u"client_established_flows", 0))
                self._l7_data[u"client"][u"traffic_duration"] = \
                    float(self._result.get(u"client_traffic_duration", 0.0))
                self._l7_data[u"client"][u"err_rx_throttled"] = \
                    int(self._result.get(u"client_err_rx_throttled", 0))
                self._l7_data[u"client"][u"err_c_nf_throttled"] = \
                    int(self._result.get(u"client_err_nf_throttled", 0))
                self._l7_data[u"client"][u"err_flow_overflow"] = \
                    int(self._result.get(u"client_err_flow_overflow", 0))
                self._l7_data[u"server"] = dict()
                self._l7_data[u"server"][u"active_flows"] = \
                    int(self._result.get(u"server_active_flows", 0))
                self._l7_data[u"server"][u"established_flows"] = \
                    int(self._result.get(u"server_established_flows", 0))
                self._l7_data[u"server"][u"traffic_duration"] = \
                    float(self._result.get(u"server_traffic_duration", 0.0))
                self._l7_data[u"server"][u"err_rx_throttled"] = \
                    int(self._result.get(u"client_err_rx_throttled", 0))
                if u"udp" in self.traffic_profile:
                    self._l7_data[u"client"][u"udp"] = dict()
                    self._l7_data[u"client"][u"udp"][u"connects"] = \
                        int(self._result.get(u"client_udp_connects", 0))
                    self._l7_data[u"client"][u"udp"][u"closed_flows"] = \
                        int(self._result.get(u"client_udp_closed", 0))
                    self._l7_data[u"client"][u"udp"][u"tx_bytes"] = \
                        int(self._result.get(u"client_udp_tx_bytes", 0))
                    self._l7_data[u"client"][u"udp"][u"rx_bytes"] = \
                        int(self._result.get(u"client_udp_rx_bytes", 0))
                    self._l7_data[u"client"][u"udp"][u"tx_packets"] = \
                        int(self._result.get(u"client_udp_tx_packets", 0))
                    self._l7_data[u"client"][u"udp"][u"rx_packets"] = \
                        int(self._result.get(u"client_udp_rx_packets", 0))
                    self._l7_data[u"client"][u"udp"][u"keep_drops"] = \
                        int(self._result.get(u"client_udp_keep_drops", 0))
                    self._l7_data[u"client"][u"udp"][u"err_cwf"] = \
                        int(self._result.get(u"client_err_cwf", 0))
                    self._l7_data[u"server"][u"udp"] = dict()
                    self._l7_data[u"server"][u"udp"][u"accepted_flows"] = \
                        int(self._result.get(u"server_udp_accepts", 0))
                    self._l7_data[u"server"][u"udp"][u"closed_flows"] = \
                        int(self._result.get(u"server_udp_closed", 0))
                    self._l7_data[u"server"][u"udp"][u"tx_bytes"] = \
                        int(self._result.get(u"server_udp_tx_bytes", 0))
                    self._l7_data[u"server"][u"udp"][u"rx_bytes"] = \
                        int(self._result.get(u"server_udp_rx_bytes", 0))
                    self._l7_data[u"server"][u"udp"][u"tx_packets"] = \
                        int(self._result.get(u"server_udp_tx_packets", 0))
                    self._l7_data[u"server"][u"udp"][u"rx_packets"] = \
                        int(self._result.get(u"server_udp_rx_packets", 0))
                elif u"tcp" in self.traffic_profile:
                    self._l7_data[u"client"][u"tcp"] = dict()
                    self._l7_data[u"client"][u"tcp"][u"initiated_flows"] = \
                        int(self._result.get(u"client_tcp_connect_inits", 0))
                    self._l7_data[u"client"][u"tcp"][u"connects"] = \
                        int(self._result.get(u"client_tcp_connects", 0))
                    self._l7_data[u"client"][u"tcp"][u"closed_flows"] = \
                        int(self._result.get(u"client_tcp_closed", 0))
                    self._l7_data[u"client"][u"tcp"][u"connattempt"] = \
                        int(self._result.get(u"client_tcp_connattempt", 0))
                    self._l7_data[u"client"][u"tcp"][u"tx_bytes"] = \
                        int(self._result.get(u"client_tcp_tx_bytes", 0))
                    self._l7_data[u"client"][u"tcp"][u"rx_bytes"] = \
                        int(self._result.get(u"client_tcp_rx_bytes", 0))
                    self._l7_data[u"server"][u"tcp"] = dict()
                    self._l7_data[u"server"][u"tcp"][u"accepted_flows"] = \
                        int(self._result.get(u"server_tcp_accepts", 0))
                    self._l7_data[u"server"][u"tcp"][u"connects"] = \
                        int(self._result.get(u"server_tcp_connects", 0))
                    self._l7_data[u"server"][u"tcp"][u"closed_flows"] = \
                        int(self._result.get(u"server_tcp_closed", 0))
                    self._l7_data[u"server"][u"tcp"][u"tx_bytes"] = \
                        int(self._result.get(u"server_tcp_tx_bytes", 0))
                    self._l7_data[u"server"][u"tcp"][u"rx_bytes"] = \
                        int(self._result.get(u"server_tcp_rx_bytes", 0))

    def _get_measurement_result(self):
        """Return the result of last measurement as MeasurementResult.

        Separate function, as measurements can end either by time
        or by explicit call, this is the common block at the end.

        The intended_load field of MeasurementResult is in
        transactions per second. Transmit count and loss count units
        depend on the transaction type. Usually they are in transactions
        per second, or aggregated packets per second.

        :returns: Structure containing the result of the measurement.
        :rtype: MeasurementResult
        """
        duration_with_overheads = time.monotonic() - self._start_time
        try:
            # Client duration seems to include a setup period
            # where TRex does not send any packets yet.
            # Server duration does not include it.
            server_data = self._l7_data[u"server"]
            approximated_duration = float(server_data[u"traffic_duration"])
        except (KeyError, AttributeError, ValueError, TypeError):
            approximated_duration = None
        try:
            if not approximated_duration:
                approximated_duration = float(self._approximated_duration)
        except ValueError:  # "manual"
            approximated_duration = None
        if not approximated_duration:
            if self._duration and self._duration > 0:
                # Known recomputed or target duration.
                approximated_duration = self._duration
            else:
                # It was an explicit stop.
                if not self._stop_time:
                    raise RuntimeError(u"Unable to determine duration.")
                approximated_duration = self._stop_time - self._start_time
        target_duration = self._target_duration
        if not target_duration:
            target_duration = approximated_duration
        transmit_rate = self._rate
        unsent = 0
        if self.transaction_type == u"packet":
            partial_attempt_count = self._sent
            packet_rate = transmit_rate * self.ppta
            # We have a float. TRex way of rounding it is not obvious.
            # The biggest source of mismatch is Inter Stream Gap.
            # So the code tolerates 10 usec of missing packets.
            expected_attempt_count = (target_duration - 1e-5) * packet_rate
            expected_attempt_count = math.ceil(expected_attempt_count)
            # TRex can send more.
            expected_attempt_count = max(expected_attempt_count, self._sent)
            unsent = expected_attempt_count - self._sent
            pass_count = self._received
            loss_count = self._loss
        elif self.transaction_type == u"udp_cps":
            if not self.transaction_scale:
                raise RuntimeError(u"Add support for no-limit udp_cps.")
            partial_attempt_count = self._l7_data[u"client"][u"sent"]
            # We do not care whether TG is slow, it should have attempted all.
            expected_attempt_count = self.transaction_scale
            unsent = expected_attempt_count - partial_attempt_count
            pass_count = self._l7_data[u"client"][u"received"]
            loss_count = partial_attempt_count - pass_count
        elif self.transaction_type == u"tcp_cps":
            if not self.transaction_scale:
                raise RuntimeError(u"Add support for no-limit tcp_cps.")
            ctca = self._l7_data[u"client"][u"tcp"][u"connattempt"]
            partial_attempt_count = ctca
            # We do not care whether TG is slow, it should have attempted all.
            expected_attempt_count = self.transaction_scale
            unsent = expected_attempt_count - partial_attempt_count
            # From TCP point of view, server/connects counts full connections,
            # but we are testing NAT session so client/connects counts that
            # (half connections from TCP point of view).
            pass_count = self._l7_data[u"client"][u"tcp"][u"connects"]
            loss_count = partial_attempt_count - pass_count
        elif self.transaction_type == u"udp_pps":
            if not self.transaction_scale:
                raise RuntimeError(u"Add support for no-limit udp_pps.")
            partial_attempt_count = self._sent
            expected_attempt_count = self.transaction_scale * self.ppta
            unsent = expected_attempt_count - self._sent
            loss_count = self._loss
        elif self.transaction_type == u"tcp_pps":
            if not self.transaction_scale:
                raise RuntimeError(u"Add support for no-limit tcp_pps.")
            partial_attempt_count = self._sent
            expected_attempt_count = self.transaction_scale * self.ppta
            # One loss-like scenario happens when TRex receives all packets
            # on L2 level, but is not fast enough to process them all
            # at L7 level, which leads to retransmissions.
            # Those manifest as opackets larger than expected.
            # A simple workaround is to add absolute difference.
            # Probability of retransmissions exactly cancelling
            # packets unsent due to duration stretching is quite low.
            unsent = abs(expected_attempt_count - self._sent)
            loss_count = self._loss
        else:
            raise RuntimeError(f"Unknown parsing {self.transaction_type!r}")
        if unsent and isinstance(self._approximated_duration, float):
            # Do not report unsent for "manual".
            logger.debug(f"Unsent packets/transactions: {unsent}")
        if loss_count < 0 and not self.negative_loss:
            loss_count = 0
        measurement = MeasurementResult(
            intended_duration=target_duration,
            intended_load=transmit_rate,
            offered_count=partial_attempt_count,
            loss_count=loss_count,
            offered_duration=approximated_duration,
            duration_with_overheads=duration_with_overheads,
            intended_count=expected_attempt_count,
        )
        measurement.latency = self.get_latency_int()
        return measurement

    def measure(self, intended_duration, intended_load):
        """Run trial measurement, parse and return results.

        The intended load is for transactions. Stateles bidirectional traffic
        is understood as sequence of (asynchronous) transactions,
        two packets each.

        The result units depend on test type, generally
        the count either transactions or packets (aggregated over directions).

        Optionally, this method sleeps if measurement finished before
        the time specified as intended_duration (PLRsearch needs time for math).

        :param intended_duration: Trial duration [s].
        :param intended_load: Target rate in transactions per second.
        :type intended_duration: float
        :type intended_load: float
        :returns: Structure containing the result of the measurement.
        :rtype: MeasurementResult
        :raises RuntimeError: If TG is not set or if node is not TG
            or if subtype is not specified.
        :raises NotImplementedError: If TG is not supported.
        """
        intended_duration = float(intended_duration)
        time_start = time.monotonic()
        time_stop = time_start + intended_duration
        if self.resetter:
            self.resetter()
        result = self._send_traffic_on_tg_with_ramp_up(
            duration=intended_duration,
            rate=intended_load,
            async_call=False,
        )
        logger.debug(f"trial measurement result: {result!r}")
        # In PLRsearch, computation needs the specified time to complete.
        if self.sleep_till_duration:
            while (sleeptime := time_stop - time.monotonic()) > 0.0:
                time.sleep(sleeptime)
        return result

    def set_rate_provider_defaults(
            self,
            frame_size,
            traffic_profile,
            ppta=1,
            resetter=None,
            traffic_directions=2,
            transaction_duration=0.0,
            transaction_scale=0,
            transaction_type=u"packet",
            duration_limit=0.0,
            negative_loss=True,
            sleep_till_duration=False,
            use_latency=False,
            ramp_up_rate=None,
            ramp_up_duration=None,
            state_timeout=240.0,
        ):
        """Store values accessed by measure().

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :param ppta: Packets per transaction, aggregated over directions.
            Needed for udp_pps which does not have a good transaction counter,
            so we need to compute expected number of packets.
            Default: 1.
        :param resetter: Callable to reset DUT state for repeated trials.
        :param traffic_directions: Traffic from packet counting point of view
            is bi- (2) or uni- (1) directional.
            Default: 2
        :param transaction_duration: Total expected time to close transaction.
        :param transaction_scale: Number of transactions to perform.
            0 (default) means unlimited.
        :param transaction_type: An identifier specifying which counters
            and formulas to use when computing attempted and failed
            transactions. Default: "packet".
        :param duration_limit: Zero or maximum limit for computed (or given)
            duration.
        :param negative_loss: If false, negative loss is reported as zero loss.
        :param sleep_till_duration: If true and measurement returned faster,
            sleep until it matches duration. Needed for PLRsearch.
        :param use_latency: Whether to measure latency during the trial.
            Default: False.
        :param ramp_up_rate: Rate to use in ramp-up trials [pps].
        :param ramp_up_duration: Duration of ramp-up trials [s].
        :param state_timeout: Time of life of DUT state [s].
        :type frame_size: str or int
        :type traffic_profile: str
        :type ppta: int
        :type resetter: Optional[Callable[[], None]]
        :type traffic_directions: int
        :type transaction_duration: float
        :type transaction_scale: int
        :type transaction_type: str
        :type duration_limit: float
        :type negative_loss: bool
        :type sleep_till_duration: bool
        :type use_latency: bool
        :type ramp_up_rate: float
        :type ramp_up_duration: float
        :type state_timeout: float
        """
        self.frame_size = frame_size
        self.traffic_profile = str(traffic_profile)
        self.resetter = resetter
        self.ppta = int(ppta)
        self.traffic_directions = int(traffic_directions)
        self.transaction_duration = float(transaction_duration)
        self.transaction_scale = int(transaction_scale)
        self.transaction_type = str(transaction_type)
        self.duration_limit = float(duration_limit)
        self.negative_loss = bool(negative_loss)
        self.sleep_till_duration = bool(sleep_till_duration)
        self.use_latency = bool(use_latency)
        self.ramp_up_rate = float(ramp_up_rate)
        self.ramp_up_duration = float(ramp_up_duration)
        self.state_timeout = float(state_timeout)


class OptimizedSearch:
    """Class to be imported as Robot Library, containing search keywords.

    Aside of setting up measurer and forwarding arguments,
    the main business is to translate min/max rate from unidir to aggregated.
    """

    @staticmethod
    def perform_mlr_search(
        frame_size: Union[int, str],
        traffic_profile: str,
        min_load: float,
        max_load: float,
        loss_ratio: float = 0.005,
        relative_width: float = 0.005,
        initial_trial_duration: float = 1.0,
        final_trial_duration: float = 1.0,
        duration_sum: float = 21.0,
        expansion_coefficient: int = 2,
        preceding_targets: int = 2,
        search_duration_max: float = 1200.0,
        ppta: int = 1,
        resetter: Optional[Callable[[], None]] = None,
        traffic_directions: int = 2,
        transaction_duration: float = 0.0,
        transaction_scale: int = 0,
        transaction_type: str = "packet",
        use_latency: bool = False,
        ramp_up_rate: float = 0.0,
        ramp_up_duration: float = 0.0,
        state_timeout: float = 240.0,
    ) -> List[GoalResult]:
        """Setup initialized TG, perform optimized search, return intervals.

        If transaction_scale is nonzero, all init and non-init trial durations
        are set to 1.0 (as they do not affect the real trial duration)
        and zero intermediate phases are used.
        This way no re-measurement happens.
        Warmup has to be handled via resetter or ramp-up mechanisms.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :param min_load: Minimal load in transactions per second.
        :param max_load: Maximal load in transactions per second.
        :param loss_ratio: Ratio of packets lost, for PDR [1].
        :param relative_width: Final lower bound intended load
            cannot be more distant that this multiple of upper bound [1].
        :param initial_trial_duration: Trial duration for the initial phase
            and also for the first intermediate phase [s].
        :param final_trial_duration: Trial duration for the final phase [s].
        :param duration_sum: Max sum of duration for deciding [s].
        :param expansion_coefficient: In external search multiply width by this.
        :param preceding_targets: Number of intermediate phases
            to perform before the final phase [1].
        :param search_duration_max: The search will fail itself
            when not finished before this overall time [s].
        :param ppta: Packets per transaction, aggregated over directions.
            Needed for udp_pps which does not have a good transaction counter,
            so we need to compute expected number of packets.
            Default: 1.
        :param resetter: Callable to reset DUT state for repeated trials.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param transaction_duration: Total expected time to close transaction.
        :param transaction_scale: Number of transactions to perform.
            0 (default) means unlimited.
        :param transaction_type: An identifier specifying which counters
            and formulas to use when computing attempted and failed
            transactions. Default: "packet".
        :param use_latency: Whether to measure latency during the trial.
            Default: False.
        :param ramp_up_rate: Rate to use in ramp-up trials [pps].
        :param ramp_up_duration: Duration of ramp-up trials [s].
        :param state_timeout: Time of life of DUT state [s].
        :type frame_size: str or int
        :type traffic_profile: str
        :type min_load: float
        :type max_load: float
        :type loss_ratio: float
        :type relative_width: float
        :type initial_trial_duration: float
        :type final_trial_duration: float
        :type duration_sum: float
        :type expansion_coefficient: int
        :type preceding_targets: int
        :type search_duration_max: float
        :type ppta: int
        :type resetter: Optional[Callable[[], None]]
        :type traffic_directions: int
        :type transaction_duration: float
        :type transaction_scale: int
        :type transaction_type: str
        :type use_latency: bool
        :type ramp_up_rate: float
        :type ramp_up_duration: float
        :type state_timeout: float
        :returns: Goal result (based on unidirectional tps) for each goal.
            The result contains both the offered load for stat trial,
            and the conditional throughput for display.
        :rtype: List[GoalResult]
        :raises RuntimeError: If search duration exceeds search_duration_max
            or if min load becomes an upper bound for any search goal.
        """
        # we need instance of TrafficGenerator instantiated by Robot Framework
        # to be able to use trex_stl-*()
        tg_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        # Overrides for fixed transaction amount.
        if transaction_scale:
            initial_trial_duration = 1.0
            final_trial_duration = 1.0
            preceding_targets = 1
            # TODO: Move the value to Constants.py?
            search_duration_max += transaction_scale * 3e-4
        tg_instance.set_rate_provider_defaults(
            frame_size=frame_size,
            traffic_profile=traffic_profile,
            sleep_till_duration=False,
            ppta=ppta,
            resetter=resetter,
            traffic_directions=traffic_directions,
            transaction_duration=transaction_duration,
            transaction_scale=transaction_scale,
            transaction_type=transaction_type,
            use_latency=use_latency,
            ramp_up_rate=ramp_up_rate,
            ramp_up_duration=ramp_up_duration,
            state_timeout=state_timeout,
        )
        if loss_ratio:
            loss_ratios = [0.0, loss_ratio]
            exceed_ratio = 0.5
        else:
            # Happens in reconf tests.
            loss_ratios = [0.0]
            exceed_ratio = 0.0
        goals = [
            SearchGoal(
                loss_ratio=loss_ratio,
                exceed_ratio=exceed_ratio,
                relative_width=relative_width,
                initial_trial_duration=initial_trial_duration,
                final_trial_duration=final_trial_duration,
                duration_sum=duration_sum,
                preceding_targets=preceding_targets,
                expansion_coefficient=expansion_coefficient,
                fail_fast=True,
            )
            for loss_ratio in loss_ratios
        ]
        config = Config()
        config.goals = goals
        config.min_load = min_load
        config.max_load = max_load
        config.search_duration_max = search_duration_max
        config.warmup_duration = 1.0
        algorithm = MultipleLossRatioSearch(config)
        results = algorithm.search(measurer=tg_instance, debug=logger.debug)
        return [results[goal] for goal in goals]

    @staticmethod
    def perform_soak_search(
            frame_size,
            traffic_profile,
            min_load,
            max_load,
            plr_target=1e-7,
            tdpt=0.1,
            initial_count=50,
            timeout=7200.0,
            ppta=1,
            resetter=None,
            trace_enabled=False,
            traffic_directions=2,
            transaction_duration=0.0,
            transaction_scale=0,
            transaction_type=u"packet",
            use_latency=False,
            ramp_up_rate=None,
            ramp_up_duration=None,
            state_timeout=240.0,
    ):
        """Setup initialized TG, perform soak search, return avg and stdev.

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See GPL/traffic_profiles/trex for implemented modules.
        :param min_load: Minimal load in transactions per second.
        :param max_load: Maximal load in transactions per second.
        :param plr_target: Ratio of packets lost to achieve [1].
        :param tdpt: Trial duration per trial.
            The algorithm linearly increases trial duration with trial number,
            this is the increment between succesive trials, in seconds.
        :param initial_count: Offset to apply before the first trial.
            For example initial_count=50 makes first trial to be 51*tdpt long.
            This is needed because initial "search" phase of integrator
            takes significant time even without any trial results.
        :param timeout: The search will stop after this overall time [s].
        :param ppta: Packets per transaction, aggregated over directions.
            Needed for udp_pps which does not have a good transaction counter,
            so we need to compute expected number of packets.
            Default: 1.
        :param resetter: Callable to reset DUT state for repeated trials.
        :param trace_enabled: True if trace enabled else False.
            This is very verbose tracing on numeric computations,
            do not use in production.
            Default: False
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :param transaction_duration: Total expected time to close transaction.
        :param transaction_scale: Number of transactions to perform.
            0 (default) means unlimited.
        :param transaction_type: An identifier specifying which counters
            and formulas to use when computing attempted and failed
            transactions. Default: "packet".
        :param use_latency: Whether to measure latency during the trial.
            Default: False.
        :param ramp_up_rate: Rate to use in ramp-up trials [pps].
        :param ramp_up_duration: Duration of ramp-up trials [s].
        :param state_timeout: Time of life of DUT state [s].
        :type frame_size: str or int
        :type traffic_profile: str
        :type min_load: float
        :type max_load: float
        :type plr_target: float
        :type initial_count: int
        :type timeout: float
        :type ppta: int
        :type resetter: Optional[Callable[[], None]]
        :type trace_enabled: bool
        :type traffic_directions: int
        :type transaction_duration: float
        :type transaction_scale: int
        :type transaction_type: str
        :type use_latency: bool
        :type ramp_up_rate: float
        :type ramp_up_duration: float
        :type state_timeout: float
        :returns: Average and stdev of estimated aggregated rate giving PLR.
        :rtype: 2-tuple of float
        """
        tg_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.TrafficGenerator"
        )
        # Overrides for fixed transaction amount.
        if transaction_scale:
            timeout = 7200.0
        tg_instance.set_rate_provider_defaults(
            frame_size=frame_size,
            traffic_profile=traffic_profile,
            negative_loss=False,
            sleep_till_duration=True,
            ppta=ppta,
            resetter=resetter,
            traffic_directions=traffic_directions,
            transaction_duration=transaction_duration,
            transaction_scale=transaction_scale,
            transaction_type=transaction_type,
            use_latency=use_latency,
            ramp_up_rate=ramp_up_rate,
            ramp_up_duration=ramp_up_duration,
            state_timeout=state_timeout,
        )
        algorithm = PLRsearch(
            measurer=tg_instance,
            trial_duration_per_trial=tdpt,
            packet_loss_ratio_target=plr_target,
            trial_number_offset=initial_count,
            timeout=timeout,
            trace_enabled=trace_enabled,
        )
        result = algorithm.search(
            min_rate=min_load,
            max_rate=max_load,
        )
        return result
