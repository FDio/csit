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

"""Library to manipulate Containers."""

from collections import OrderedDict, Counter
from io import open
from re import search
from string import Template
from time import sleep

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.Constants import Constants
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import Topology, SocketType
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
from resources.libraries.python.VPPUtil import VPPUtil


__all__ = [
    u"ContainerManager", u"ContainerEngine", u"LXC", u"Docker", u"Container"
]

SUPERVISOR_CONF = u"/etc/supervisor/supervisord.conf"


class ContainerManager:
    """Container lifecycle management class."""

    def __init__(self, engine):
        """Initialize Container Manager class.

        :param engine: Container technology used (LXC/Docker/...).
        :type engine: str
        :raises NotImplementedError: If container technology is not implemented.
        """
        try:
            self.engine = globals()[engine]()
        except KeyError:
            raise NotImplementedError(f"{engine} is not implemented.")
        self.containers = OrderedDict()

    def get_container_by_name(self, name):
        """Get container instance.

        :param name: Container name.
        :type name: str
        :returns: Container instance.
        :rtype: Container
        :raises RuntimeError: If failed to get container with name.
        """
        try:
            return self.containers[name]
        except KeyError:
            raise RuntimeError(f"Failed to get container with name: {name}")

    def construct_container(self, **kwargs):
        """Construct container object on node with specified parameters.

        :param kwargs: Key-value pairs used to construct container.
        :param kwargs: dict
        """
        # Create base class
        self.engine.initialize()
        # Set parameters
        for key in kwargs:
            setattr(self.engine.container, key, kwargs[key])

        # Set additional environmental variables
        setattr(
            self.engine.container, u"env",
            f"MICROSERVICE_LABEL={kwargs[u'name']}"
        )

        # Store container instance
        self.containers[kwargs[u"name"]] = self.engine.container

    def construct_containers(self, **kwargs):
        """Construct 1..N container(s) on node with specified name.

        Ordinal number is automatically added to the name of container as
        suffix.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        name = kwargs[u"name"]
        for i in range(kwargs[u"count"]):
            # Name will contain ordinal suffix
            kwargs[u"name"] = u"".join([name, str(i+1)])
            # Create container
            self.construct_container(i=i, **kwargs)

    def acquire_all_containers(self):
        """Acquire all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.acquire()

    def build_all_containers(self):
        """Build all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.build()

    def create_all_containers(self):
        """Create all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.create()

    def execute_on_container(self, name, command):
        """Execute command on container with name.

        :param name: Container name.
        :param command: Command to execute.
        :type name: str
        :type command: str
        """
        self.engine.container = self.get_container_by_name(name)
        self.engine.execute(command)

    def execute_on_all_containers(self, command):
        """Execute command on all containers.

        :param command: Command to execute.
        :type command: str
        """
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.execute(command)

    def start_vpp_in_all_containers(self, verify=True):
        """Start VPP in all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            # For multiple containers, delayed verify is faster.
            self.engine.start_vpp(verify=False)
        if verify:
            self.verify_vpp_in_all_containers()

    def _disconnect_papi_to_all_containers(self):
        """Disconnect any open PAPI connections to VPPs in containers.

        The current PAPI implementation caches open connections,
        so explicit disconnect is needed before VPP becomes inaccessible.

        Currently this is a protected method, as restart, stop and destroy
        are the only dangerous methods, and all are handled by ContainerManager.
        """
        for container_object in self.containers.values():
            PapiSocketExecutor.disconnect_by_node_and_socket(
                container_object.node,
                container_object.api_socket,
            )

    def restart_vpp_in_all_containers(self, verify=True):
        """Restart VPP in all containers."""
        self._disconnect_papi_to_all_containers()
        for container in self.containers:
            self.engine.container = self.containers[container]
            # For multiple containers, delayed verify is faster.
            self.engine.restart_vpp(verify=False)
        if verify:
            self.verify_vpp_in_all_containers()

    def verify_vpp_in_all_containers(self):
        """Verify that VPP is installed and running in all containers."""
        # For multiple containers, multiple fors are faster.
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.verify_vppctl()
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.adjust_privileges()
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.verify_vpp_papi()

    def configure_vpp_in_all_containers(self, chain_topology, **kwargs):
        """Configure VPP in all containers.

        :param chain_topology: Topology used for chaining containers can be
            chain or cross_horiz. Chain topology is using 1 memif pair per
            container. Cross_horiz topology is using 1 memif and 1 physical
            interface in container (only single container can be configured).
        :param kwargs: Named parameters.
        :type chain_topology: str
        :type kwargs: dict
        """
        # Count number of DUTs based on node's host information
        dut_cnt = len(
            Counter(
                [
                    f"{container.node['host']}{container.node['port']}"
                    for container in self.containers.values()
                ]
            )
        )
        mod = len(self.containers) // dut_cnt

        for i, container in enumerate(self.containers):
            mid1 = i % mod + 1
            mid2 = i % mod + 1
            sid1 = i % mod * 2 + 1
            sid2 = i % mod * 2 + 2
            self.engine.container = self.containers[container]
            guest_dir = self.engine.container.mnt[0].split(u":")[1]

            if chain_topology == u"chain":
                self._configure_vpp_chain_l2xc(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs
                )
            elif chain_topology == u"cross_horiz":
                self._configure_vpp_cross_horiz(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs
                )
            elif chain_topology == u"chain_functional":
                self._configure_vpp_chain_functional(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs
                )
            elif chain_topology == u"chain_ip4":
                self._configure_vpp_chain_ip4(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs
                )
            elif chain_topology == u"pipeline_ip4":
                self._configure_vpp_pipeline_ip4(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs
                )
            elif chain_topology == u"chain_vswitch":
                self._configure_vpp_chain_vswitch(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs)
            elif chain_topology == u"chain_ipsec":
                idx_match = search(r"\d+$", self.engine.container.name)
                if idx_match:
                    idx = int(idx_match.group())
                self._configure_vpp_chain_ipsec(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, nf_instance=idx, **kwargs)
            elif chain_topology == u"chain_dma":
                self._configure_vpp_chain_dma(
                    mid1=mid1, mid2=mid2, sid1=sid1, sid2=sid2,
                    guest_dir=guest_dir, **kwargs
                )
            else:
                raise RuntimeError(
                    f"Container topology {chain_topology} not implemented"
                )

    def _configure_vpp_chain_l2xc(self, **kwargs):
        """Configure VPP in chain topology with l2xc.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self.engine.create_vpp_startup_config()
        logger.debug(f"kwargs {kwargs}")
        self.engine.create_vpp_exec_config(
            u"memif_create_chain_l2xc.exec",
            mid1=kwargs[u"mid1"], mid2=kwargs[u"mid2"],
            sid1=kwargs[u"sid1"], sid2=kwargs[u"sid2"],
            socket1=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid1']}",
            socket2=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid2']}"
        )

    def _configure_vpp_chain_dma(self, **kwargs):
        """Configure VPP in chain topology with l2xc (dma).

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        dma_wqs = kwargs[f"dma_wqs"]
        self.engine.create_vpp_startup_config_dma(dma_wqs)

        self.engine.create_vpp_exec_config(
            u"memif_create_chain_dma.exec",
            mid1=kwargs[u"mid1"], mid2=kwargs[u"mid2"],
            sid1=kwargs[u"sid1"], sid2=kwargs[u"sid2"],
            socket1=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid1']}",
            socket2=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid2']}"
        )

    def _configure_vpp_cross_horiz(self, **kwargs):
        """Configure VPP in cross horizontal topology (single memif).

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        if u"DUT1" in self.engine.container.name:
            if_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs[u"dut1_if"])
            if_name = Topology.get_interface_name(
                self.engine.container.node, kwargs[u"dut1_if"])
        if u"DUT2" in self.engine.container.name:
            if_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs[u"dut2_if"])
            if_name = Topology.get_interface_name(
                self.engine.container.node, kwargs[u"dut2_if"])
        self.engine.create_vpp_startup_config_dpdk_dev(if_pci)
        self.engine.create_vpp_exec_config(
            u"memif_create_cross_horizon.exec",
            mid1=kwargs[u"mid1"], sid1=kwargs[u"sid1"], if_name=if_name,
            socket1=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid1']}"
        )

    def _configure_vpp_chain_functional(self, **kwargs):
        """Configure VPP in chain topology with l2xc (functional).

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self.engine.create_vpp_startup_config()
        self.engine.create_vpp_exec_config(
            u"memif_create_chain_functional.exec",
            mid1=kwargs[u"mid1"], mid2=kwargs[u"mid2"],
            sid1=kwargs[u"sid1"], sid2=kwargs[u"sid2"],
            socket1=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid1']}",
            socket2=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid2']}",
            rx_mode=u"interrupt"
        )

    def _configure_vpp_chain_ip4(self, **kwargs):
        """Configure VPP in chain topology with ip4.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self.engine.create_vpp_startup_config()

        vif1_mac = kwargs[u"tg_pf1_mac"] \
            if (kwargs[u"mid1"] - 1) % kwargs[u"nodes"] + 1 == 1 \
            else f"52:54:00:00:{(kwargs[u'mid1'] - 1):02X}:02"
        vif2_mac = kwargs[u"tg_pf2_mac"] \
            if (kwargs[u"mid2"] - 1) % kwargs[u"nodes"] + 1 == kwargs[u"nodes"]\
            else f"52:54:00:00:{(kwargs['mid2'] + 1):02X}:01"
        self.engine.create_vpp_exec_config(
            u"memif_create_chain_ip4.exec",
            mid1=kwargs[u"mid1"], mid2=kwargs[u"mid2"],
            sid1=kwargs[u"sid1"], sid2=kwargs[u"sid2"],
            socket1=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid1']}",
            socket2=f"{kwargs[u'guest_dir']}/memif-"
            f"{self.engine.container.name}-{kwargs[u'sid2']}",
            mac1=f"52:54:00:00:{kwargs[u'mid1']:02X}:01",
            mac2=f"52:54:00:00:{kwargs[u'mid2']:02X}:02",
            vif1_mac=vif1_mac, vif2_mac=vif2_mac
        )

    def _configure_vpp_chain_vswitch(self, **kwargs):
        """Configure VPP as vswitch in container.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        dut = self.engine.container.name.split(u"_")[0]
        if dut == u"DUT1":
            if1_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs[u"dut1_if2"])
            if2_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs[u"dut1_if1"])
            if_red_name = Topology.get_interface_name(
                self.engine.container.node, kwargs[u"dut1_if2"])
            if_black_name = Topology.get_interface_name(
                self.engine.container.node, kwargs[u"dut1_if1"])
            tg_pf_ip4 = kwargs[u"tg_pf2_ip4"]
            tg_pf_mac = kwargs[u"tg_pf2_mac"]
        else:
            tg_pf_ip4 = kwargs[u"tg_pf1_ip4"]
            tg_pf_mac = kwargs[u"tg_pf1_mac"]
            if1_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs[u"dut2_if1"])
            if2_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs[u"dut2_if2"])
            if_red_name = Topology.get_interface_name(
                self.engine.container.node, kwargs[u"dut2_if1"])
            if_black_name = Topology.get_interface_name(
                self.engine.container.node, kwargs[u"dut2_if2"])

        n_instances = int(kwargs[u"n_instances"])
        rxq = 1
        if u"rxq" in kwargs:
            rxq = int(kwargs[u"rxq"])
        nodes = kwargs[u"nodes"]
        cpuset_cpus = CpuUtils.get_affinity_nf(
            nodes, dut, nf_chains=1, nf_nodes=1, nf_chain=1,
            nf_node=1, vs_dtc=0, nf_dtc=8, nf_mtcr=1, nf_dtcr=1
        )
        self.engine.create_vpp_startup_config_vswitch(
            cpuset_cpus, rxq, if1_pci, if2_pci
        )

        instances = []
        for i in range(1, n_instances + 1):
            instances.append(
                f"create interface memif id {i} socket-id 1 master\n"
                f"set interface state memif1/{i} up\n"
                f"set interface l2 bridge memif1/{i} 1\n"
                f"create interface memif id {i} socket-id 2 master\n"
                f"set interface state memif2/{i} up\n"
                f"set interface l2 bridge memif2/{i} 2\n"
                f"set ip neighbor memif2/{i} {tg_pf_ip4} {tg_pf_mac} "
                f"static\n\n"
            )

        self.engine.create_vpp_exec_config(
            u"memif_create_chain_vswitch_ipsec.exec",
            socket1=f"{kwargs[u'guest_dir']}/{dut}_memif-vswitch-1",
            socket2=f"{kwargs[u'guest_dir']}/{dut}_memif-vswitch-2",
            if_red_name=if_red_name,
            if_black_name=if_black_name,
            instances=u"\n\n".join(instances))


    def _configure_vpp_chain_ipsec(self, **kwargs):
        """Configure VPP in container with memifs.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        nf_nodes = int(kwargs[u"nf_nodes"])
        nf_instance = int(kwargs[u"nf_instance"])
        nodes = kwargs[u"nodes"]
        dut = self.engine.container.name.split(u"_")[0]
        cpuset_cpus = CpuUtils.get_affinity_nf(
            nodes, dut, nf_chains=1, nf_nodes=nf_nodes, nf_chain=1,
            nf_node=nf_instance, vs_dtc=10, nf_dtc=1, nf_mtcr=1, nf_dtcr=1)
        self.engine.create_vpp_startup_config_ipsec(cpuset_cpus)
        local_ip_base = kwargs[u"dut2_if1_ip4"].rsplit(u".", 1)[0]

        if dut == u"DUT1":
            tnl_local_ip = f"{local_ip_base}.{nf_instance + 100}"
            tnl_remote_ip = f"{local_ip_base}.{nf_instance}"
            remote_ip_base = kwargs[u"dut1_if1_ip4"].rsplit(u".", 1)[0]
            tg_pf_ip4 = kwargs[u"tg_pf1_ip4"]
            tg_pf_mac = kwargs[u"tg_pf1_mac"]
            raddr_ip4 = kwargs[u"laddr_ip4"]
            l_mac1 = 17
            l_mac2 = 18
            r_mac = 1
        else:
            tnl_local_ip = f"{local_ip_base}.{nf_instance}"
            tnl_remote_ip = f"{local_ip_base}.{nf_instance + 100}"
            remote_ip_base = kwargs[u"dut2_if2_ip4"].rsplit(u".", 1)[0]
            tg_pf_ip4 = kwargs[u"tg_pf2_ip4"]
            tg_pf_mac = kwargs[u"tg_pf2_mac"]
            raddr_ip4 = kwargs[u"raddr_ip4"]
            l_mac1 = 1
            l_mac2 = 2
            r_mac = 17

        self.engine.create_vpp_exec_config(
            u"memif_create_chain_ipsec.exec",
            socket1=f"{kwargs['guest_dir']}/{dut}_memif-vswitch-1",
            socket2=f"{kwargs['guest_dir']}/{dut}_memif-vswitch-2",
            mid1=nf_instance,
            mid2=nf_instance,
            sid1=u"1",
            sid2=u"2",
            mac1=f"02:02:00:00:{l_mac1:02X}:{(nf_instance - 1):02X}",
            mac2=f"02:02:00:00:{l_mac2:02X}:{(nf_instance - 1):02X}",
            tg_pf2_ip4=tg_pf_ip4,
            tg_pf2_mac=tg_pf_mac,
            raddr_ip4=raddr_ip4,
            tnl_local_ip=tnl_local_ip,
            tnl_remote_ip=tnl_remote_ip,
            tnl_remote_mac=f"02:02:00:00:{r_mac:02X}:{(nf_instance - 1):02X}",
            remote_ip=f"{remote_ip_base}.{nf_instance}"
        )
        self.engine.execute(
            f"cat {kwargs['guest_dir']}/ipsec_create_tunnel_cnf_"
            f"{dut}_{nf_instance}.config >> /tmp/running.exec"
        )

    def _configure_vpp_pipeline_ip4(self, **kwargs):
        """Configure VPP in pipeline topology with ip4.

        :param kwargs: Named parameters.
        :type kwargs: dict
        """
        self.engine.create_vpp_startup_config()
        node = (kwargs[u"mid1"] - 1) % kwargs[u"nodes"] + 1
        mid1 = kwargs[u"mid1"]
        mid2 = kwargs[u"mid2"]
        role1 = u"master"
        role2 = u"master" if node == kwargs[u"nodes"] else u"slave"
        kwargs[u"mid2"] = kwargs[u"mid2"] \
            if node == kwargs[u"nodes"] else kwargs[u"mid2"] + 1
        vif1_mac = kwargs[u"tg_pf1_mac"] \
            if (kwargs[u"mid1"] - 1) % kwargs[u"nodes"] + 1 == 1 \
            else f"52:54:00:00:{(kwargs[u'mid1'] - 1):02X}:02"
        vif2_mac = kwargs[u"tg_pf2_mac"] \
            if (kwargs[u"mid2"] - 1) % kwargs[u"nodes"] + 1 == kwargs[u"nodes"]\
            else f"52:54:00:00:{(kwargs[u'mid2'] + 1):02X}:01"
        socket1 = f"{kwargs[u'guest_dir']}/memif-{self.engine.container.name}-"\
            f"{kwargs[u'sid1']}" if node == 1 \
            else f"{kwargs[u'guest_dir']}/memif-pipe-{kwargs[u'mid1']}"
        socket2 = f"{kwargs[u'guest_dir']}/memif-{self.engine.container.name}-"\
            f"{kwargs[u'sid2']}" \
            if node == 1 and kwargs[u"nodes"] == 1 or node == kwargs[u"nodes"] \
            else f"{kwargs[u'guest_dir']}/memif-pipe-{kwargs[u'mid2']}"

        self.engine.create_vpp_exec_config(
            u"memif_create_pipeline_ip4.exec",
            mid1=kwargs[u"mid1"], mid2=kwargs[u"mid2"],
            sid1=kwargs[u"sid1"], sid2=kwargs[u"sid2"],
            socket1=socket1, socket2=socket2, role1=role1, role2=role2,
            mac1=f"52:54:00:00:{mid1:02X}:01",
            mac2=f"52:54:00:00:{mid2:02X}:02",
            vif1_mac=vif1_mac, vif2_mac=vif2_mac
        )

    def stop_all_containers(self):
        """Stop all containers."""
        # TODO: Rework if containers can be affected outside ContainerManager.
        self._disconnect_papi_to_all_containers()
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.stop()

    def destroy_all_containers(self):
        """Destroy all containers."""
        # TODO: Rework if containers can be affected outside ContainerManager.
        self._disconnect_papi_to_all_containers()
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.destroy()


class ContainerEngine:
    """Abstract class for container engine."""

    def __init__(self):
        """Init ContainerEngine object."""
        self.container = None

    def initialize(self):
        """Initialize container object."""
        self.container = Container()

    def acquire(self, force):
        """Acquire/download container.

        :param force: Destroy a container if exists and create.
        :type force: bool
        """
        raise NotImplementedError

    def build(self):
        """Build container (compile)."""
        raise NotImplementedError

    def create(self):
        """Create/deploy container."""
        raise NotImplementedError

    def execute(self, command):
        """Execute process inside container.

        :param command: Command to run inside container.
        :type command: str
        """
        raise NotImplementedError

    def stop(self):
        """Stop container."""
        raise NotImplementedError

    def destroy(self):
        """Destroy/remove container."""
        raise NotImplementedError

    def info(self):
        """Info about container."""
        raise NotImplementedError

    def system_info(self):
        """System info."""
        raise NotImplementedError

    def start_vpp(self, verify=True):
        """Start VPP inside a container."""
        self.execute(
            u"/usr/bin/vpp -c /etc/vpp/startup.conf")

        topo_instance = BuiltIn().get_library_instance(
            u"resources.libraries.python.topology.Topology"
        )
        topo_instance.add_new_socket(
            self.container.node,
            SocketType.CLI,
            self.container.name,
            self.container.cli_socket,
        )
        topo_instance.add_new_socket(
            self.container.node,
            SocketType.PAPI,
            self.container.name,
            self.container.api_socket,
        )
        topo_instance.add_new_socket(
            self.container.node,
            SocketType.STATS,
            self.container.name,
            self.container.stats_socket,
        )
        if verify:
            self.verify_vpp()

    def restart_vpp(self, verify=True):
        """Restart VPP service inside a container."""
        self.execute(u"pkill vpp")
        self.start_vpp(verify=verify)

    def verify_vpp(self):
        """Verify VPP is running and ready."""
        self.verify_vppctl()
        self.adjust_privileges()
        self.verify_vpp_papi()

    # TODO Rewrite to use the VPPUtil.py functionality and remove this.
    def verify_vppctl(self, retries=120, retry_wait=1):
        """Verify that VPP is installed and running inside container.

        This function waits a while so VPP can start.
        PCI interfaces are listed for debug purposes.
        When the check passes, VPP API socket is created on remote side,
        but perhaps its directory does not have the correct access rights yet.

        :param retries: Check for VPP for this number of times Default: 120
        :param retry_wait: Wait for this number of seconds between retries.
        """
        for _ in range(retries + 1):
            try:
                # Execute puts the command into single quotes,
                # so inner arguments are enclosed in qouble quotes here.
                self.execute(
                    u'/usr/bin/vppctl show pci 2>&1 | '
                    u'fgrep -v "Connection refused" | '
                    u'fgrep -v "No such file or directory"'
                )
                break
            except (RuntimeError, AssertionError):
                sleep(retry_wait)
        else:
            self.execute(u"cat /tmp/vppd.log")
            raise RuntimeError(
                f"VPP did not come up in container: {self.container.name}"
            )

    def adjust_privileges(self):
        """Adjust privileges to control VPP without sudo."""
        self.execute("chmod -R o+rwx /run/vpp")

    def verify_vpp_papi(self, retries=120, retry_wait=1):
        """Verify that VPP is available for PAPI.

        This also opens and caches PAPI connection for quick reuse.
        The connection is disconnected when ContainerManager decides to do so.

        :param retries: Check for VPP for this number of times Default: 120
        :param retry_wait: Wait for this number of seconds between retries.
        """
        # Wait for success.
        for _ in range(retries + 1):
            try:
                VPPUtil.vpp_show_version(
                    node=self.container.node,
                    remote_vpp_socket=self.container.api_socket,
                    log=False,
                )
                break
            except (RuntimeError, AssertionError):
                sleep(retry_wait)
        else:
            self.execute(u"cat /tmp/vppd.log")
            raise RuntimeError(
                f"VPP PAPI fails in container: {self.container.name}"
            )

    def create_base_vpp_startup_config(self, cpuset_cpus=None):
        """Create base startup configuration of VPP on container.

        :param cpuset_cpus: List of CPU cores to allocate.
        :type cpuset_cpus: list.
        :returns: Base VPP startup configuration.
        :rtype: VppConfigGenerator
        """
        if cpuset_cpus is None:
            cpuset_cpus = self.container.cpuset_cpus

        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(self.container.node)
        vpp_config.add_unix_cli_listen()
        vpp_config.add_unix_exec(u"/tmp/running.exec")
        vpp_config.add_socksvr(socket=Constants.SOCKSVR_PATH)
        if cpuset_cpus:
            # We will pop the first core from the list to be a main core
            vpp_config.add_cpu_main_core(str(cpuset_cpus.pop(0)))
            # If more cores in the list, the rest will be used as workers.
            corelist_workers = u",".join(str(cpu) for cpu in cpuset_cpus[:1])
            vpp_config.add_cpu_corelist_workers(corelist_workers)
        vpp_config.add_buffers_per_numa(215040)
        vpp_config.add_plugin(u"disable", u"default")
        vpp_config.add_plugin(u"enable", u"memif_plugin.so")
        vpp_config.add_plugin(u"enable", u"perfmon_plugin.so")
        vpp_config.add_main_heap_size(u"2G")
        vpp_config.add_main_heap_page_size(self.container.page_size)
        vpp_config.add_default_hugepage_size(self.container.page_size)
        vpp_config.add_statseg_size(u"2G")
        vpp_config.add_statseg_page_size(self.container.page_size)
        vpp_config.add_statseg_per_node_counters(u"on")

        return vpp_config

    def create_vpp_startup_config(self):
        """Create startup configuration of VPP without DPDK on container.
        """
        vpp_config = self.create_base_vpp_startup_config()

        # Apply configuration
        self.execute(u"mkdir -p /etc/vpp/")
        self.execute(
            f'echo "{vpp_config.get_config_str()}" | '
            f'tee /etc/vpp/startup.conf'
        )

    def create_vpp_startup_config_vswitch(self, cpuset_cpus, rxq, *devices):
        """Create startup configuration of VPP vswitch.

        :param cpuset_cpus: CPU list to run on.
        :param rxq: Number of interface RX queues.
        :param devices: PCI devices.
        :type cpuset_cpus: list
        :type rxq: int
        :type devices: list
        """
        vpp_config = self.create_base_vpp_startup_config(cpuset_cpus)
        vpp_config.add_dpdk_dev(*devices)
        vpp_config.add_dpdk_log_level(u"debug")
        vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_dpdk_dev_default_rxq(rxq)
        vpp_config.add_plugin(u"enable", u"dpdk_plugin.so")
        vpp_config.add_plugin(u"enable", u"perfmon_plugin.so")

        # Apply configuration
        self.execute(u"mkdir -p /etc/vpp/")
        self.execute(
            f'echo "{vpp_config.get_config_str()}" | tee /etc/vpp/startup.conf'
        )

    def create_vpp_startup_config_ipsec(self, cpuset_cpus):
        """Create startup configuration of VPP with IPsec on container.

        :param cpuset_cpus: CPU list to run on.
        :type cpuset_cpus: list
        """
        vpp_config = self.create_base_vpp_startup_config(cpuset_cpus)
        vpp_config.add_plugin(u"enable", u"crypto_native_plugin.so")
        vpp_config.add_plugin(u"enable", u"crypto_ipsecmb_plugin.so")
        vpp_config.add_plugin(u"enable", u"crypto_openssl_plugin.so")
        vpp_config.add_plugin(u"enable", u"perfmon_plugin.so")

        # Apply configuration
        self.execute(u"mkdir -p /etc/vpp/")
        self.execute(
            f'echo "{vpp_config.get_config_str()}" | tee /etc/vpp/startup.conf'
        )

    def create_vpp_startup_config_dma(self, dma_devices):
        """Create startup configuration of VPP DMA.

        :param dma_devices: DMA devices list.
        :type dma_devices: list
        """
        vpp_config = self.create_base_vpp_startup_config()
        vpp_config.add_plugin(u"enable", u"dma_intel_plugin.so")
        vpp_config.add_dma_dev(dma_devices)

        # Apply configuration
        self.execute(u"mkdir -p /etc/vpp/")
        self.execute(
            f'echo "{vpp_config.get_config_str()}" | tee /etc/vpp/startup.conf'
        )

    def create_vpp_exec_config(self, template_file, **kwargs):
        """Create VPP exec configuration on container.

        :param template_file: File name of a template script.
        :param kwargs: Parameters for script.
        :type template_file: str
        :type kwargs: dict
        """
        running = u"/tmp/running.exec"
        template = f"{Constants.RESOURCES_TPL_CONTAINER}/{template_file}"

        with open(template, u"rt") as src_file:
            src = Template(src_file.read())
            self.execute(f'echo "{src.safe_substitute(**kwargs)}" > {running}')

    def is_container_running(self):
        """Check if container is running."""
        raise NotImplementedError

    def is_container_present(self):
        """Check if container is present."""
        raise NotImplementedError

    def _configure_cgroup(self, name):
        """Configure the control group associated with a container.

        By default the cpuset cgroup is using exclusive CPU/MEM. When Docker/LXC
        container is initialized a new cgroup /docker or /lxc is created under
        cpuset parent tree. This newly created cgroup is inheriting parent
        setting for cpu/mem exclusive parameter and thus cannot be overriden
        within /docker or /lxc cgroup. This function is supposed to set cgroups
        to allow coexistence of both engines.

        :param name: Name of cgroup.
        :type name: str
        :raises RuntimeError: If applying cgroup settings via cgset failed.
        """
        ret, _, _ = self.container.ssh.exec_command_sudo(
            f"cgcreate -g cpuset:/{name}"
        )
        if int(ret) != 0:
            raise RuntimeError(u"Failed to copy cgroup settings from root.")

        ret, _, _ = self.container.ssh.exec_command_sudo(
            f"cgset -r cpuset.cpus=0 /{name}"
        )
        if int(ret) != 0:
            raise RuntimeError(u"Failed to apply cgroup settings.")

        ret, _, _ = self.container.ssh.exec_command_sudo(
            f"cgset -r cpuset.mems=0 /{name}"
        )
        if int(ret) != 0:
            raise RuntimeError(u"Failed to apply cgroup settings.")


class LXC(ContainerEngine):
    """LXC implementation."""

    # Implicit constructor is inherited.

    def acquire(self, force=True):
        """Acquire a privileged system object where configuration is stored.

        :param force: If a container exists, destroy it and create a new
            container.
        :type force: bool
        :raises RuntimeError: If creating the container or writing the container
            config fails.
        """
        if self.is_container_present():
            if force:
                self.destroy()
            else:
                return

        target_arch = u"arm64" \
            if Topology.get_node_arch(self.container.node) == u"aarch64" \
            else u"amd64"

        image = self.container.image if self.container.image \
            else f"-d ubuntu -r jammy -a {target_arch}"

        cmd = f"lxc-create -t download --name {self.container.name} " \
            f"-- {image} --no-validate"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=1800)
        if int(ret) != 0:
            raise RuntimeError(u"Failed to create container.")

        self._configure_cgroup(u"lxc")

    def build(self):
        """Build container (compile)."""
        raise NotImplementedError

    def create(self):
        """Create/deploy an application inside a container on system.

        :raises RuntimeError: If creating the container fails.
        """
        if self.container.mnt:
            # LXC fix for tmpfs
            # https://github.com/lxc/lxc/issues/434
            mnt_e = u"lxc.mount.entry = tmpfs run tmpfs defaults"
            ret, _, _ = self.container.ssh.exec_command_sudo(
                f"sh -c \"echo '{mnt_e}' >> "
                f"/var/lib/lxc/{self.container.name}/config\""
            )
            if int(ret) != 0:
                raise RuntimeError(
                    f"Failed to write {self.container.name} config."
                )

            for mount in self.container.mnt:
                host_dir, guest_dir = mount.split(u":")
                options = u"bind,create=dir" if guest_dir.endswith(u"/") \
                    else u"bind,create=file"
                entry = f"lxc.mount.entry = {host_dir} {guest_dir[1:]} " \
                    f"none {options} 0 0"
                self.container.ssh.exec_command_sudo(
                    f"sh -c \"mkdir -p {host_dir}\""
                )
                ret, _, _ = self.container.ssh.exec_command_sudo(
                    f"sh -c \"echo '{entry}' "
                    f">> /var/lib/lxc/{self.container.name}/config\""
                )
                if int(ret) != 0:
                    raise RuntimeError(
                        f"Failed to write {self.container.name} config."
                    )

        cpuset_cpus = u",".join(
            f"{cpu!s}" for cpu in self.container.cpuset_cpus) \
            if self.container.cpuset_cpus else u""

        ret, _, _ = self.container.ssh.exec_command_sudo(
            f"lxc-start --name {self.container.name} --daemon"
        )
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to start container {self.container.name}."
            )
        self._lxc_wait(u"RUNNING")

        # Workaround for LXC to be able to allocate all cpus including isolated.
        ret, _, _ = self.container.ssh.exec_command_sudo(
            u"cgset --copy-from / lxc/"
        )
        if int(ret) != 0:
            raise RuntimeError(u"Failed to copy cgroup to LXC")

        ret, _, _ = self.container.ssh.exec_command_sudo(
            f"lxc-cgroup --name {self.container.name} cpuset.cpus {cpuset_cpus}"
        )
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to set cpuset.cpus to container {self.container.name}."
            )

    def execute(self, command):
        """Start a process inside a running container.

        Runs the specified command inside the container specified by name. The
        container has to be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If running the command failed.
        """
        env = u"--keep-env " + u" ".join(
            f"--set-var {env!s}" for env in self.container.env) \
            if self.container.env else u""

        cmd = f"lxc-attach {env} --name {self.container.name} " \
            f"-- /bin/sh -c '{command}'"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to run command inside container {self.container.name}."
            )

    def stop(self):
        """Stop a container.

        :raises RuntimeError: If stopping the container failed.
        """
        cmd = f"lxc-stop --name {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to stop container {self.container.name}."
            )
        self._lxc_wait(u"STOPPED|FROZEN")

    def destroy(self):
        """Destroy a container.

        :raises RuntimeError: If destroying container failed.
        """
        cmd = f"lxc-destroy --force --name {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to destroy container {self.container.name}."
            )

    def info(self):
        """Query and shows information about a container.

        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = f"lxc-info --name {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to get info about container {self.container.name}."
            )

    def system_info(self):
        """Check the current kernel for LXC support.

        :raises RuntimeError: If checking LXC support failed.
        """
        cmd = u"lxc-checkconfig"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(u"Failed to check LXC support.")

    def is_container_running(self):
        """Check if container is running on node.

        :returns: True if container is running.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = f"lxc-info --no-humanize --state --name {self.container.name}"

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to get info about container {self.container.name}."
            )
        return u"RUNNING" in stdout

    def is_container_present(self):
        """Check if container is existing on node.

        :returns: True if container is present.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = f"lxc-info --no-humanize --name {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        return not ret

    def _lxc_wait(self, state):
        """Wait for a specific container state.

        :param state: Specify the container state(s) to wait for.
        :type state: str
        :raises RuntimeError: If waiting for state of a container failed.
        """
        cmd = f"lxc-wait --name {self.container.name} --state '{state}'"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to wait for state '{state}' "
                f"of container {self.container.name}."
            )


class Docker(ContainerEngine):
    """Docker implementation."""

    # Implicit constructor is inherited.

    def acquire(self, force=True):
        """Pull an image or a repository from a registry.

        :param force: Destroy a container if exists.
        :type force: bool
        :raises RuntimeError: If pulling a container failed.
        """
        if self.is_container_present():
            if force:
                self.destroy()
            else:
                return

        if not self.container.image:
            img = Constants.DOCKER_SUT_IMAGE_UBUNTU_ARM \
                if Topology.get_node_arch(self.container.node) == u"aarch64" \
                else Constants.DOCKER_SUT_IMAGE_UBUNTU
            setattr(self.container, u"image", img)

        if "/" in self.container.image:
            cmd = f"docker pull {self.container.image}"
            ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=1800)
            if int(ret) != 0:
                raise RuntimeError(
                    f"Failed to create container {self.container.name}."
                )

        if self.container.cpuset_cpus:
            self._configure_cgroup(u"docker")

    def build(self):
        """Build container (compile)."""
        raise NotImplementedError

    def create(self):
        """Create/deploy container.

        :raises RuntimeError: If creating a container failed.
        """
        cpuset_cpus = u"--cpuset-cpus=" + u",".join(
            f"{cpu!s}" for cpu in self.container.cpuset_cpus) \
            if self.container.cpuset_cpus else u""

        cpuset_mems = f"--cpuset-mems={self.container.cpuset_mems}" \
            if self.container.cpuset_mems is not None else u""
        # Temporary workaround - disabling due to bug in memif
        cpuset_mems = u""

        env = u" ".join(f"--env {env!s}" for env in self.container.env) \
            if self.container.env else u""

        command = str(self.container.command) if self.container.command else u""

        publish = u" ".join(
            f"--publish  {var!s}" for var in self.container.publish
        ) if self.container.publish else u""

        volume = u" ".join(
            f"--volume {mnt!s}" for mnt in self.container.mnt) \
            if self.container.mnt else u""

        cmd = f"docker run --privileged --detach --interactive --tty --rm " \
            f"--cgroup-parent docker.slice {cpuset_cpus} {cpuset_mems} " \
            f"{publish} {env} {volume} --name {self.container.name} " \
            f"{self.container.image} {command}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to create container {self.container.name}"
            )

        self.info()

    def execute(self, command):
        """Start a process inside a running container.

        Runs the specified command inside the container specified by name. The
        container has to be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If running the command in a container failed.
        """
        cmd = f"docker exec --interactive {self.container.name} " \
            f"/bin/sh -c '{command}'"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to execute command in container {self.container.name}."
            )

    def stop(self):
        """Stop running container.

        :raises RuntimeError: If stopping a container failed.
        """
        cmd = f"docker stop {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to stop container {self.container.name}."
            )

    def destroy(self):
        """Remove a container.

        :raises RuntimeError: If removing a container failed.
        """
        cmd = f"docker rm --force {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to destroy container {self.container.name}."
            )

    def info(self):
        """Return low-level information on Docker objects.

        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = f"docker inspect {self.container.name}"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to get info about container {self.container.name}."
            )

    def system_info(self):
        """Display the docker system-wide information.

        :raises RuntimeError: If displaying system information failed.
        """
        cmd = u"docker system info"

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(u"Failed to get system info.")

    def is_container_present(self):
        """Check if container is present on node.

        :returns: True if container is present.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = f"docker ps --all --quiet --filter name={self.container.name}"

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to get info about container {self.container.name}."
            )
        return bool(stdout)

    def is_container_running(self):
        """Check if container is running on node.

        :returns: True if container is running.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = f"docker ps --quiet --filter name={self.container.name}"

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError(
                f"Failed to get info about container {self.container.name}."
            )
        return bool(stdout)


class Container:
    """Container class."""

    def __getattr__(self, attr):
        """Get attribute custom implementation.

        :param attr: Attribute to get.
        :type attr: str
        :returns: Attribute value or None.
        :rtype: any
        """
        try:
            return self.__dict__[attr]
        except KeyError:
            return None

    def __setattr__(self, attr, value):
        """Set attribute custom implementation.

        :param attr: Attribute to set.
        :param value: Value to set.
        :type attr: str
        :type value: any
        """
        try:
            # Check if attribute exists
            self.__dict__[attr]
        except KeyError:
            # Creating new attribute
            if attr == u"node":
                # Create and cache a connected SSH instance.
                self.__dict__[u"ssh"] = SSH()
                self.__dict__[u"ssh"].connect(value)
            elif attr == u"name":
                # Socket paths to not have mutable state,
                # this just saves some horizontal space in callers.
                # TODO: Rename the dir so other apps can add sockets easily.
                # E.g. f"/tmp/app_sockets/{value}/vpp_api.sock"
                path = f"/tmp/vpp_sockets/{value}"
                self.__dict__[u"socket_dir"] = path
                self.__dict__[u"api_socket"] = f"{path}/api.sock"
                self.__dict__[u"cli_socket"] = f"{path}/cli.sock"
                self.__dict__[u"stats_socket"] = f"{path}/stats.sock"
            self.__dict__[attr] = value
        else:
            # Updating attribute base of type
            if isinstance(self.__dict__[attr], list):
                self.__dict__[attr].append(value)
            else:
                self.__dict__[attr] = value
