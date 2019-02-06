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

from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.ssh import exec_cmd_no_error, scp_node
from resources.libraries.python.topology import NodeType

__all__ = ["CoreDumpUtil"]

KERNEL_CORE_PATTERN = '/tmp/%p-%u-%g-%s-%t-%h-%e.core'

class CoreDumpUtil(object):
    """Class contains methods for processing core dumps."""

    def __init__(self, nodes):
        """Initialize CoreDumpUtil class.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        self.core_armor = False
        self.linux_setup_corekeeper_on_all_duts(nodes)

    @staticmethod
    def linux_get_pid_limit(node, pid):
        """Get process resource limits.

        :param node: Node in the topology.
        :param pid: Process ID.
        :type node: dict
        :type pid: int
        """
        command = 'prlimit --pid={pid}'.format(pid=pid)

        message = 'Node {host} failed to run {command}'.\
            format(host=node['host'], command=command)

        exec_cmd_no_error(node, command, sudo=True, message=message)

    @staticmethod
    def linux_setup_corekeeper(node):
        """Setup core dumps system wide on node.

        :param node: Node in the topology.
        :type node: dict
        """
        # Any binary which normally would not be dumped is dumped anyway, but
        # only if the "core_pattern" kernel sysctl is set to either a pipe
        # handler or a fully qualified path. (For more details on this
        # limitation, see CVE-2006-2451.) This mode is appropriate when
        # administrators are attempting to debug problems in a normal
        # environment, and either have a core dump pipe handler that knows to
        # treat privileged core dumps with care, or specific directory defined
        # for catching core dumps. If a core dump happens without a pipe
        # handler or fully qualifid path, a message will be emitted to syslog
        # warning about the lack of a correct setting.
        CoreDumpUtil.linux_set_sysctl(node, 'fs.suid_dumpable', 2)

        # Specify a core dumpfile pattern name (for the output filename).
        # %p    pid
        # %u    uid (in initial user namespace)
        # %g    gid (in initial user namespace)
        # %s    signal number
        # %t    UNIX time of dump
        # %h    hostname
        # %e    executable filename (may be shortened)
        CoreDumpUtil.linux_set_sysctl(node, 'kernel.core_pattern',
                                      KERNEL_CORE_PATTERN)

    @staticmethod
    def linux_setup_corekeeper_on_all_duts(nodes):
        """Setup core dumps system wide on all DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                CoreDumpUtil.linux_setup_corekeeper(node)

    def linux_set_pid_limit(self, node, resource, limit, pid):
        """Set process resource limits.

        :param node: Node in the topology.
        :param resource: Resource to set limits.
        :param limit: Limit value.
        :param pid: Process ID.
        :type node: dict
        :type resource: str
        :type limit: str
        :type pid: int
        """
        command = 'prlimit --{resource}={limit} --pid={pid}'.format(
            resource=resource, limit=limit, pid=pid)

        message = 'Node {host} failed to run {command}'.\
            format(host=node['host'], command=command)

        exec_cmd_no_error(node, command, sudo=True, message=message)

        self.core_armor = True

    @staticmethod
    def linux_set_sysctl(node, key, value):
        """Set sysctl key to specific value.

        :param node: Node in the topology.
        :param key: Key that will be set.
        :param value: Value to set.
        :type node: dict
        :type key: str
        :type value: str
        """
        command = 'sysctl -w {key}={value}'.format(key=key, value=value)

        message = 'Node {host} failed to run {command}'.\
            format(host=node['host'], command=command)

        exec_cmd_no_error(node, command, sudo=True, message=message)

    @staticmethod
    def linux_enable_coredump_vpp(node):
        """Enable coredump for all VPP PIDs by setting no core limits.

        :param node: Node in the topology.
        :type node: dict
        """
        pid = DUTSetup.get_vpp_pid(node)
        if isinstance(pid, list):
            for p in pid:
                CoreDumpUtil.linux_set_pid_limit(node, 'core', 'unlimited', p)
                CoreDumpUtil.linux_get_pid_limit(node, p)
        else:
            CoreDumpUtil.linux_set_pid_limit(node, 'core', 'unlimited', pid)
            CoreDumpUtil.linux_get_pid_limit(node, pid)

    @staticmethod
    def linux_enable_coredump_vpp_on_all_duts(nodes):
        """Enable coredump for all VPP PIDs by setting no core limits on all
        DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                CoreDumpUtil.linux_enable_coredump_vpp(node)

    @staticmethod
    def linux_compress_core_files(node):
        """Compress all core files into separate packed files and removes the
        original files.

        :param node: Node in the topology.
        :type node: dict
        """
        command = ('sh -c "cd /tmp; for f in *.core; do '
                   'tar c *.core | '
                   'lzop -1 | '
                   'lrzip -n -T -p 1 -w 5 | '
                   'xz -9e > $f.tar.lzo.lrz.xz; '
                   'done; rm *.core"')

        message = 'Node {host} failed to run {command}'.\
            format(host=node['host'], command=command)

        exec_cmd_no_error(node, command, timeout=3600, sudo=True,
                          message=message)

    @staticmethod
    def linux_compress_core_files_on_all_duts(nodes):
        """Compress all core files into separate packed files and removes the
        original files on all DUTs.

        :param nodes: Nodes in the topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                CoreDumpUtil.linux_compress_core_files(node)
