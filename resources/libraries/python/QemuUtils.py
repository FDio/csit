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
import re
# Disable due to pylint bug
# pylint: disable=no-name-in-module,import-error
from distutils.version import StrictVersion

from robot.api import logger

from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.topology import NodeType, Topology


class QemuParams(object):
    """QEMU startup parameters."""

    def __init__(self):
        self.params = list()

    def add(self, param, val):
        """Add parameter to the list.

        :param param: QEMU parameter.
        :param val: Parameter value.
        :type param: str
        :type val: str
        """
        self.params.append({str(param): str(val)})

    def __repr__(self):
        """Return string of QEMU parameter that can be used as parameters.

        :returns: String of QEMU parameters.
        :rtype: str
        """
        return " ".join(["-{k} {v}".format(k=i.keys()[0], v=i.values()[0])
                         for i in self.params])

class QemuOptions(object):
    """QEMU option class."""

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
            self.__dict__[attr] = value
        else:
            # Updating attribute base of type
            if isinstance(self.__dict__[attr], list):
                self.__dict__[attr].append(value)
            else:
                self.__dict__[attr] = value

    def get_values(self):
        """Return list of all parameter's values."""
        return self.__dict__.values()

class QemuUtils(object):
    """QEMU utilities."""

    def __init__(self, node=None, qemu_id=1, smp=1, sockets=1, cores=1,
                 threads=1, mem=512, img='/var/lib/vm/vhost-nested.img'):
        self._params = QemuParams()

        self._opt = QemuOptions()
        self._opt.node = node
        self._opt.qemu_id = qemu_id
        self._opt.vhost_id = 0
        self._opt.bin_path = '/usr/bin'
        self._opt.mem = mem
        self._opt.smp = smp
        self._opt.sockets = sockets
        self._opt.cores = cores
        self._opt.threads = threads
        self._opt.img = img

        self._temp = QemuOptions()
        self._temp.qmp = '/var/run/qmp{id}.sock'.format(id=qemu_id)
        self._temp.qga = '/var/run/qga{id}.sock'.format(id=qemu_id)
        self._temp.log = '/tmp/serial{id}.log'.format(id=qemu_id)
        self._temp.pid = '/var/run/qemu{id}.pid'.format(id=qemu_id)

        self._vm_info = {
            'type': NodeType.VM,
            'port': 10021 + qemu_id,
            'serial': 4555 + qemu_id,
            'username': 'cisco',
            'password': 'cisco',
            'interfaces': {},
        }
        self._add_default_params()
        if node:
            self.qemu_set_node(node)

    def _add_default_params(self):
        """Set default QEMU parameters."""

        self._params.add('daemonize', '')
        self._params.add('nodefaults', '')
        self._params.add('name', '{opt.qemu_id}'.format(opt=self._opt))
        self._params.add('no-user-config', '')
        self._params.add('monitor', 'none')
        self._params.add('display', 'none')
        self._params.add('vga', 'none')
        self._params.add('enable-kvm', '')
        self._params.add('pidfile', '{pid}'.format(pid=self._temp.pid))
        self._params.add('cpu', 'host')
        self._params.add('machine', 'pc,accel=kvm,usb=off,mem-merge=off')
        self._params.add('smp',
                         '{opt.smp},sockets={opt.sockets},cores={opt.cores},'
                         'threads={opt.threads}'.
                         format(opt=self._opt))
        self._params.add('object',
                         'memory-backend-file,id=mem,size={opt.mem}M,'
                         'mem-path=/mnt/huge,share=on'.
                         format(opt=self._opt))
        self._params.add('m', '{opt.mem}M'.
                         format(opt=self._opt))
        self._params.add('numa', 'node,memdev=mem')
        self._params.add('balloon', 'none')

    def qemu_set_path(self, path):
        """Set binary path for QEMU.

        :param path: Absolute path in filesystem.
        :type path: str
        """
        self._opt.bin_path = path

    def qemu_set_node(self, node):
        """Set node to run QEMU on.

        :param node: Node to run QEMU on.
        :type node: dict
        """
        self._opt.node = node
        self._vm_info['host'] = node['host']
        if node['port'] != 22:
            self._vm_info['host_port'] = node['port']
            self._vm_info['host_username'] = node['username']
            self._vm_info['host_password'] = node['password']

    def qemu_set_affinity(self, *host_cpus):
        """Set qemu affinity by getting thread PIDs via QMP and taskset to list
        of CPU cores.

        :param host_cpus: List of CPU cores.
        :type host_cpus: list
        """
        qemu_cpus = self._qemu_qmp_exec('query-cpus')['return']

        if len(qemu_cpus) != len(host_cpus):
            raise ValueError('Host CPU count must match Qemu Thread count')

        for qemu_cpu, host_cpu in zip(qemu_cpus, host_cpus):
            command = ('taskset -pc {host_cpu} {thread}'.
                       format(host_cpu=host_cpu, thread=qemu_cpu['thread_id']))
            message = ('QEMU: Set affinity failed on {host}'.
                       format(host=self._vm_info.get('host')))
            exec_cmd_no_error(self._opt.node, command, sudo=True,
                              message=message)

    def qemu_set_scheduler_policy(self):
        """Set scheduler policy to SCHED_RR with priority 1 for all Qemu CPU
        processes.

        :raises RuntimeError: Set scheduler policy failed.
        """
        qemu_cpus = self._qemu_qmp_exec('query-cpus')['return']

        for qemu_cpu in qemu_cpus:
            command = ('chrt -r -p 1 {thread}'.
                       format(thread=qemu_cpu['thread_id']))
            message = ('QEMU: Set SCHED_RR failed on {host}'.
                       format(host=self._vm_info.get('host')))
            exec_cmd_no_error(self._opt.node, command, sudo=True,
                              message=message)

    def qemu_add_vhost_user_if(self, socket, server=True, mac=None,
                               jumbo_frames=False, queue_size=None, queues=1):
        """Add Vhost-user interface.

        :param socket: Path of the unix socket.
        :param server: If True the socket shall be a listening socket.
        :param mac: Vhost-user interface MAC address (optional, otherwise is
            used auto-generated MAC 52:54:00:00:xx:yy).
        :param jumbo_frames: Set True if jumbo frames are used in the test.
        :type socket: str
        :type server: bool
        :type mac: str
        :type jumbo_frames: bool
        """
        self._opt.vhost_id += 1

        self._params.add('chardev',
                         'socket,id=char{opt.vhost_id},path={socket}{server}'.
                         format(opt=self._opt, socket=socket,
                                server=',server' if server is True else ''))
        self._params.add('netdev',
                         'vhost-user,id=vhost{opt.vhost_id},'
                         'chardev=char{opt.vhost_id},queues={queues}'.
                         format(opt=self._opt, queues=queues))

        mac = ('52:54:00:00:{opt.qemu_id:02x}:{opt.vhost_id:02x}'.
               format(opt=self._opt)) if mac is None else mac
        queue_size = ('rx_queue_size={queue_size},tx_queue_size={queue_size}'.
                      format(queue_size=queue_size)) if queue_size else ''
        mbuf = 'on,host_mtu=9200'

        self._params.add('device',
                         'virtio-net-pci,netdev=vhost{opt.vhost_id},'
                         'mac={mac},mq=on,vectors={vectors},csum=off,gso=off,'
                         'guest_tso4=off,guest_tso6=off,guest_ecn=off,'
                         'mrg_rxbuf={mbuf},{queue_size}'.
                         format(opt=self._opt, mac=mac,
                                mbuf=mbuf if jumbo_frames else 'off',
                                queue_size=queue_size,
                                vectors=(2 * queues + 2)))

        # Add interface MAC and socket to the node dict.
        if_data = {'mac_address': mac, 'socket': socket}
        if_name = 'vhost{opt.vhost_id}'.format(opt=self._opt)
        self._vm_info['interfaces'][if_name] = if_data
        # Add socket to temporary file list.
        self._temp.socket = socket

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
                   format(cmd=cmd, qmp=self._temp.qmp))
        message = ('QMP execute "{cmd}" failed on {host}'.
                   format(cmd=cmd, host=self._vm_info.get('host')))
        stdout, _ = exec_cmd_no_error(self._opt.node, command,
                                      sudo=False, message=message)

        # Skip capabilities negotiation messages.
        out_list = stdout.splitlines()
        if len(out_list) < 3:
            raise RuntimeError('Invalid QMP output on {host}'.
                               format(host=self._vm_info.get('host')))
        return json.loads(out_list[2])

    def _qemu_qga_flush(self):
        """Flush the QGA parser state."""
        command = ('(printf "\xFF"; sleep 1) | '
                   'sudo -S socat - UNIX-CONNECT:{qga}'.
                   format(qga=self._temp.qga))
        message = ('QGA flush failed on {host}'.
                   format(host=self._vm_info.get('host')))
        stdout, _ = exec_cmd_no_error(self._opt.node, command,
                                      sudo=False, message=message)

        return json.loads(stdout.split('\n', 1)[0]) if stdout else dict()

    def _qemu_qga_exec(self, cmd):
        """Execute QGA command.

        QGA provide access to a system-level agent via standard QMP commands.

        :param cmd: QGA command to execute.
        :type cmd: str
        """
        command = ('(echo "{{ \\"execute\\": \\"{cmd}\\" }}"; sleep 1) | '
                   'sudo -S socat - UNIX-CONNECT:{qga}'.
                   format(cmd=cmd, qga=self._temp.qga))
        message = ('QGA execute "{cmd}" failed on {host}'.
                   format(cmd=cmd, host=self._vm_info.get('host')))
        stdout, _ = exec_cmd_no_error(self._opt.node, command,
                                      sudo=False, message=message)

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
                                   format(host=self._vm_info.get('host')))
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
                                   format(host=self._vm_info.get('host')))
            out = None
            try:
                out = self._qemu_qga_exec('guest-ping')
            except ValueError:
                logger.trace('QGA guest-ping unexpected output {out}'.
                             format(out=out))
            # Empty output - VM not booted yet
            if not out:
                sleep(5)
            # Non-error return - VM booted
            elif out.get('return') is not None:
                break
            # Skip error and wait
            elif out.get('error') is not None:
                sleep(5)
            else:
                # If there is an unexpected output from QGA guest-info, try
                # again until timeout.
                logger.trace('QGA guest-ping unexpected output {out}'.
                             format(out=out))

        logger.trace('VM booted on {host}'.
                     format(host=self._vm_info.get('host')))

    def _update_vm_interfaces(self):
        """Update interface names in VM node dict."""
        # Send guest-network-get-interfaces command via QGA, output example:
        # {"return": [{"name": "eth0", "hardware-address": "52:54:00:00:04:01"},
        # {"name": "eth1", "hardware-address": "52:54:00:00:04:02"}]}
        out = self._qemu_qga_exec('guest-network-get-interfaces')
        interfaces = out.get('return')
        mac_name = {}
        if not interfaces:
            raise RuntimeError('Get VM interface list failed on {host}'.
                               format(host=self._vm_info.get('host')))
        # Create MAC-name dict
        for interface in interfaces:
            if 'hardware-address' not in interface:
                continue
            mac_name[interface['hardware-address']] = interface['name']
        # Match interface by MAC and save interface name
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
        DUTSetup.check_huge_page(self._opt.node, '/mnt/huge',
                                 self._opt.mem, False)

        self._params.add('net', 'nic,macaddr=52:54:00:00:{opt.qemu_id:02x}:ff'.
                         format(opt=self._opt))
        self._params.add('net', 'user,hostfwd=tcp::{info[port]}-:22'.
                         format(info=self._vm_info))
        self._params.add('drive',
                         'file={opt.img},format=raw,cache=none,if=virtio'
                         '{locking}'.
                         format(opt=self._opt, locking=',file.locking=off'\
                                if self._version_greater('2.10') else ''))
        self._params.add('qmp', 'unix:{qmp},server,nowait'.
                         format(qmp=self._temp.qmp))
        self._params.add('chardev', 'socket,host=127.0.0.1,port={info[serial]},'
                         'id=gnc0,server,nowait'.format(info=self._vm_info))
        self._params.add('device', 'isa-serial,chardev=gnc0')
        self._params.add('chardev',
                         'socket,path={qga},server,nowait,id=qga0'.
                         format(qga=self._temp.qga))
        self._params.add('device', 'isa-serial,chardev=qga0')

        command = ('{opt.bin_path}/qemu-system-{arch} {params}'.
                   format(opt=self._opt,
                          arch=Topology.get_node_arch(self._opt.node),
                          params=self._params))
        message = ('QEMU start failed on {host}'.
                   format(host=self._vm_info.get('host')))

        try:
            exec_cmd_no_error(self._opt.node, command, timeout=300,
                              sudo=True, message=message)
            self._wait_until_vm_boot()
        except RuntimeError:
            self.qemu_kill_all()
            self.qemu_clear_socks()
            raise
        logger.trace('QEMU started successfully.')
        # Update interface names in VM node dict
        self._update_vm_interfaces()
        # Return VM node dict
        return self._vm_info

    def qemu_kill(self):
        """Kill qemu process."""
        exec_cmd(self._opt.node, 'chmod +r {pid}'.
                 format(pid=self._temp.pid), sudo=True)
        exec_cmd(self._opt.node, 'kill -SIGKILL $(cat {pid})'.
                 format(pid=self._temp.pid), sudo=True)
        exec_cmd(self._opt.node, 'rm -f {pid}'.
                 format(pid=self._temp.pid), sudo=True)

    def qemu_kill_all(self, node=None):
        """Kill all qemu processes on DUT node if specified.

        :param node: Node to kill all QEMU processes on.
        :type node: dict
        """
        if node:
            exec_cmd(self._opt.node, 'pkill -SIGKILL qemu', sudo=True)

    def qemu_clear_socks(self):
        """Remove all sockets created by QEMU."""
        # If serial console port still open kill process.
        exec_cmd(self._opt.node, 'fuser -k {info[serial]}/tcp'.
                 format(info=self._vm_info), sudo=True)

        for value in self._temp.get_values():
            exec_cmd(self._opt.node, 'rm -f {value}'.
                     format(value=value), sudo=True)

    def qemu_version(self):
        """Return Qemu version.

        :returns: Qemu version.
        :rtype: str
        """
        command = ('{opt.bin_path}/qemu-system-{arch} --version'.
                   format(opt=self._opt,
                          arch=Topology.get_node_arch(self._opt.node)))
        try:
            stdout, _ = exec_cmd_no_error(self._opt.node, command, sudo=True)
            return re.match(r'QEMU emulator version ([\d.]*)', stdout).group(1)
        except RuntimeError:
            self.qemu_kill_all()
            self.qemu_clear_socks()
            raise

    def _version_greater(self, version):
        """Compare Qemu versions.

        :param version: Node to build QEMU on.
        :type versin: str
        :returns: True if installed Qemu version is greater.
        :rtype: bool
        """
        return StrictVersion(self.qemu_version()) > StrictVersion(version)

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
        arch = Topology.get_node_arch(node)
        target_list = (' --target-list={arch}-softmmu'.
                       format(arch=arch))

        command = ("sudo -E sh -c "
                   "'{fw_dir}/{lib_sh}/qemu_build.sh{version}{directory}"
                   "{force}{patch}{target_list}'".
                   format(fw_dir=Constants.REMOTE_FW_DIR,
                          lib_sh=Constants.RESOURCES_LIB_SH,
                          version=version, directory=directory, force=force,
                          patch=patch, target_list=target_list))
        message = ('QEMU build failed on {host}'.
                   format(host=node['host']))
        exec_cmd_no_error(node, command, sudo=False, message=message,
                          timeout=1000)
