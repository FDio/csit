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

# Bug workaround in pylint for abstract classes.
# pylint: disable=W0223

"""Library to manipulate Containers."""

from time import sleep
from string import Template
from collections import OrderedDict, Counter

from resources.libraries.python.ssh import SSH
from resources.libraries.python.Constants import Constants
from resources.libraries.python.topology import Topology
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
from resources.libraries.python.CpuUtils import CpuUtils

__all__ = ["ContainerManager", "ContainerEngine", "LXC", "Docker", "Container"]

SUPERVISOR_CONF = '/etc/supervisord.conf'


class ContainerManager(object):
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
            raise NotImplementedError('{engine} is not implemented.'.
                                      format(engine=engine))
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
            raise RuntimeError('Failed to get container with name: {name}'.
                               format(name=name))

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
        setattr(self.engine.container, 'env',
                'MICROSERVICE_LABEL={label}'.format(label=kwargs['name']))

        # Store container instance
        self.containers[kwargs['name']] = self.engine.container

    def construct_containers(self, **kwargs):
        """Construct 1..N container(s) on node with specified name.

        Ordinal number is automatically added to the name of container as
        suffix.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        name = kwargs['name']
        for i in range(kwargs['count']):
            # Name will contain ordinal suffix
            kwargs['name'] = ''.join([name, str(i+1)])
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

    def start_vpp_in_all_containers(self):
        """Start VPP in all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            # We need to install supervisor client/server system to control VPP
            # as a service
            self.engine.install_supervisor()
            self.engine.start_vpp()

    def restart_vpp_in_all_containers(self):
        """Restart VPP in all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.restart_vpp()

    def verify_vpp_in_all_containers(self):
        """Verify that VPP is installed and running in all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.verify_vpp()

    def configure_vpp_in_all_containers(self, chain_topology, **kwargs):
        """Configure VPP in all containers.

        :param chain_topology: Topology used for chaining containers can be
            chain or cross_horiz. Chain topology is using 1 memif pair per
            container. Cross_horiz topology is using 1 memif and 1 physical
            interface in container (only single container can be configured).
        :param kwargs: Named parameters.
        :type chain_topology: str
        :param kwargs: dict
        """
        # Count number of DUTs based on node's host information
        dut_cnt = len(Counter([self.containers[container].node['host']
                               for container in self.containers]))
        mod = len(self.containers)/dut_cnt

        for i, container in enumerate(self.containers):
            mid1 = i % mod + 1
            mid2 = i % mod + 1
            sid1 = i % mod * 2 + 1
            sid2 = i % mod * 2 + 2
            self.engine.container = self.containers[container]
            guest_dir = self.engine.container.mnt[0].split(':')[1]

            if chain_topology == 'chain':
                self._configure_vpp_chain_l2xc(mid1=mid1, mid2=mid2,
                                               sid1=sid1, sid2=sid2,
                                               guest_dir=guest_dir,
                                               **kwargs)
            elif chain_topology == 'cross_horiz':
                self._configure_vpp_cross_horiz(mid1=mid1, mid2=mid2,
                                                sid1=sid1, sid2=sid2,
                                                guest_dir=guest_dir,
                                                **kwargs)
            elif chain_topology == 'chain_functional':
                self._configure_vpp_chain_functional(mid1=mid1, mid2=mid2,
                                                     sid1=sid1, sid2=sid2,
                                                     guest_dir=guest_dir,
                                                     **kwargs)
            elif chain_topology == 'chain_ip4':
                self._configure_vpp_chain_ip4(mid1=mid1, mid2=mid2,
                                              sid1=sid1, sid2=sid2,
                                              guest_dir=guest_dir,
                                              **kwargs)
            elif chain_topology == 'chain_vswitch':
                self._configure_vpp_chain_vswitch(mid1=mid1, mid2=mid2,
                                                  sid1=sid1, sid2=sid2,
                                                  guest_dir=guest_dir,
                                                  **kwargs)
            elif chain_topology == 'chain_ipsec':
                self._configure_vpp_chain_ipsec(mid1=mid1, mid2=mid2,
                                                sid1=sid1, sid2=sid2,
                                                guest_dir=guest_dir,
                                                nf_instance=(i % mod + 1),
                                                **kwargs)
            elif chain_topology == 'pipeline_ip4':
                self._configure_vpp_pipeline_ip4(mid1=mid1, mid2=mid2,
                                                 sid1=sid1, sid2=sid2,
                                                 guest_dir=guest_dir,
                                                 **kwargs)
            else:
                raise RuntimeError('Container topology {name} not implemented'.
                                   format(name=chain_topology))

    def _configure_vpp_chain_l2xc(self, **kwargs):
        """Configure VPP in chain topology with l2xc.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        self.engine.create_vpp_startup_config()
        self.engine.create_vpp_exec_config(
            'memif_create_chain_l2xc.exec',
            mid1=kwargs['mid1'], mid2=kwargs['mid2'],
            sid1=kwargs['sid1'], sid2=kwargs['sid2'],
            socket1='{guest_dir}/memif-{c.name}-{sid1}'.
            format(c=self.engine.container, **kwargs),
            socket2='{guest_dir}/memif-{c.name}-{sid2}'.
            format(c=self.engine.container, **kwargs))

    def _configure_vpp_cross_horiz(self, **kwargs):
        """Configure VPP in cross horizontal topology (single memif).

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        if 'DUT1' in self.engine.container.name:
            if_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs['dut1_if'])
            if_name = Topology.get_interface_name(
                self.engine.container.node, kwargs['dut1_if'])
        if 'DUT2' in self.engine.container.name:
            if_pci = Topology.get_interface_pci_addr(
                self.engine.container.node, kwargs['dut2_if'])
            if_name = Topology.get_interface_name(
                self.engine.container.node, kwargs['dut2_if'])
        self.engine.create_vpp_startup_config_dpdk_dev(if_pci)
        self.engine.create_vpp_exec_config(
            'memif_create_cross_horizon.exec',
            mid1=kwargs['mid1'], sid1=kwargs['sid1'], if_name=if_name,
            socket1='{guest_dir}/memif-{c.name}-{sid1}'.
            format(c=self.engine.container, **kwargs))

    def _configure_vpp_chain_functional(self, **kwargs):
        """Configure VPP in chain topology with l2xc (functional).

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        self.engine.create_vpp_startup_config_func_dev()
        self.engine.create_vpp_exec_config(
            'memif_create_chain_functional.exec',
            mid1=kwargs['mid1'], mid2=kwargs['mid2'],
            sid1=kwargs['sid1'], sid2=kwargs['sid2'],
            socket1='{guest_dir}/memif-{c.name}-{sid1}'.
            format(c=self.engine.container, **kwargs),
            socket2='{guest_dir}/memif-{c.name}-{sid2}'.
            format(c=self.engine.container, **kwargs),
            rx_mode='interrupt')

    def _configure_vpp_chain_ip4(self, **kwargs):
        """Configure VPP in chain topology with ip4.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        self.engine.create_vpp_startup_config()

        vif1_mac = kwargs['tg_if1_mac'] \
            if (kwargs['mid1'] - 1) % kwargs['nodes'] + 1 == 1 \
            else '52:54:00:00:{0:02X}:02'.format(kwargs['mid1'] - 1)
        vif2_mac = kwargs['tg_if2_mac'] \
            if (kwargs['mid2'] - 1) % kwargs['nodes'] + 1 == kwargs['nodes'] \
            else '52:54:00:00:{0:02X}:01'.format(kwargs['mid2'] + 1)
        self.engine.create_vpp_exec_config(
            'memif_create_chain_ip4.exec',
            mid1=kwargs['mid1'], mid2=kwargs['mid2'],
            sid1=kwargs['sid1'], sid2=kwargs['sid2'],
            socket1='{guest_dir}/memif-{c.name}-{sid1}'.
            format(c=self.engine.container, **kwargs),
            socket2='{guest_dir}/memif-{c.name}-{sid2}'.
            format(c=self.engine.container, **kwargs),
            mac1='52:54:00:00:{0:02X}:01'.format(kwargs['mid1']),
            mac2='52:54:00:00:{0:02X}:02'.format(kwargs['mid2']),
            vif1_mac=vif1_mac, vif2_mac=vif2_mac)

    def _configure_vpp_chain_vswitch(self, **kwargs):
        """Configure VPP as vswitch in container.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        if1_pci = Topology.get_interface_pci_addr(
            self.engine.container.node, kwargs['dut2_if1'])
        if2_pci = Topology.get_interface_pci_addr(
            self.engine.container.node, kwargs['dut2_if2'])
        if_red_name = Topology.get_interface_name(
            self.engine.container.node, kwargs['dut2_if1'])
        if_black_name = Topology.get_interface_name(
            self.engine.container.node, kwargs['dut2_if2'])
        n_instances = int(kwargs['n_instances'])
        rxq = 1
        if 'rxq' in kwargs:
            rxq = int(kwargs['rxq'])
        heapsize = '4G'
        if 'heapsize' in kwargs:
            heapsize = kwargs['heapsize']
        buffers = 215040
        if 'buffers' in kwargs:
            buffers = int(kwargs['buffers'])
        nodes = kwargs['nodes']
        cpuset_cpus = CpuUtils.get_affinity_nf(nodes, 'DUT2', nf_chains=1,
                                               nf_nodes=1, nf_chain=1,
                                               nf_node=1, vs_dtc=0, nf_dtc=4,
                                               nf_mtcr=1, nf_dtcr=1)
        self.engine.create_vpp_startup_config_vswitch(cpuset_cpus, rxq,
                                                      buffers, heapsize,
                                                      if1_pci, if2_pci)
        script = []
        script.append(
            'create memif socket id 1 filename {socket1}\n'
            'create memif socket id 2 filename {socket2}\n'
            'create bridge-domain 1 learn 1 forward 1 uu-flood 1 flood 1 '
            'arp-term 0\n'
            'create bridge-domain 2 learn 1 forward 1 uu-flood 1 flood 1 '
            'arp-term 0\n'
            'set interface l2 bridge {if_red_name} 1\n'
            'set interface l2 bridge {if_black_name} 2\n'
            'set interface state {if_red_name} up\n'
            'set interface state {if_black_name} up\n\n'
            .format(socket1='{guest_dir}/memif-vswitch-1'.format(**kwargs),
                    socket2='{guest_dir}/memif-vswitch-2'.format(**kwargs),
                    if_red_name=if_red_name,
                    if_black_name=if_black_name))

        for i in range(1, n_instances + 1):
            script.append(
                'create interface memif id {mid1} socket-id {sid1} master\n'
                'set interface state memif{sid1}/{mid1} up\n'
                'set interface l2 bridge memif{sid1}/{mid1} 1\n\n'

                'create interface memif id {mid2} socket-id {sid2} master\n'
                'set interface state memif{sid2}/{mid2} up\n'
                'set interface l2 bridge memif{sid2}/{mid2} 2\n\n'

                'set ip arp memif{sid2}/{mid2} {tg_if2_ip4} {tg_if2_mac} '
                'static\n\n'.format(
                    mid1=i,
                    mid2=i,
                    sid1='1',
                    sid2='2',
                    tg_if2_ip4=kwargs['tg_if2_ip4'],
                    tg_if2_mac=kwargs['tg_if2_mac']))
            self.engine.execute('echo "{script_content}" > /tmp/running.exec'
                                .format(script_content=''.join(script)))

    def _configure_vpp_chain_ipsec(self, **kwargs):
        """Configure VPP in container with memifs.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        nf_nodes = int(kwargs['nf_nodes'])
        nf_instance = int(kwargs['nf_instance'])
        nodes = kwargs['nodes']
        cpuset_cpus = CpuUtils.get_affinity_nf(nodes, 'DUT2', nf_chains=1,
                                               nf_nodes=nf_nodes, nf_chain=1,
                                               nf_node=nf_instance, vs_dtc=10,
                                               nf_dtc=1, nf_mtcr=1, nf_dtcr=1)
        self.engine.create_vpp_startup_config_ipsec(cpuset_cpus)
        script = []
        local_ip_base = kwargs['dut2_if1_ip4'].rsplit('.', 1)[0]
        remote_ip_base = kwargs['dut2_if2_ip4'].rsplit('.', 1)[0]
        script.append(
            'create memif socket id 1 filename {socket1}\n'
            'create interface memif id {mid1} socket-id {sid1} '
            'hw-addr {mac1} slave\n'
            'set interface ip address memif{sid1}/{mid1} {local_ip}/24\n'
            'set interface state memif{sid1}/{mid1} up\n\n'

            'create memif socket id 2 filename {socket2}\n'
            'create interface memif id {mid2} socket-id {sid2} '
            'hw-addr {mac2} slave\n'
            'set interface ip address memif{sid2}/{mid1} {remote_ip}/24\n'
            'set interface state memif{sid2}/{mid2} up\n\n'

            'set ip arp memif{sid2}/{mid2} {tg_if2_ip4} {tg_if2_mac} static\n'
            'ip route add {raddr_ip4}/8 via {tg_if2_ip4} memif{sid2}/{mid2}\n'
            .format(socket1='{guest_dir}/memif-vswitch-1'.format(**kwargs),
                    socket2='{guest_dir}/memif-vswitch-2'.format(**kwargs),
                    mid1=nf_instance,
                    mid2=nf_instance,
                    sid1='1',
                    sid2='2',
                    mac1='02:01:00:00:00:{0:02X}'.format(nf_instance - 1),
                    mac2='02:02:00:00:00:{0:02X}'.format(nf_instance - 1),
                    tg_if2_ip4=kwargs['tg_if2_ip4'],
                    tg_if2_mac=kwargs['tg_if2_mac'],
                    raddr_ip4=kwargs['raddr_ip4'],
                    local_ip='{base}.{instance}'.format(base=local_ip_base,
                                                        instance=nf_instance),
                    remote_ip='{base}.{instance}'.format(base=remote_ip_base,
                                                         instance=nf_instance)
                   ))
        self.engine.execute('echo "{script_content}" > /tmp/running.exec'
                            .format(script_content=''.join(script)))

    def _configure_vpp_pipeline_ip4(self, **kwargs):
        """Configure VPP in pipeline topology with ip4.

        :param kwargs: Named parameters.
        :param kwargs: dict
        """
        self.engine.create_vpp_startup_config()
        node = (kwargs['mid1'] - 1) % kwargs['nodes'] + 1
        mid1 = kwargs['mid1']
        mid2 = kwargs['mid2']
        role1 = 'master'
        role2 = 'master' \
            if node == kwargs['nodes'] or node == kwargs['nodes'] and node == 1\
            else 'slave'
        kwargs['mid2'] = kwargs['mid2'] \
            if node == kwargs['nodes'] or node == kwargs['nodes'] and node == 1\
            else kwargs['mid2'] + 1
        vif1_mac = kwargs['tg_if1_mac'] \
            if (kwargs['mid1'] - 1) % kwargs['nodes'] + 1 == 1 \
            else '52:54:00:00:{0:02X}:02'.format(kwargs['mid1'] - 1)
        vif2_mac = kwargs['tg_if2_mac'] \
            if (kwargs['mid2'] - 1) % kwargs['nodes'] + 1 == kwargs['nodes'] \
            else '52:54:00:00:{0:02X}:01'.format(kwargs['mid2'] + 1)
        socket1 = '{guest_dir}/memif-{c.name}-{sid1}'.\
            format(c=self.engine.container, **kwargs) \
            if node == 1 else '{guest_dir}/memif-pipe-{mid1}'.\
            format(c=self.engine.container, **kwargs)
        socket2 = '{guest_dir}/memif-{c.name}-{sid2}'.\
            format(c=self.engine.container, **kwargs) \
            if node == 1 and kwargs['nodes'] == 1 or node == kwargs['nodes'] \
            else '{guest_dir}/memif-pipe-{mid2}'.\
            format(c=self.engine.container, **kwargs)

        self.engine.create_vpp_exec_config(
            'memif_create_pipeline_ip4.exec',
            mid1=kwargs['mid1'], mid2=kwargs['mid2'],
            sid1=kwargs['sid1'], sid2=kwargs['sid2'],
            socket1=socket1, socket2=socket2, role1=role1, role2=role2,
            mac1='52:54:00:00:{0:02X}:01'.format(mid1),
            mac2='52:54:00:00:{0:02X}:02'.format(mid2),
            vif1_mac=vif1_mac, vif2_mac=vif2_mac)

    def gather_vpp_statistics_from_all_containers(self):
        """Gather VPP statistics from all containers."""
        cmd = (
            'set -x;'
            'vppctl show int;'
            'vppctl show memif;'
            'vppctl show hardware detail;'
            'vppctl show errors;'
            'vppctl show runtime')
        self.execute_on_all_containers(cmd)

    def stop_all_containers(self):
        """Stop all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.stop()

    def destroy_all_containers(self):
        """Destroy all containers."""
        for container in self.containers:
            self.engine.container = self.containers[container]
            self.engine.destroy()


class ContainerEngine(object):
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

    def install_supervisor(self):
        """Install supervisord inside a container."""
        if isinstance(self, LXC):
            self.execute('sleep 3; apt-get update')
            self.execute('apt-get install -y supervisor')
        self.execute('echo "{config}" > {config_file} && '
                     'supervisord -c {config_file}'.
                     format(
                         config='[unix_http_server]\n'
                         'file  = /tmp/supervisor.sock\n\n'
                         '[rpcinterface:supervisor]\n'
                         'supervisor.rpcinterface_factory = '
                         'supervisor.rpcinterface:make_main_rpcinterface\n\n'
                         '[supervisorctl]\n'
                         'serverurl = unix:///tmp/supervisor.sock\n\n'
                         '[supervisord]\n'
                         'pidfile = /tmp/supervisord.pid\n'
                         'identifier = supervisor\n'
                         'directory = /tmp\n'
                         'logfile=/tmp/supervisord.log\n'
                         'loglevel=debug\n'
                         'nodaemon=false\n\n',
                         config_file=SUPERVISOR_CONF))

    def start_vpp(self):
        """Start VPP inside a container."""
        self.execute('echo "{config}" >> {config_file}'.
                     format(
                         config='[program:vpp]\n'
                         'command=/usr/bin/vpp -c /etc/vpp/startup.conf\n'
                         'autostart=false\n'
                         'autorestart=false\n'
                         'redirect_stderr=true\n'
                         'priority=1',
                         config_file=SUPERVISOR_CONF))
        self.execute('supervisorctl reload')
        self.execute('supervisorctl start vpp')

    def restart_vpp(self):
        """Restart VPP service inside a container."""
        self.execute('supervisorctl restart vpp')
        self.execute('cat /tmp/supervisord.log')

    # TODO Rewrite .execute to accept retries parameter and get rid of this
    # function.
    def verify_vpp(self, retries=120, retry_wait=1):
        """Verify that VPP is installed and running inside container.

        :param retries: Check for VPP for this number of times Default: 120
        :param retry_wait: Wait for this number of seconds between retries.

        """
        cmd = ('vppctl show pci 2>&1 | '
               'fgrep -v "Connection refused" | '
               'fgrep -v "No such file or directory"')

        for _ in range(retries + 1):
            try:
                self.execute(cmd)
                break
            except RuntimeError:
                sleep(retry_wait)
        else:
            msg = 'VPP did not come up in container: {name}'.format(
                name=self.container.name)
            raise RuntimeError(msg)

    def create_base_vpp_startup_config(self, cpuset_cpus=None):
        """Create base startup configuration of VPP on container.

        :returns: Base VPP startup configuration.
        :rtype: VppConfigGenerator
        """
        if cpuset_cpus is None:
            cpuset_cpus = self.container.cpuset_cpus

        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(self.container.node)
        vpp_config.add_unix_cli_listen()
        vpp_config.add_unix_nodaemon()
        vpp_config.add_unix_exec('/tmp/running.exec')
        vpp_config.add_socksvr()
        # We will pop the first core from the list to be a main core
        vpp_config.add_cpu_main_core(str(cpuset_cpus.pop(0)))
        # If more cores in the list, the rest will be used as workers.
        if cpuset_cpus:
            corelist_workers = ','.join(str(cpu) for cpu in cpuset_cpus)
            vpp_config.add_cpu_corelist_workers(corelist_workers)

        return vpp_config

    def create_vpp_startup_config(self):
        """Create startup configuration of VPP without DPDK on container.
        """
        vpp_config = self.create_base_vpp_startup_config()
        vpp_config.add_plugin('disable', 'dpdk_plugin.so')

        # Apply configuration
        self.execute('mkdir -p /etc/vpp/')
        self.execute('echo "{config}" | tee /etc/vpp/startup.conf'
                     .format(config=vpp_config.get_config_str()))

    def create_vpp_startup_config_dpdk_dev(self, *devices):
        """Create startup configuration of VPP with DPDK on container.

        :param devices: List of PCI devices to add.
        :type devices: list
        """
        vpp_config = self.create_base_vpp_startup_config()
        vpp_config.add_dpdk_dev(*devices)
        vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_dpdk_log_level('debug')
        vpp_config.add_plugin('disable', 'default')
        vpp_config.add_plugin('enable', 'dpdk_plugin.so')
        vpp_config.add_plugin('enable', 'memif_plugin.so')

        # Apply configuration
        self.execute('mkdir -p /etc/vpp/')
        self.execute('echo "{config}" | tee /etc/vpp/startup.conf'
                     .format(config=vpp_config.get_config_str()))

    def create_vpp_startup_config_func_dev(self):
        """Create startup configuration of VPP on container for functional
        vpp_device tests.
        """
        # Create config instance
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(self.container.node)
        vpp_config.add_unix_cli_listen()
        vpp_config.add_unix_nodaemon()
        vpp_config.add_unix_exec('/tmp/running.exec')
        vpp_config.add_socksvr()
        vpp_config.add_plugin('disable', 'dpdk_plugin.so')

        # Apply configuration
        self.execute('mkdir -p /etc/vpp/')
        self.execute('echo "{config}" | tee /etc/vpp/startup.conf'
                     .format(config=vpp_config.get_config_str()))

    def create_vpp_startup_config_vswitch(self, cpuset_cpus, rxq, buffers,
                                          heapsize, *devices):
        """Create startup configuration of VPP vswitch.

        :param devices: List of PCI devices to add.
        :type devices: list
        """
        vpp_config = self.create_base_vpp_startup_config(cpuset_cpus)
        vpp_config.add_heapsize(heapsize)
        vpp_config.add_ip_heap_size(heapsize)
        vpp_config.add_dpdk_dev(*devices)
        vpp_config.add_dpdk_log_level('debug')
        vpp_config.add_plugin('disable', 'default')
        vpp_config.add_plugin('enable', 'dpdk_plugin.so')
        vpp_config.add_plugin('enable', 'memif_plugin.so')
        vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_buffers_per_numa(buffers)
        vpp_config.add_dpdk_dev_default_rxq(rxq)

        # Apply configuration
        self.execute('mkdir -p /etc/vpp/')
        self.execute('echo "{config}" | tee /etc/vpp/startup.conf'
                     .format(config=vpp_config.get_config_str()))

    def create_vpp_startup_config_ipsec(self, cpuset_cpus):
        """Create startup configuration of VPP with IPsec on container.
        """
        vpp_config = self.create_base_vpp_startup_config(cpuset_cpus)
        vpp_config.add_heapsize('4G')
        vpp_config.add_ip_heap_size('4G')

        vpp_config.add_plugin('disable', 'default')
        vpp_config.add_plugin('enable', 'memif_plugin.so')
        vpp_config.add_plugin('enable', 'crypto_ia32_plugin.so')
        vpp_config.add_plugin('enable', 'crypto_ipsecmb_plugin.so')
        vpp_config.add_plugin('enable', 'crypto_openssl_plugin.so')

        # Apply configuration
        self.execute('mkdir -p /etc/vpp/')
        self.execute('echo "{config}" | tee /etc/vpp/startup.conf'
                     .format(config=vpp_config.get_config_str()))

    def create_vpp_exec_config(self, template_file, **kwargs):
        """Create VPP exec configuration on container.

        :param template_file: File name of a template script.
        :param kwargs: Parameters for script.
        :type template_file: str
        :type kwargs: dict
        """
        running = '/tmp/running.exec'

        template = '{res}/{tpl}'.format(
            res=Constants.RESOURCES_TPL_CONTAINER, tpl=template_file)

        with open(template, 'r') as src_file:
            src = Template(src_file.read())
            self.execute('echo "{out}" > {running}'.format(
                out=src.safe_substitute(**kwargs), running=running))

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
            'cgset -r cpuset.cpu_exclusive=0 /')
        if int(ret) != 0:
            raise RuntimeError('Failed to apply cgroup settings.')

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'cgset -r cpuset.mem_exclusive=0 /')
        if int(ret) != 0:
            raise RuntimeError('Failed to apply cgroup settings.')

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'cgcreate -g cpuset:/{name}'.format(name=name))
        if int(ret) != 0:
            raise RuntimeError('Failed to copy cgroup settings from root.')

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'cgset -r cpuset.cpu_exclusive=0 /{name}'.format(name=name))
        if int(ret) != 0:
            raise RuntimeError('Failed to apply cgroup settings.')

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'cgset -r cpuset.mem_exclusive=0 /{name}'.format(name=name))
        if int(ret) != 0:
            raise RuntimeError('Failed to apply cgroup settings.')


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

        target_arch = 'arm64' \
            if Topology.get_node_arch(self.container.node) == 'aarch64' \
            else 'amd64'

        image = self.container.image if self.container.image else\
            "-d ubuntu -r bionic -a {arch}".format(arch=target_arch)

        cmd = 'lxc-create -t download --name {c.name} -- {image} '\
            '--no-validate'.format(c=self.container, image=image)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=1800)
        if int(ret) != 0:
            raise RuntimeError('Failed to create container.')

        self._configure_cgroup('lxc')

    def create(self):
        """Create/deploy an application inside a container on system.

        :raises RuntimeError: If creating the container fails.
        """
        if self.container.mnt:
            for mount in self.container.mnt:
                host_dir, guest_dir = mount.split(':')
                options = 'bind,create=dir' \
                    if guest_dir.endswith('/') else 'bind,create=file'
                entry = 'lxc.mount.entry = {host_dir} '\
                    '/var/lib/lxc/{c.name}/rootfs{guest_dir} none ' \
                    '{options} 0 0'.format(c=self.container,
                                           host_dir=host_dir,
                                           guest_dir=guest_dir,
                                           options=options)
                ret, _, _ = self.container.ssh.exec_command_sudo(
                    "sh -c 'echo \"{e}\" >> /var/lib/lxc/{c.name}/config'".
                    format(e=entry, c=self.container))
                if int(ret) != 0:
                    raise RuntimeError('Failed to write {c.name} config.'
                                       .format(c=self.container))

        cpuset_cpus = '{0}'.format(
            ','.join('%s' % cpu for cpu in self.container.cpuset_cpus))\
            if self.container.cpuset_cpus else ''

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'lxc-start --name {c.name} --daemon'.
            format(c=self.container))
        if int(ret) != 0:
            raise RuntimeError('Failed to start container {c.name}.'.
                               format(c=self.container))
        self._lxc_wait('RUNNING')

        # Workaround for LXC to be able to allocate all cpus including isolated.
        ret, _, _ = self.container.ssh.exec_command_sudo(
            'cgset --copy-from / lxc/')
        if int(ret) != 0:
            raise RuntimeError('Failed to copy cgroup to LXC')

        ret, _, _ = self.container.ssh.exec_command_sudo(
            'lxc-cgroup --name {c.name} cpuset.cpus {cpus}'.
            format(c=self.container, cpus=cpuset_cpus))
        if int(ret) != 0:
            raise RuntimeError('Failed to set cpuset.cpus to container '
                               '{c.name}.'.format(c=self.container))

    def execute(self, command):
        """Start a process inside a running container.

        Runs the specified command inside the container specified by name. The
        container has to be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If running the command failed.
        """
        env = '--keep-env {0}'.format(
            ' '.join('--set-var %s' % env for env in self.container.env))\
            if self.container.env else ''

        cmd = "lxc-attach {env} --name {c.name} -- /bin/sh -c '{command}; "\
            "exit $?'".format(env=env, c=self.container, command=command)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret) != 0:
            raise RuntimeError('Failed to run command inside container '
                               '{c.name}.'.format(c=self.container))

    def stop(self):
        """Stop a container.

        :raises RuntimeError: If stopping the container failed.
        """
        cmd = 'lxc-stop --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to stop container {c.name}.'
                               .format(c=self.container))
        self._lxc_wait('STOPPED|FROZEN')

    def destroy(self):
        """Destroy a container.

        :raises RuntimeError: If destroying container failed.
        """
        cmd = 'lxc-destroy --force --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to destroy container {c.name}.'
                               .format(c=self.container))

    def info(self):
        """Query and shows information about a container.

        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = 'lxc-info --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))

    def system_info(self):
        """Check the current kernel for LXC support.

        :raises RuntimeError: If checking LXC support failed.
        """
        cmd = 'lxc-checkconfig'

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to check LXC support.')

    def is_container_running(self):
        """Check if container is running on node.

        :returns: True if container is running.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = 'lxc-info --no-humanize --state --name {c.name}'\
            .format(c=self.container)

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))
        return True if 'RUNNING' in stdout else False

    def is_container_present(self):
        """Check if container is existing on node.

        :returns: True if container is present.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = 'lxc-info --no-humanize --name {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        return False if int(ret) else True

    def _lxc_wait(self, state):
        """Wait for a specific container state.

        :param state: Specify the container state(s) to wait for.
        :type state: str
        :raises RuntimeError: If waiting for state of a container failed.
        """
        cmd = 'lxc-wait --name {c.name} --state "{s}"'\
            .format(c=self.container, s=state)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to wait for state "{s}" of container '
                               '{c.name}.'.format(s=state, c=self.container))


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
                if Topology.get_node_arch(self.container.node) == 'aarch64' \
                else Constants.DOCKER_SUT_IMAGE_UBUNTU
            setattr(self.container, 'image', img)

        cmd = 'docker pull {image}'.format(image=self.container.image)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=1800)
        if int(ret) != 0:
            raise RuntimeError('Failed to create container {c.name}.'
                               .format(c=self.container))

        if self.container.cpuset_cpus:
            self._configure_cgroup('docker')

    def create(self):
        """Create/deploy container.

        :raises RuntimeError: If creating a container failed.
        """
        cpuset_cpus = '--cpuset-cpus={0}'.format(
            ','.join('%s' % cpu for cpu in self.container.cpuset_cpus))\
            if self.container.cpuset_cpus else ''

        cpuset_mems = '--cpuset-mems={0}'.format(self.container.cpuset_mems)\
            if self.container.cpuset_mems is not None else ''
        # Temporary workaround - disabling due to bug in memif
        cpuset_mems = ''

        env = '{0}'.format(
            ' '.join('--env %s' % env for env in self.container.env))\
            if self.container.env else ''

        command = '{0}'.format(self.container.command)\
            if self.container.command else ''

        publish = '{0}'.format(
            ' '.join('--publish %s' % var for var in self.container.publish))\
            if self.container.publish else ''

        volume = '{0}'.format(
            ' '.join('--volume %s' % mnt for mnt in self.container.mnt))\
            if self.container.mnt else ''

        cmd = 'docker run '\
            '--privileged --detach --interactive --tty --rm '\
            '--cgroup-parent docker {cpuset_cpus} {cpuset_mems} {publish} '\
            '{env} {volume} --name {container.name} {container.image} '\
            '{command}'.format(cpuset_cpus=cpuset_cpus, cpuset_mems=cpuset_mems,
                               container=self.container, command=command,
                               env=env, publish=publish, volume=volume)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to create container {c.name}'
                               .format(c=self.container))

        self.info()

    def execute(self, command):
        """Start a process inside a running container.

        Runs the specified command inside the container specified by name. The
        container has to be running already.

        :param command: Command to run inside container.
        :type command: str
        :raises RuntimeError: If running the command in a container failed.
        """
        cmd = "docker exec --interactive {c.name} /bin/sh -c '{command}; "\
            "exit $?'".format(c=self.container, command=command)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret) != 0:
            raise RuntimeError('Failed to execute command in container '
                               '{c.name}.'.format(c=self.container))

    def stop(self):
        """Stop running container.

        :raises RuntimeError: If stopping a container failed.
        """
        cmd = 'docker stop {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to stop container {c.name}.'
                               .format(c=self.container))

    def destroy(self):
        """Remove a container.

        :raises RuntimeError: If removing a container failed.
        """
        cmd = 'docker rm --force {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to destroy container {c.name}.'
                               .format(c=self.container))

    def info(self):
        """Return low-level information on Docker objects.

        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = 'docker inspect {c.name}'.format(c=self.container)

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))

    def system_info(self):
        """Display the docker system-wide information.

        :raises RuntimeError: If displaying system information failed.
        """
        cmd = 'docker system info'

        ret, _, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get system info.')

    def is_container_present(self):
        """Check if container is present on node.

        :returns: True if container is present.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = 'docker ps --all --quiet --filter name={c.name}'\
            .format(c=self.container)

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))
        return True if stdout else False

    def is_container_running(self):
        """Check if container is running on node.

        :returns: True if container is running.
        :rtype: bool
        :raises RuntimeError: If getting info about a container failed.
        """
        cmd = 'docker ps --quiet --filter name={c.name}'\
            .format(c=self.container)

        ret, stdout, _ = self.container.ssh.exec_command_sudo(cmd)
        if int(ret) != 0:
            raise RuntimeError('Failed to get info about container {c.name}.'
                               .format(c=self.container))
        return True if stdout else False


class Container(object):
    """Container class."""

    def __init__(self):
        """Initialize Container object."""
        pass

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
            if attr == 'node':
                self.__dict__['ssh'] = SSH()
                self.__dict__['ssh'].connect(value)
            self.__dict__[attr] = value
        else:
            # Updating attribute base of type
            if isinstance(self.__dict__[attr], list):
                self.__dict__[attr].append(value)
            else:
                self.__dict__[attr] = value
