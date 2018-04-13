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
        for _, value in def_setting_tb_displayed.items():
            ssh.exec_command_sudo('vppctl sh {}'.format(value))

    @staticmethod
    def stop_vpp_service(node):
        """Stop VPP service on the specified node.

        :param node: VPP node.
        :type node: dict
        :raises RuntimeError: If VPP fails to stop.
        """

        ssh = SSH()
        ssh.connect(node)
        cmd = "service vpp stop"
        ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=80)
        if int(ret_code) != 0:
            raise RuntimeError("VPP service did not shut down gracefully.")

    @staticmethod
    def start_vpp_service(node):
        """start VPP service on the specified node.

        :param node: VPP node.
        :type node: dict
        :raises RuntimeError: If VPP fails to start.
        """

        ssh = SSH()
        ssh.connect(node)
        cmd = "service vpp start"
        ret_code, _, _ = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise RuntimeError("VPP service did not start.")
