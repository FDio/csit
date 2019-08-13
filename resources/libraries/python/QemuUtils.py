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

"""QEMU utilities library."""

# Disable due to pylint bug
# pylint: disable=no-name-in-module,import-error
from distutils.version import StrictVersion
import json
from re import match
from string import Template
from time import sleep

from robot.api import logger
from resources.libraries.python.Constants import Constants
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
from resources.libraries.python.VPPUtil import VPPUtil
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology

__all__ = ["QemuUtils"]


class QemuUtils(object):
    """QEMU utilities."""

    # Use one instance of class per tests.
    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self, node, qemu_id=1, smp=1, mem=512, vnf=None,
                 img=Constants.QEMU_VM_IMAGE):
        """Initialize QemuUtil class.

        :param node: Node to run QEMU on.
        :param qemu_id: QEMU identifier.
        :param smp: Number of virtual SMP units (cores).
        :param mem: Amount of memory.
        :param vnf: Network function workload.
        :param img: QEMU disk image or kernel image path.
        :type node: dict
        :type qemu_id: int
        :type smp: int
        :type mem: int
        :type vnf: str
        :type img: str
        """
        self._vhost_id = 0
        self._node = node
        self._arch = Topology.get_node_arch(self._node)
        dpdk_target = 'arm64-armv8a' if self._arch == 'aarch64' \
            else 'x86_64-native'
        self._testpmd_path = '{path}/{dpdk_target}-linuxapp-gcc/app'\
            .format(path=Constants.QEMU_VM_DPDK, dpdk_target=dpdk_target)
        self._vm_info = {
            'host': node['host'],
            'type': NodeType.VM,
            'port': 10021 + qemu_id,
            'serial': 4555 + qemu_id,
            'username': 'cisco',
            'password': 'cisco',
            'interfaces': {},
        }
        if node['port'] != 22:
            self._vm_info['host_port'] = node['port']
            self._vm_info['host_username'] = node['username']
            self._vm_info['host_password'] = node['password']
        # Input Options.
        self._opt = dict()
        self._opt['qemu_id'] = qemu_id
        self._opt['mem'] = int(mem)
        self._opt['smp'] = int(smp)
        self._opt['img'] = img
        self._opt['vnf'] = vnf
        # Temporary files.
        self._temp = dict()
        self._temp['pidfile'] = '/var/run/qemu_{id}.pid'.format(id=qemu_id)
        if img == Constants.QEMU_VM_IMAGE:
            self._opt['vm_type'] = 'nestedvm'
            self._temp['qmp'] = '/var/run/qmp_{id}.sock'.format(id=qemu_id)
            self._temp['qga'] = '/var/run/qga_{id}.sock'.format(id=qemu_id)
        elif img == Constants.QEMU_VM_KERNEL:
            self._opt['img'], _ = exec_cmd_no_error(
                node,
                'ls -1 {img}* | tail -1'.format(img=Constants.QEMU_VM_KERNEL),
                message='Qemu Kernel VM image not found!')
            self._opt['vm_type'] = 'kernelvm'
            self._temp['log'] = '/tmp/serial_{id}.log'.format(id=qemu_id)
            self._temp['ini'] = '/etc/vm_init_{id}.conf'.format(id=qemu_id)
            self._opt['initrd'], _ = exec_cmd_no_error(
                node,
                'ls -1 {initrd}* | tail -1'.format(
                    initrd=Constants.QEMU_VM_KERNEL_INITRD),
                message='Qemu Kernel initrd image not found!')
        else:
            raise RuntimeError('QEMU: Unknown VM image option: {}'.format(img))
        # Computed parameters for QEMU command line.
        self._params = OptionString(prefix='-')
        self.add_params()

    def add_params(self):
        """Set QEMU command line parameters."""
        self.add_default_params()
        if self._opt.get('vm_type', '') == 'nestedvm':
            self.add_nestedvm_params()
        elif self._opt.get('vm_type', '') == 'kernelvm':
            self.add_kernelvm_params()
        else:
            raise RuntimeError('QEMU: Unsupported VM type!')

    def add_default_params(self):
        """Set default QEMU command line parameters."""
        self._params.add('daemonize')
        self._params.add('nodefaults')
        self._params.add_with_value('name', 'vnf{qemu},debug-threads=on'.format(
            qemu=self._opt.get('qemu_id')))
        self._params.add('no-user-config')
        self._params.add_with_value('monitor', 'none')
        self._params.add_with_value('display', 'none')
        self._params.add_with_value('vga', 'none')
        self._params.add('enable-kvm')
        self._params.add_with_value('pidfile', self._temp.get('pidfile'))
        self._params.add_with_value('cpu', 'host')

        if self._arch == 'aarch64':
            machine_args = 'virt,accel=kvm,usb=off,mem-merge=off,gic-version=3'
        else:
            machine_args = 'pc,accel=kvm,usb=off,mem-merge=off'
        self._params.add_with_value(
            'machine', machine_args)
        self._params.add_with_value(
            'smp', '{smp},sockets=1,cores={smp},threads=1'.format(
                smp=self._opt.get('smp')))
        self._params.add_with_value(
            'object', 'memory-backend-file,id=mem,size={mem}M,'
            'mem-path=/dev/hugepages,share=on'.format(mem=self._opt.get('mem')))
        self._params.add_with_value(
            'm', '{mem}M'.format(mem=self._opt.get('mem')))
        self._params.add_with_value('numa', 'node,memdev=mem')
        self._params.add_with_value('balloon', 'none')

    def add_nestedvm_params(self):
        """Set NestedVM QEMU parameters."""
        self._params.add_with_value(
            'net', 'nic,macaddr=52:54:00:00:{qemu:02x}:ff'.format(
                qemu=self._opt.get('qemu_id')))
        self._params.add_with_value(
            'net', 'user,hostfwd=tcp::{info[port]}-:22'.format(
                info=self._vm_info))
        # TODO: Remove try except after fully migrated to Bionic or
        # qemu_set_node is removed.
        try:
            locking = ',file.locking=off'\
                if self.qemu_version(version='2.10') else ''
        except AttributeError:
            locking = ''
        self._params.add_with_value(
            'drive', 'file={img},format=raw,cache=none,if=virtio{locking}'.
            format(img=self._opt.get('img'), locking=locking))
        self._params.add_with_value(
            'qmp', 'unix:{qmp},server,nowait'.format(qmp=self._temp.get('qmp')))
        self._params.add_with_value(
            'chardev', 'socket,host=127.0.0.1,port={info[serial]},'
            'id=gnc0,server,nowait'.format(info=self._vm_info))
        self._params.add_with_value('device', 'isa-serial,chardev=gnc0')
        self._params.add_with_value(
            'chardev', 'socket,path={qga},server,nowait,id=qga0'.format(
                qga=self._temp.get('qga')))
        self._params.add_with_value('device', 'isa-serial,chardev=qga0')

    def add_kernelvm_params(self):
        """Set KernelVM QEMU parameters."""
        console = 'ttyAMA0' if self._arch == 'aarch64' else 'ttyS0'
        self._params.add_with_value('serial', 'file:{log}'.format(
            log=self._temp.get('log')))
        self._params.add_with_value(
            'fsdev', 'local,id=root9p,path=/,security_model=none')
        self._params.add_with_value(
            'device', 'virtio-9p-pci,fsdev=root9p,mount_tag=virtioroot')
        self._params.add_with_value(
            'kernel', '{img}'.format(img=self._opt.get('img')))
        self._params.add_with_value(
            'initrd', '{initrd}'.format(initrd=self._opt.get('initrd')))
        self._params.add_with_value(
            'append', '"ro rootfstype=9p rootflags=trans=virtio '
                      'root=virtioroot console={console} tsc=reliable '
                      'hugepages=256 init={init} fastboot"'.format(
                          console=console, init=self._temp.get('ini')))

    def create_kernelvm_config_vpp(self, **kwargs):
        """Create QEMU VPP config files.

        :param kwargs: Key-value pairs to replace content of VPP configuration
            file.
        :type kwargs: dict
        """
        startup = ('/etc/vpp/vm_startup_{id}.conf'.
                   format(id=self._opt.get('qemu_id')))
        running = ('/etc/vpp/vm_running_{id}.exec'.
                   format(id=self._opt.get('qemu_id')))

        self._temp['startup'] = startup
        self._temp['running'] = running
        self._opt['vnf_bin'] = ('/usr/bin/vpp -c {startup}'.
                                format(startup=startup))

        # Create VPP startup configuration.
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(self._node)
        vpp_config.add_unix_nodaemon()
        vpp_config.add_unix_cli_listen()
        vpp_config.add_unix_exec(running)
        vpp_config.add_socksvr()
        vpp_config.add_cpu_main_core('0')
        if self._opt.get('smp') > 1:
            vpp_config.add_cpu_corelist_workers('1-{smp}'.format(
                smp=self._opt.get('smp')-1))
        vpp_config.add_dpdk_dev('0000:00:06.0', '0000:00:07.0')
        vpp_config.add_dpdk_dev_default_rxq(kwargs['queues'])
        vpp_config.add_dpdk_log_level('debug')
        if not kwargs['jumbo_frames']:
            vpp_config.add_dpdk_no_multi_seg()
            vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_plugin('disable', 'default')
        vpp_config.add_plugin('enable', 'dpdk_plugin.so')
        vpp_config.write_config(startup)

        # Create VPP running configuration.
        template = '{res}/{tpl}.exec'.format(res=Constants.RESOURCES_TPL_VM,
                                             tpl=self._opt.get('vnf'))
        exec_cmd_no_error(self._node, 'rm -f {running}'.format(running=running),
                          sudo=True)

        with open(template, 'r') as src_file:
            src = Template(src_file.read())
            exec_cmd_no_error(
                self._node, "echo '{out}' | sudo tee {running}".format(
                    out=src.safe_substitute(**kwargs), running=running))

    def create_kernelvm_config_testpmd_io(self, **kwargs):
        """Create QEMU testpmd-io command line.

        :param kwargs: Key-value pairs to construct command line parameters.
        :type kwargs: dict
        """
        testpmd_cmd = DpdkUtil.get_testpmd_cmdline(
            eal_corelist='0-{smp}'.format(smp=self._opt.get('smp') - 1),
            eal_driver=False,
            eal_in_memory=True,
            pmd_num_mbufs=16384,
            pmd_rxq=kwargs['queues'],
            pmd_txq=kwargs['queues'],
            pmd_tx_offloads='0x0',
            pmd_disable_hw_vlan=False,
            pmd_nb_cores=str(self._opt.get('smp') - 1))

        self._opt['vnf_bin'] = ('{testpmd_path}/{testpmd_cmd}'.
                                format(testpmd_path=self._testpmd_path,
                                       testpmd_cmd=testpmd_cmd))

    def create_kernelvm_config_testpmd_mac(self, **kwargs):
        """Create QEMU testpmd-mac command line.

        :param kwargs: Key-value pairs to construct command line parameters.
        :type kwargs: dict
        """
        testpmd_cmd = DpdkUtil.get_testpmd_cmdline(
            eal_corelist='0-{smp}'.format(smp=self._opt.get('smp') - 1),
            eal_driver=False,
            eal_in_memory=True,
            pmd_num_mbufs=16384,
            pmd_fwd_mode='mac',
            pmd_eth_peer_0='0,{mac}'.format(mac=kwargs['vif1_mac']),
            pmd_eth_peer_1='1,{mac}'.format(mac=kwargs['vif2_mac']),
            pmd_rxq=kwargs['queues'],
            pmd_txq=kwargs['queues'],
            pmd_tx_offloads='0x0',
            pmd_disable_hw_vlan=False,
            pmd_nb_cores=str(self._opt.get('smp') - 1))

        self._opt['vnf_bin'] = ('{testpmd_path}/{testpmd_cmd}'.
                                format(testpmd_path=self._testpmd_path,
                                       testpmd_cmd=testpmd_cmd))

    def create_kernelvm_init(self, **kwargs):
        """Create QEMU init script.

        :param kwargs: Key-value pairs to replace content of init startup file.
        :type kwargs: dict
        """
        template = '{res}/init.sh'.format(res=Constants.RESOURCES_TPL_VM)
        init = self._temp.get('ini')
        exec_cmd_no_error(
            self._node, 'rm -f {init}'.format(init=init), sudo=True)

        with open(template, 'r') as src_file:
            src = Template(src_file.read())
            exec_cmd_no_error(
                self._node, "echo '{out}' | sudo tee {init}".format(
                    out=src.safe_substitute(**kwargs), init=init))
            exec_cmd_no_error(
                self._node, "chmod +x {init}".format(init=init), sudo=True)

    def configure_kernelvm_vnf(self, **kwargs):
        """Create KernelVM VNF configurations.

        :param kwargs: Key-value pairs for templating configs.
        :type kwargs: dict
        """
        if 'vpp' in self._opt.get('vnf'):
            self.create_kernelvm_config_vpp(**kwargs)
        elif 'testpmd_io' in self._opt.get('vnf'):
            self.create_kernelvm_config_testpmd_io(**kwargs)
        elif 'testpmd_mac' in self._opt.get('vnf'):
            self.create_kernelvm_config_testpmd_mac(**kwargs)
        else:
            raise RuntimeError('QEMU: Unsupported VNF!')
        self.create_kernelvm_init(vnf_bin=self._opt['vnf_bin'])

    def get_qemu_pids(self):
        """Get QEMU CPU pids.

        :returns: List of QEMU CPU pids.
        :rtype: list of str
        """
        command = ("grep -rwl 'CPU' /proc/$(sudo cat {pidfile})/task/*/comm ".
                   format(pidfile=self._temp.get('pidfile')))
        command += (r"| xargs dirname | sed -e 's/\/.*\///g' | uniq")

        stdout, _ = exec_cmd_no_error(self._node, command)
        return stdout.splitlines()

    def qemu_set_affinity(self, *host_cpus):
        """Set qemu affinity by getting thread PIDs via QMP and taskset to list
        of CPU cores. Function tries to execute 3 times to avoid race condition
        in getting thread PIDs.

        :param host_cpus: List of CPU cores.
        :type host_cpus: list
        """
        for _ in range(3):
            try:
                qemu_cpus = self.get_qemu_pids()

                if len(qemu_cpus) != len(host_cpus):
                    sleep(1)
                    continue
                for qemu_cpu, host_cpu in zip(qemu_cpus, host_cpus):
                    command = ('taskset -pc {host_cpu} {thread}'.
                               format(host_cpu=host_cpu, thread=qemu_cpu))
                    message = ('QEMU: Set affinity failed on {host}!'.
                               format(host=self._node['host']))
                    exec_cmd_no_error(self._node, command, sudo=True,
                                      message=message)
                break
            except (RuntimeError, ValueError):
                self.qemu_kill_all()
                raise
        else:
            self.qemu_kill_all()
            raise RuntimeError('Failed to set Qemu threads affinity!')

    def qemu_set_scheduler_policy(self):
        """Set scheduler policy to SCHED_RR with priority 1 for all Qemu CPU
        processes.

        :raises RuntimeError: Set scheduler policy failed.
        """
        try:
            qemu_cpus = self.get_qemu_pids()

            for qemu_cpu in qemu_cpus:
                command = ('chrt -r -p 1 {thread}'.
                           format(thread=qemu_cpu))
                message = ('QEMU: Set SCHED_RR failed on {host}'.
                           format(host=self._node['host']))
                exec_cmd_no_error(self._node, command, sudo=True,
                                  message=message)
        except (RuntimeError, ValueError):
            self.qemu_kill_all()
            raise

    def qemu_add_vhost_user_if(self, socket, server=True, jumbo_frames=False,
                               queue_size=None, queues=1):
        """Add Vhost-user interface.

        :param socket: Path of the unix socket.
        :param server: If True the socket shall be a listening socket.
        :param jumbo_frames: Set True if jumbo frames are used in the test.
        :param queue_size: Vring queue size.
        :param queues: Number of queues.
        :type socket: str
        :type server: bool
        :type jumbo_frames: bool
        :type queue_size: int
        :type queues: int
        """
        self._vhost_id += 1
        self._params.add_with_value(
            'chardev', 'socket,id=char{vhost},path={socket}{server}'.format(
                vhost=self._vhost_id, socket=socket,
                server=',server' if server is True else ''))
        self._params.add_with_value(
            'netdev', 'vhost-user,id=vhost{vhost},chardev=char{vhost},'
            'queues={queues}'.format(vhost=self._vhost_id, queues=queues))
        mac = ('52:54:00:00:{qemu:02x}:{vhost:02x}'.
               format(qemu=self._opt.get('qemu_id'), vhost=self._vhost_id))
        queue_size = ('rx_queue_size={queue_size},tx_queue_size={queue_size}'.
                      format(queue_size=queue_size)) if queue_size else ''
        mbuf = 'on,host_mtu=9200'
        self._params.add_with_value(
            'device', 'virtio-net-pci,netdev=vhost{vhost},mac={mac},'
            'addr={addr}.0,mq=on,vectors={vectors},csum=off,gso=off,'
            'guest_tso4=off,guest_tso6=off,guest_ecn=off,mrg_rxbuf={mbuf},'
            '{queue_size}'.format(
                addr=self._vhost_id+5, vhost=self._vhost_id, mac=mac,
                mbuf=mbuf if jumbo_frames else 'off', queue_size=queue_size,
                vectors=(2 * queues + 2)))

        # Add interface MAC and socket to the node dict.
        if_data = {'mac_address': mac, 'socket': socket}
        if_name = 'vhost{vhost}'.format(vhost=self._vhost_id)
        self._vm_info['interfaces'][if_name] = if_data
        # Add socket to temporary file list.
        self._temp[if_name] = socket

    def _qemu_qmp_exec(self, cmd):
        """Execute QMP command.

        QMP is JSON based protocol which allows to control QEMU instance.

        :param cmd: QMP command to execute.
        :type cmd: str
        :returns: Command output in python representation of JSON format. The
            { "return": {} } response is QMP's success response. An error
            response will contain the "error" keyword instead of "return".
        """
        # To enter command mode, the qmp_capabilities command must be issued.
        command = ('echo "{{ \\"execute\\": \\"qmp_capabilities\\" }}'
                   '{{ \\"execute\\": \\"{cmd}\\" }}" | '
                   'sudo -S socat - UNIX-CONNECT:{qmp}'.
                   format(cmd=cmd, qmp=self._temp.get('qmp')))
        message = ('QMP execute "{cmd}" failed on {host}'.
                   format(cmd=cmd, host=self._node['host']))
        stdout, _ = exec_cmd_no_error(
            self._node, command, sudo=False, message=message)

        # Skip capabilities negotiation messages.
        out_list = stdout.splitlines()
        if len(out_list) < 3:
            raise RuntimeError(
                'Invalid QMP output on {host}'.format(host=self._node['host']))
        return json.loads(out_list[2])

    def _qemu_qga_flush(self):
        """Flush the QGA parser state."""
        command = ('(printf "\xFF"; sleep 1) | '
                   'sudo -S socat - UNIX-CONNECT:{qga}'.
                   format(qga=self._temp.get('qga')))
        message = ('QGA flush failed on {host}'.format(host=self._node['host']))
        stdout, _ = exec_cmd_no_error(
            self._node, command, sudo=False, message=message)

        return json.loads(stdout.split('\n', 1)[0]) if stdout else dict()

    def _qemu_qga_exec(self, cmd):
        """Execute QGA command.

        QGA provide access to a system-level agent via standard QMP commands.

        :param cmd: QGA command to execute.
        :type cmd: str
        """
        command = ('(echo "{{ \\"execute\\": \\"{cmd}\\" }}"; sleep 1) | '
                   'sudo -S socat - UNIX-CONNECT:{qga}'.
                   format(cmd=cmd, qga=self._temp.get('qga')))
        message = ('QGA execute "{cmd}" failed on {host}'.
                   format(cmd=cmd, host=self._node['host']))
        stdout, _ = exec_cmd_no_error(
            self._node, command, sudo=False, message=message)

        return json.loads(stdout.split('\n', 1)[0]) if stdout else dict()

    def _wait_until_vm_boot(self):
        """Wait until QEMU with NestedVM is booted."""
        if self._opt.get('vm_type') == 'nestedvm':
            self._wait_until_nestedvm_boot()
            self._update_vm_interfaces()
        elif self._opt.get('vm_type') == 'kernelvm':
            self._wait_until_kernelvm_boot()
        else:
            raise RuntimeError('QEMU: Unsupported VM type!')

    def _wait_until_nestedvm_boot(self, retries=12):
        """Wait until QEMU with NestedVM is booted.

        First try to flush qga until there is output.
        Then ping QEMU guest agent each 5s until VM booted or timeout.

        :param retries: Number of retries with 5s between trials.
        :type retries: int
        """
        for _ in range(retries):
            out = None
            try:
                out = self._qemu_qga_flush()
            except ValueError:
                logger.trace('QGA qga flush unexpected output {out}'.
                             format(out=out))
            # Empty output - VM not booted yet
            if not out:
                sleep(5)
            else:
                break
        else:
            raise RuntimeError('QEMU: Timeout, VM not booted on {host}!'.
                               format(host=self._node['host']))
        for _ in range(retries):
            out = None
            try:
                out = self._qemu_qga_exec('guest-ping')
            except ValueError:
                logger.trace('QGA guest-ping unexpected output {out}'.
                             format(out=out))
            # Empty output - VM not booted yet.
            if not out:
                sleep(5)
            # Non-error return - VM booted.
            elif out.get('return') is not None:
                break
            # Skip error and wait.
            elif out.get('error') is not None:
                sleep(5)
            else:
                # If there is an unexpected output from QGA guest-info, try
                # again until timeout.
                logger.trace('QGA guest-ping unexpected output {out}'.
                             format(out=out))
        else:
            raise RuntimeError('QEMU: Timeout, VM not booted on {host}!'.
                               format(host=self._node['host']))

    def _wait_until_kernelvm_boot(self, retries=60):
        """Wait until QEMU KernelVM is booted.

        :param retries: Number of retries.
        :type retries: int
        """
        vpp_ver = VPPUtil.vpp_show_version(self._node)

        for _ in range(retries):
            command = ('tail -1 {log}'.format(log=self._temp.get('log')))
            stdout = None
            try:
                stdout, _ = exec_cmd_no_error(self._node, command, sudo=True)
                sleep(1)
            except RuntimeError:
                pass
            if vpp_ver in stdout or 'Press enter to exit' in stdout:
                break
            if 'reboot: Power down' in stdout:
                raise RuntimeError('QEMU: NF failed to run on {host}!'.
                                   format(host=self._node['host']))
        else:
            raise RuntimeError('QEMU: Timeout, VM not booted on {host}!'.
                               format(host=self._node['host']))

    def _update_vm_interfaces(self):
        """Update interface names in VM node dict."""
        # Send guest-network-get-interfaces command via QGA, output example:
        # {"return": [{"name": "eth0", "hardware-address": "52:54:00:00:04:01"},
        # {"name": "eth1", "hardware-address": "52:54:00:00:04:02"}]}.
        out = self._qemu_qga_exec('guest-network-get-interfaces')
        interfaces = out.get('return')
        mac_name = {}
        if not interfaces:
            raise RuntimeError('Get VM interface list failed on {host}'.
                               format(host=self._node['host']))
        # Create MAC-name dict.
        for interface in interfaces:
            if 'hardware-address' not in interface:
                continue
            mac_name[interface['hardware-address']] = interface['name']
        # Match interface by MAC and save interface name.
        for interface in self._vm_info['interfaces'].values():
            mac = interface.get('mac_address')
            if_name = mac_name.get(mac)
            if if_name is None:
                logger.trace(
                    'Interface name for MAC {mac} not found'.format(mac=mac))
            else:
                interface['name'] = if_name

    def qemu_start(self):
        """Start QEMU and wait until VM boot.

        :returns: VM node info.
        :rtype: dict
        """
        cmd_opts = OptionString()
        cmd_opts.add('{bin_path}/qemu-system-{arch}'.format(
            bin_path=Constants.QEMU_BIN_PATH, arch=self._arch))
        cmd_opts.extend(self._params)
        message = ('QEMU: Start failed on {host}!'.
                   format(host=self._node['host']))
        try:
            DUTSetup.check_huge_page(
                self._node, '/dev/hugepages', self._opt.get('mem'))

            exec_cmd_no_error(
                self._node, cmd_opts, timeout=300, sudo=True, message=message)
            self._wait_until_vm_boot()
        except RuntimeError:
            self.qemu_kill_all()
            raise
        return self._vm_info

    def qemu_kill(self):
        """Kill qemu process."""
        exec_cmd(self._node, 'chmod +r {pidfile}'.
                 format(pidfile=self._temp.get('pidfile')), sudo=True)
        exec_cmd(self._node, 'kill -SIGKILL $(cat {pidfile})'.
                 format(pidfile=self._temp.get('pidfile')), sudo=True)

        for value in self._temp.values():
            exec_cmd(self._node, 'cat {value}'.format(value=value), sudo=True)
            exec_cmd(self._node, 'rm -f {value}'.format(value=value), sudo=True)

    def qemu_kill_all(self):
        """Kill all qemu processes on DUT node if specified."""
        exec_cmd(self._node, 'pkill -SIGKILL qemu', sudo=True)

        for value in self._temp.values():
            exec_cmd(self._node, 'cat {value}'.format(value=value), sudo=True)
            exec_cmd(self._node, 'rm -f {value}'.format(value=value), sudo=True)

    def qemu_version(self, version=None):
        """Return Qemu version or compare if version is higher than parameter.

        :param version: Version to compare.
        :type version: str
        :returns: Qemu version or Boolean if version is higher than parameter.
        :rtype: str or bool
        """
        command = ('{bin_path}/qemu-system-{arch} --version'.format(
            bin_path=Constants.QEMU_BIN_PATH,
            arch=self._arch))
        try:
            stdout, _ = exec_cmd_no_error(self._node, command, sudo=True)
            ver = match(r'QEMU emulator version ([\d.]*)', stdout).group(1)
            return StrictVersion(ver) > StrictVersion(version) \
                if version else ver
        except RuntimeError:
            self.qemu_kill_all()
            raise
