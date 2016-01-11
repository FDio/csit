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

"""Common IP utilities library."""

from ssh import SSH
from constants import Constants


class IPUtil(object):
    """Common IP utilities"""

    def __init__(self):
        pass

    @staticmethod
    def vpp_ip_probe(node, interface, addr):
        """Run ip probe on VPP node.

           Args:
               node (Dict): VPP node.
               interface (str): Interface name
               addr (str): IPv4/IPv6 address
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "{c}".format(c=Constants.VAT_BIN_NAME)
        cmd_input = 'exec ip probe {dev} {ip}'.format(dev=interface, ip=addr)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, cmd_input)
        if int(ret_code) != 0:
            raise Exception('VPP ip probe {dev} {ip} failed on {h}'.format(
                dev=interface, ip=addr, h=node['host']))
