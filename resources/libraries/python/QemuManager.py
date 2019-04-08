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

"""QEMU Manager library."""

from collections import OrderedDict

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.QemuUtils import QemuUtils
from resources.libraries.python.topology import NodeType, Topology

__all__ = ["QemuManager"]


def get_affinity_vm(nodes, node, nf_chains=1, nf_nodes=1, nf_chain=1, nf_node=1,
                    cpu_count_int=1, vnf_count_int=1):
    """Get affinity of VM. Result will be used to compute the amount of
    CPUs and also affinity.

    :param node: SUT nodes.
    :param node: DUT node.
    :param nf_chains: Number of NF chains.
    :param nf_nodes: Number of NF nodes in chain.
    :param nf_chain: Chain ID.
    :param nf_node: Node ID.
    :param cpu_count_int: Amount of Dataplane threads of vswitch.
    :param vnf_count_int: Amount of Dataplane threads of vnf.
    :type nodes: dict
    :type node: dict
    :type nf_chains: int
    :type nf_nodes: int
    :type nf_chain: int
    :type nf_node: int
    :type cpu_count_int: int
    :type vnf_count_int: int
    :returns: List of CPUs allocated to VM.
    :rtype: list
    """
    sut_sc = 1
    dut_mc = 1
    dut_dc = cpu_count_int
    skip_cnt = sut_sc + dut_mc + dut_dc
    dtc = vnf_count_int

    interface_list = []
    interface_list.append(
        BuiltIn().get_variable_value('${{{node}_if1}}'.format(node=node)))
    interface_list.append(
        BuiltIn().get_variable_value('${{{node}_if2}}'.format(node=node)))

    cpu_node = Topology.get_interfaces_numa_node(nodes[node], *interface_list)

    nf_cpus = CpuUtils.cpu_slice_of_list_for_nf(
        node=nodes[node], cpu_node=cpu_node, chains=nf_chains,
        nodeness=nf_nodes, chain_id=nf_chain, node_id=nf_node, mtcr=2, dtcr=1,
        dtc=dtc, skip_cnt=skip_cnt)

    return nf_cpus

class QemuManager(object):
    """QEMU lifecycle management class"""

    # Use one instance of class per tests.
    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self, nodes):
        """Init QemuManager object."""
        self.machines = None
        self.machines_affinity = None
        self.nodes = nodes

    def initialize(self):
        """Initialize QemuManager object."""
        self.machines = OrderedDict()
        self.machines_affinity = OrderedDict()

    def construct_vms_on_node(self, **kwargs):
        """Construct 1..Mx1..N VMs(s) on node with specified name.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        node = kwargs['node']
        nf_chains = int(kwargs['nf_chains'])
        nf_nodes = int(kwargs['nf_nodes'])
        queues = kwargs['rxq_count_int'] if kwargs['auto_scale'] else 1
        cpu_count_int = kwargs['cpu_count_int']
        vnf_count_int = kwargs['cpu_count_int'] if kwargs['auto_scale'] else 1

        img = Constants.QEMU_PERF_VM_KERNEL

        for nf_chain in range(1, nf_chains + 1):
            for nf_node in range(1, nf_nodes + 1):
                qemu_id = (nf_chain - 1) * nf_nodes + nf_node
                name = '{node}_{qemu_id}'.format(node=node, qemu_id=qemu_id)
                sock1 = '/var/run/vpp/sock-{qemu_id}-1'.format(qemu_id=qemu_id)
                sock2 = '/var/run/vpp/sock-{qemu_id}-2'.format(qemu_id=qemu_id)
                vif1_mac = kwargs['tg_if1_mac'] if nf_node == 1 \
                        else '52:54:00:00:{id:02x}:02'.format(id=qemu_id - 1)
                vif2_mac = kwargs['tg_if2_mac'] if nf_node == nf_nodes \
                        else '52:54:00:00:{id:02x}:01'.format(id=qemu_id + 1)

                self.machines_affinity[name] = get_affinity_vm(
                    nodes=self.nodes, node=node, nf_chains=nf_chains,
                    nf_nodes=nf_nodes, nf_chain=nf_chain, nf_node=nf_node,
                    cpu_count_int=cpu_count_int, vnf_count_int=vnf_count_int)

                self.machines[name] = QemuUtils(
                    node=self.nodes[node], qemu_id=qemu_id,
                    smp=len(self.machines_affinity[name]), mem=4096,
                    vnf=kwargs['vnf'], img=img)
                self.machines[name].configure_kernelvm_vnf(
                    mac1='52:54:00:00:{id:02x}:01'.format(id=qemu_id),
                    mac2='52:54:00:00:{id:02x}:02'.format(id=qemu_id),
                    vif1_mac=vif1_mac,
                    vif2_mac=vif2_mac,
                    queues=queues,
                    jumbo_frames=kwargs['jumbo'])
                self.machines[name].qemu_add_vhost_user_if(
                    sock1, jumbo_frames=kwargs['jumbo'], queues=queues,
                    queue_size=1024)
                self.machines[name].qemu_add_vhost_user_if(
                    sock2, jumbo_frames=kwargs['jumbo'], queues=queues,
                    queue_size=1024)

    def construct_vms_on_all_nodes(self, **kwargs):
        """Construct 1..Mx1..N VMs(s) with specified name on all nodes.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self.initialize()
        for node in self.nodes:
            if self.nodes[node]['type'] == NodeType.DUT:
                self.construct_vms_on_node(node=node, **kwargs)

    def start_all_vms(self, pinning=False):
        """Start all added VMs in manager.

        :param pinning: If True, then do also QEMU process pinning.
        :type pinning: bool
        """
        for machine, machine_affinity in zip(self.machines.values(),
                                             self.machines_affinity.values()):
            machine.qemu_start()
            if pinning:
                machine.qemu_set_affinity(*machine_affinity)

    def set_scheduler_all_vms(self):
        """Set CFS scheduler policy on all VMs in manager."""
        for machine in self.machines.values():
            machine.qemu_set_scheduler_policy()

    def kill_all_vms(self, force=False):
        """Kill all added VMs in manager.

        :param force: Force kill all Qemu instances by pkill qemu if True.
        :type force: bool
        """
        for machine in self.machines.values():
            if force:
                machine.qemu_kill_all()
            else:
                machine.qemu_kill()
