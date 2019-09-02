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

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.QemuUtils import QemuUtils
from resources.libraries.python.topology import NodeType, Topology

__all__ = ["QemuManager"]


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
        vs_dtc = kwargs['vs_dtc']
        nf_dtc = kwargs['vs_dtc'] if kwargs['auto_scale'] else kwargs['nf_dtc']
        nf_dtcr = kwargs['nf_dtcr'] if isinstance(kwargs['nf_dtcr'], int) else 2

        img = Constants.QEMU_VM_KERNEL

        for nf_chain in range(1, nf_chains + 1):
            for nf_node in range(1, nf_nodes + 1):
                qemu_id = (nf_chain - 1) * nf_nodes + nf_node
                name = '{node}_{qemu_id}'.format(node=node, qemu_id=qemu_id)
                sock1 = '/var/run/vpp/sock-{qemu_id}-1'.format(qemu_id=qemu_id)
                sock2 = '/var/run/vpp/sock-{qemu_id}-2'.format(qemu_id=qemu_id)
                vif1_mac = Topology.get_interface_mac(node, 'vhost{idx}'.format(
                    idx=(nf_chain - 1) * nf_nodes * 2 + nf_node * 2 - 1)) \
                    if kwargs['vnf'] == 'testpmd_mac' \
                    else kwargs['tg_if1_mac'] if nf_node == 1 \
                    else '52:54:00:00:{id:02x}:02'.format(id=qemu_id - 1)
                vif2_mac = Topology.get_interface_mac(node, 'vhost{idx}'.format(
                    idx=(nf_chain - 1) * nf_nodes * 2 + nf_node * 2)) \
                    if kwargs['vnf'] == 'testpmd_mac' \
                    else kwargs['tg_if2_mac'] if nf_node == nf_nodes \
                    else '52:54:00:00:{id:02x}:01'.format(id=qemu_id + 1)

                self.machines_affinity[name] = CpuUtils.get_affinity_nf(
                    nodes=self.nodes, node=node, nf_chains=nf_chains,
                    nf_nodes=nf_nodes, nf_chain=nf_chain, nf_node=nf_node,
                    vs_dtc=vs_dtc, nf_dtc=nf_dtc, nf_dtcr=nf_dtcr)

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
                    queue_size=kwargs['perf_qemu_qsz'])
                self.machines[name].qemu_add_vhost_user_if(
                    sock2, jumbo_frames=kwargs['jumbo'], queues=queues,
                    queue_size=kwargs['perf_qemu_qsz'])

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
