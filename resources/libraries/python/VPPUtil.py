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

"""VPP util library"""
from resources.libraries.python.ssh import SSH


class VPPUtil(object):
    """General class for any VPP related methods/functions."""

    @staticmethod
    def show_vpp_settings(node, *additional_cmds):
        """Print default VPP settings. In case others are needed, can be
        accepted as next parameters (each setting one parameter), preferably
        in form of a string.

        :param node: VPP node.
        :param additional_cmds: Additional commands that the vpp should print
         settings for.
        :type node: dict
        :type additional_cmds: tuple
        """
        def_setting_tb_displayed = {
            'IPv6 FIB': 'ip6 fib',
            'IPv4 FIB': 'ip fib',
            'Interface IP': 'int addr',
            'Interfaces': 'int',
            'ARP': 'ip arp',
            'Errors': 'err'
        }

        if additional_cmds:
            for cmd in additional_cmds:
                def_setting_tb_displayed['Custom Setting: {}'.format(cmd)] = cmd
        ssh = SSH()
        ssh.connect(node)
        print("=" * 40)
        for key, value in def_setting_tb_displayed.iteritems():
            (_, stdout, _) = ssh.exec_command_sudo('vppctl sh {}'.format(value))
            print("{} : {} \n".format(key, value))
            print(stdout)
            print("=" * 40)

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
                (ret, stdout, _) = ssh.exec_command_sudo(cmd)
                if ret != 0:
                    raise RuntimeError("Failed to set CFS on PID {0}."\
                        .format(pid))

