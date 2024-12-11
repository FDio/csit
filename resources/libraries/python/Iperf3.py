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

"""iPerf3 utilities library."""

import json

from robot.api import logger

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
    def get_iperf_type():
        """Log and return the installed traffic generator type.

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
        command = "iperf3 --version | head -1"
        message = "Get iPerf version failed!"
        stdout, _ = exec_cmd_no_error(node, command, message=message)
        return stdout.strip()

    def initialize_iperf_server(
        self,
        node,
        pf_key,
        interface,
        bind,
        bind_gw,
        bind_mask,
        namespace=None,
        cpu_skip_cnt=0,
        cpu_cnt=8,
        instances=1,
    ):
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
                node,
                interface=interface,
                ip_addr=bind,
                prefix=bind_mask,
                namespace=namespace,
            )
            IPUtil.set_linux_interface_up(
                node, interface=interface, namespace=namespace
            )
            Namespaces.add_default_route_to_namespace(
                node, namespace=namespace, default_route=bind_gw
            )

        # Compute affinity for iPerf server.
        self._s_affinity = CpuUtils.get_affinity_iperf(
            node, pf_key, cpu_skip_cnt=cpu_skip_cnt, cpu_cnt=cpu_cnt * instances
        )
        # Compute affinity for iPerf client.
        self._c_affinity = CpuUtils.get_affinity_iperf(
            node,
            pf_key,
            cpu_skip_cnt=cpu_skip_cnt + cpu_cnt * instances,
            cpu_cnt=cpu_cnt * instances,
        )
        logger.debug(f"{self._s_affinity=}")
        logger.debug(f"{self._c_affinity=}")
        # Local processed server affinity.
        aff_split = tuple(map(int, self._s_affinity.split("-")))
        if len(aff_split) == 1:
            aff_first, aff_last = aff_split, aff_split
        elif len(aff_split) == 2:
            aff_first, aff_last = aff_split
        else:
            raise RuntimeError(f"Unsplittable {self._s_affinity=}")
        aff_list = list(range(aff_first, aff_last + 1))
        # TODO: Turn the block above into a helper function in CpuUtils.
        for i in range(0, instances):
            cmd = IPerf3Server.iperf3_cmdline(
                namespace=namespace, port=5201 + i, affinity=aff_list[i]
            )
            exec_cmd_no_error(
                node, cmd, sudo=True, message="Failed to start iPerf3 server!"
            )

    @staticmethod
    def is_iperf_running(node):
        """Check if iPerf3 is running using pgrep.

        :param node: Topology node running iPerf3.
        :type node: dict
        :returns: True if iPerf3 is running otherwise False.
        :rtype: bool
        """
        ret, _, _ = exec_cmd(node, "pgrep iperf3", sudo=True)
        return bool(int(ret) == 0)

    @staticmethod
    def teardown_iperf(node):
        """iPerf3 teardown.

        :param node: Topology node running iPerf3.
        :type node: dict
        """
        pidfile = "/tmp/iperf3_server.pid"
        logfile = "/tmp/iperf3.log"

        exec_cmd_no_error(
            node,
            f"sh -c 'if [ -f {pidfile} ]; then "
            f"pkill iperf3; "
            f"cat {logfile}; "
            f"rm {logfile}; "
            f"fi'",
            sudo=True,
            message="iPerf3 kill failed!",
        )

    def iperf_client_start_remote_exec(
        self,
        node,
        duration,
        rate,
        frame_size,
        async_call=False,
        traffic_directions=1,
        namespace=None,
        udp=False,
        host=None,
        bind=None,
        affinity=None,
    ):
        """Execute iPerf3 client script on remote node over ssh to start running
        traffic.

        :param node: Topology node running iPerf3.
        :param duration: Time expressed in seconds for how long to send traffic.
        :param rate: Traffic rate.
        :param frame_size: L2 frame size to send (without padding and IPG).
        :param async_call: If enabled then don't wait for all incoming traffic.
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
        :type traffic_directions: int
        :type namespace: str
        :type udp: bool
        :type host: str
        :type bind: str
        :type affinity: str
        :returns: List of iPerf3 PIDs. FIXME
        :rtype: list FIXME
        """
        if not isinstance(duration, (float, int)):
            duration = float(duration)
        if not affinity:
            affinity = self._c_affinity

        kwargs = dict()
        if namespace:
            kwargs["namespace"] = namespace
        kwargs["host"] = host
        kwargs["bind"] = bind
        kwargs["udp"] = udp
        if affinity:
            kwargs["affinity"] = affinity
        kwargs["duration"] = duration
        kwargs["rate"] = rate
        kwargs["frame_size"] = frame_size
        kwargs["traffic_directions"] = traffic_directions
        kwargs["async_call"] = async_call

        cmd = IPerf3Client.iperf3_cmdline(**kwargs)

        stdout, _ = exec_cmd_no_error(
            node,
            cmd,
            timeout=duration + 3,
            message="iPerf3 runtime error!",
        )

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
                node, f"kill {pid}", sudo=True, message="Kill iPerf3 failed!"
            )


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
        if namespace := kwargs["namespace"]:
            cmd.add(f"ip netns exec {namespace}")
        cmd.add("iperf3")

        cmd_options = OptionString(prefix="--")
        # Run iPerf in server mode. (This will only allow one iperf connection
        # at a time)
        cmd_options.add("server")

        # Run the server in background as a daemon.
        cmd_options.add_if_from_dict("daemon", "daemon", kwargs, True)

        # Write a file with the process ID, most useful when running as a
        # daemon.
        cmd_options.add_with_value_from_dict(
            "pidfile", "pidfile", kwargs, "/tmp/iperf3_server.pid"
        )

        # Send output to a log file.
        cmd_options.add_with_value_from_dict(
            "logfile", "logfile", kwargs, "/tmp/iperf3.log"
        )

        # The server port for the server to listen on and the client to
        # connect to. This should be the same in both client and server.
        # Default is 5201.
        cmd_options.add_with_value_from_dict("port", "port", kwargs, 5201)

        # Set the CPU affinity, if possible (Linux and FreeBSD only).
        cmd_options.add_with_value_from_dict("affinity", "affinity", kwargs)

        # Output in JSON format.
        cmd_options.add_if_from_dict("json", "json", kwargs, True)

        # Give more detailed output.
        cmd_options.add_if_from_dict("verbose", "verbose", kwargs, True)

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
        cmd.add("python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/resources/tools/iperf"
        cmd.add(f"'{dirname}/iperf_client.py'")

        cmd_options = OptionString(prefix="--")
        # Namespace to execute iPerf3 client on.
        cmd_options.add_with_value_from_dict("namespace", "namespace", kwargs)

        # Client connecting to an iPerf3 server running on host.
        cmd_options.add_with_value_from_dict("host", "host", kwargs)

        # Client bind IP address.
        cmd_options.add_with_value_from_dict("bind", "bind", kwargs)

        # Use UDP rather than TCP.
        cmd_options.add_if_from_dict("udp", "udp", kwargs, False)

        # Set the CPU affinity, if possible.
        cmd_options.add_with_value_from_dict("affinity", "affinity", kwargs)

        # Time expressed in seconds for how long to send traffic.
        cmd_options.add_with_value_from_dict("duration", "duration", kwargs)

        # Send bi- (2) or uni- (1) directional traffic.
        cmd_options.add_with_value_from_dict(
            "traffic_directions", "traffic_directions", kwargs, 1
        )

        # L2 frame size to send (without padding and IPG).
        cmd_options.add_with_value_from_dict("frame_size", "frame_size", kwargs)

        # Traffic rate expressed with units.
        cmd_options.add_with_value_from_dict("rate", "rate", kwargs)

        # If enabled then don't wait for all incoming traffic.
        cmd_options.add_if_from_dict("async_start", "async_call", kwargs, False)

        # Number of iPerf3 client parallel instances.
        cmd_options.add_with_value_from_dict(
            "instances", "instances", kwargs, 1
        )

        # Number of iPerf3 client parallel flows.
        cmd_options.add_with_value_from_dict("parallel", "parallel", kwargs, 8)

        return cmd.extend(cmd_options)
