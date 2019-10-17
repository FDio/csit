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

"""Linux scheduler util library"""

from resources.libraries.python.ssh import exec_cmd_no_error

__all__ = [u"SchedUtils"]


class SchedUtils:
    """General class for any linux scheduler related methods/functions."""

    @staticmethod
    def set_vpp_scheduling_rr(node):
        """Set real-time scheduling attributes of VPP worker threads to
        SCHED_RR with priority 1.

        :param node: DUT node with running VPP.
        :type node: dict
        :raises RuntimeError: Failed to retrieve PID for VPP worker threads.
        """
        cmd = (
            u"grep -i vpp_wk /proc/$(pidof vpp)/task/*/stat "
            u"| grep -o '^[0-9]*'"
        )
        message = u"Failed to retrieve PIDs for VPP worker threads."
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, retries=2, message=message)
        for pid in stdout.split():
            SchedUtils.set_proc_scheduling_rr(node, int(pid))

    @staticmethod
    def set_proc_scheduling_rr(node, pid, priority=1):
        """Set real-time scheduling of a process to SCHED_RR with priority for
        specified PID.

        :param node: Node where to apply scheduling changes.
        :param pid: Process ID.
        :param priority: Realtime priority in range 1-99. Default is 1.
        :type node: dict
        :type pid: int
        :type priority: int
        :raises ValueError: Parameters out of allowed ranges.
        :raises RuntimeError: Failed to set policy for PID.
        """
        if pid < 1:
            raise ValueError("SCHED_RR: PID must be at least 1.")
        if not 1 <= priority <= 99:
            raise ValueError(u"SCHED_RR: Priority must be in range 1-99.")

        cmd = f"chrt -r -p {priority} {pid}"
        message = f"SCHED_RR: Failed to set policy for PID {pid}."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

    @staticmethod
    def set_proc_scheduling_other(node, pid):
        """Set normal scheduling of a process to SCHED_OTHER for specified PID.

        :param node: Node where to apply scheduling changes.
        :param pid: Process ID.
        :type node: dict
        :type pid: int
        :raises ValueError: Parameters out of allowed ranges.
        :raises RuntimeError: Failed to set policy for PID.
        """
        if pid < 1:
            raise ValueError("SCHED_OTHER: PID must be at least 1.")
        cmd = f"chrt -o -p 0 {pid}"
        message = f"SCHED_OTHER: Failed to set policy for PID {pid}."
        exec_cmd_no_error(node, cmd, sudo=True, message=message)
