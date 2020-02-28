<<<<<<< HEAD   (d7aec8 Backport CRC checking from master)
# Copyright (c) 2018 Cisco and/or its affiliates.
=======
# Copyright (c) 2020 Cisco and/or its affiliates.
>>>>>>> CHANGE (6daa2d Make RXQs/TXQs configurable)
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

<<<<<<< HEAD   (d7aec8 Backport CRC checking from master)
from resources.libraries.python.ssh import SSH
from resources.libraries.python.Constants import Constants
from resources.libraries.python.topology import NodeType, Topology
=======
from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType
>>>>>>> CHANGE (6daa2d Make RXQs/TXQs configurable)


class L2fwdTest(object):
    """Setup the DPDK for l2fwd performance test."""

    @staticmethod
<<<<<<< HEAD   (d7aec8 Backport CRC checking from master)
    def start_the_l2fwd_test(dut_node, cpu_cores, nb_cores, queue_nums,
                             jumbo_frames):
=======
    def start_the_l2fwd_test(
            node, cpu_cores, nb_cores, queue_nums, jumbo_frames,
            rxq_size=1024, txq_size=1024):
>>>>>>> CHANGE (6daa2d Make RXQs/TXQs configurable)
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
<<<<<<< HEAD   (d7aec8 Backport CRC checking from master)
        if dut_node['type'] == NodeType.DUT:
            ssh = SSH()
            ssh.connect(dut_node)

            arch = Topology.get_node_arch(dut_node)
            jumbo = 'yes' if jumbo_frames else 'no'
            cmd = '{fwdir}/tests/dpdk/dpdk_scripts/run_l2fwd.sh {cpu_cores} ' \
                  '{nb_cores} {queues} {jumbo} {arch}'.\
                  format(fwdir=Constants.REMOTE_FW_DIR, cpu_cores=cpu_cores,
                         nb_cores=nb_cores, queues=queue_nums,
                         jumbo=jumbo, arch=arch)
=======
        if node[u"type"] == NodeType.DUT:
            jumbo = u"yes" if jumbo_frames else u"no"
            command = f"{Constants.REMOTE_FW_DIR}/tests/dpdk/dpdk_scripts" \
                f"/run_l2fwd.sh {cpu_cores} {nb_cores} {queue_nums} {jumbo} " \
                f"{rxq_size} {txq_size}"
>>>>>>> CHANGE (6daa2d Make RXQs/TXQs configurable)

<<<<<<< HEAD   (d7aec8 Backport CRC checking from master)
            ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=600)
            if ret_code != 0:
                raise RuntimeError('Failed to execute l2fwd test at node '
                                   '{name}'.format(name=dut_node['host']))
=======
            message = f"Failed to execute l2fwd test at node {node['host']}"

            exec_cmd_no_error(node, command, timeout=1800, message=message)
>>>>>>> CHANGE (6daa2d Make RXQs/TXQs configurable)
