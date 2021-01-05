# Copyright (c) 2020 Intel and/or its affiliates.
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

"""NgInx util library.
"""

from resources.libraries.python.topology import NodeType
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error


def run_nginx(node, mode, rps_cps, core_num, tls_tcp):
    """ Run nginx.

    :param node: generator node.
    :param mode: vcl nginx or ldp nginx.
    :param rps_cps: test case rps or cps.
    :param core_num: nginx work processes number.
    :param tls_tcp: TLS or TCP.
    :type node: dict
    :type mode: string
    :type rps_cps: string
    :type core_num: int
    :type tls_tcp: int
    :returns: nothing.
    :raises: RuntimeError if node type is not a DUT.
    """
    if node['type'] != NodeType.DUT:
        raise RuntimeError('Node type is not a DUT.')

    command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_ENTRY}" \
              f"/nginx_utils.sh {mode} {rps_cps} {core_num} {tls_tcp}"
    exec_cmd_no_error(
        node, command, timeout=180,
        message=u"Run the nginx failed!"
    )


def kill_nginx(node):
    """Kill all ginx.

    :param node: generator node.
    :type node: dict
    :returns: nothing.
    :raises: RuntimeError if node type is not a DUT.
    """

    if node['type'] != NodeType.DUT:
        raise RuntimeError('Node type is not a DUT.')

    command = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_LIB_ENTRY}" \
              f"/nginx_utils.sh kill"
    exec_cmd_no_error(
        node, command, timeout=180,
        message=u"Kill the nginx failed!"
    )
