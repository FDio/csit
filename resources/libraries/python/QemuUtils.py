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

import json

from re import match
from string import Template
from time import sleep

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DpdkUtil import DpdkUtil
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.OptionString import OptionString
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
from resources.libraries.python.VPPUtil import VPPUtil

__all__ = [u"QemuUtils"]


class QemuUtils:
    """QEMU utilities."""

    # Use one instance of class per tests.
    ROBOT_LIBRARY_SCOPE = u"TEST CASE"

    def __init__(
            self, node, qemu_id=1, smp=1, mem=512, vnf=None,
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
        dpdk_target = u"arm64-armv8a" if self._arch == u"aarch64" \
            else u"x86_64-native"
        self._testpmd_path = f"{Constants.QEMU_VM_DPDK}/" \
            f"{dpdk_target}-linuxapp-gcc/app"
        self._vm_info = {
            u"host": node[u"host"],
            u"type": NodeType.VM,
            u"port": 10021 + qemu_id,
            u"serial": 4555 + qemu_id,
            u"username": 'cisco',
            u"password": 'cisco',
            u"interfaces": {},
        }
        if node[u"port"] != 22:
            self._vm_info[u"host_port"] = node[u"port"]
            self._vm_info[u"host_username"] = node[u"username"]
            self._vm_info[u"host_password"] = node[u"password"]
        # Input Options.
        self._opt = dict()
        self._opt[u"qemu_id"] = qemu_id
        self._opt[u"mem"] = int(mem)
        self._opt[u"smp"] = int(smp)
        self._opt[u"img"] = img
        self._opt[u"vnf"] = vnf
        # Temporary files.
        self._temp = dict()
        self._temp[u"pidfile"] = f"/var/run/qemu_{qemu_id}.pid"
        if img == Constants.QEMU_VM_IMAGE:
            self._opt[u"vm_type"] = u"nestedvm"
            self._temp[u"qmp"] = f"/var/run/qmp_{qemu_id}.sock"
            self._temp[u"qga"] = f"/var/run/qga_{qemu_id}.sock"
        elif img == Constants.QEMU_VM_KERNEL:
            self._opt[u"img"], _ = exec_cmd_no_error(
                node, f"ls -1 {Constants.QEMU_VM_KERNEL}* | tail -1",
                message=u"Qemu Kernel VM image not found!"
            )
            self._opt[u"vm_type"] = u"kernelvm"
            self._temp[u"log"] = f"/tmp/serial_{qemu_id}.log"
            self._temp[u"ini"] = f"/etc/vm_init_{qemu_id}.conf"
            self._opt[u"initrd"], _ = exec_cmd_no_error(
                node, f"ls -1 {Constants.QEMU_VM_KERNEL_INITRD}* | tail -1",
                message=u"Qemu Kernel initrd image not found!"
            )
        else:
            raise RuntimeError(f"QEMU: Unknown VM image option: {img}")
        # Computed parameters for QEMU command line.
        self._params = OptionString(prefix=u"-")
        self.add_params()

    def add_params(self):
        """Set QEMU command line parameters."""
        self.add_default_params()
        if self._opt.get(u"vm_type", u"") == u"nestedvm":
            self.add_nestedvm_params()
        elif self._opt.get(u"vm_type", u"") == u"kernelvm":
            self.add_kernelvm_params()
        else:
            raise RuntimeError(u"QEMU: Unsupported VM type!")

    def add_default_params(self):
        """Set default QEMU command line parameters."""
        self._params.add(u"daemonize")
        self._params.add(u"nodefaults")
        self._params.add_with_value(
            u"name", f"vnf{self._opt.get(u'qemu_id')},debug-threads=on"
        )
        self._params.add(u"no-user-config")
        self._params.add_with_value(u"monitor", u"none")
        self._params.add_with_value(u"display", u"none")
        self._params.add_with_value(u"vga", u"none")
        self._params.add(u"enable-kvm")
        self._params.add_with_value(u"pidfile", self._temp.get(u"pidfile"))
        self._params.add_with_value(u"cpu", u"host")

        if self._arch == u"aarch64":
            machine_args = u"virt,accel=kvm,usb=off,mem-merge=off,gic-version=3"
        else:
            machine_args = u"pc,accel=kvm,usb=off,mem-merge=off"
        self._params.add_with_value(u"machine", machine_args)
        self._params.add_with_value(
            u"smp", f"{self._opt.get(u'smp')},sockets=1,"
            f"cores={self._opt.get(u'smp')},threads=1"
        )
        self._params.add_with_value(
            u"object", f"memory-backend-file,id=mem,"
            f"size={self._opt.get(u'mem')}M,mem-path=/dev/hugepages,share=on"
        )
        self._params.add_with_value(u"m", f"{self._opt.get(u'mem')}M")
        self._params.add_with_value(u"numa", u"node,memdev=mem")
        self._params.add_with_value(u"balloon", u"none")

    def add_nestedvm_params(self):
        """Set NestedVM QEMU parameters."""
        self._params.add_with_value(
            u"net",
            f"nic,macaddr=52:54:00:00:{self._opt.get(u'qemu_id'):02x}:ff"
        )
        self._params.add_with_value(
            u"net", f"user,hostfwd=tcp::{self._vm_info[u'port']}-:22"
        )
        locking = u",file.locking=off"
        self._params.add_with_value(
            u"drive", f"file={self._opt.get(u'img')},"
            f"format=raw,cache=none,if=virtio{locking}"
        )
        self._params.add_with_value(
            u"qmp", f"unix:{self._temp.get(u'qmp')},server,nowait"
        )
        self._params.add_with_value(
            u"chardev", f"socket,host=127.0.0.1,"
            f"port={self._vm_info[u'serial']},id=gnc0,server,nowait")
        self._params.add_with_value(u"device", u"isa-serial,chardev=gnc0")
        self._params.add_with_value(
            u"chardev", f"socket,path={self._temp.get(u'qga')},"
            f"server,nowait,id=qga0"
        )
        self._params.add_with_value(u"device", u"isa-serial,chardev=qga0")

    def add_kernelvm_params(self):
        """Set KernelVM QEMU parameters."""
        console = u"ttyAMA0" if self._arch == u"aarch64" else u"ttyS0"
        self._params.add_with_value(
            u"serial", f"file:{self._temp.get(u'log')}"
        )
        self._params.add_with_value(
            u"fsdev", u"local,id=root9p,path=/,security_model=none"
        )
        self._params.add_with_value(
            u"device", u"virtio-9p-pci,fsdev=root9p,mount_tag=virtioroot"
        )
        self._params.add_with_value(u"kernel", f"{self._opt.get(u'img')}")
        self._params.add_with_value(u"initrd", f"{self._opt.get(u'initrd')}")
        self._params.add_with_value(
            u"append", f"'ro rootfstype=9p rootflags=trans=virtio "
            f"root=virtioroot console={console} tsc=reliable hugepages=256 "
            f"init={self._temp.get(u'ini')} fastboot'"
        )

    def create_kernelvm_config_vpp(self, **kwargs):
        """Create QEMU VPP config files.

        :param kwargs: Key-value pairs to replace content of VPP configuration
            file.
        :type kwargs: dict
        """
        startup = f"/etc/vpp/vm_startup_{self._opt.get(u'qemu_id')}.conf"
        running = f"/etc/vpp/vm_running_{self._opt.get(u'qemu_id')}.exec"

        self._temp[u"startup"] = startup
        self._temp[u"running"] = running
        self._opt[u"vnf_bin"] = f"/usr/bin/vpp -c {startup}"

        # Create VPP startup configuration.
        vpp_config = VppConfigGenerator()
        vpp_config.set_node(self._node)
        vpp_config.add_unix_nodaemon()
        vpp_config.add_unix_cli_listen()
        vpp_config.add_unix_exec(running)
        vpp_config.add_socksvr()
        vpp_config.add_cpu_main_core(u"0")
        if self._opt.get(u"smp") > 1:
            vpp_config.add_cpu_corelist_workers(f"1-{self._opt.get(u'smp')-1}")
        vpp_config.add_dpdk_dev(u"0000:00:06.0", u"0000:00:07.0")
        vpp_config.add_dpdk_dev_default_rxq(kwargs[u"queues"])
        vpp_config.add_dpdk_log_level(u"debug")
        if not kwargs[u"jumbo_frames"]:
            vpp_config.add_dpdk_no_multi_seg()
            vpp_config.add_dpdk_no_tx_checksum_offload()
        vpp_config.add_plugin(u"disable", [u"default"])
        vpp_config.add_plugin(u"enable", [u"dpdk_plugin.so"])
        vpp_config.write_config(startup)

        # Create VPP running configuration.
        template = f"{Constants.RESOURCES_TPL_VM}/{self._opt.get(u'vnf')}.exec"
        exec_cmd_no_error(self._node, f"rm -f {running}", sudo=True)

        with open(template, u"rt") as src_file:
            src = Template(src_file.read())
            exec_cmd_no_error(
                self._node, f"echo '{src.safe_substitute(**kwargs)}' | "
                f"sudo tee {running}"
            )

    def create_kernelvm_config_testpmd_io(self, **kwargs):
        """Create QEMU testpmd-io command line.

        :param kwargs: Key-value pairs to construct command line parameters.
        :type kwargs: dict
        """
        testpmd_cmd = DpdkUtil.get_testpmd_cmdline(
            eal_corelist=f"0-{self._opt.get(u'smp') - 1}",
            eal_driver=False,
            eal_in_memory=True,
            pmd_num_mbufs=16384,
            pmd_rxq=kwargs[u"queues"],
            pmd_txq=kwargs[u"queues"],
            pmd_tx_offloads='0x0',
            pmd_disable_hw_vlan=False,
            pmd_nb_cores=str(self._opt.get(u"smp") - 1)
        )

        self._opt[u"vnf_bin"] = f"{self._testpmd_path}/{testpmd_cmd}"

    def create_kernelvm_config_testpmd_mac(self, **kwargs):
        """Create QEMU testpmd-mac command line.

        :param kwargs: Key-value pairs to construct command line parameters.
        :type kwargs: dict
        """
        testpmd_cmd = DpdkUtil.get_testpmd_cmdline(
            eal_corelist=f"0-{self._opt.get(u'smp') - 1}",
            eal_driver=False,
            eal_in_memory=True,
            pmd_num_mbufs=16384,
            pmd_fwd_mode=u"mac",
            pmd_eth_peer_0=f"0,{kwargs[u'vif1_mac']}",
            pmd_eth_peer_1=f"1,{kwargs[u'vif2_mac']}",
            pmd_rxq=kwargs[u"queues"],
            pmd_txq=kwargs[u"queues"],
            pmd_tx_offloads=u"0x0",
            pmd_disable_hw_vlan=False,
            pmd_nb_cores=str(self._opt.get(u"smp") - 1)
        )

        self._opt[u"vnf_bin"] = f"{self._testpmd_path}/{testpmd_cmd}"

    def create_kernelvm_init(self, **kwargs):
        """Create QEMU init script.

        :param kwargs: Key-value pairs to replace content of init startup file.
        :type kwargs: dict
        """
        template = f"{Constants.RESOURCES_TPL_VM}/init.sh"
        init = self._temp.get(u"ini")
        exec_cmd_no_error(self._node, f"rm -f {init}", sudo=True)

        with open(template, u"rt") as src_file:
            src = Template(src_file.read())
            exec_cmd_no_error(
                self._node, f"echo '{src.safe_substitute(**kwargs)}' | "
                f"sudo tee {init}"
            )
            exec_cmd_no_error(self._node, f"chmod +x {init}", sudo=True)

    def configure_kernelvm_vnf(self, **kwargs):
        """Create KernelVM VNF configurations.

        :param kwargs: Key-value pairs for templating configs.
        :type kwargs: dict
        """
        if u"vpp" in self._opt.get(u"vnf"):
            self.create_kernelvm_config_vpp(**kwargs)
        elif u"testpmd_io" in self._opt.get(u"vnf"):
            self.create_kernelvm_config_testpmd_io(**kwargs)
        elif u"testpmd_mac" in self._opt.get(u"vnf"):
            self.create_kernelvm_config_testpmd_mac(**kwargs)
        else:
            raise RuntimeError(u"QEMU: Unsupported VNF!")
        self.create_kernelvm_init(vnf_bin=self._opt[u"vnf_bin"])

    def get_qemu_pids(self):
        """Get QEMU CPU pids.

        :returns: List of QEMU CPU pids.
        :rtype: list of str
        """
        command = f"grep -rwl 'CPU' /proc/$(sudo cat " \
            f"{self._temp.get(u'pidfile')})/task/*/comm "
        command += r"| xargs dirname | sed -e 's/\/.*\///g' | uniq"

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
                    command = f"taskset -pc {host_cpu} {qemu_cpu}"
                    message = f"QEMU: Set affinity failed " \
                        f"on {self._node[u'host']}!"
                    exec_cmd_no_error(
                        self._node, command, sudo=True, message=message
                    )
                break
            except (RuntimeError, ValueError):
                self.qemu_kill_all()
                raise
        else:
            self.qemu_kill_all()
            raise RuntimeError(u"Failed to set Qemu threads affinity!")

    def qemu_set_scheduler_policy(self):
        """Set scheduler policy to SCHED_RR with priority 1 for all Qemu CPU
        processes.

        :raises RuntimeError: Set scheduler policy failed.
        """
        try:
            qemu_cpus = self.get_qemu_pids()

            for qemu_cpu in qemu_cpus:
                command = f"chrt -r -p 1 {qemu_cpu}"
                message = f"QEMU: Set SCHED_RR failed on {self._node[u'host']}"
                exec_cmd_no_error(
                    self._node, command, sudo=True, message=message
                )
        except (RuntimeError, ValueError):
            self.qemu_kill_all()
            raise

    def qemu_add_vhost_user_if(
            self, socket, server=True, jumbo_frames=False, queue_size=None,
            queues=1, csum=False, gso=False):
        """Add Vhost-user interface.

        :param socket: Path of the unix socket.
        :param server: If True the socket shall be a listening socket.
        :param jumbo_frames: Set True if jumbo frames are used in the test.
        :param queue_size: Vring queue size.
        :param queues: Number of queues.
        :param csum: Checksum offloading.
        :param gso: Generic segmentation offloading.
        :type socket: str
        :type server: bool
        :type jumbo_frames: bool
        :type queue_size: int
        :type queues: int
        :type csum: bool
        :type gso: bool
        """
        self._vhost_id += 1
        self._params.add_with_value(
            u"chardev", f"socket,id=char{self._vhost_id},"
            f"path={socket}{u',server' if server is True else u''}"
        )
        self._params.add_with_value(
            u"netdev", f"vhost-user,id=vhost{self._vhost_id},"
            f"chardev=char{self._vhost_id},queues={queues}"
        )
        mac = f"52:54:00:00:{self._opt.get(u'qemu_id'):02x}:" \
            f"{self._vhost_id:02x}"
        queue_size = f"rx_queue_size={queue_size},tx_queue_size={queue_size}" \
            if queue_size else u""
        self._params.add_with_value(
            u"device", f"virtio-net-pci,netdev=vhost{self._vhost_id},mac={mac},"
            f"addr={self._vhost_id+5}.0,mq=on,vectors={2 * queues + 2},"
            f"csum={u'on' if csum else u'off'},gso={u'on' if gso else u'off'},"
            f"guest_tso4=off,guest_tso6=off,guest_ecn=off,"
            f"mrg_rxbuf={u'on,host_mtu=9200' if jumbo_frames else u'off'},"
            f"{queue_size}"
        )

        # Add interface MAC and socket to the node dict.
        if_data = {u"mac_address": mac, u"socket": socket}
        if_name = f"vhost{self._vhost_id}"
        self._vm_info[u"interfaces"][if_name] = if_data
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
        command = f"echo \"{{{{ \\\"execute\\\": " \
            f"\\\"qmp_capabilities\\\" }}}}" \
            f"{{{{ \\\"execute\\\": \\\"{cmd}\\\" }}}}\" | " \
            f"sudo -S socat - UNIX-CONNECT:{self._temp.get(u'qmp')}"
        message = f"QMP execute '{cmd}' failed on {self._node[u'host']}"

        stdout, _ = exec_cmd_no_error(
            self._node, command, sudo=False, message=message
        )

        # Skip capabilities negotiation messages.
        out_list = stdout.splitlines()
        if len(out_list) < 3:
            raise RuntimeError(f"Invalid QMP output on {self._node[u'host']}")
        return json.loads(out_list[2])

    def _qemu_qga_flush(self):
        """Flush the QGA parser state."""
        command = f"(printf \"\xFF\"; sleep 1) | sudo -S socat " \
            f"- UNIX-CONNECT:{self._temp.get(u'qga')}"
        message = f"QGA flush failed on {self._node[u'host']}"
        stdout, _ = exec_cmd_no_error(
            self._node, command, sudo=False, message=message
        )

        return json.loads(stdout.split(u"\n", 1)[0]) if stdout else dict()

    def _qemu_qga_exec(self, cmd):
        """Execute QGA command.

        QGA provide access to a system-level agent via standard QMP commands.

        :param cmd: QGA command to execute.
        :type cmd: str
        """
        command = f"(echo \"{{{{ \\\"execute\\\": " \
            f"\\\"{cmd}\\\" }}}}\"; sleep 1) | " \
            f"sudo -S socat - UNIX-CONNECT:{self._temp.get(u'qga')}"
        message = f"QGA execute '{cmd}' failed on {self._node[u'host']}"
        stdout, _ = exec_cmd_no_error(
            self._node, command, sudo=False, message=message
        )

        return json.loads(stdout.split(u"\n", 1)[0]) if stdout else dict()

    def _wait_until_vm_boot(self):
        """Wait until QEMU with NestedVM is booted."""
        if self._opt.get(u"vm_type") == u"nestedvm":
            self._wait_until_nestedvm_boot()
            self._update_vm_interfaces()
        elif self._opt.get(u"vm_type") == u"kernelvm":
            self._wait_until_kernelvm_boot()
        else:
            raise RuntimeError(u"QEMU: Unsupported VM type!")

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
                logger.trace(f"QGA qga flush unexpected output {out}")
            # Empty output - VM not booted yet
            if not out:
                sleep(5)
            else:
                break
        else:
            raise RuntimeError(
                f"QEMU: Timeout, VM not booted on {self._node[u'host']}!"
            )
        for _ in range(retries):
            out = None
            try:
                out = self._qemu_qga_exec(u"guest-ping")
            except ValueError:
                logger.trace(f"QGA guest-ping unexpected output {out}")
            # Empty output - VM not booted yet.
            if not out:
                sleep(5)
            # Non-error return - VM booted.
            elif out.get(u"return") is not None:
                break
            # Skip error and wait.
            elif out.get(u"error") is not None:
                sleep(5)
            else:
                # If there is an unexpected output from QGA guest-info, try
                # again until timeout.
                logger.trace(f"QGA guest-ping unexpected output {out}")
        else:
            raise RuntimeError(
                f"QEMU: Timeout, VM not booted on {self._node[u'host']}!"
            )

    def _wait_until_kernelvm_boot(self, retries=60):
        """Wait until QEMU KernelVM is booted.

        :param retries: Number of retries.
        :type retries: int
        """
        vpp_ver = VPPUtil.vpp_show_version(self._node)

        for _ in range(retries):
            command = f"tail -1 {self._temp.get(u'log')}"
            stdout = None
            try:
                stdout, _ = exec_cmd_no_error(self._node, command, sudo=True)
                sleep(1)
            except RuntimeError:
                pass
            if vpp_ver in stdout or u"Press enter to exit" in stdout:
                break
            if u"reboot: Power down" in stdout:
                raise RuntimeError(
                    f"QEMU: NF failed to run on {self._node[u'host']}!"
                )
        else:
            raise RuntimeError(
                f"QEMU: Timeout, VM not booted on {self._node[u'host']}!"
            )

    def _update_vm_interfaces(self):
        """Update interface names in VM node dict."""
        # Send guest-network-get-interfaces command via QGA, output example:
        # {"return": [{"name": "eth0", "hardware-address": "52:54:00:00:04:01"},
        # {"name": "eth1", "hardware-address": "52:54:00:00:04:02"}]}.
        out = self._qemu_qga_exec(u"guest-network-get-interfaces")
        interfaces = out.get(u"return")
        mac_name = {}
        if not interfaces:
            raise RuntimeError(
                f"Get VM interface list failed on {self._node[u'host']}"
            )
        # Create MAC-name dict.
        for interface in interfaces:
            if u"hardware-address" not in interface:
                continue
            mac_name[interface[u"hardware-address"]] = interface[u"name"]
        # Match interface by MAC and save interface name.
        for interface in self._vm_info[u"interfaces"].values():
            mac = interface.get(u"mac_address")
            if_name = mac_name.get(mac)
            if if_name is None:
                logger.trace(f"Interface name for MAC {mac} not found")
            else:
                interface[u"name"] = if_name

    def qemu_start(self):
        """Start QEMU and wait until VM boot.

        :returns: VM node info.
        :rtype: dict
        """
        cmd_opts = OptionString()
        cmd_opts.add(f"{Constants.QEMU_BIN_PATH}/qemu-system-{self._arch}")
        cmd_opts.extend(self._params)
        message = f"QEMU: Start failed on {self._node[u'host']}!"
        try:
            DUTSetup.check_huge_page(
                self._node, u"/dev/hugepages", int(self._opt.get(u"mem")))

            exec_cmd_no_error(
                self._node, cmd_opts, timeout=300, sudo=True, message=message
            )
            self._wait_until_vm_boot()
        except RuntimeError:
            self.qemu_kill_all()
            raise
        return self._vm_info

    def qemu_kill(self):
        """Kill qemu process."""
        exec_cmd(
            self._node, f"chmod +r {self._temp.get(u'pidfile')}", sudo=True
        )
        exec_cmd(
            self._node, f"kill -SIGKILL $(cat {self._temp.get(u'pidfile')})",
            sudo=True
        )

        for value in self._temp.values():
            exec_cmd(self._node, f"cat {value}", sudo=True)
            exec_cmd(self._node, f"rm -f {value}", sudo=True)

    def qemu_kill_all(self):
        """Kill all qemu processes on DUT node if specified."""
        exec_cmd(self._node, u"pkill -SIGKILL qemu", sudo=True)

        for value in self._temp.values():
            exec_cmd(self._node, f"cat {value}", sudo=True)
            exec_cmd(self._node, f"rm -f {value}", sudo=True)

    def qemu_version(self):
        """Return Qemu version.

        :returns: Qemu version.
        :rtype: str
        """
        command = f"{Constants.QEMU_BIN_PATH}/qemu-system-{self._arch} " \
            f"--version"
        try:
            stdout, _ = exec_cmd_no_error(self._node, command, sudo=True)
            return match(r"QEMU emulator version ([\d.]*)", stdout).group(1)
        except RuntimeError:
            self.qemu_kill_all()
            raise
