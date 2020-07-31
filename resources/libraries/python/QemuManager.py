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
        nf_dtc = kwargs[u"vs_dtc"] if kwargs[u"auto_scale"] \
            else kwargs[u"nf_dtc"]
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
            mac1=f"52:54:00:00:{qemu_id:02x}:01",
            mac2=f"52:54:00:00:{qemu_id:02x}:02",
            vif1_mac=kwargs[u"vif1_mac"],
            vif2_mac=kwargs[u"vif2_mac"],
            queues=kwargs[u"queues"],
            jumbo_frames=kwargs[u"jumbo"]
        )
        self.machines[name].add_vhost_user_if(
            f"/run/vpp/sock-{qemu_id}-1",
            jumbo_frames=kwargs[u"jumbo"],
            queues=kwargs[u"queues"],
            queue_size=kwargs[u"perf_qemu_qsz"],
            csum=kwargs[u"enable_csum"],
            gso=kwargs[u"enable_gso"]
        )
        self.machines[name].add_vhost_user_if(
            f"/run/vpp/sock-{qemu_id}-2",
            jumbo_frames=kwargs[u"jumbo"],
            queues=kwargs[u"queues"],
            queue_size=kwargs[u"perf_qemu_qsz"],
            csum=kwargs[u"enable_csum"],
            gso=kwargs[u"enable_gso"]
        )

    def _c_csr_ip4base_plen24(self, **kwargs):
        """Instantiate one VM with csr_ip4base_plen24 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        qemu_id=kwargs[u"qemu_id"]
        name = kwargs[u"name"]

        self.machines[name] = QemuUtils(
            node=self.nodes[kwargs[u"node"]],
            qemu_id=qemu_id,
            smp=len(self.machines_affinity[name]),
            mem=8192,
            vnf=kwargs[u"vnf"],
            img=Constants.QEMU_VM_IMAGE
        )
        self.machines[name].add_default_params()
        self.machines[name].configure_kernelvm_vnf(
            name=name
        )
        self.machines[name].add_net_user()
        self.machines[name].add_serial()
        self.machines[name].add_drive_cdrom(
            drive_file=f"/tmp/{kwargs['vnf']}.iso",
            index=1
        )
        self.machines[name].add_drive_cdrom(
            drive_file=Constants.QEMU_VM_IMAGE
        )
        self.machines[name].add_drive(
            drive_file=f"/var/lib/vm/csr_empty.qcow2",
            drive_format=u"qcow2"
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )

    def _c_csr_ip4scale2k_plen30(self, **kwargs):
        """Instantiate one VM with csr_ip4scale2k_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ip4scale20k_plen30(self, **kwargs):
        """Instantiate one VM with csr_ip4scale20k_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ip4scale200k_plen30(self, **kwargs):
        """Instantiate one VM with csr_ip4scale200k_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ethip4ipsec1tnl_plen30(self, **kwargs):
        """Instantiate one VM with csr_ethip4ipsec1tnl_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ethip4ipsec40tnl_plen30(self, **kwargs):
        """Instantiate one VM with csr_ethip4ipsec40tnl_plen30 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ethip4_nat44ed_h1024_p63_s64512(self, **kwargs):
        """Instantiate one VM with ethip4_nat44ed_h1024_p63_s64512 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ethip4_nat44ed_h4096_p63_s258048(self, **kwargs):
        """Instantiate one VM with ethip4_nat44ed_h4096_p63_s258048 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ethip4_nat44ed_h16384_p63_s1032192(self, **kwargs):
        """Instantiate one VM with ethip4_nat44ed_h16384_p63_s1032192 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

    def _c_csr_ethip4ipsec1tnl_nat44ed_s64512(self, **kwargs):
        """Instantiate one VM with ethip4ipsec1tnl_nat44ed_s64512 configuration.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self._c_csr_ip4base_plen24(**kwargs)

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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
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
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ethip4ipsec1tnl_plen30(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ethip4ipsec1tnl_plen30 configuration.

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
                ip1=u"200.0.0.1/24",
                ip2=u"192.168.10.1/24",
                route1=u"10.0.0.0/8",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"192.168.10.2",
                arpif1=u"avf-0/0/7/0",
                arpip1=u"192.168.10.2",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                ipsec=\
                    u"create loopback interface \n" \
                    u"set interface ip address loop0 100.0.0.1/32 \n" \
                    u"set interface state loop0 up \n" \
                    u"create ipsec tunnel local-spi 10000 remote-spi 20000 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.0.1 remote-ip 200.0.0.2 instance 0 salt 0x0 \n" \
                    u"set interface unnumbered ipip0 use avf-0/0/6/0 \n" \
                    u"set interface state ipip0 up \n" \
                    u"ip route add 20.0.0.0/30 via ipip0 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"192.168.20.1/24",
                ip2=u"200.0.0.2/24",
                route1=u"20.0.0.0/8",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"192.168.20.2",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"192.168.20.2",
                arpif1=u"avf-0/0/6/0",
                ipsec=\
                    u"create ipsec tunnel local-spi 20000 remote-spi 10000 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.0.1 instance 0 salt 0x0 \n" \
                    u"ip route add 100.0.0.1/8 via 200.0.0.1 avf-0/0/7/0 \n" \
                    u"set interface unnumbered ipip0 use avf-0/0/7/0 \n" \
                    u"set interface state ipip0 up \n" \
                    u"ip route add 10.0.0.0/30 via ipip0 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ethip4ipsec40tnl_plen30(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ethip4ipsec40tnl_plen30 configuration.

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
                ip1=u"200.0.0.1/24",
                ip2=u"192.168.10.1/24",
                route1=u"10.0.0.0/8",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"192.168.10.2",
                arpif1=u"avf-0/0/7/0",
                arpip1=u"192.168.10.2",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                ipsec=\
                    u"create loopback interface \n" \
                    u"set interface state loop0 up \n" \
                    u"set interface ip address loop0 100.0.0.1/32 \n" \
                    u"create ipsec tunnel local-spi 10000 remote-spi 20000 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.0.1 remote-ip 200.0.0.2 instance 0 salt 0x0 \n" \
                    u"set interface unnumbered ipip0 use avf-0/0/6/0 \n" \
                    u"set interface state ipip0 up \n" \
                    u"ip route add 20.0.0.0/30 via ipip0 \n" \
                    u"set interface ip address loop0 100.0.1.1/32 \n" \
                    u"create ipsec tunnel local-spi 10001 remote-spi 20001 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.1.1 remote-ip 200.0.0.2 instance 1 salt 0x0 \n"
                    u"set interface unnumbered ipip1 use avf-0/0/6/0 \n"
                    u"set interface state ipip1 up \n"
                    u"ip route add 20.0.0.4/30 via ipip1 \n"
                    u"set interface ip address loop0 100.0.2.1/32 \n"
                    u"create ipsec tunnel local-spi 10002 remote-spi 20002 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.2.1 remote-ip 200.0.0.2 instance 2 salt 0x0 \n"
                    u"set interface unnumbered ipip2 use avf-0/0/6/0 \n"
                    u"set interface state ipip2 up \n"
                    u"ip route add 20.0.0.8/30 via ipip2 \n"
                    u"set interface ip address loop0 100.0.3.1/32 \n"
                    u"create ipsec tunnel local-spi 10003 remote-spi 20003 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.3.1 remote-ip 200.0.0.2 instance 3 salt 0x0 \n"
                    u"set interface unnumbered ipip3 use avf-0/0/6/0 \n"
                    u"set interface state ipip3 up \n"
                    u"ip route add 20.0.0.12/30 via ipip3 \n"
                    u"set interface ip address loop0 100.0.4.1/32 \n"
                    u"create ipsec tunnel local-spi 10004 remote-spi 20004 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.4.1 remote-ip 200.0.0.2 instance 4 salt 0x0 \n"
                    u"set interface unnumbered ipip4 use avf-0/0/6/0 \n"
                    u"set interface state ipip4 up \n"
                    u"ip route add 20.0.0.16/30 via ipip4 \n"
                    u"set interface ip address loop0 100.0.5.1/32 \n"
                    u"create ipsec tunnel local-spi 10005 remote-spi 20005 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.5.1 remote-ip 200.0.0.2 instance 5 salt 0x0 \n"
                    u"set interface unnumbered ipip5 use avf-0/0/6/0 \n"
                    u"set interface state ipip5 up \n"
                    u"ip route add 20.0.0.20/30 via ipip5 \n"
                    u"set interface ip address loop0 100.0.6.1/32 \n"
                    u"create ipsec tunnel local-spi 10006 remote-spi 20006 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.6.1 remote-ip 200.0.0.2 instance 6 salt 0x0 \n"
                    u"set interface unnumbered ipip6 use avf-0/0/6/0 \n"
                    u"set interface state ipip6 up \n"
                    u"ip route add 20.0.0.24/30 via ipip6 \n"
                    u"set interface ip address loop0 100.0.7.1/32 \n"
                    u"create ipsec tunnel local-spi 10007 remote-spi 20007 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.7.1 remote-ip 200.0.0.2 instance 7 salt 0x0 \n"
                    u"set interface unnumbered ipip7 use avf-0/0/6/0 \n"
                    u"set interface state ipip7 up \n"
                    u"ip route add 20.0.0.28/30 via ipip7 \n"
                    u"set interface ip address loop0 100.0.8.1/32 \n"
                    u"create ipsec tunnel local-spi 10008 remote-spi 20008 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.8.1 remote-ip 200.0.0.2 instance 8 salt 0x0 \n"
                    u"set interface unnumbered ipip8 use avf-0/0/6/0 \n"
                    u"set interface state ipip8 up \n"
                    u"ip route add 20.0.0.32/30 via ipip8 \n"
                    u"set interface ip address loop0 100.0.9.1/32 \n"
                    u"create ipsec tunnel local-spi 10009 remote-spi 20009 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.9.1 remote-ip 200.0.0.2 instance 9 salt 0x0 \n"
                    u"set interface unnumbered ipip9 use avf-0/0/6/0 \n"
                    u"set interface state ipip9 up \n"
                    u"ip route add 20.0.0.36/30 via ipip9 \n"
                    u"set interface ip address loop0 100.0.10.1/32 \n"
                    u"create ipsec tunnel local-spi 10010 remote-spi 20010 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.10.1 remote-ip 200.0.0.2 instance 10 salt 0x0 \n"
                    u"set interface unnumbered ipip10 use avf-0/0/6/0 \n"
                    u"set interface state ipip10 up \n"
                    u"ip route add 20.0.0.40/30 via ipip10 \n"
                    u"set interface ip address loop0 100.0.11.1/32 \n"
                    u"create ipsec tunnel local-spi 10011 remote-spi 20011 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.11.1 remote-ip 200.0.0.2 instance 11 salt 0x0 \n"
                    u"set interface unnumbered ipip11 use avf-0/0/6/0 \n"
                    u"set interface state ipip11 up \n"
                    u"ip route add 20.0.0.44/30 via ipip11 \n"
                    u"set interface ip address loop0 100.0.12.1/32 \n"
                    u"create ipsec tunnel local-spi 10012 remote-spi 20012 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.12.1 remote-ip 200.0.0.2 instance 12 salt 0x0 \n"
                    u"set interface unnumbered ipip12 use avf-0/0/6/0 \n"
                    u"set interface state ipip12 up \n"
                    u"ip route add 20.0.0.48/30 via ipip12 \n"
                    u"set interface ip address loop0 100.0.13.1/32 \n"
                    u"create ipsec tunnel local-spi 10013 remote-spi 20013 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.13.1 remote-ip 200.0.0.2 instance 13 salt 0x0 \n"
                    u"set interface unnumbered ipip13 use avf-0/0/6/0 \n"
                    u"set interface state ipip13 up \n"
                    u"ip route add 20.0.0.52/30 via ipip13 \n"
                    u"set interface ip address loop0 100.0.14.1/32 \n"
                    u"create ipsec tunnel local-spi 10014 remote-spi 20014 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.14.1 remote-ip 200.0.0.2 instance 14 salt 0x0 \n"
                    u"set interface unnumbered ipip14 use avf-0/0/6/0 \n"
                    u"set interface state ipip14 up \n"
                    u"ip route add 20.0.0.56/30 via ipip14 \n"
                    u"set interface ip address loop0 100.0.15.1/32 \n"
                    u"create ipsec tunnel local-spi 10015 remote-spi 20015 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.15.1 remote-ip 200.0.0.2 instance 15 salt 0x0 \n"
                    u"set interface unnumbered ipip15 use avf-0/0/6/0 \n"
                    u"set interface state ipip15 up \n"
                    u"ip route add 20.0.0.60/30 via ipip15 \n"
                    u"set interface ip address loop0 100.0.16.1/32 \n"
                    u"create ipsec tunnel local-spi 10016 remote-spi 20016 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.16.1 remote-ip 200.0.0.2 instance 16 salt 0x0 \n"
                    u"set interface unnumbered ipip16 use avf-0/0/6/0 \n"
                    u"set interface state ipip16 up \n"
                    u"ip route add 20.0.0.64/30 via ipip16 \n"
                    u"set interface ip address loop0 100.0.17.1/32 \n"
                    u"create ipsec tunnel local-spi 10017 remote-spi 20017 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.17.1 remote-ip 200.0.0.2 instance 17 salt 0x0 \n"
                    u"set interface unnumbered ipip17 use avf-0/0/6/0 \n"
                    u"set interface state ipip17 up \n"
                    u"ip route add 20.0.0.68/30 via ipip17 \n"
                    u"set interface ip address loop0 100.0.18.1/32 \n"
                    u"create ipsec tunnel local-spi 10018 remote-spi 20018 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.18.1 remote-ip 200.0.0.2 instance 18 salt 0x0 \n"
                    u"set interface unnumbered ipip18 use avf-0/0/6/0 \n"
                    u"set interface state ipip18 up \n"
                    u"ip route add 20.0.0.72/30 via ipip18 \n"
                    u"set interface ip address loop0 100.0.19.1/32 \n"
                    u"create ipsec tunnel local-spi 10019 remote-spi 20019 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.19.1 remote-ip 200.0.0.2 instance 19 salt 0x0 \n"
                    u"set interface unnumbered ipip19 use avf-0/0/6/0 \n"
                    u"set interface state ipip19 up \n"
                    u"ip route add 20.0.0.76/30 via ipip19 \n"
                    u"set interface ip address loop0 100.0.20.1/32 \n"
                    u"create ipsec tunnel local-spi 10020 remote-spi 20020 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.20.1 remote-ip 200.0.0.2 instance 20 salt 0x0 \n"
                    u"set interface unnumbered ipip20 use avf-0/0/6/0 \n"
                    u"set interface state ipip20 up \n"
                    u"ip route add 20.0.0.80/30 via ipip20 \n"
                    u"set interface ip address loop0 100.0.21.1/32 \n"
                    u"create ipsec tunnel local-spi 10021 remote-spi 20021 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.21.1 remote-ip 200.0.0.2 instance 21 salt 0x0 \n"
                    u"set interface unnumbered ipip21 use avf-0/0/6/0 \n"
                    u"set interface state ipip21 up \n"
                    u"ip route add 20.0.0.84/30 via ipip21 \n"
                    u"set interface ip address loop0 100.0.22.1/32 \n"
                    u"create ipsec tunnel local-spi 10022 remote-spi 20022 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.22.1 remote-ip 200.0.0.2 instance 22 salt 0x0 \n"
                    u"set interface unnumbered ipip22 use avf-0/0/6/0 \n"
                    u"set interface state ipip22 up \n"
                    u"ip route add 20.0.0.88/30 via ipip22 \n"
                    u"set interface ip address loop0 100.0.23.1/32 \n"
                    u"create ipsec tunnel local-spi 10023 remote-spi 20023 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.23.1 remote-ip 200.0.0.2 instance 23 salt 0x0 \n"
                    u"set interface unnumbered ipip23 use avf-0/0/6/0 \n"
                    u"set interface state ipip23 up \n"
                    u"ip route add 20.0.0.92/30 via ipip23 \n"
                    u"set interface ip address loop0 100.0.24.1/32 \n"
                    u"create ipsec tunnel local-spi 10024 remote-spi 20024 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.24.1 remote-ip 200.0.0.2 instance 24 salt 0x0 \n"
                    u"set interface unnumbered ipip24 use avf-0/0/6/0 \n"
                    u"set interface state ipip24 up \n"
                    u"ip route add 20.0.0.96/30 via ipip24 \n"
                    u"set interface ip address loop0 100.0.25.1/32 \n"
                    u"create ipsec tunnel local-spi 10025 remote-spi 20025 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.25.1 remote-ip 200.0.0.2 instance 25 salt 0x0 \n"
                    u"set interface unnumbered ipip25 use avf-0/0/6/0 \n"
                    u"set interface state ipip25 up \n"
                    u"ip route add 20.0.0.100/30 via ipip25 \n"
                    u"set interface ip address loop0 100.0.26.1/32 \n"
                    u"create ipsec tunnel local-spi 10026 remote-spi 20026 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.26.1 remote-ip 200.0.0.2 instance 26 salt 0x0 \n"
                    u"set interface unnumbered ipip26 use avf-0/0/6/0 \n"
                    u"set interface state ipip26 up \n"
                    u"ip route add 20.0.0.104/30 via ipip26 \n"
                    u"set interface ip address loop0 100.0.27.1/32 \n"
                    u"create ipsec tunnel local-spi 10027 remote-spi 20027 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.27.1 remote-ip 200.0.0.2 instance 27 salt 0x0 \n"
                    u"set interface unnumbered ipip27 use avf-0/0/6/0 \n"
                    u"set interface state ipip27 up \n"
                    u"ip route add 20.0.0.108/30 via ipip27 \n"
                    u"set interface ip address loop0 100.0.28.1/32 \n"
                    u"create ipsec tunnel local-spi 10028 remote-spi 20028 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.28.1 remote-ip 200.0.0.2 instance 28 salt 0x0 \n"
                    u"set interface unnumbered ipip28 use avf-0/0/6/0 \n"
                    u"set interface state ipip28 up \n"
                    u"ip route add 20.0.0.112/30 via ipip28 \n"
                    u"set interface ip address loop0 100.0.29.1/32 \n"
                    u"create ipsec tunnel local-spi 10029 remote-spi 20029 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.29.1 remote-ip 200.0.0.2 instance 29 salt 0x0 \n"
                    u"set interface unnumbered ipip29 use avf-0/0/6/0 \n"
                    u"set interface state ipip29 up \n"
                    u"ip route add 20.0.0.116/30 via ipip29 \n"
                    u"set interface ip address loop0 100.0.30.1/32 \n"
                    u"create ipsec tunnel local-spi 10030 remote-spi 20030 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.30.1 remote-ip 200.0.0.2 instance 30 salt 0x0 \n"
                    u"set interface unnumbered ipip30 use avf-0/0/6/0 \n"
                    u"set interface state ipip30 up \n"
                    u"ip route add 20.0.0.120/30 via ipip30 \n"
                    u"set interface ip address loop0 100.0.31.1/32 \n"
                    u"create ipsec tunnel local-spi 10031 remote-spi 20031 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.31.1 remote-ip 200.0.0.2 instance 31 salt 0x0 \n"
                    u"set interface unnumbered ipip31 use avf-0/0/6/0 \n"
                    u"set interface state ipip31 up \n"
                    u"ip route add 20.0.0.124/30 via ipip31 \n"
                    u"set interface ip address loop0 100.0.32.1/32 \n"
                    u"create ipsec tunnel local-spi 10032 remote-spi 20032 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.32.1 remote-ip 200.0.0.2 instance 32 salt 0x0 \n"
                    u"set interface unnumbered ipip32 use avf-0/0/6/0 \n"
                    u"set interface state ipip32 up \n"
                    u"ip route add 20.0.0.128/30 via ipip32 \n"
                    u"set interface ip address loop0 100.0.33.1/32 \n"
                    u"create ipsec tunnel local-spi 10033 remote-spi 20033 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.33.1 remote-ip 200.0.0.2 instance 33 salt 0x0 \n"
                    u"set interface unnumbered ipip33 use avf-0/0/6/0 \n"
                    u"set interface state ipip33 up \n"
                    u"ip route add 20.0.0.132/30 via ipip33 \n"
                    u"set interface ip address loop0 100.0.34.1/32 \n"
                    u"create ipsec tunnel local-spi 10034 remote-spi 20034 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.34.1 remote-ip 200.0.0.2 instance 34 salt 0x0 \n"
                    u"set interface unnumbered ipip34 use avf-0/0/6/0 \n"
                    u"set interface state ipip34 up \n"
                    u"ip route add 20.0.0.136/30 via ipip34 \n"
                    u"set interface ip address loop0 100.0.35.1/32 \n"
                    u"create ipsec tunnel local-spi 10035 remote-spi 20035 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.35.1 remote-ip 200.0.0.2 instance 35 salt 0x0 \n"
                    u"set interface unnumbered ipip35 use avf-0/0/6/0 \n"
                    u"set interface state ipip35 up \n"
                    u"ip route add 20.0.0.140/30 via ipip35 \n"
                    u"set interface ip address loop0 100.0.36.1/32 \n"
                    u"create ipsec tunnel local-spi 10036 remote-spi 20036 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.36.1 remote-ip 200.0.0.2 instance 36 salt 0x0 \n"
                    u"set interface unnumbered ipip36 use avf-0/0/6/0 \n"
                    u"set interface state ipip36 up \n"
                    u"ip route add 20.0.0.144/30 via ipip36 \n"
                    u"set interface ip address loop0 100.0.37.1/32 \n"
                    u"create ipsec tunnel local-spi 10037 remote-spi 20037 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.37.1 remote-ip 200.0.0.2 instance 37 salt 0x0 \n"
                    u"set interface unnumbered ipip37 use avf-0/0/6/0 \n"
                    u"set interface state ipip37 up \n"
                    u"ip route add 20.0.0.148/30 via ipip37 \n"
                    u"set interface ip address loop0 100.0.38.1/32 \n"
                    u"create ipsec tunnel local-spi 10038 remote-spi 20038 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.38.1 remote-ip 200.0.0.2 instance 38 salt 0x0 \n"
                    u"set interface unnumbered ipip38 use avf-0/0/6/0 \n"
                    u"set interface state ipip38 up \n"
                    u"ip route add 20.0.0.152/30 via ipip38 \n"
                    u"set interface ip address loop0 100.0.39.1/32 \n"
                    u"create ipsec tunnel local-spi 10039 remote-spi 20039 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.39.1 remote-ip 200.0.0.2 instance 39 salt 0x0 \n"
                    u"set interface unnumbered ipip39 use avf-0/0/6/0 \n"
                    u"set interface state ipip39 up \n"
                    u"ip route add 20.0.0.156/30 via ipip39 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"192.168.20.1/24",
                ip2=u"200.0.0.2/24",
                route1=u"20.0.0.0/8",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"192.168.20.2",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"192.168.20.2",
                arpif1=u"avf-0/0/6/0",
                ipsec=\
                    u"ip route add 100.0.0.0/8 via 200.0.0.1 avf-0/0/7/0 \n"
                    u"create ipsec tunnel local-spi 20000 remote-spi 10000 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.0.1 instance 0 salt 0x0 \n"
                    u"set interface unnumbered ipip0 use avf-0/0/7/0 \n"
                    u"set interface state ipip0 up \n"
                    u"ip route add 10.0.0.0/30 via ipip0 \n"
                    u"create ipsec tunnel local-spi 20001 remote-spi 10001 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.1.1 instance 1 salt 0x0 \n"
                    u"set interface unnumbered ipip1 use avf-0/0/7/0 \n"
                    u"set interface state ipip1 up \n"
                    u"ip route add 10.0.0.4/30 via ipip1 \n"
                    u"create ipsec tunnel local-spi 20002 remote-spi 10002 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.2.1 instance 2 salt 0x0 \n"
                    u"set interface unnumbered ipip2 use avf-0/0/7/0 \n"
                    u"set interface state ipip2 up \n"
                    u"ip route add 10.0.0.8/30 via ipip2 \n"
                    u"create ipsec tunnel local-spi 20003 remote-spi 10003 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.3.1 instance 3 salt 0x0 \n"
                    u"set interface unnumbered ipip3 use avf-0/0/7/0 \n"
                    u"set interface state ipip3 up \n"
                    u"ip route add 10.0.0.12/30 via ipip3 \n"
                    u"create ipsec tunnel local-spi 20004 remote-spi 10004 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.4.1 instance 4 salt 0x0 \n"
                    u"set interface unnumbered ipip4 use avf-0/0/7/0 \n"
                    u"set interface state ipip4 up \n"
                    u"ip route add 10.0.0.16/30 via ipip4 \n"
                    u"create ipsec tunnel local-spi 20005 remote-spi 10005 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.5.1 instance 5 salt 0x0 \n"
                    u"set interface unnumbered ipip5 use avf-0/0/7/0 \n"
                    u"set interface state ipip5 up \n"
                    u"ip route add 10.0.0.20/30 via ipip5 \n"
                    u"create ipsec tunnel local-spi 20006 remote-spi 10006 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.6.1 instance 6 salt 0x0 \n"
                    u"set interface unnumbered ipip6 use avf-0/0/7/0 \n"
                    u"set interface state ipip6 up \n"
                    u"ip route add 10.0.0.24/30 via ipip6 \n"
                    u"create ipsec tunnel local-spi 20007 remote-spi 10007 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.7.1 instance 7 salt 0x0 \n"
                    u"set interface unnumbered ipip7 use avf-0/0/7/0 \n"
                    u"set interface state ipip7 up \n"
                    u"ip route add 10.0.0.28/30 via ipip7 \n"
                    u"create ipsec tunnel local-spi 20008 remote-spi 10008 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.8.1 instance 8 salt 0x0 \n"
                    u"set interface unnumbered ipip8 use avf-0/0/7/0 \n"
                    u"set interface state ipip8 up \n"
                    u"ip route add 10.0.0.32/30 via ipip8 \n"
                    u"create ipsec tunnel local-spi 20009 remote-spi 10009 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.9.1 instance 9 salt 0x0 \n"
                    u"set interface unnumbered ipip9 use avf-0/0/7/0 \n"
                    u"set interface state ipip9 up \n"
                    u"ip route add 10.0.0.36/30 via ipip9 \n"
                    u"create ipsec tunnel local-spi 20010 remote-spi 10010 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.10.1 instance 10 salt 0x0 \n"
                    u"set interface unnumbered ipip10 use avf-0/0/7/0 \n"
                    u"set interface state ipip10 up \n"
                    u"ip route add 10.0.0.40/30 via ipip10 \n"
                    u"create ipsec tunnel local-spi 20011 remote-spi 10011 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.11.1 instance 11 salt 0x0 \n"
                    u"set interface unnumbered ipip11 use avf-0/0/7/0 \n"
                    u"set interface state ipip11 up \n"
                    u"ip route add 10.0.0.44/30 via ipip11 \n"
                    u"create ipsec tunnel local-spi 20012 remote-spi 10012 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.12.1 instance 12 salt 0x0 \n"
                    u"set interface unnumbered ipip12 use avf-0/0/7/0 \n"
                    u"set interface state ipip12 up \n"
                    u"ip route add 10.0.0.48/30 via ipip12 \n"
                    u"create ipsec tunnel local-spi 20013 remote-spi 10013 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.13.1 instance 13 salt 0x0 \n"
                    u"set interface unnumbered ipip13 use avf-0/0/7/0 \n"
                    u"set interface state ipip13 up \n"
                    u"ip route add 10.0.0.52/30 via ipip13 \n"
                    u"create ipsec tunnel local-spi 20014 remote-spi 10014 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.14.1 instance 14 salt 0x0 \n"
                    u"set interface unnumbered ipip14 use avf-0/0/7/0 \n"
                    u"set interface state ipip14 up \n"
                    u"ip route add 10.0.0.56/30 via ipip14 \n"
                    u"create ipsec tunnel local-spi 20015 remote-spi 10015 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.15.1 instance 15 salt 0x0 \n"
                    u"set interface unnumbered ipip15 use avf-0/0/7/0 \n"
                    u"set interface state ipip15 up \n"
                    u"ip route add 10.0.0.60/30 via ipip15 \n"
                    u"create ipsec tunnel local-spi 20016 remote-spi 10016 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.16.1 instance 16 salt 0x0 \n"
                    u"set interface unnumbered ipip16 use avf-0/0/7/0 \n"
                    u"set interface state ipip16 up \n"
                    u"ip route add 10.0.0.64/30 via ipip16 \n"
                    u"create ipsec tunnel local-spi 20017 remote-spi 10017 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.17.1 instance 17 salt 0x0 \n"
                    u"set interface unnumbered ipip17 use avf-0/0/7/0 \n"
                    u"set interface state ipip17 up \n"
                    u"ip route add 10.0.0.68/30 via ipip17 \n"
                    u"create ipsec tunnel local-spi 20018 remote-spi 10018 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.18.1 instance 18 salt 0x0 \n"
                    u"set interface unnumbered ipip18 use avf-0/0/7/0 \n"
                    u"set interface state ipip18 up \n"
                    u"ip route add 10.0.0.72/30 via ipip18 \n"
                    u"create ipsec tunnel local-spi 20019 remote-spi 10019 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.19.1 instance 19 salt 0x0 \n"
                    u"set interface unnumbered ipip19 use avf-0/0/7/0 \n"
                    u"set interface state ipip19 up \n"
                    u"ip route add 10.0.0.76/30 via ipip19 \n"
                    u"create ipsec tunnel local-spi 20020 remote-spi 10020 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.20.1 instance 20 salt 0x0 \n"
                    u"set interface unnumbered ipip20 use avf-0/0/7/0 \n"
                    u"set interface state ipip20 up \n"
                    u"ip route add 10.0.0.80/30 via ipip20 \n"
                    u"create ipsec tunnel local-spi 20021 remote-spi 10021 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.21.1 instance 21 salt 0x0 \n"
                    u"set interface unnumbered ipip21 use avf-0/0/7/0 \n"
                    u"set interface state ipip21 up \n"
                    u"ip route add 10.0.0.84/30 via ipip21 \n"
                    u"create ipsec tunnel local-spi 20022 remote-spi 10022 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.22.1 instance 22 salt 0x0 \n"
                    u"set interface unnumbered ipip22 use avf-0/0/7/0 \n"
                    u"set interface state ipip22 up \n"
                    u"ip route add 10.0.0.88/30 via ipip22 \n"
                    u"create ipsec tunnel local-spi 20023 remote-spi 10023 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.23.1 instance 23 salt 0x0 \n"
                    u"set interface unnumbered ipip23 use avf-0/0/7/0 \n"
                    u"set interface state ipip23 up \n"
                    u"ip route add 10.0.0.92/30 via ipip23 \n"
                    u"create ipsec tunnel local-spi 20024 remote-spi 10024 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.24.1 instance 24 salt 0x0 \n"
                    u"set interface unnumbered ipip24 use avf-0/0/7/0 \n"
                    u"set interface state ipip24 up \n"
                    u"ip route add 10.0.0.96/30 via ipip24 \n"
                    u"create ipsec tunnel local-spi 20025 remote-spi 10025 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.25.1 instance 25 salt 0x0 \n"
                    u"set interface unnumbered ipip25 use avf-0/0/7/0 \n"
                    u"set interface state ipip25 up \n"
                    u"ip route add 10.0.0.100/30 via ipip25 \n"
                    u"create ipsec tunnel local-spi 20026 remote-spi 10026 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.26.1 instance 26 salt 0x0 \n"
                    u"set interface unnumbered ipip26 use avf-0/0/7/0 \n"
                    u"set interface state ipip26 up \n"
                    u"ip route add 10.0.0.104/30 via ipip26 \n"
                    u"create ipsec tunnel local-spi 20027 remote-spi 10027 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.27.1 instance 27 salt 0x0 \n"
                    u"set interface unnumbered ipip27 use avf-0/0/7/0 \n"
                    u"set interface state ipip27 up \n"
                    u"ip route add 10.0.0.108/30 via ipip27 \n"
                    u"create ipsec tunnel local-spi 20028 remote-spi 10028 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.28.1 instance 28 salt 0x0 \n"
                    u"set interface unnumbered ipip28 use avf-0/0/7/0 \n"
                    u"set interface state ipip28 up \n"
                    u"ip route add 10.0.0.112/30 via ipip28 \n"
                    u"create ipsec tunnel local-spi 20029 remote-spi 10029 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.29.1 instance 29 salt 0x0 \n"
                    u"set interface unnumbered ipip29 use avf-0/0/7/0 \n"
                    u"set interface state ipip29 up \n"
                    u"ip route add 10.0.0.116/30 via ipip29 \n"
                    u"create ipsec tunnel local-spi 20030 remote-spi 10030 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.30.1 instance 30 salt 0x0 \n"
                    u"set interface unnumbered ipip30 use avf-0/0/7/0 \n"
                    u"set interface state ipip30 up \n"
                    u"ip route add 10.0.0.120/30 via ipip30 \n"
                    u"create ipsec tunnel local-spi 20031 remote-spi 10031 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.31.1 instance 31 salt 0x0 \n"
                    u"set interface unnumbered ipip31 use avf-0/0/7/0 \n"
                    u"set interface state ipip31 up \n"
                    u"ip route add 10.0.0.124/30 via ipip31 \n"
                    u"create ipsec tunnel local-spi 20032 remote-spi 10032 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.32.1 instance 32 salt 0x0 \n"
                    u"set interface unnumbered ipip32 use avf-0/0/7/0 \n"
                    u"set interface state ipip32 up \n"
                    u"ip route add 10.0.0.128/30 via ipip32 \n"
                    u"create ipsec tunnel local-spi 20033 remote-spi 10033 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.33.1 instance 33 salt 0x0 \n"
                    u"set interface unnumbered ipip33 use avf-0/0/7/0 \n"
                    u"set interface state ipip33 up \n"
                    u"ip route add 10.0.0.132/30 via ipip33 \n"
                    u"create ipsec tunnel local-spi 20034 remote-spi 10034 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.34.1 instance 34 salt 0x0 \n"
                    u"set interface unnumbered ipip34 use avf-0/0/7/0 \n"
                    u"set interface state ipip34 up \n"
                    u"ip route add 10.0.0.136/30 via ipip34 \n"
                    u"create ipsec tunnel local-spi 20035 remote-spi 10035 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.35.1 instance 35 salt 0x0 \n"
                    u"set interface unnumbered ipip35 use avf-0/0/7/0 \n"
                    u"set interface state ipip35 up \n"
                    u"ip route add 10.0.0.140/30 via ipip35 \n"
                    u"create ipsec tunnel local-spi 20036 remote-spi 10036 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.36.1 instance 36 salt 0x0 \n"
                    u"set interface unnumbered ipip36 use avf-0/0/7/0 \n"
                    u"set interface state ipip36 up \n"
                    u"ip route add 10.0.0.144/30 via ipip36 \n"
                    u"create ipsec tunnel local-spi 20037 remote-spi 10037 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.37.1 instance 37 salt 0x0 \n"
                    u"set interface unnumbered ipip37 use avf-0/0/7/0 \n"
                    u"set interface state ipip37 up \n"
                    u"ip route add 10.0.0.148/30 via ipip37 \n"
                    u"create ipsec tunnel local-spi 20038 remote-spi 10038 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.38.1 instance 38 salt 0x0 \n"
                    u"set interface unnumbered ipip38 use avf-0/0/7/0 \n"
                    u"set interface state ipip38 up \n"
                    u"ip route add 10.0.0.152/30 via ipip38 \n"
                    u"create ipsec tunnel local-spi 20039 remote-spi 10039 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 200.0.0.2 remote-ip 100.0.39.1 instance 39 salt 0x0 \n"
                    u"set interface unnumbered ipip39 use avf-0/0/7/0 \n"
                    u"set interface state ipip39 up \n"
                    u"ip route add 10.0.0.156/30 via ipip39 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ethip4_nat44ed_h1024_p63_s64512(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ethip4_nat44ed_h1024_p63_s64512
        configuration.

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
                route1=u"20.0.0.0/8",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"192.168.0.0/16",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                nat=u"",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"192.168.0.0/16",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/8",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                nat=u"" \
                    u"set interface nat44 in avf-0/0/7/0 out avf-0/0/6/0 \n"
                    u"set nat44 session limit 1032192 \n"
                    u"nat44 add address 68.142.68.0 - 68.142.68.0 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ethip4_nat44ed_h4096_p63_s258048(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ethip4_nat44ed_h4096_p63_s258048
        configuration.

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
                route1=u"20.0.0.0/8",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"192.168.0.0/8",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                nat=u"",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"192.168.0.0/8",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/8",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                nat=u"" \
                    u"set interface nat44 in avf-0/0/7/0 out avf-0/0/6/0 \n"
                    u"set nat44 session limit 1032192 \n"
                    u"nat44 add address 68.142.68.0 - 68.142.68.3 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ethip4_nat44ed_h16384_p63_s1032192(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ethip4_nat44ed_h16384_p63_s1032192
        configuration.

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
                route1=u"20.0.0.0/8",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"2.2.2.2",
                route2=u"192.168.0.0/8",
                routeif2=u"avf-0/0/7/0",
                nexthop2=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                nat=u"",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"192.168.0.0/16",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"2.2.2.1",
                route2=u"20.0.0.0/8",
                routeif2=u"avf-0/0/6/0",
                nexthop2=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                nat=u"" \
                    u"set interface nat44 in avf-0/0/7/0 out avf-0/0/6/0 \n"
                    u"set nat44 session limit 1032192 \n"
                    u"nat44 add address 68.142.68.0 - 68.142.68.15 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )

    def _c_vpp_2vfpt_ethip4ipsec1tnl_nat44ed_s64512(self, **kwargs):
        """Instantiate one VM with vpp_2vfpt_ethip4ipsec1tnl_nat44ed_s64512
        configuration.

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
                route1=u"192.168.0.0/16",
                routeif1=u"avf-0/0/7/0",
                nexthop1=u"1.1.1.1",
                arpmac1=u"3c:fd:fe:d1:5c:d8",
                arpip1=u"1.1.1.1",
                arpif1=u"avf-0/0/7/0",
                nat_ipsec=u"" \
                    u"create loopback interface \n"
                    u"set interface ip address loop0 100.0.0.1/32 \n"
                    u"set interface state loop0 up \n"
                    u"create ipsec tunnel local-spi 10000 remote-spi 20000 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 100.0.0.1 remote-ip 2.2.2.2 instance 0 salt 0x0 \n"
                    u"set interface unnumbered ipip0 use avf-0/0/6/0 \n"
                    u"set interface state ipip0 up \n"
                    u"ip route add 20.0.0.0/8 via ipip0 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        else:
            self.machines[name].configure_kernelvm_vnf(
                ip1=u"3.3.3.2/30",
                ip2=u"2.2.2.2/30",
                route1=u"20.0.0.0/8",
                routeif1=u"avf-0/0/6/0",
                nexthop1=u"3.3.3.1",
                arpmac1=u"3c:fd:fe:d1:5c:d9",
                arpip1=u"3.3.3.1",
                arpif1=u"avf-0/0/6/0",
                nat_ipsec=u"" \
                    u"ip route add 100.0.0.1/8 via 2.2.2.1 avf-0/0/7/0 \n"
                    u"create ipsec tunnel local-spi 20000 remote-spi 10000 crypto-alg aes-gcm-128 local-crypto-key 4f484443536343634b614f4452437747 remote-crypto-key 4f484443536343634b614f4452437747 local-ip 2.2.2.2 remote-ip 100.0.0.1 instance 0 salt 0x0 \n"
                    u"set interface unnumbered ipip0 use avf-0/0/7/0 \n"
                    u"set interface state ipip0 up \n"
                    u"ip route add 192.168.0.0/16 via ipip0 \n"
                    u"set interface nat44 in ipip0 out avf-0/0/6/0 \n"
                    u"nat44 add address 68.142.68.0 - 68.142.68.0 \n",
                queues=kwargs[u"queues"],
                jumbo_frames=kwargs[u"jumbo"]
            )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if2"])
        )
        self.machines[name].add_vfio_pci_if(
            pci=Topology.get_interface_pci_addr(
                self.nodes[kwargs[u"node"]], kwargs[u"if1"])
        )
