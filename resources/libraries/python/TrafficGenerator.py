# Copyright (c) 2019 Cisco and/or its affiliates.
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
import yaml

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from .Constants import Constants
from .ssh import exec_cmd_no_error
from .topology import NodeType
from .topology import NodeSubTypeTG
from .topology import Topology
from .MLRsearch.AbstractMeasurer import AbstractMeasurer
from .MLRsearch.MultipleLossRatioSearch import MultipleLossRatioSearch
from .MLRsearch.ReceiveRateMeasurement import ReceiveRateMeasurement
from .PLRsearch.PLRsearch import PLRsearch

__all__ = ['TrafficGenerator', 'OptimizedSearch']


class TrafficGenerator(AbstractMeasurer):
    """Traffic Generator for performance testing

    A Traffic Generator instance is created in scope for test suites measuring
    performance in a given topology. A dedicated TG node in the topology is
    remotely controlled by this instance. The subtype of this node selects which
    implementation of traffic generator is to be used on the node. The only
    supported subtype at this time is TRex.

    A test suite must initialize the generator instance by providing it with
    node and interface information, including information on adjacent nodes.

    Depending on the kind of testing, as denoted by the OSI layer for the suite,
    source and destination addresses are required for configuration of the
    generator.

    Once initialized, traffic may be configured and sent by the generator,
    provided a complete set of required parameters, such as duration, transmit
    rate, and a traffic profile for the 'content' of the generated stream.

    The traffic may be started for either synchronous or asynchronous mode;
    in the former, the generator blocks for the required duration of the run,
    and returns its results. When the traffic is sent asynchronously, it
    must be stopped at a later time, and the same result will be returned then.
    Only a single traffic run may be active at any given time.

    Finally, the traffic generator should be torn down during suite cleanups.
    """

    # TODO: Decrease friction between various search and rate provider APIs.

    # Use one instance of TrafficGenerator for all tests in test suite
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self):
        self._driver = None
        # Input parameters not available in measure(), hence need to be preset
        self.frame_size = None
        self.traffic_profile = None
        self.warmup_time = None
        self.traffic_directions = None

    @staticmethod
    def get_driver(node):
        """Return supported TrafficGeneratorDriver for given node

        At this time, only a TRex driver is supported.

        :param node: Topology node to check.
        :type node: dict
        :returns: Driver for supported node types
        :rtype: TrafficGeneratorDriver
        :raises RuntimeError: If node is not supported, message explains how.
        """
        if node.get('type') is None:
            raise RuntimeError('Node type is not defined')
        elif node['type'] != NodeType.TG:
            raise RuntimeError('Node type is {typ!r}, not a TG'.format(
                typ=node['type']))
        elif node.get('subtype') is None:
            raise RuntimeError('TG subtype is not defined')
        elif node['subtype'] == NodeSubTypeTG.TREX:
            return TrexDriver(node)
        raise RuntimeError('TG subtype {sub!r} is not supported'.format(
            sub=node['subtype']))

    def initialize_traffic_generator(
            self, tg_node, tg_if1, tg_if2, tg_if1_adj_node, tg_if1_adj_if,
            tg_if2_adj_node, tg_if2_adj_if, osi_layer, tg_if1_dst_mac=None,
            tg_if2_dst_mac=None):
        """TG initialization.

        :param tg_node: Traffic generator node.
        :param tg_if1: TG - name of first interface.
        :param tg_if2: TG - name of second interface.
        :param tg_if1_adj_node: TG if1 adjacent node.
        :param tg_if1_adj_if: TG if1 adjacent interface.
        :param tg_if2_adj_node: TG if2 adjacent node.
        :param tg_if2_adj_if: TG if2 adjacent interface.
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
        if self._driver is not None:
            raise RuntimeError('Traffic Generator is already initialized')
        self._driver = self.get_driver(tg_node)
        links = [
            DirectedLink(TopologyInterface(tg_node, tg_if1),
                         TopologyInterface(tg_if1_adj_node, tg_if1_adj_if),
                         tg_if1_dst_mac),
            DirectedLink(TopologyInterface(tg_node, tg_if2),
                         TopologyInterface(tg_if2_adj_node, tg_if2_adj_if),
                         tg_if2_dst_mac)]
        self._driver.setup(osi_layer, links)

    def teardown_traffic_generator_if_setup(self, tg_node):
        """Check if a traffic generator is currently set up on the node

        The generator may either be set up for use currently, or may be left
        over from an unsuccessful cleanup.

        :param node: Node to be inspected for possibly leftover generator
        :type node: dict
        :raises RuntimeError: If node is unsupported, or teardown fails
        """
        if self._driver is not None and self._driver.match_node(tg_node):
            self.teardown_traffic_generator()
        else:
            driver = self.get_driver(tg_node)
            driver.teardown()

    def teardown_traffic_generator(self):
        """TG teardown.

        If a driver for traffic generator was initialized, its teardown
        shall put the node into an inactive state, ready for another
        initialization for a different test suite. This includes terminating
        processes and services, and potentially resetting OS-level state.
        The current driver is destroyed as well.

        :raises RuntimeError: If generator teardown fails.
        """
        if self._driver is not None:
            self._driver.teardown()
            self._driver = None

    def stop_traffic_on_tg(self):
        """Stop all traffic on TG and return measurement results

        Can only be called after a run was previously started with
        send_traffic_on_tg with async_call set to True.

        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        :raises RuntimeError: If TG is not set up and sending traffic.
        """
        if self._driver is None:
            raise RuntimeError('TrafficGenerator is uninitialized')
        self._driver.stop()
        return self._driver.collect()

    def send_traffic_on_tg(
            self, duration, rate, frame_size, traffic_profile, warmup_time=5,
            async_call=False, latency=True, traffic_directions=2, tx_port=0,
            rx_port=1):
        """Send traffic from all configured interfaces on TG.

        Note that bidirectional traffic also contains flows
        transmitted from rx_port and received in tx_port.
        But some tests use asymmetric traffic, so those arguments are relevant.

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
        :raises RuntimeError: If TG is not set up or starting traffic fails
        """
        if self._driver is None:
            raise RuntimeError('TrafficGenerator is uninitialized')

        # Values from Robot can introduce type unicode,
        # we need to encode them, so that repr() does not lead with 'u'.
        if isinstance(rate, unicode):
            rate = rate.encode("utf-8")
        if not isinstance(duration, (float, int)):
            duration = float(duration)
        if not isinstance(warmup_time, (float, int)):
            warmup_time = float(warmup_time)

        self._driver.start(
            duration, rate, frame_size, traffic_profile, warmup_time,
            async_call, latency, traffic_directions, tx_port, rx_port)
        if async_call:
            return None
        else:
            return self._driver.collect()

    @staticmethod
    def fail_if_traffic_loss_occurred(measurements):
        """Fail if loss occurred in traffic run.

        :param measurements: Results of traffic generator runs
        :type measurements: List of ReceiveRateMeasurement
        :raises RuntimeError: If loss occured.
        """
        losses = []
        for idx, measurement in enumerate(measurements, start=1):
            if measurement.loss_count > 0:
                losses.append('{idx}={loss_count}'.format(
                    idx=idx, loss_count=measurement.loss_count))
        if losses:
            raise RuntimeError(
                'Traffic loss occurred in {count} out of {total} runs: {which}'
                .format(count=len(losses), total=len(measurements),
                        which=', '.join(losses)))

    @staticmethod
    def fail_if_no_traffic_forwarded(measurements):
        """Fail if no traffic forwarded.

        :param measurements: Results of traffic generator runs
        :type measurements: List of ReceiveRateMeasurement
        :raises Exception: If no traffic forwarded.
        """
        no_traffic = []
        for idx, measurement in enumerate(measurements, start=1):
            if measurement.receive_count == 0:
                no_traffic.append(str(idx))
        if no_traffic:
            raise RuntimeError(
                'No traffic forwarded in {count} out of {total} runs: {which}'
                .format(count=len(no_traffic), total=len(measurements),
                        which=', '.join(no_traffic)))

    @staticmethod
    def extract_measurement_receive_rates(measurements):
        """Extract apparent receive rates from measurements

        Computed as a ratio of a measurement's receive count and duration.

        :param measurements: Results of traffic generator runs
        :type measurements: List of ReceiveRateMeasurement
        :returns: list of receive rates from the measurements
        :rtype: list of float
        """
        return [float(measurement.receive_count) / measurement.duration
                for measurement in measurements]

    def set_rate_provider_defaults(self, frame_size, traffic_profile,
                                   warmup_time=0.0, traffic_directions=2):
        """Store values accessed by measure().

        :param frame_size: Frame size identifier or value [B].
        :param traffic_profile: Module name as a traffic profile identifier.
            See resources/traffic_profiles/trex for implemented modules.
        :param warmup_time: Traffic duration before measurement starts [s].
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :type frame_size: str or int
        :type traffic_profile: str
        :type warmup_time: float
        :type traffic_directions: int
        """
        # TODO: perhaps these parameters could be preset by other callers too
        # and then send_traffic_on_tg arg list pruned
        self.frame_size = frame_size
        self.traffic_profile = str(traffic_profile)
        self.warmup_time = float(warmup_time)
        self.traffic_directions = traffic_directions

    def measure(self, duration, transmit_rate):
        """Run trial measurement, parse and return aggregate results.

        Prior to calling this function, other traffic generator parameters
        must be set via set_rate_provider_defaults.

        Aggregate means sum over traffic directions.

        :param duration: Trial duration [s].
        :param transmit_rate: Target aggregate transmit rate [pps].
        :type duration: float
        :type transmit_rate: float
        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        :raises RuntimeError: If TG or measurement is not set up.
        :raises NotImplementedError: If TG is not supported.
        """
        duration = float(duration)
        transmit_rate = float(transmit_rate)

        # TG needs target Tr per stream, but reports aggregate Tx and Dx.
        # TODO: this may only be true for TRex
        # Also, do other uses of send_traffic_on_tg account for this?
        unit_rate_one = transmit_rate / float(self.traffic_directions)
        unit_rate_str = str(unit_rate_one) + "pps"
        return self.send_traffic_on_tg(
            duration, unit_rate_str, self.frame_size, self.traffic_profile,
            warmup_time=self.warmup_time, latency=True,
            traffic_directions=self.traffic_directions)


class OptimizedSearch(object):
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
            timeout=720.0, doublings=1, traffic_directions=2):
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
            'resources.libraries.python.TrafficGenerator')
        tg_instance.set_rate_provider_defaults(
            frame_size, traffic_profile, traffic_directions=traffic_directions)
        algorithm = MultipleLossRatioSearch(
            measurer=tg_instance, final_trial_duration=final_trial_duration,
            final_relative_width=final_relative_width,
            number_of_intermediate_phases=number_of_intermediate_phases,
            initial_trial_duration=initial_trial_duration, timeout=timeout,
            doublings=doublings)
        result = algorithm.narrow_down_ndr_and_pdr(
            minimum_transmit_rate, maximum_transmit_rate, packet_loss_ratio)
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
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 2
        :type frame_size: str or int
        :type traffic_profile: str
        :type minimum_transmit_rate: float
        :type maximum_transmit_rate: float
        :type plr_target: float
        :type initial_count: int
        :type timeout: float
        :type traffic_directions: int
        :returns: Average and stdev of estimated aggregate rate giving PLR.
        :rtype: 2-tuple of float
        """
        minimum_transmit_rate *= traffic_directions
        maximum_transmit_rate *= traffic_directions
        tg_instance = BuiltIn().get_library_instance(
            'resources.libraries.python.TrafficGenerator')
        tg_instance.set_rate_provider_defaults(
            frame_size, traffic_profile, traffic_directions=traffic_directions)
        algorithm = PLRsearch(
            measurer=tg_instance, trial_duration_per_trial=tdpt,
            packet_loss_ratio_target=plr_target,
            trial_number_offset=initial_count, timeout=timeout,
            trace_enabled=trace_enabled)
        result = algorithm.search(minimum_transmit_rate, maximum_transmit_rate)
        return result


class TrafficGeneratorDriver(object):
    """Drive a specific implementation of traffic generator

    A driver is responsible both for generator setup and teardown,
    as well as for configuring and management of traffic streams, and access
    to the results of each traffic generator run.

    """

    def __init__(self, node):
        """Initialize a driver instance to be run on a given node.

        A setup method must be called in order to configure global parameters
        for the generator, and to start any required processes or services.
        """
        self._node = node

    def match_node(self, node):
        """Return whether current driver is for the same node

        :returns: Whether this instance is managing the specified node
        :rtype: bool
        """
        return node is self._node or node['host'] == self._node['host']

    def setup(self, osi_layer, links):
        """Configure and run the traffic generator on target node

        A non-empty sequence of directed links is required to inform which
        interfaces of the node shall be used by the driver for the current
        test suite.

        Each link's source is on the TG node. The driver implementation shall
        pick whichever parameters it requires for both links to configure,
        including suite-lever network addressing values. The values are picked
        based on the OSI level of the test suite being set up at the time.

        If the call is successful, all required services should be running and
        ready for service, i.e. sending generated traffic.

        :param osi_layer: kind of traffic to be generated; affects addressing
        :param links: a series of directed links from the TG to other nodes
        :type osi_layer: str
        :type links: list of DirectedLink
        :raises RuntimeError: generator configuration or start failed.
        """
        raise NotImplementedError()

    def teardown(self):
        """Terminate and disable the traffic generator on target node.

        The generator need not be actually set up on the target node.
        Generator processes on the node shall not run, and the node shall be
        ready to be configured again, perhaps with a different parameter set.

        :raises RuntimeError: teardown failed, generator is not cleaned up
        """
        raise NotImplementedError()

    def start(
            self, duration, rate, frame_size, traffic_profile, warmup_time=5,
            async_call=False, latency=True, traffic_directions=2, tx_port=0,
            rx_port=1):
        """Send traffic from all configured interfaces on TG.

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
        :type duration: float
        :type rate: str
        :type frame_size: str
        :type traffic_profile: str
        :type warmup_time: float
        :type async_call: bool
        :type latency: bool
        :type traffic_directions: int
        :type tx_port: int
        :type rx_port: int
        :raises RuntimeError: If TG is not set up or starting traffic fails
        """
        raise NotImplementedError()

    def stop(self):
        """Stop async running traffic.

        :raises RuntimeError: If traffic wasn't started or stop traffic fails.
        """
        raise NotImplementedError()

    def collect(self):
        """Collect and clear the result of last traffic generator run.

        Duration and transmit_rate in the result may be estimates.
        List of latency data is also passed in the result, as ad-hoc attribute.

        The data collection may be a separate procedure for individual drivers,
        or the data may be immediately available with traffic stop.

        The collect function must be called in order to make the driver ready
        for another traffic run, regardless if it was asynchronous or not.

        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        """
        raise NotImplementedError()


class TrexDriver(TrafficGeneratorDriver):
    """Driver for the TRex traffic generator.

    Trex uses DPDK driver which will reorder port numbers based on wiring
    and PCI numbering. A message is issues in logs if this occurres, and
    swapped port values will be seen in debug logs.

    """

    def __init__(self, node):
        """Initialize a driver instance to be run on a given node.

        A setup method must be called in order to configure global parameters
        for the generator, and to start any required processes or services.
        """
        super(TrexDriver, self).__init__(node)
        # interfaces have been reordered to use lower PCI address first
        self._ifaces_reordered = False
        # time when traffic run started if async, 0 if sync, None if not running
        self._start_time = None
        # duration of traffic run, measured by driver if async
        self._duration = None
        # configured transmit rate per direction
        self._rate = None
        # collectable results from generator after a successful run
        self._stdout = None
        # previous stats from TRex start used in async mode
        self._xstats = None, None

    def setup(self, osi_layer, links):
        """Configure and run the traffic generator on target node

        A non-empty sequence of directed links is required to inform which
        interfaces of the node shall be used by the driver for the current
        test suite.

        Each link's source is on the TG node. The driver implementation shall
        pick whichever parameters it requires for both links to configure,
        including suite-lever network addressing values. The values are picked
        based on the OSI level of the test suite being set up at the time.

        If the call is successful, all required services should be running and
        ready for service, i.e. sending generated traffic.

        :param osi_layer: kind of traffic to be generated; affects addressing
        :param links: a series of directed links from the TG to other nodes
        :type osi_layer: str
        :type links: list of DirectedLink
        :raises RuntimeError: generator configuration or start failed.
        """
        if len(links) != 2:
            raise RuntimeError('TRex requires exactly 2 links')

        interfaces = [link.source.pci for link in links]
        if interfaces[0] > interfaces[1]:
            self._ifaces_reordered = True
            interfaces.reverse()
            links.reverse()
            logger.info('TRex interfaces are reordered as: {interfaces}'.format(
                interfaces=" ".join(interfaces)))
        else:
            self._ifaces_reordered = False

        if osi_layer == 'L2':
            port_info = [
                dict(src_mac=self._format_mac(link.source.mac),
                     dest_mac=self._format_mac(
                         link.dest_mac or other.source.mac))
                for link, other in zip(links, reversed(links))]

        elif osi_layer == 'L3':
            port_info = [
                dict(src_mac=self._format_mac(link.source.mac),
                     dest_mac=self._format_mac(link.target.mac))
                for link in links]
        elif osi_layer == 'L7':
            port_info = [
                dict(ip=[link.source.ip4], default_gw=[link.target.ip4])
                for link in links]
        else:
            raise RuntimeError("Unsupported Test OSI layer")

        config = [dict(version=2, interfaces=interfaces, port_info=port_info)]
        stdin = yaml.safe_dump(config).replace("'", '"')
        exec_cmd_no_error(self._node,
                          "sh -c 'tee /etc/trex_cfg.yaml <<EOF\n{stdin}\nEOF'"
                          .format(stdin=stdin),
                          sudo=True,
                          message='TRex config generation error')

        self._startup_trex(osi_layer)

    def _startup_trex(self, osi_layer):
        """Startup sequence for the TRex traffic generator.

        :param osi_layer: 'L2', 'L3' or 'L7' - OSI Layer testing type.
        :type osi_layer: str
        :raises RuntimeError: If node subtype is not a TREX or startup failed.
        """
        # No need to check subtype, we know it is TREX.
        for _ in range(0, 3):
            # Kill TRex only if it is already running.
            cmd = ("sh -c 'if pid=$(pidof t-rex) ; "
                   "then kill \"${pid}\" && sleep 3 ; fi'")
            exec_cmd_no_error(
                self._node, cmd, sudo=True, message='Kill TRex failed!')

            # Configure TRex.
            ports = ''
            for port in self._node['interfaces'].values():
                ports += ' {pci}'.format(pci=port.get('pci_address', ''))

            cmd = ("sh -c 'cd {dir}/scripts/ && "
                   "./dpdk_nic_bind.py -u {ports} || true'"
                   .format(dir=Constants.TREX_INSTALL_DIR, ports=ports))
            exec_cmd_no_error(
                self._node, cmd, sudo=True,
                message='Unbind PCI ports from driver failed!')

            cmd = ("sh -c 'cd {dir}/scripts/ && ./trex-cfg "
                   "--unbind-unused-ports'"
                   .format(dir=Constants.TREX_INSTALL_DIR))
            exec_cmd_no_error(
                self._node, cmd, sudo=True, message='Config TRex failed!')

            # Start TRex.
            cmd = ("sh -c 'cd {dir}/scripts/ && "
                   "nohup ./t-rex-64 --hdrh{mode} -i -c 7 > "
                   "/tmp/trex.log 2>&1 & > /dev/null'"
                   .format(dir=Constants.TREX_INSTALL_DIR,
                           mode=' --astf' if osi_layer == 'L7' else ''))
            try:
                exec_cmd_no_error(self._node, cmd, sudo=True,
                                  message='Start TRex failed!')
            except RuntimeError:
                cmd = "cat /tmp/trex.log"
                exec_cmd_no_error(
                    self._node, cmd, sudo=True, message='Get TRex logs failed!')
                raise

            # Test if TRex starts successfuly.
            cmd = ("{dir}/resources/tools/trex/trex_server_info.py"
                   .format(dir=Constants.REMOTE_FW_DIR))
            try:
                exec_cmd_no_error(
                    self._node, cmd, sudo=True, message='Test TRex failed!',
                    retries=20)
            except RuntimeError:
                continue
            return
        # After max retries TRex is still not responding to API critical error
        # occurred.
        raise RuntimeError('Start TRex failed after multiple retries!')

    def teardown(self):
        cmd = "sh -c 'if pid=$(pidof t-rex) ; then kill ${pid} && sleep 3 ; fi'"
        message = 'Terminating t-rex failed'
        exec_cmd_no_error(self._node, cmd, sudo=True, message=message)

    def start(
            self, duration, rate, frame_size, traffic_profile, warmup_time=5,
            async_call=False, latency=True, traffic_directions=2, tx_port=0,
            rx_port=1):
        """Send traffic from all configured interfaces on TG.

        In async mode, xstats is stored internally,
        to enable getting correct result when stopping the traffic.
        In sync mode, stdout is stored.

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
        :type duration: float
        :type rate: str
        :type frame_size: str
        :type traffic_profile: str
        :type warmup_time: float
        :type async_call: bool
        :type latency: bool
        :type traffic_directions: int
        :type tx_port: int
        :type rx_port: int
        :returns:
        :rtype: None if async_call else ReceivedRateMeasurement
        :raises RuntimeError: If TG is not set up or starting traffic fails
        """
        if self._start_time is not None:
            raise RuntimeError('TRex generator traffic already sent')
        self._start_time = 0
        if self._ifaces_reordered:
            rx_port, tx_port = tx_port, rx_port

        command = (
            "{tool}/resources/tools/trex/trex_stateless_profile.py"
            " --profile {prof}/resources/traffic_profiles/trex/{traffic}.py"
            " --duration {duration!r} --frame_size {frame_size} --rate {rate!r}"
            " --warmup_time {warmup!r} --port_0 {p_0} --port_1 {p_1}"
            " --traffic_directions {dirs}").format(
                tool=Constants.REMOTE_FW_DIR, prof=Constants.REMOTE_FW_DIR,
                traffic=traffic_profile, duration=duration,
                frame_size=frame_size, rate=rate, warmup=warmup_time,
                p_0=tx_port, p_1=rx_port, dirs=traffic_directions)

        timeout = 60
        if async_call:
            command += " --async"
        else:
            timeout += duration
        if latency:
            command += " --latency"

        stdout, _ = exec_cmd_no_error(
            self._node, command, timeout=timeout,
            message='TRex stateless runtime error')

        self._rate = float(rate[:-3] if "pps" in rate else rate)
        self._rate *= traffic_directions
        self._duration = duration
        if async_call:
            self._start_time = time.time()
            xstats = [None, None]
            index = 0
            for line in stdout.splitlines():
                if "Xstats snapshot {i}: ".format(i=index) in line:
                    xstats[index] = line[19:]
                    index += 1
                if index == 2:
                    break
            self._xstats = tuple(xstats)
        else:
            self._stdout = stdout

    def stop(self):
        """Stop async running traffic.

        Output from TRex script performing the stop contains the relevant stats.

        :raises RuntimeError: If traffic wasn't started or stop traffic fails.
        """
        if not self._start_time:
            raise RuntimeError('TRex traffic is not started as async_call')

        x_args = ""
        for index, value in enumerate(self._xstats):
            if value is not None:
                # Nested quoting is fun.
                value = value.replace("'", "\"")
                x_args += " --xstat{i}='\"'\"'{v}'\"'\"'".format(
                    i=index, v=value)

        stdout, _ = exec_cmd_no_error(
            self._node,
            "{d}/resources/tools/trex/trex_stateless_stop.py{a}".format(
                d=Constants.REMOTE_FW_DIR, a=x_args),
            message='TRex stateless runtime error')

        self._duration = time.time() - self._start_time
        self._stdout = stdout
        self._start_time = 0

    def collect(self):
        """Collect and clear the result of last traffic generation run.

        Duration and transmit_rate are not taken from TRex output, but
        by apparent runtime (for async mode) and input parameters.

        The data is parsed off output from either the send or stop command.

        The collect function must be called in order to make the driver ready
        for another traffic run, regardless if it's sent asynchronously or not.

        :returns: Structure containing the result of the measurement.
        :rtype: ReceiveRateMeasurement
        """
        # last line from console output, for example:
        # [ignored] rate='3343736.09758pps', totalReceived=3595076,
        # totalSent=6687474, frameLoss=3092398,
        # latencyStream0(usec)=-1/-1/-1, latencyStream1(usec)=-1/-1/-1,
        # [ignored] targetDuration=1.0
        if self._stdout is None:
            raise RuntimeError('No TRex generator run to collect')
        line = self._stdout.splitlines()[-1].strip()
        logger.info('TrafficGen result: {0}'.format(line))
        parts = dict(part.split('=') for part in line.split(', '))

        transmit_count = int(parts['totalSent'])
        loss_count = int(parts['frameLoss'])

        measurement = ReceiveRateMeasurement(
            self._duration, self._rate, transmit_count, loss_count)
        # TODO make latency a proper measurement attribute
        measurement.latency = [
            parts['latencyStream0(usec)'], parts['latencyStream1(usec)']]
        self._stdout = None
        self._start_time = None
        self._duration = None
        self._rate = None

        return measurement

    @staticmethod
    def _format_mac(mac):
        """Format mac address for TRex

        :param mac: mac address in linux format
        :type mac: str
        :returns: mac address in TRex format
        :rtype: str
        """
        return [int(part, 16) for part in mac.split(":")]


class TopologyInterface(object):
    """Access properties of a topology node's interface

    Convenience accessor for information which may be required by individual
    traffic generator drivers at certain times, without the need to retrieve
    them all in advance.
    """

    def __init__(self, node, interface):
        """Initalize topology interface property accessor

        :param node: Topology node
        :param interface: Interface key for topology node
        :type node: dict
        :type interface: str
        """
        self._node = node
        self._interface = interface

    @property
    def pci(self):
        """Return pci address for interface if known

        :rtype: str
        """
        return Topology().get_interface_pci_addr(self._node, self._interface)

    @property
    def mac(self):
        """Return mac address for interface if known

        :rtype: str
        """
        return Topology().get_interface_mac(self._node, self._interface)

    @property
    def ip4(self):
        """Return ipv4 address for interface if known

        :rtype: str
        """
        return Topology().get_interface_ip4(self._node, self._interface)


class DirectedLink(object):
    """A link from source interface to target interface

    Used to group together related interface objects, and to possibly denote
    relevant traffic forwarding information in the direction of the link.
    """

    def __init__(self, source, target, dest_mac=None):
        """Initialize directed link from one interface to another.

        :param source: source interface
        :param target: target interface
        :param dest_mac: override output mac address for L2 traffic
        :type source: TopologyInterface
        :type target: TopologyInterface
        :type dest_mac: str or None
        """
        self._source = source
        self._target = target
        self._dest_mac = dest_mac

    @property
    def source(self):
        """Return source interface

        :rtype: TopologyInterface
        """
        return self._source

    @property
    def target(self):
        """Return target interface

        :rtype: TopologyInterface
        """
        return self._target

    @property
    def dest_mac(self):
        """Return output mac address for L2 traffic

        :rtype: str
        """
        return self._dest_mac
