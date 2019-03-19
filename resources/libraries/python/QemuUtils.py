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

from time import sleep
from string import Template
import json
from re import match
# Disable due to pylint bug
# pylint: disable=no-name-in-module,import-error
from distutils.version import StrictVersion

from robot.api import logger
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
from resources.libraries.python.VPPUtil import VPPUtil

__all__ = ["QemuOptions", "QemuUtils"]


class QemuOptions(object):
    """QEMU option class.

    The class can handle input parameters that acts as QEMU command line
    parameters. The only variable is a list of dictionaries where dictionaries
    can be added multiple times. This emulates the QEMU behavior where one
    command line parameter can be used multiple times (1..N). Example can be
    device or object (so it is not an issue to have one memory
    block of 2G and and second memory block of 512M but from other numa).

    Class does support get value or string representation that will return
    space separated, dash prefixed string of key value pairs used for command
    line.
    """

    # Use one instance of class per tests.
    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self):
        self.variables = list()

    def add(self, variable, value):
        """Add parameter to the list.

        :param variable: QEMU parameter name (without dash).
        :param value: Paired value.
        :type variable: str
        :type value: str or int
        """
        self.variables.append({str(variable): value})

    def __str__(self):
        """Return space separated string of key value pairs.

        The format is suitable to be pasted to qemu command line.

        :returns: Space separated string of key value pairs.
        :rtype: str
        """
        return " ".join(["-{k} {v}".format(k=d.keys()[0], v=d.values()[0])
                         for d in self.variables])


class QemuUtils(object):
    """QEMU utilities."""

    # Use one instance of class per tests.
    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self, node=None, qemu_id=1, smp=1, mem=512, vnf=None,
                 img='/var/lib/vm/vhost-nested.img', bin_path='/usr/bin'):
        """Initialize QemuUtil class.

        :param node: Node to run QEMU on.
        :param qemu_id: QEMU identifier.
        :param smp: Number of virtual SMP units (cores).
        :param mem: Amount of memory.
        :param vnf: Network function workload.
        :param img: QEMU disk image or kernel image path.
        :param bin_path: QEMU binary path.
        :type node: dict
        :type qemu_id: int
        :type smp: int
        :type mem: int
        :type vnf: str
        :type img: str
        :type bin_path: str
        """
        self._vhost_id = 0
        self._vm_info = {
            'type': NodeType.VM,
            'port': 10021 + qemu_id,
            'serial': 4555 + qemu_id,
            'username': 'cisco',
            'password': 'cisco',
            'interfaces': {},
        }
        if node:
            self.qemu_set_node(node)
        # Input Options.
        self._opt = dict()
        self._opt['qemu_id'] = qemu_id
        self._opt['bin_path'] = bin_path
        self._opt['mem'] = int(mem)
        self._opt['smp'] = int(smp)
        self._opt['img'] = img
        self._opt['vnf'] = vnf
        # Temporary files.
        self._temp = dict()
        self._temp['pidfile'] = '/var/run/qemu_{id}.pid'.format(id=qemu_id)
        if '/var/lib/vm/' in img:
            self._opt['vm_type'] = 'nestedvm'
            self._temp['qmp'] = '/var/run/qmp_{id}.sock'.format(id=qemu_id)
            self._temp['qga'] = '/var/run/qga_{id}.sock'.format(id=qemu_id)
        elif '/opt/boot/vmlinuz' in img:
            self._opt['vm_type'] = 'kernelvm'
            self._temp['log'] = '/tmp/serial_{id}.log'.format(id=qemu_id)
            self._temp['ini'] = '/etc/vm_init_{id}.conf'.format(id=qemu_id)
        else:
            raise RuntimeError('QEMU: Unknown VM image option!')
        # Computed parameters for QEMU command line.
        self._params = QemuOptions()
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
        self._params.add('daemonize', '')
        self._params.add('nodefaults', '')
        self._params.add('name', 'vnf{qemu},debug-threads=on'.
                         format(qemu=self._opt.get('qemu_id')))
        self._params.add('no-user-config', '')
        self._params.add('monitor', 'none')
        self._params.add('display', 'none')
        self._params.add('vga', 'none')
        self._params.add('enable-kvm', '')
        self._params.add('pidfile', '{pidfile}'.
                         format(pidfile=self._temp.get('pidfile')))
        self._params.add('cpu', 'host')
        self._params.add('machine', 'pc,accel=kvm,usb=off,mem-merge=off')
        self._params.add('smp', '{smp},sockets=1,cores={smp},threads=1'.
                         format(smp=self._opt.get('smp')))
        self._params.add('object',
                         'memory-backend-file,id=mem,size={mem}M,'
                         'mem-path=/dev/hugepages,share=on'.
                         format(mem=self._opt.get('mem')))
        self._params.add('m', '{mem}M'.
                         format(mem=self._opt.get('mem')))
        self._params.add('numa', 'node,memdev=mem')
        self._params.add('balloon', 'none')

    def add_nestedvm_params(self):
        """Set NestedVM QEMU parameters."""
        self._params.add('net', 'nic,macaddr=52:54:00:00:{qemu:02x}:ff'.
                         format(qemu=self._opt.get('qemu_id')))
        self._params.add('net', 'user,hostfwd=tcp::{info[port]}-:22'.
                         format(info=self._vm_info))
        # TODO: Remove try except after fully migrated to Bionic or
        # qemu_set_node is removed.
        try:
            locking = ',file.locking=off'\
                if self.qemu_version(version='2.10') else ''
        except AttributeError:
            locking = ''
        self._params.add('drive',
                         'file={img},format=raw,cache=none,if=virtio{locking}'.
                         format(img=self._opt.get('img'), locking=locking))
        self._params.add('qmp', 'unix:{qmp},server,nowait'.
                         format(qmp=self._temp.get('qmp')))
        self._params.add('chardev', 'socket,host=127.0.0.1,port={info[serial]},'
                         'id=gnc0,server,nowait'.format(info=self._vm_info))
        self._params.add('device', 'isa-serial,chardev=gnc0')
        self._params.add('chardev',
                         'socket,path={qga},server,nowait,id=qga0'.
                         format(qga=self._temp.get('qga')))
        self._params.add('device', 'isa-serial,chardev=qga0')

    def add_kernelvm_params(self):
        """Set KernelVM QEMU parameters."""
        self._params.add('chardev', 'file,id=char0,path={log}'.
                         format(log=self._temp.get('log')))
        self._params.add('device', 'isa-serial,chardev=char0')
        self._params.add('fsdev', 'local,id=root9p,path=/,security_model=none')
        self._params.add('device',
                         'virtio-9p-pci,fsdev=root9p,mount_tag=/dev/root')
        self._params.add('kernel', '$(readlink -m {img}* | tail -1)'.
                         format(img=self._opt.get('img')))
        self._params.add('append',
                         '"ro rootfstype=9p rootflags=trans=virtio '
                         'console=ttyS0 tsc=reliable hugepages=256 '
                         'init={init}"'.format(init=self._temp.get('ini')))

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
        vpp_config.add_cpu_main_core('0')
        vpp_config.add_cpu_corelist_workers('1-{smp}'.
                                            format(smp=self._opt.get('smp')-1))
        vpp_config.add_dpdk_dev('0000:00:06.0', '0000:00:07.0')
        vpp_config.add_dpdk_log_level('debug')
        vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_dpdk_no_multi_seg()
        vpp_config.add_plugin('disable', 'default')
        vpp_config.add_plugin('enable', 'dpdk_plugin.so')
        vpp_config.apply_config(startup, restart_vpp=False)

        # Create VPP running configuration.
        template = '{res}/{tpl}.exec'.format(res=Constants.RESOURCES_TPL_VM,
                                             tpl=self._opt.get('vnf'))
        exec_cmd_no_error(self._node, 'rm -f {running}'.format(running=running),
                          sudo=True)

        with open(template, 'r') as src_file:
            src = Template(src_file.read())
            exec_cmd_no_error(self._node, "echo '{out}' | sudo tee {running}".
                              format(out=src.safe_substitute(**kwargs),
                                     running=running))

    def create_kernelvm_init(self, **kwargs):
        """Create QEMU init script.

        :param kwargs: Key-value pairs to replace content of init startup file.
        :type kwargs: dict
        """
        template = '{res}/init.sh'.format(res=Constants.RESOURCES_TPL_VM)
        init = self._temp.get('ini')
        exec_cmd_no_error(self._node, 'rm -f {init}'.format(init=init),
                          sudo=True)

        with open(template, 'r') as src_file:
            src = Template(src_file.read())
            exec_cmd_no_error(self._node, "echo '{out}' | sudo tee {init}".
                              format(out=src.safe_substitute(**kwargs),
                                     init=init))
            exec_cmd_no_error(self._node, "chmod +x {init}".
                              format(init=init), sudo=True)

    def configure_kernelvm_vnf(self, **kwargs):
        """Create KernelVM VNF configurations.

        :param kwargs: Key-value pairs for templating configs.
        :type kwargs: dict
        """
        if 'vpp' in self._opt.get('vnf'):
            self.create_kernelvm_config_vpp(**kwargs)
        else:
            raise RuntimeError('QEMU: Unsupported VNF!')
        self.create_kernelvm_init(vnf_bin=self._opt.get('vnf_bin'))

    def qemu_set_node(self, node):
        """Set node to run QEMU on.

        :param node: Node to run QEMU on.
        :type node: dict
        """
        self._node = node
        self._vm_info['host'] = node['host']
        if node['port'] != 22:
            self._vm_info['host_port'] = node['port']
            self._vm_info['host_username'] = node['username']
            self._vm_info['host_password'] = node['password']

    def get_qemu_pids(self):
        """Get QEMU CPU pids.

        :returns: List of QEMU CPU pids.
        :rtype: list of str
        """
        command = ("grep -rwl 'CPU' /proc/$(sudo cat {pidfile})/task/*/comm ".
                   format(pidfile=self._temp.get('pidfile')))
        command += (r"| xargs dirname | sed -e 's/\/.*\///g'")

        stdout, _ = exec_cmd_no_error(self._node, command)
        return stdout.splitlines()

    def qemu_set_affinity(self, *host_cpus):
        """Set qemu affinity by getting thread PIDs via QMP and taskset to list
        of CPU cores.

        :param host_cpus: List of CPU cores.
        :type host_cpus: list
        """
        try:
            qemu_cpus = self.get_qemu_pids()

            if len(qemu_cpus) != len(host_cpus):
                raise ValueError('Host CPU count must match Qemu Thread count!')

            for qemu_cpu, host_cpu in zip(qemu_cpus, host_cpus):
                command = ('taskset -pc {host_cpu} {thread}'.
                           format(host_cpu=host_cpu, thread=qemu_cpu))
                message = ('QEMU: Set affinity failed on {host}!'.
                           format(host=self._node['host']))
                exec_cmd_no_error(self._node, command, sudo=True,
                                  message=message)
        except (RuntimeError, ValueError):
            self.qemu_kill_all()
            raise

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
        self._params.add('chardev',
                         'socket,id=char{vhost},path={socket}{server}'.
                         format(vhost=self._vhost_id, socket=socket,
                                server=',server' if server is True else ''))
        self._params.add('netdev',
                         'vhost-user,id=vhost{vhost},'
                         'chardev=char{vhost},queues={queues}'.
                         format(vhost=self._vhost_id, queues=queues))
        mac = ('52:54:00:00:{qemu:02x}:{vhost:02x}'.
               format(qemu=self._opt.get('qemu_id'), vhost=self._vhost_id))
        queue_size = ('rx_queue_size={queue_size},tx_queue_size={queue_size}'.
                      format(queue_size=queue_size)) if queue_size else ''
        mbuf = 'on,host_mtu=9200'
        self._params.add('device',
                         'virtio-net-pci,netdev=vhost{vhost},'
                         'mac={mac},bus=pci.0,addr={addr}.0,mq=on,'
                         'vectors={vectors},csum=off,gso=off,'
                         'guest_tso4=off,guest_tso6=off,guest_ecn=off,'
                         'mrg_rxbuf={mbuf},{queue_size}'.
                         format(addr=self._vhost_id+5,
                                vhost=self._vhost_id, mac=mac,
                                mbuf=mbuf if jumbo_frames else 'off',
                                queue_size=queue_size,
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
        stdout, _ = exec_cmd_no_error(self._node, command, sudo=False,
                                      message=message)

        # Skip capabilities negotiation messages.
        out_list = stdout.splitlines()
        if len(out_list) < 3:
            raise RuntimeError('Invalid QMP output on {host}'.
                               format(host=self._node['host']))
        return json.loads(out_list[2])

    def _qemu_qga_flush(self):
        """Flush the QGA parser state."""
        command = ('(printf "\xFF"; sleep 1) | '
                   'sudo -S socat - UNIX-CONNECT:{qga}'.
                   format(qga=self._temp.get('qga')))
        message = ('QGA flush failed on {host}'.format(host=self._node['host']))
        stdout, _ = exec_cmd_no_error(self._node, command, sudo=False,
                                      message=message)

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
        stdout, _ = exec_cmd_no_error(self._node, command, sudo=False,
                                      message=message)

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
        for _ in range(retries):
            command = ('tail -1 {log}'.format(log=self._temp.get('log')))
            stdout = None
            try:
                stdout, _ = exec_cmd_no_error(self._node, command, sudo=True)
                sleep(1)
            except RuntimeError:
                pass
            if VPPUtil.vpp_show_version(self._node) in stdout:
                break
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
                logger.trace('Interface name for MAC {mac} not found'.
                             format(mac=mac))
            else:
                interface['name'] = if_name

    def qemu_start(self):
        """Start QEMU and wait until VM boot.

        :returns: VM node info.
        :rtype: dict
        """
        command = ('{bin_path}/qemu-system-{arch} {params}'.
                   format(bin_path=self._opt.get('bin_path'),
                          arch=Topology.get_node_arch(self._node),
                          params=self._params))
        message = ('QEMU: Start failed on {host}!'.
                   format(host=self._node['host']))
        try:
            DUTSetup.check_huge_page(self._node, '/dev/hugepages',
                                     self._opt.get('mem'))

            exec_cmd_no_error(self._node, command, timeout=300, sudo=True,
                              message=message)
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
            exec_cmd(self._node, 'rm -f {value}'.format(value=value), sudo=True)

    def qemu_kill_all(self, node=None):
        """Kill all qemu processes on DUT node if specified.

        :param node: Node to kill all QEMU processes on.
        :type node: dict
        """
        if node:
            self.qemu_set_node(node)
        exec_cmd(self._node, 'pkill -SIGKILL qemu', sudo=True)

        for value in self._temp.values():
            exec_cmd(self._node, 'rm -f {value}'.format(value=value), sudo=True)

    def qemu_version(self, version=None):
        """Return Qemu version or compare if version is higher than parameter.

        :param version: Version to compare.
        :type version: str
        :returns: Qemu version or Boolean if version is higher than parameter.
        :rtype: str or bool
        """
        command = ('{bin_path}/qemu-system-{arch} --version'.
                   format(bin_path=self._opt.get('bin_path'),
                          arch=Topology.get_node_arch(self._node)))
        try:
            stdout, _ = exec_cmd_no_error(self._node, command, sudo=True)
            ver = match(r'QEMU emulator version ([\d.]*)', stdout).group(1)
            return StrictVersion(ver) > StrictVersion(version) \
                if version else ver
        except RuntimeError:
            self.qemu_kill_all()
            raise

    @staticmethod
    def build_qemu(node, force_install=False, apply_patch=False):
        """Build QEMU from sources.

        :param node: Node to build QEMU on.
        :param force_install: If True, then remove previous build.
        :param apply_patch: If True, then apply patches from qemu_patches dir.
        :type node: dict
        :type force_install: bool
        :type apply_patch: bool
        :raises RuntimeError: If building QEMU failed.
        """
        directory = (' --directory={install_dir}{patch}'.
                     format(install_dir=Constants.QEMU_INSTALL_DIR,
                            patch='-patch' if apply_patch else '-base'))
        version = (' --version={install_version}'.
                   format(install_version=Constants.QEMU_INSTALL_VERSION))
        force = ' --force' if force_install else ''
        patch = ' --patch' if apply_patch else ''
        target_list = (' --target-list={arch}-softmmu'.
                       format(arch=Topology.get_node_arch(node)))

        command = ("sudo -E sh -c "
                   "'{fw_dir}/{lib_sh}/qemu_build.sh{version}{directory}"
                   "{force}{patch}{target_list}'".
                   format(fw_dir=Constants.REMOTE_FW_DIR,
                          lib_sh=Constants.RESOURCES_LIB_SH,
                          version=version, directory=directory, force=force,
                          patch=patch, target_list=target_list))
        message = ('QEMU: Build failed on {host}!'.format(host=node['host']))
        exec_cmd_no_error(node, command, sudo=False, message=message,
                          timeout=1000)
