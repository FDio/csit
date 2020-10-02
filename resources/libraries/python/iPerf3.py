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

"""iPerf3 utilities library."""

import json

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.Namespaces import Namespaces
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error


class iPerf3:
    """iPerf3 traffic generator utilities."""

    @staticmethod
    def initialize_iperf_server(
            node, if1_pci, if2_pci, interface, bind, bind_gw, bind_mask,
            namespace=None, flows=1, cpu_skip_cnt=0):
        """iPerf3 initialization.

        :param node: Topology node running iPerf3 server.
        :param if1_pci: First TG's interface (To compute numa location).
        :param if2_pci: Second TG's interface (To compute numa location).
        :param interface: Name of TG bind interface.
        :param bind: Bind to host, one of node's addresses.
        :param bind_gw: Bind gateway (default route).
        :param bind_mask: Bind address mask.
        :param namespace: Name of TG namespace to execute.
        :param flows: Number of flows.
        :param cpu_skip_cnt: Amount of CPU cores to skip.
        :type node: dict
        :type if1_pci: str
        :type if2_pci: str
        :type interface: str
        :type bind: str
        :type bind_gw: str
        :type bind_mask: str
        :type namespace: str
        :type flows: int
        :type cpu_skip_cnt: int
        """
        # Compute affinity for iPerf server.
        s_affinity = CpuUtils.get_affinity_iperf(
            node, if1_pci, if2_pci, cpu_skip_cnt=cpu_skip_cnt, tg_mtc=1
        )
        c_affinity = CpuUtils.get_affinity_iperf(
            node, if1_pci, if2_pci, cpu_skip_cnt=cpu_skip_cnt + 1, tg_mtc=1
        )

        config = {
            u"server": {
                u"bind": bind,
                u"bind_mask": bind_mask,
                u"interface": interface,
                u"namespace": namespace,
                u"affinity": s_affinity,
                u"port": 5201
            },
            u"client": {
                u"bind": bind,
                u"bind_mask": bind_mask,
                u"affinity": c_affinity,
                u"port": 5201
            }
        }
        exec_cmd_no_error(
            node,
            f"sh -c 'cat << EOF > /etc/iperf_cfg.json\n"
            f"{json.dumps(config, sort_keys=True, indent=4)}\n"
            f"EOF'",
            sudo=True, message=u"iPerf3 config generation!"
        )

        iPerf3.start_iperf_server(
            node, bind=bind, bind_gw=bind_gw, bind_mask=bind_mask,
            interface=interface, namespace=namespace, port=5201,
            affinity=s_affinity)

    @staticmethod
    def start_iperf_server(
            node, bind, bind_gw, bind_mask, interface, namespace=None,
            port=5201, affinity=0):
        """Start iPerf3 server as a deamon.

        :param node: Topology node running iPerf3 server.
        :param bind: Bind to host, one of node's addresses.
        :param bind_gw: Bind gateway (default route).
        :param bind_mask: Bind address mask.
        :param interface: Name of TG bing interface.
        :param namespace: Name of TG namespace to execute.
        :param port: The server port for the server to listen on.
        :param affinity: iPerf3 server affinity.
        :type node: dict
        :type bind: str
        :type bind_gw: str
        :type bind_mask: str
        :type interface: str
        :type namespace: str
        :type port: int
        :type affinity: str
        """
        if iPerf3.is_iperf_running(node):
            iPerf3.teardown_iperf(node)

        IPUtil.set_linux_interface_ip(
            node, interface=interface, ip_addr=bind, prefix=bind_mask,
            namespace=namespace)
        IPUtil.set_linux_interface_up(
            node, interface=interface, namespace=namespace)
        Namespaces.add_default_route_to_namespace(
            node, namespace=namespace, default_route=bind_gw)

        cmd_options = OptionString(prefix=u"--")
        # Run iPerf in server mode. (This will only allow one iperf connection
        # at a time)
        cmd_options.add(u"server")
        # Run the server in background as a daemon.
        cmd_options.add(u"daemon")
        # Write a file with the process ID, most useful when running as a
        # daemon.
        cmd_options.add_with_value(u"pidfile", f"/tmp/iperf3_server.pid")
        # Send output to a log file.
        cmd_options.add_with_value(u"logfile", f"/tmp/iperf3.log")
        # The server port for the server to listen on and the client to
        # connect to. This should be the same in both client and server.
        # Default is 5201."
        cmd_options.add_with_value(u"port", port)
        # Set the CPU affinity, if possible (Linux and FreeBSD only).
        cmd_options.add_with_value(u"affinity", affinity)
        # Output in JSON format.
        cmd_options.add(u"json")
        # Give more detailed output.
        cmd_options.add(u"verbose")
        cmd = OptionString()
        if namespace:
            cmd.add(f"ip netns exec {namespace}")
        cmd.add(f"iperf3")
        cmd.extend(cmd_options)
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
            f"pkill -F {pidfile}; "
            f"cat {logfile}; "
            f"rm {logfile}; "
            f"fi'",
            sudo=True,
            message=u"iPerf3 kill failed!"
        )

    @staticmethod
    def iperf_client_start_remote_exec(
            node, duration, rate, frame_size, async_call=False, warmup_time=5.0,
            traffic_directions=1, namespace=None, udp=False):
        """Execute iPerf3 client script on remote node over ssh to start running
        traffic.

        :param duration: Time expressed in seconds for how long to send traffic.
        :param rate: Traffic rate expressed with units (pps, %)
        :param frame_size: L2 frame size to send (without padding and IPG).
        :param async_call: If enabled then don't wait for all incoming traffic.
        :param warmup_time: Warmup time period.
        :param traffic_directions: Traffic is bi- (2) or uni- (1) directional.
            Default: 1
        :param namespace: Namespace to execute iPerf3 client on.
        :param udp: UDP traffic.
        :type duration: float
        :type rate: str
        :type frame_size: str
        :type async_call: bool
        :type warmup_time: float
        :type traffic_directions: int
        :type namespace: str
        :type udp: bool
        :returns: List of iPerf3 PIDs.
        :rtype: list
        """
        if not isinstance(duration, (float, int)):
            duration = float(duration)
        if not isinstance(warmup_time, (float, int)):
            warmup_time = float(warmup_time)

        cmd_options = OptionString(prefix=u"--")
        cmd_options.add_with_value(u"port_netns", namespace)
        cmd_options.add_with_value(u"duration", duration)
        cmd_options.add_with_value(u"frame_size", frame_size)
        cmd_options.add_with_value(u"rate", rate)
        cmd_options.add_with_value(u"warmup_time", warmup_time)
        cmd_options.add_with_value(u"traffic_directions", traffic_directions)
        cmd_options.add_if(u"async_start", async_call)
        cmd_options.add_if(u"udp", udp)

        cmd = OptionString()
        cmd.add(u"python3")
        dirname = f"{Constants.REMOTE_FW_DIR}/resources/tools/iperf"
        cmd.add(f"'{dirname}/iperf_client.py'")
        cmd.extend(cmd_options)

        stdout, _ = exec_cmd_no_error(
            node, cmd, timeout=int(duration) + 30,
            message=u"iPerf3 runtime error!"
        )

        if async_call:
            return stdout.split()
        else:
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
                node, f"kill {pid}", sudo=True, message=u"Kill iPerf3 failed!"
            )