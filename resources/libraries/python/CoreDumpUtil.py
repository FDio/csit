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

from uuid import uuid1 as uid_gen

from resources.libraries.python.constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.LimitUtil import LimitUtil
from resources.libraries.python.SysctlUtil import SysctlUtil
from resources.libraries.python.ssh import exec_cmd_no_error, scp_node
from resources.libraries.python.topology import NodeType

__all__ = ["CoreDumpUtil"]


class CoreDumpUtil(object):
    """Class contains methods for processing core dumps."""

    # Use one instance of class for all tests in test suite
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        """Initialize CoreDumpUtil class."""
        self._dump_initialized = False
        self._dump_enabled = True

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
            # pipe handler or fully qualifid path, a message will be emitted to
            # syslog warning about the lack of a correct setting.
            SysctlUtil.set_sysctl_value(node, 'fs.suid_dumpable', 2)

            # Specify a core dumpfile pattern name (for the output filename).
            # %p    pid
            # %u    uid (in initial user namespace)
            # %g    gid (in initial user namespace)
            # %s    signal number
            # %t    UNIX time of dump
            # %h    hostname
            # %e    executable filename (may be shortened)
            SysctlUtil.set_sysctl_value(node, 'kernel.core_pattern',
                                        Constants.KERNEL_CORE_PATTERN)

        self._dump_initialized = True

    @staticmethod
    def enable_coredump_limit(node, pid):
        """Enable coredump for PID(s) by setting no core limits.

        :param node: Node in the topology.
        :param pid: Process ID(s) to set core dump limit to unlimited.
        :type node: dict
        :type pid: list or int
        """
        if isinstance(pid, list):
            for p in pid:
                LimitUtil.set_pid_limit(node, p, 'core', 'unlimited')
                LimitUtil.get_pid_limit(node, p)
        else:
            LimitUtil.set_pid_limit(node, pid, 'core', 'unlimited')
            LimitUtil.get_pid_limit(node, pid)

    def enable_coredump_limit_vpp_on_all_duts(self, nodes):
        """Enable coredump for all VPP PIDs by setting no core limits on all
        DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT \
                and self._dump_initialized and self._dump_enabled:
                vpp_pid = DUTSetup.get_vpp_pid(node)
                self.enable_coredump_limit(node, vpp_pid)

    def get_core_files_on_all_nodes(self, nodes):
        """Compress all core files into single file and remove the original
        core files on all nodes.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            uuid = '{uuid}.tar.lzo.lrz.xz'.format(uuid=uid_gen())

            command = ('sudo tar c {dir}/*.core | '
                       'lzop -1 | '
                       'lrzip -n -T -p 1 -w 5 | '
                       'xz -9e > {dir}/{uuid}; '
                       'sudo rm -f {dir}/*.core || true'
                       .format(dir=Constants.CORE_DUMP_DIR, uuid=uuid))
            exec_cmd_no_error(node, command, timeout=3600)

            local_path = 'archive/{uuid}'.format(uuid=uuid)
            remote_path = '{dir}/{uuid}'.format(dir=Constants.CORE_DUMP_DIR,
                                                uuid=uuid)
            try:
                scp_node(node, local_path, remote_path, get=True, timeout=3600)
                self._dump_enabled = False
            except RuntimeError:
                pass

            command = 'rm -f {dir}/{uuid} || true'\
                       .format(dir=Constants.CORE_DUMP_DIR, uuid=uuid)
            exec_cmd_no_error(node, command, sudo=True)
