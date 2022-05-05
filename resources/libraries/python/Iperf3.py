# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""iPerf3 utilities library."""

import json

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.Namespaces import Namespaces
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error


class Iperf3:
    """iPerf3 traffic generator utilities."""

    def __init__(self):
        """Initialize iPerf3 class."""
        # Computed affinity for iPerf server.
        self._s_affinity = None
        # Computed affinity for iPerf client.
        self._c_affinity = None

    @staticmethod
    def get_iperf_type(node):
        """Log and return the installed traffic generator type.

        :param node: Node from topology file.
        :type node: dict
        :returns: Traffic generator type string.
        :rtype: str
        """
        return "IPERF"

    @staticmethod
    def get_iperf_version(node):
        """Log and return the installed traffic generator version.

        :param node: Node from topology file.
        :type node: dict
        :returns: Traffic generator version string.
        :rtype: str
        """
        command = f"iperf3 --version | head -1"
        message = u"Get iPerf version failed!"
        stdout, _ = exec_cmd_no_error(node, command, message=message)
        return stdout.strip()

    def initialize_iperf_server(
            self, node, pf_key, interface, bind, bind_gw, bind_mask,
            namespace=None, cpu_skip_cnt=0, cpu_cnt=1, instances=1):
        """iPerf3 initialization.

        :param node: Topology node running iPerf3 server.
        :param pf_key: First TG's interface (To compute numa location).
        :param interface: Name of TG bind interface.
        :param bind: Bind to host, one of node's addresses.
        :param bind_gw: Bind gateway (required for default route).
        :param bind_mask: Bind address mask.
        :param namespace: Name of TG namespace to execute.
        :param cpu_skip_cnt: Amount of CPU cores to skip.
        :param cpu_cnt: iPerf3 main thread count.
        :param instances: Number of simultaneous iPerf3 instances.
        :type node: dict
        :type pf_key: str
        :type interface: str
        :type bind: str
        :type bind_gw: str
        :type bind_mask: str
        :type namespace: str
        :type cpu_skip_cnt: int
        :type cpu_cnt: int
        :type instances: int
        """
        if Iperf3.is_iperf_running(node):
            Iperf3.teardown_iperf(node)

        if namespace:
            IPUtil.set_linux_interface_ip(
                node, interface=interface, ip_addr=bind, prefix=bind_mask,
                namespace=namespace)
            IPUtil.set_linux_interface_up(
                node, interface=interface, namespace=namespace)
            Namespaces.add_default_route_to_namespace(
                node, namespace=namespace, default_route=bind_gw)

        # Compute affinity for iPerf server.
        self._s_affinity = CpuUtils.get_affinity_iperf(
            node, pf_key, cpu_skip_cnt=cpu_skip_cnt,
            cpu_cnt=cpu_cnt * instances)
        # Compute affinity for iPerf client.
        self._c_affinity = CpuUtils.get_affinity_iperf(
            node, pf_key, cpu_skip_cnt=cpu_skip_cnt + cpu_cnt * instances,
            cpu_cnt=cpu_cnt * instances)

        for i in range(0, instances):
            Iperf3.start_iperf_server(
                node, namespace=namespace, port=5201 + i,
                affinity=self._s_affinity)

    @staticmethod
    def start_iperf_server(
            node, namespace=None, port=5201, affinity=None):
        """Start iPerf3 server instance as a deamon.

        :param node: Topology node running iPerf3 server.
        :param namespace: Name of TG namespace to execute.
        :param port: The server port for the server to listen on.
        :param affinity: iPerf3 server affinity.
        :type node: dict
        :type namespace: str
        :type port: int
        :type affinity: str
        """
        cmd = IPerf3Server.iperf3_cmdline(
            namespace=namespace, port=port, affinity=affinity)
        exec_cmd_no_error(
            node, cmd, sudo=True, message=u"Failed to start iPerf3 server!")

    @staticmethod
    def is_iperf_running(node):
        """Check if iPerf3 is running using pgrep.

        :param node: Topology node running iPerf3.
        :type node: dict
        :returns: True if iPerf3 is running otherwise False.
        :rtype: bool
        """
        ret, _, _ = exec_cmd(node, u"pgrep iperf3", sudo=True)
        return bool(int(ret) == 0)

    @staticmethod
    def teardown_iperf(node):
        """iPerf3 teardown.

        :param node: Topology node running iPerf3.
        :type node: dict
        """
        pidfile = u"/tmp/iperf3_server.pid"
        logfile = u"/tmp/iperf3.log"

        exec_cmd_no_error(
            node,
            f"sh -c 'if [ -f {pidfile} ]; then "
            f"pkill iperf3; "
            f"cat {logfile}; "
            f"rm {logfile}; "
            f"fi'",
            sudo=True, message=u"iPerf3 kill failed!")

    def iperf_client_start_remote_exec(
            self, node, duration, rate, frame_size, async_call=False,
            warmup_time=0, traffic_directions=1, namespace=None, udp=False,
            host=None, bind=None, affinity=None):
        """Execute iPerf3 client script on remote node over ssh to start running
        traffic.

        :param node: Topology node running iPerf3.
        :param duration: Time expressed in seconds for how long to send traffic.
        :param rate: Traffic rate.
        :param frame_size: L2 frame size to send (without padding and IPG).
        :param async_call: If enabled then don't wait for all incoming traffic.
        :param warmup_time: Warmup time period.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 1
        :param namespace: Namespace to execute iPerf3 client on.
        :param udp: UDP traffic.
        :param host: Client connecting to an iPerf server running on host.
        :param bind: Client bind IP address.
        :param affinity: iPerf3 client affinity.
        :type node: dict
        :type duration: float
        :type rate: str
        :type frame_size: str
        :type async_call: bool
        :type warmup_time: float
        :type traffic_directions: int
        :type namespace: str
        :type udp: bool
        :type host: str
        :type bind: str
        :type affinity: str
        :returns: List of iPerf3 PIDs.
        :rtype: list
        """
        if not isinstance(duration, (float, int)):
            duration = float(duration)
        if not isinstance(warmup_time, (float, int)):
            warmup_time = float(warmup_time)
        if not affinity:
            affinity = self._c_affinity

        kwargs = dict()
        if namespace:
            kwargs[u"namespace"] = namespace
        kwargs[u"host"] = host
        kwargs[u"bind"] = bind
        kwargs[u"udp"] = udp
        if affinity:
            kwargs[u"affinity"] = affinity
        kwargs[u"duration"] = duration
        kwargs[u"rate"] = rate
        kwargs[u"frame_size"] = frame_size
        kwargs[u"warmup_time"] = warmup_time
        kwargs[u"traffic_directions"] = traffic_directions
        kwargs[u"async_call"] = async_call

        cmd = IPerf3Client.iperf3_cmdline(**kwargs)

        stdout, _ = exec_cmd_no_error(
            node, cmd, timeout=int(duration) + 30,
            message=u"iPerf3 runtime error!")

        if async_call:
            return stdout.split()
        return json.loads(stdout)

    @staticmethod
    def iperf_client_stop_remote_exec(node, pids):
        """Stop iPerf3 client execution.

        :param pids: PID or List of PIDs of iPerf3 client.
        :type pids: str or list
        """
        if not isinstance(pids, list):
            pids = [pids]

        for pid in pids:
            exec_cmd_no_error(
                node, f"kill {pid}", sudo=True, message=u"Kill iPerf3 failed!")


class IPerf3Server:
    """iPerf3 server utilities."""

    @staticmethod
    def iperf3_cmdline(**kwargs):
        """Get iPerf3 server command line.

        :param kwargs: List of iPerf3 server parameters.
        :type kwargs: dict
        :returns: iPerf3 server command line.
        :rtype: OptionString
        """
        cmd = OptionString()
        if kwargs['namespace']:
            cmd.add(f"ip netns exec {kwargs['namespace']}")
        cmd.add(f"iperf3")

        cmd_options = OptionString(prefix=u"--")
        # Run iPerf in server mode. (This will only allow one iperf connection
        # at a time)
        cmd_options.add(
            u"server")

        # Run the server in background as a daemon.
        cmd_options.add_if_from_dict(
            u"daemon", u"daemon", kwargs, True)

        # Write a file with the process ID, most useful when running as a
        # daemon.
        cmd_options.add_with_value_from_dict(
            u"pidfile", u"pidfile", kwargs, f"/tmp/iperf3_server.pid")

        # Send output to a log file.
        cmd_options.add_with_value_from_dict(
            u"logfile", u"logfile", kwargs, f"/tmp/iperf3.log")

        # The server port for the server to listen on and the client to
        # connect to. This should be the same in both client and server.
        # Default is 5201.
        cmd_options.add_with_value_from_dict(
            u"port", u"port", kwargs, 5201)

        # Set the CPU affinity, if possible (Linux and FreeBSD only).
        cmd_options.add_with_value_from_dict(
            u"affinity", u"affinity", kwargs)

        # Output in JSON format.
        cmd_options.add_if_from_dict(
            u"json", u"json", kwargs, True)

        # Give more detailed output.
        cmd_options.add_if_from_dict(
            u"verbose", u"verbose", kwargs, True)

        return cmd.extend(cmd_options)


class IPerf3Client:
    """iPerf3 client utilities."""

    @staticmethod
    def iperf3_cmdline(**kwargs):
        """Get iperf_client driver command line.

        :param kwargs: List of iperf_client driver parameters.
        :type kwargs: dict
        :returns: iperf_client driver command line.
        :rtype: OptionString
        """
        cmd = OptionString()
        cmd.add(u"python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/resources/tools/iperf"
        cmd.add(f"'{dirname}/iperf_client.py'")

        cmd_options = OptionString(prefix=u"--")
        # Namespace to execute iPerf3 client on.
        cmd_options.add_with_value_from_dict(
            u"namespace", u"namespace", kwargs)

        # Client connecting to an iPerf3 server running on host.
        cmd_options.add_with_value_from_dict(
            u"host", u"host", kwargs)

        # Client bind IP address.
        cmd_options.add_with_value_from_dict(
            u"bind", u"bind", kwargs)

        # Use UDP rather than TCP.
        cmd_options.add_if_from_dict(
            u"udp", u"udp", kwargs, False)

        # Set the CPU affinity, if possible.
        cmd_options.add_with_value_from_dict(
            u"affinity", u"affinity", kwargs)

        # Time expressed in seconds for how long to send traffic.
        cmd_options.add_with_value_from_dict(
            u"duration", u"duration", kwargs)

        # Send bi- (2) or uni- (1) directional traffic.
        cmd_options.add_with_value_from_dict(
            u"traffic_directions", u"traffic_directions", kwargs, 1)

        # Traffic warm-up time in seconds, (0=disable).
        cmd_options.add_with_value_from_dict(
            u"warmup_time", u"warmup_time", kwargs, 5.0)

        # L2 frame size to send (without padding and IPG).
        cmd_options.add_with_value_from_dict(
            u"frame_size", u"frame_size", kwargs)

        # Traffic rate expressed with units.
        cmd_options.add_with_value_from_dict(
            u"rate", u"rate", kwargs)

        # If enabled then don't wait for all incoming traffic.
        cmd_options.add_if_from_dict(
            u"async_start", u"async_call", kwargs, False)

        # Number of iPerf3 client parallel instances.
        cmd_options.add_with_value_from_dict(
            u"instances", u"instances", kwargs, 1)

        # Number of iPerf3 client parallel flows.
        cmd_options.add_with_value_from_dict(
            u"parallel", u"parallel", kwargs, 8)

        return cmd.extend(cmd_options)
