# Copyright (c) 2016 Cisco and/or its affiliates.
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
from resources.libraries.python.ssh import SSH


__all__ = ["SchedUtils"]

class SchedUtils(object):
    """General class for any linux scheduler related methods/functions."""

    @staticmethod
    def set_vpp_scheduling_rr(node):
        """Set real-time scheduling attributes of VPP worker threads to
        SCHED_RR with priority 1.

        :param node: DUT node with running VPP.
        :type node: dict
        :raises RuntimeError: Failed to retrieve PID for VPP worker threads.
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "cat /proc/`/usr/sbin/pidof vpp`/task/*/stat | grep -i vpp_wk"\
            " | awk '{print $1}'"

        for _ in range(3):
            (ret, out, _) = ssh.exec_command_sudo(cmd)
            if ret == 0:
                try:
                    if not out:
                        raise ValueError
                except ValueError:
                    print 'Reading VPP worker thread PID failed.'
                else:
                    for pid in out.split("\n"):
                        if len(pid) > 0 and pid[0] != "#":
                            SchedUtils.set_proc_scheduling_rr(node, int(pid))
                    break
        else:
            raise RuntimeError('Failed to retrieve PID for VPP worker threads.')

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
        ssh = SSH()
        ssh.connect(node)

        if pid < 1:
            raise ValueError("SCHED_RR: PID must be higher then 1.")

        if 1 <= priority <= 99:
            cmd = "chrt -r -p {0} {1}".format(priority, pid)
            (ret, _, _) = ssh.exec_command_sudo(cmd)
            if ret != 0:
                raise RuntimeError("SCHED_RR: Failed to set policy "\
                    "for PID {0}.".format(pid))
        else:
            raise ValueError("SCHED_RR: Priority must be in range 1-99.")

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
        ssh = SSH()
        ssh.connect(node)

        if pid < 1:
            raise ValueError("SCHED_OTHER: PID must be higher then 1.")

        cmd = "chrt -o -p 0 {1}".format(pid)
        (ret, _, _) = ssh.exec_command_sudo(cmd)
        if ret != 0:
            raise RuntimeError("SCHED_OTHER: Failed to set policy "\
                    "for PID {0}.".format(pid))
