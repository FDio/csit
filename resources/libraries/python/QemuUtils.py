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

from time import time, sleep
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

__all__ = ["QemuOptions", "QemuUtils"]


class QemuOptions(object):
    """QEMU option class."""

    def __init__(self):
        self.variables = list()

    def add(self, variable, value):
        """Add parameter to the list.

        :param variable: QEMU parameter.
        :param value: Parameter value.
        :type variable: str
        :type value: str or int
        """
        self.variables.append({str(variable): value})

    def get(self, variable):
        """Get value of variable(s) from list that matches input paramter.

        :param variable: QEMU parameter to get.
        :type variable: str
        :returns: List of values or value that matches input parameter.
        :rtype: list or str
        """
        selected = [d[variable] for d in self.variables if variable in d]
        return selected if len(selected) > 1 else selected[0]

    def replace(self, variable, value):
        """Replace parameter in the list.

        :param variable: QEMU parameter to replace.
        :param value: Parameter value.
        :type variable: str
        :type value: str or int
        """
        for item in self.variables:
            if variable in item:
                item[variable] = value

    def get_values(self):
        """Get all values from dict items in list.

        :returns: List of all dictionary values.
        :rtype: list
        """
        return [item.values()[0] for item in self.variables]

    def __str__(self):
        """Return space separated string of key value pairs.

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
        self._opt = QemuOptions()
        self._opt.add('qemu_id', qemu_id)
        self._opt.add('bin_path', bin_path)
        self._opt.add('mem', int(mem))
        self._opt.add('smp', int(smp))
        self._opt.add('img', img)
        self._opt.add('vnf', vnf)
        # Temporary files.
        self._temp = QemuOptions()
        self._temp.add('pid', '/var/run/qemu_{id}.pid'.format(id=qemu_id))
        # Computed parameters for QEMU command line.
        if '/var/lib/vm/' in img:
            self._opt.add('vm_type', 'nestedvm')
            self._temp.add('qmp', '/var/run/qmp_{id}.sock'.format(id=qemu_id))
            self._temp.add('qga', '/var/run/qga_{id}.sock'.format(id=qemu_id))
        else:
            raise RuntimeError('QEMU: Unknown VM image option!')
        self._params = QemuOptions()
        self.add_params()

    def add_params(self):
        """Set QEMU command line parameters."""
        self.add_default_params()
        if self._opt.get('vm_type') == 'nestedvm':
            self.add_nestedvm_params()
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
        self._params.add('pidfile', '{pid}'.
                         format(pid=self._temp.get('pid')))
        self._params.add('cpu', 'host')
        self._params.add('machine', 'pc,accel=kvm,usb=off,mem-merge=off')
        self._params.add('smp', '{smp},sockets=1,cores={smp},threads=1'.
                         format(smp=self._opt.get('smp')))
        self._params.add('object',
                         'memory-backend-file,id=mem,size={mem}M,'
                         'mem-path=/mnt/huge,share=on'.
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

    def qemu_set_smp(self, smp):
        """Set node to run QEMU on.

        :param smp: Number of virtual SMP units (cores).
        :type smp: int
        """
        self._opt.replace('smp', int(smp))
        self._params.replace('smp', '{smp},sockets=1,cores={smp},threads=1'.
                             format(smp=smp))

    def get_qemu_pids(self):
        """Get QEMU CPU pids.

        :returns: List of QEMU CPU pids.
        :rtype: list of str
        """
        command = (r'grep -rwl "CPU" /proc/$(sudo cat {pid})/task/*/comm '
                   '| xargs dirname | sed -e \'s/\/.*\///g\''.
                   format(pid=self._temp.get('pid')))
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
                         'mac={mac},mq=on,vectors={vectors},csum=off,gso=off,'
                         'guest_tso4=off,guest_tso6=off,guest_ecn=off,'
                         'mrg_rxbuf={mbuf},{queue_size}'.
                         format(vhost=self._vhost_id, mac=mac,
                                mbuf=mbuf if jumbo_frames else 'off',
                                queue_size=queue_size,
                                vectors=(2 * queues + 2)))

        # Add interface MAC and socket to the node dict.
        if_data = {'mac_address': mac, 'socket': socket}
        if_name = 'vhost{vhost}'.format(vhost=self._vhost_id)
        self._vm_info['interfaces'][if_name] = if_data
        # Add socket to temporary file list.
        self._temp.add(socket, socket)

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

    def _wait_until_vm_boot(self, timeout=60):
        """Wait until QEMU VM is booted.

        First try to flush qga until there is output.
        Then ping QEMU guest agent each 5s until VM booted or timeout.

        :param timeout: Waiting timeout in seconds (optional, default 60s).
        :type timeout: int
        """
        start = time()
        while True:
            if time() - start > timeout:
                raise RuntimeError('timeout, VM not booted on {host}'.
                                   format(host=self._node['host']))
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
        while True:
            if time() - start > timeout:
                raise RuntimeError('timeout, VM not booted on {host}'.
                                   format(host=self._node['host']))
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

        logger.trace('VM booted on {host}'.format(host=self._node['host']))

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
        DUTSetup.check_huge_page(self._node, '/mnt/huge', self._opt.get('mem'))

        command = ('{bin_path}/qemu-system-{arch} {params}'.
                   format(bin_path=self._opt.get('bin_path'),
                          arch=Topology.get_node_arch(self._node),
                          params=self._params))
        message = ('QEMU: Start failed on {host}!'.
                   format(host=self._node['host']))

        try:
            exec_cmd_no_error(self._node, command, timeout=300, sudo=True,
                              message=message)
            self._wait_until_vm_boot()
            # Update interface names in VM node dict.
            self._update_vm_interfaces()
        except RuntimeError:
            self.qemu_kill_all()
            raise
        return self._vm_info

    def qemu_kill(self):
        """Kill qemu process."""
        exec_cmd(self._node, 'chmod +r {pid}'.
                 format(pid=self._temp.get('pid')), sudo=True)
        exec_cmd(self._node, 'kill -SIGKILL $(cat {pid})'.
                 format(pid=self._temp.get('pid')), sudo=True)

        for value in self._temp.get_values():
            exec_cmd(self._node, 'rm -f {value}'.format(value=value), sudo=True)

    def qemu_kill_all(self, node=None):
        """Kill all qemu processes on DUT node if specified.

        :param node: Node to kill all QEMU processes on.
        :type node: dict
        """
        if node:
            self.qemu_set_node(node)
        exec_cmd(self._node, 'pkill -SIGKILL qemu', sudo=True)

        for value in self._temp.get_values():
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
