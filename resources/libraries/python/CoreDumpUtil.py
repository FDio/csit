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

"""Core dump library."""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.LimitUtil import LimitUtil
from resources.libraries.python.SysctlUtil import SysctlUtil
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType

__all__ = [u"CoreDumpUtil"]


class CoreDumpUtil:
    """Class contains methods for processing core dumps."""

    # Use one instance of class for all tests. If the functionality should
    # be enabled per suite or per test case, change the scope to "TEST SUITE" or
    # "TEST CASE" respectively.
    ROBOT_LIBRARY_SCOPE = u"GLOBAL"

    def __init__(self):
        """Initialize CoreDumpUtil class."""
        # Corekeeper is configured.
        self._corekeeper_configured = False
        # Enable setting core limit for process. This can be used to prevent
        # library to further set the core limit for unwanted behavior.
        self._core_limit_enabled = True

    def set_core_limit_enabled(self):
        """Enable setting of core limit for PID."""
        self._core_limit_enabled = True

    def set_core_limit_disabled(self):
        """Disable setting of core limit for PID."""
        self._core_limit_enabled = False

    def is_core_limit_enabled(self):
        """Check if core limit is set for process.

        :returns: True if core limit is set for process.
        :rtype: bool
        """
        return self._corekeeper_configured and self._core_limit_enabled

    def setup_corekeeper_on_all_nodes(self, nodes):
        """Setup core dumps system wide on all nodes.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            # Any binary which normally would not be dumped is dumped anyway,
            # but only if the "core_pattern" kernel sysctl is set to either a
            # pipe handler or a fully qualified path. (For more details on this
            # limitation, see CVE-2006-2451.) This mode is appropriate when
            # administrators are attempting to debug problems in a normal
            # environment, and either have a core dump pipe handler that knows
            # to treat privileged core dumps with care, or specific directory
            # defined for catching core dumps. If a core dump happens without a
            # pipe handler or fully qualified path, a message will be emitted to
            # syslog warning about the lack of a correct setting.
            SysctlUtil.set_sysctl_value(node, u"fs.suid_dumpable", 2)

            # Specify a core dumpfile pattern name (for the output filename).
            # %p    pid
            # %u    uid (in initial user namespace)
            # %g    gid (in initial user namespace)
            # %s    signal number
            # %t    UNIX time of dump
            # %h    hostname
            # %e    executable filename (may be shortened)
            SysctlUtil.set_sysctl_value(
                node, u"kernel.core_pattern", Constants.KERNEL_CORE_PATTERN
            )

        self._corekeeper_configured = True

    @staticmethod
    def enable_coredump_limit(node, pid):
        """Enable coredump for PID(s) by setting no core limits.

        :param node: Node in the topology.
        :param pid: Process ID(s) to set core dump limit to unlimited.
        :type node: dict
        :type pid: list or int
        """
        if isinstance(pid, list):
            for item in pid:
                LimitUtil.set_pid_limit(node, item, u"core", u"unlimited")
                LimitUtil.get_pid_limit(node, item)
        else:
            LimitUtil.set_pid_limit(node, pid, u"core", u"unlimited")
            LimitUtil.get_pid_limit(node, pid)

    def enable_coredump_limit_vpp_on_all_duts(self, nodes):
        """Enable coredump for all VPP PIDs by setting no core limits on all
        DUTs if setting of core limit by this library is enabled.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT and self.is_core_limit_enabled():
                vpp_pid = DUTSetup.get_vpp_pid(node)
                self.enable_coredump_limit(node, vpp_pid)

    def get_core_files_on_all_nodes(self, nodes, disable_on_success=True):
        """Process all core files and remove the original core files on all
        nodes.

        :param nodes: Nodes in the topology.
        :param disable_on_success: If True, disable setting of core limit by
            this instance of library. Default: True
        :type nodes: dict
        :type disable_on_success: bool
        """
        for node in nodes.values():
            command = (
                f"for f in {Constants.CORE_DUMP_DIR}/*.core; do sudo gdb"
                f" /usr/bin/vpp ${{f}} -ex 'source -v {Constants.REMOTE_FW_DIR}"
                f"/resources/tools/scripts/gdb-commands' -ex quit;"
                f" sudo rm -f ${{f}}; done"
            )
            try:
                exec_cmd_no_error(node, command, timeout=3600)
                if disable_on_success:
                    self.set_core_limit_disabled()
            except RuntimeError:
                # If compress was not successful ignore error and skip further
                # processing.
                continue
