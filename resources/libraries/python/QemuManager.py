# Copyright (c) 2024 Cisco and/or its affiliates.
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

__all__ = [u"QemuManager"]


class QemuManager:
    """QEMU lifecycle management class"""

    # Use one instance of class per tests.
    ROBOT_LIBRARY_SCOPE = u"TEST CASE"

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
        node = kwargs[u"node"]
        nf_chains = int(kwargs[u"nf_chains"])
        nf_nodes = int(kwargs[u"nf_nodes"])
        queues = kwargs[u"rxq_count_int"] if kwargs[u"auto_scale"] else 1
        vs_dtc = kwargs[u"vs_dtc"]
        nf_dtc = kwargs[u"nf_dtc"]
        if kwargs[u"auto_scale"] and not kwargs[u"fixed_auto_scale"]:
            nf_dtc = kwargs[u"vs_dtc"]
        nf_dtcr = kwargs[u"nf_dtcr"] \
            if isinstance(kwargs[u"nf_dtcr"], int) else 2

        for nf_chain in range(1, nf_chains + 1):
            for nf_node in range(1, nf_nodes + 1):
                qemu_id = (nf_chain - 1) * nf_nodes + nf_node
                name = f"{node}_{qemu_id}"
                idx1 = (nf_chain - 1) * nf_nodes * 2 + nf_node * 2 - 1

                vif1_mac = Topology.get_interface_mac(
                    self.nodes[node], f"vhost{idx1}"
                ) if kwargs[u"vnf"] == u"testpmd_mac" \
                    else kwargs[u"tg_pf1_mac"] if nf_node == 1 \
                    else f"52:54:00:00:{(qemu_id - 1):02x}:02"
                idx2 = (nf_chain - 1) * nf_nodes * 2 + nf_node * 2
                vif2_mac = Topology.get_interface_mac(
                    self.nodes[node], f"vhost{idx2}"
                ) if kwargs[u"vnf"] == u"testpmd_mac" \
                    else kwargs[u"tg_pf2_mac"] if nf_node == nf_nodes \
                    else f"52:54:00:00:{(qemu_id + 1):02x}:01"

                self.machines_affinity[name] = CpuUtils.get_affinity_nf(
                    nodes=self.nodes, node=node, nf_chains=nf_chains,
                    nf_nodes=nf_nodes, nf_chain=nf_chain, nf_node=nf_node,
                    vs_dtc=vs_dtc, nf_dtc=nf_dtc, nf_dtcr=nf_dtcr
                )

                try:
                    getattr(self, f'_c_{kwargs["vnf"]}')(
                        qemu_id=qemu_id, name=name, queues=queues, **kwargs
                    )
                except AttributeError:
                    self._c_default(
                        qemu_id=qemu_id, name=name, queues=queues,
                        vif1_mac=vif1_mac, vif2_mac=vif2_mac, **kwargs
                    )

    def construct_vms_on_all_nodes(self, **kwargs):
        """Construct 1..Mx1..N VMs(s) with specified name on all nodes.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self.initialize()
        for node in self.nodes:
            if self.nodes[node][u"type"] == NodeType.DUT:
                self.construct_vms_on_node(node=node, **kwargs)

    def start_all_vms(self, pinning=False):
        """Start all added VMs in manager.

        :param pinning: If True, then do also QEMU process pinning.
        :type pinning: bool
        """
        cpus = []
        for machine, machine_affinity in \
                zip(self.machines.values(), self.machines_affinity.values()):
            index = list(self.machines.values()).index(machine)
            name = list(self.machines.keys())[index]
            self.nodes[name] = machine.qemu_start()
            if pinning:
                machine.qemu_set_affinity(*machine_affinity)
                cpus.extend(machine_affinity)
        return ",".join(str(cpu) for cpu in cpus)

    def kill_all_vms(self, force=False):
        """Kill all added VMs in manager.

        :param force: Force kill all Qemu instances by pkill qemu if True.
        :type force: bool
        """
        for node in list(self.nodes.values()):
            if node["type"] == NodeType.VM:
                try:
                    self.nodes.popitem(node)
                except TypeError:
                    pass
        for machine in self.machines.values():
            if force:
                machine.qemu_kill_all()
            else:
                machine.qemu_kill()

    def _c_default(self, **kwargs):
        """Instantiate one VM with default configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id = kwargs[u"qemu_id"]
        name = kwargs[u"name"]
        virtio_feature_mask = kwargs[u"virtio_feature_mask"] \
            if u"virtio_feature_mask" in kwargs else None

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=4096,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_KERNEL,
            page_size=kwargs[u"page_size"]
        )
        self.machines[name].add_default_params()
        self.machines[name].add_kernelvm_params()
        self.machines[name].configure_kernelvm_vnf(
            mac1=f"52:54:00:00:{qemu_id:02x}:01",
            mac2=f"52:54:00:00:{qemu_id:02x}:02",
            vif1_mac=kwargs[u"vif1_mac"],
            vif2_mac=kwargs[u"vif2_mac"],
            queues=kwargs[u"queues"],
            jumbo=kwargs[u"jumbo"]
        )
        self.machines[name].add_vhost_user_if(
            f"/run/vpp/sock-{qemu_id}-1",
            jumbo=kwargs[u"jumbo"],
            queues=kwargs[u"queues"],
            queue_size=kwargs[u"perf_qemu_qsz"],
            virtio_feature_mask=virtio_feature_mask
        )
        self.machines[name].add_vhost_user_if(
            f"/run/vpp/sock-{qemu_id}-2",
            jumbo=kwargs[u"jumbo"],
            queues=kwargs[u"queues"],
            queue_size=kwargs[u"perf_qemu_qsz"],
            virtio_feature_mask=virtio_feature_mask
        )

    def _c_vpp_2vfpt_ip4base_plen24(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ip4base_plen24 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id = kwargs[u"qemu_id"]
        name = kwargs[u"name"]

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=4096,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_KERNEL
        )
        self.machines[name].add_default_params()
        self.machines[name].add_kernelvm_params()
        if u"DUT1" in name:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"2.2.2.1/30",
                ip2=u"1.1.1.2/30",
                route1=u"20.0.0.0/24",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"10.0.0.0/24",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"10.0.0.0/24",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/24",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ip4scale2k_plen30(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ip4scale2k_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id = kwargs[u"qemu_id"]
        name = kwargs[u"name"]

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=4096,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_KERNEL
        )
        self.machines[name].add_default_params()
        self.machines[name].add_kernelvm_params()
        if u"DUT1" in name:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"2.2.2.1/30",
                ip2=u"1.1.1.2/30",
                route1=u"20.0.0.0/30",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"10.0.0.0/30",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"10.0.0.0/30",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/30",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ip4scale20k_plen30(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ip4scale20k_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id = kwargs[u"qemu_id"]
        name = kwargs[u"name"]

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=4096,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_KERNEL
        )
        self.machines[name].add_default_params()
        self.machines[name].add_kernelvm_params()
        if u"DUT1" in name:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"2.2.2.1/30",
                ip2=u"1.1.1.2/30",
                route1=u"20.0.0.0/30",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"10.0.0.0/30",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"10.0.0.0/30",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/30",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ip4scale200k_plen30(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ip4scale200k_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id = kwargs[u"qemu_id"]
        name = kwargs[u"name"]

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=4096,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_KERNEL
        )
        self.machines[name].add_default_params()
        self.machines[name].add_kernelvm_params()
        if u"DUT1" in name:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"2.2.2.1/30",
                ip2=u"1.1.1.2/30",
                route1=u"20.0.0.0/30",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"10.0.0.0/30",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"10.0.0.0/30",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/30",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                queues=kwargs[u"queues"],
                jumbo=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_iperf3(self, **kwargs):
        """Instantiate one VM with iperf3 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id = kwargs[u"qemu_id"]
        name = kwargs[u"name"]
        virtio_feature_mask = kwargs[u"virtio_feature_mask"] \
            if u"virtio_feature_mask" in kwargs else None

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=4096,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_KERNEL
        )
        self.machines[name].add_default_params()
        self.machines[name].add_kernelvm_params()
        self.machines[name].configure_kernelvm_vnf(
            queues=kwargs[u"queues"],
            jumbo=kwargs[u"jumbo"]
        )
        self.machines[name].add_net_user()
        self.machines[name].add_vhost_user_if(
            f"/run/vpp/sock-{qemu_id}-1",
            server=False,
            jumbo=kwargs[u"jumbo"],
            queues=kwargs[u"queues"],
            queue_size=kwargs[u"perf_qemu_qsz"],
            virtio_feature_mask=virtio_feature_mask
        )
