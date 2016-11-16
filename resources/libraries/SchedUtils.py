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


class SchedUtil(object):
    """General class for any linux scheduler related methods/functions."""

    @staticmethod
    def set_vpp_scheduler_policy_rr(node):
        """Set CFS scheduler policy to SCHED_RR with priority 1 on all vpp
        worker threads.

        :param node: VPP node.
        :type node: dict
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "cat /proc/`pidof vpp`/task/*/stat | grep -i vpp_wk"\
            " | awk '{print $1}'"

        (ret, stdout, _) = ssh.exec_command_sudo(cmd)
        if ret != 0:
            raise RuntimeError("Failed to get VPP worker threads.")

        for pid in stdout.split("\n"):
            if len(pid) > 0:
                cmd = "chrt -r -p 1 {0}".format(pid)
                (ret, _, _) = ssh.exec_command_sudo(cmd)
                if ret != 0:
                    raise RuntimeError("Failed to set CFS on PID {0}."\
                        .format(pid))

