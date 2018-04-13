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

"""Implementation of keywords for testing Honeycomb performance."""

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as Const
from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError


class Performance(object):
    """Keywords used in Honeycomb performance testing."""

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def configure_netconf_threads(node, threads):
        """Set Honeycomb's Netconf thread count in configuration.

        :param node: Honeycomb node.
        :param threads: Number of threads.
        :type node: dict
        :type threads: int
        :raises HoneycombError: If the operation fails.
        """

        find = "netconf-netty-threads"
        replace = '\\"netconf-netty-threads\\": {0},'.format(threads)

        argument = '"/{0}/c\\ {1}"'.format(find, replace)
        path = "{0}/config/netconf.json".format(Const.REMOTE_HC_DIR)
        command = "sed -i {0} {1}".format(argument, path)

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, stderr) = ssh.exec_command_sudo(command)
        if ret_code != 0:
            raise HoneycombError("Failed to modify configuration on "
                                 "node {0}, {1}".format(node, stderr))

    @staticmethod
    def run_traffic_script_on_dut(node, script, cores, reserved=2,
                                  *args, **kwargs):
        """Copy traffic script over to the specified node and execute with
        the provided arguments.

        :param node: Node in topology.
        :param script: Name of the script to execute.
        :param cores: Number of processor cores to use.
        :param reserved: Number of cores reserved for other tasks. Default is 2,
            one for system tasks and one for VPP main thread.
        :param args: Sequential arguments for the script.
        :param kwargs: Named arguments for the script.
        :type node: dict
        :type script: str
        :type cores: int
        :type reserved: int
        :type args: list
        :type kwargs: dict
        """

        path = "resources/traffic_scripts/honeycomb/{0}".format(script)

        # Assemble arguments for traffic script
        arguments = ""
        for arg in args:
            arguments += "{0} ".format(arg)

        for key, value in kwargs.items():
            arguments += "--{0} {1} ".format(key, value)

        ssh = SSH()
        ssh.connect(node)
        ssh.scp(path, "/tmp")

        # Use alternate scheduler, Ubuntu's default can't load-balance
        # over isolcpus
        scheduler = "chrt -f 99"
        core_afi = "taskset -c {first}-{last}".format(
            first=reserved, last=cores-1)

        cmd = "{scheduler} {affinity} python /tmp/{script} {args}".format(
            scheduler=scheduler,
            affinity=core_afi,
            script=script,
            args=arguments)

        ret_code, stdout, _ = ssh.exec_command_sudo(cmd, timeout=600)

        ssh.exec_command("sudo pkill python ; rm /tmp/{0}".format(script))
        if ret_code != 0:
            raise HoneycombError("Traffic script failed to execute.")
        for line in stdout.splitlines():
            if "Avg. requests" in line:
                return line

    @staticmethod
    def log_core_schedule(node, process):
        """Determine which cores the process' threads are running on.

        :param node: Honeycomb node.
        :param process: Name of the process.
        :type node: dict
        :type process: str
        """

        # Get info on process and all of its children
        cmd1 = """cat /proc/`pidof {0}`/task/*/stat""".format(process)

        # Parse process ID, name and core index
        cmd2 = """awk '{print $1" "$2" "$39}'"""

        cmd = "{0} | {1}".format(cmd1, cmd2)

        ssh = SSH()
        ssh.connect(node)
        ssh.exec_command(cmd)
