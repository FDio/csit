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

from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.Namespaces import Namespaces
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error


class iPerf3:
    """iPerf3 server utilities."""

    @staticmethod
    def initialize_iperf_server(
            node, bind, bind_mask, interface, namespace=None, port=5201,
            flows=1):
        """iPerf3 initialization.

        :param node: Topology node.
        :type node: dict
        """
        iPerf3.start_iperf_server(
            node, bind=bind, bind_mask=bind_mask, interface=interface,
            namespace=namespace, port=port, flows=flows)

    @staticmethod
    def start_iperf_server(
            node, bind, bind_mask, interface, namespace=None, port=5201,
            flows=1):
        """Start iPerf3 server as a deamon.

        :param node: Topology node running iPerf3 server.
        :param bind: Bind to host, one of node's addresses.
        :param bind_mask: Bind address mask.
        :param interface: Bind interface.
        :param namespace: Namespace to execute.
        :param port: The server port for the server to listen on.
        :param flows: Number of iPerf3 flows.
        :type node: dict
        :type bind: str
        :type bind_mask: str
        :type interface: str
        :type namespace: str
        :type port: int
        :type flows: int
        """
        if iPerf3.is_iperf_running(node):
            iPerf3.teardown_iperf(node)

        IPUtil.set_linux_interface_ip(
            node, interface=interface, ip_addr=bind, prefix=bind_mask,
            namespace=namespace)
        IPUtil.set_linux_interface_up(
            node, interface=interface, namespace=namespace)
        Namespaces.add_default_route_to_namespace(
            node, namespace=namespace, default_route=bind)

        cmd_options = OptionString(prefix=u"--")
        # Run iPerf in server mode. (This will only allow one iperf connection
        # at a time)
        cmd_options.add(u"server")
        # Run the server in background as a daemon.
        cmd_options.add(u"daemon")
        # Write a file with the process ID, most useful when running as a
        # daemon.
        cmd_options.add_with_value(u"pidfile", f"/tmp/iperf3_server.pid")
        # The server port for the server to listen on and the client to
        # connect to. This should be the same in both client and server.
        # Default is 5201."
        cmd_options.add_with_value(u"port", port)
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

        :param node: Topology node.
        :type node: dict
        :returns: True if iPerf3 is running otherwise False.
        :rtype: bool
        """
        ret, _, _ = exec_cmd(node, u"pgrep iperf3", sudo=True)
        return bool(int(ret) == 0)

    @staticmethod
    def teardown_iperf(node):
        """iPerf3 teardown.

        :param node: Topology node running iPerf3 server.
        :type node: dict
        """
        exec_cmd_no_error(
            node,
            u"sh -c \"if pgrep iperf3; then sudo pkill iperf3; fi\"",
            sudo=False,
            message=u"iPerf3 kill failed!"
        )
