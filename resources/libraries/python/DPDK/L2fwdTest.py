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

"""This module implements functionality which sets L2 forwarding for DPDK on
DUT nodes.
"""

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType


class L2fwdTest:
    """Setup the DPDK for l2fwd performance test."""

    @staticmethod
    def start_the_l2fwd_test(
            node, cpu_cores, nb_cores, queue_nums, jumbo_frames,
            rxq_size=1024, txq_size=1024):
        """
        Execute the l2fwd on the DUT node.

        :param node: Will execute the l2fwd on this node.
        :param cpu_cores: The DPDK run cores.
        :param nb_cores: The cores number for the forwarding.
        :param queue_nums: The queues number for the NIC.
        :param jumbo_frames: Indication if the jumbo frames are used (True) or
            not (False).
        :param rxq_size: RXQ size. Default=1024.
        :param txq_size: TXQ size. Default=1024.
        :type node: dict
        :type cpu_cores: str
        :type nb_cores: str
        :type queue_nums: str
        :type jumbo_frames: bool
        :type rxq_size: int
        :type txq_size: int
        :raises RuntimeError: If the script "run_l2fwd.sh" fails.
        """
        if node[u"type"] == NodeType.DUT:
            jumbo = u"yes" if jumbo_frames else u"no"
            command = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/run_l2fwd.sh {cpu_cores} {nb_cores} {queue_nums} {jumbo} " \
                f"{rxq_size} {txq_size}"

            message = f"Failed to execute l2fwd test at node {node['host']}"
            exec_cmd_no_error(node, command, timeout=1800, message=message)
