# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""DUT setup library."""

from time import sleep
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class DUTSetup:
    """Contains methods for setting up DUTs."""

    @staticmethod
    def get_service_logs(node, service):
        """Get specific service unit logs from node.

        :param node: Node in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        if DUTSetup.running_in_container(node):
            command = u"cat /var/log/vpp/vpp.log"
        else:
            command = (
                f"journalctl --no-pager _SYSTEMD_INVOCATION_ID=$(systemctl "
                f"show -p InvocationID --value {service})"
            )
        message = f"Node {node[u'host']} failed to get logs from unit {service}"

        exec_cmd_no_error(
            node, command, timeout=30, sudo=True, message=message
        )

    @staticmethod
    def get_service_logs_on_all_duts(nodes, service):
        """Get specific service unit logs from all DUTs.

        :param nodes: Nodes in the topology.
        :param service: Service unit name.
        :type nodes: dict
        :type service: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                DUTSetup.get_service_logs(node, service)

    @staticmethod
    def restart_service(node, service):
        """Restart the named service on node.

        :param node: Node in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        if DUTSetup.running_in_container(node):
            command = f"supervisorctl restart {service}"
        else:
            command = f"systemctl restart {service}"
        message = f"Node {node[u'host']} failed to restart service {service}"

        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message
        )

        DUTSetup.get_service_logs(node, service)

    @staticmethod
    def restart_service_on_all_duts(nodes, service):
        """Restart the named service on all DUTs.

        :param nodes: Nodes in the topology.
        :param service: Service unit name.
        :type nodes: dict
        :type service: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                DUTSetup.restart_service(node, service)

    @staticmethod
    def start_service(node, service):
        """Start up the named service on node.

        :param node: Node in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        if DUTSetup.running_in_container(node):
            command = f"supervisorctl restart {service}"
        else:
            command = f"systemctl restart {service}"
        message = f"Node {node[u'host']} failed to start service {service}"

        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message
        )

        DUTSetup.get_service_logs(node, service)

    @staticmethod
    def start_service_on_all_duts(nodes, service):
        """Start up the named service on all DUTs.

        :param nodes: Nodes in the topology.
        :param service: Service unit name.
        :type nodes: dict
        :type service: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                DUTSetup.start_service(node, service)

    @staticmethod
    def stop_service(node, service):
        """Stop the named service on node.

        :param node: Node in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        DUTSetup.get_service_logs(node, service)

        if DUTSetup.running_in_container(node):
            command = f"supervisorctl stop {service}"
        else:
            command = f"systemctl stop {service}"
        message = f"Node {node[u'host']} failed to stop service {service}"

        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message
        )

    @staticmethod
    def stop_service_on_all_duts(nodes, service):
        """Stop the named service on all DUTs.

        :param nodes: Nodes in the topology.
        :param service: Service unit name.
        :type nodes: dict
        :type service: str
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                DUTSetup.stop_service(node, service)

    @staticmethod
    def kill_program(node, program, namespace=None):
        """Kill program on the specified topology node.

        :param node: Topology node.
        :param program: Program name.
        :param namespace: Namespace program is running in.
        :type node: dict
        :type program: str
        :type namespace: str
        """
        host = node[u"host"]
        cmd_timeout = 5
        if namespace in (None, u"default"):
            shell_cmd = u"sh -c"
        else:
            shell_cmd = f"ip netns exec {namespace} sh -c"

        pgrep_cmd = f"{shell_cmd} \'pgrep -c {program}\'"
        _, stdout, _ = exec_cmd(node, pgrep_cmd, timeout=cmd_timeout,
                                sudo=True)
        if int(stdout) == 0:
            logger.trace(f"{program} is not running on {host}")
            return
        exec_cmd(node, f"{shell_cmd} \'pkill {program}\'",
                 timeout=cmd_timeout, sudo=True)
        for attempt in range(5):
            _, stdout, _ = exec_cmd(node, pgrep_cmd, timeout=cmd_timeout,
                                    sudo=True)
            if int(stdout) == 0:
                logger.trace(f"Attempt {attempt}: {program} is dead on {host}")
                return
            sleep(1)
        logger.trace(f"SIGKILLing {program} on {host}")
        exec_cmd(node, f"{shell_cmd} \'pkill -9 {program}\'",
                 timeout=cmd_timeout, sudo=True)

    @staticmethod
    def verify_program_installed(node, program):
        """Verify that program is installed on the specified topology node.

        :param node: Topology node.
        :param program: Program name.
        :type node: dict
        :type program: str
        """
        cmd = f"command -v {program}"
        exec_cmd_no_error(node, cmd, message=f"{program} is not installed")

    @staticmethod
    def get_pid(node, process, retries=3):
        """Get PID of running process.

        :param node: DUT node.
        :param process: process name.
        :param retries: How many times to retry on failure.
        :type node: dict
        :type process: str
        :type retries: int
        :returns: PID
        :rtype: int
        :raises RuntimeError: If it is not possible to get the PID.
        """
        cmd = f"pidof {process}"
        stdout, _ = exec_cmd_no_error(
            node, cmd, retries=retries,
            message=f"No {process} PID found on node {node[u'host']}")
        pid_list = stdout.split()
        return [int(pid) for pid in pid_list]

    @staticmethod
    def get_vpp_pids(nodes):
        """Get PID of running VPP process on all DUTs.

        :param nodes: DUT nodes.
        :type nodes: dict
        :returns: PIDs
        :rtype: dict
        """
        pids = dict()
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                pids[node[u"host"]] = DUTSetup.get_pid(node, u"vpp")
        return pids

    @staticmethod
    def crypto_device_verify(node, crypto_type, numvfs, force_init=False):
        """Verify if Crypto QAT device virtual functions are initialized on all
        DUTs. If parameter force initialization is set to True, then try to
        initialize or remove VFs on QAT.

        :param node: DUT node.
        :crypto_type: Crypto device type - HW_DH895xcc, HW_C3xxx or HW_C4xxx.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :param force_init: If True then try to initialize to specific value.
        :type node: dict
        :type crypto_type: string
        :type numvfs: int
        :type force_init: bool
        :returns: nothing
        :raises RuntimeError: If QAT VFs are not created and force init is set
                              to False.
        """
        pci_addr = Topology.get_cryptodev(node)
        sriov_numvfs = DUTSetup.get_sriov_numvfs(node, pci_addr)

        if sriov_numvfs != numvfs:
            if force_init:
                # QAT is not initialized and we want to initialize with numvfs
                DUTSetup.crypto_device_init(node, crypto_type, numvfs)
            else:
                raise RuntimeError(
                    f"QAT device failed to create VFs on {node[u'host']}"
                )

    @staticmethod
    def crypto_device_init(node, crypto_type, numvfs):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :crypto_type: Crypto device type - HW_DH895xcc, HW_C3xxx or HW_C4xxx.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :type node: dict
        :type crypto_type: string
        :type numvfs: int
        :returns: nothing
        :raises RuntimeError: If failed to stop VPP or QAT failed to initialize.
        """
        if crypto_type == u"HW_DH895xcc":
            kernel_mod = u"qat_dh895xcc"
            kernel_drv = u"dh895xcc"
        elif crypto_type == u"HW_C3xxx":
            kernel_mod = u"qat_c3xxx"
            kernel_drv = u"c3xxx"
        elif crypto_type == u"HW_C4xxx":
            kernel_mod = u"qat_c4xxx"
            kernel_drv = u"c4xxx"
        else:
            raise RuntimeError(
                f"Unsupported crypto device type on {node[u'host']}"
            )

        pci_addr = Topology.get_cryptodev(node)

        # QAT device must be re-bound to kernel driver before initialization.
        DUTSetup.verify_kernel_module(node, kernel_mod, force_load=True)

        # Stop VPP to prevent deadlock.
        DUTSetup.stop_service(node, Constants.VPP_UNIT)

        current_driver = DUTSetup.get_pci_dev_driver(
            node, pci_addr.replace(u":", r"\:")
        )
        if current_driver is not None:
            DUTSetup.pci_driver_unbind(node, pci_addr)

        # Bind to kernel driver.
        DUTSetup.pci_driver_bind(node, pci_addr, kernel_drv)

        # Initialize QAT VFs.
        if numvfs > 0:
            DUTSetup.set_sriov_numvfs(node, pci_addr, numvfs)

    @staticmethod
    def get_virtfn_pci_addr(node, pf_pci_addr, vf_id):
        """Get PCI address of Virtual Function.

        :param node: DUT node.
        :param pf_pci_addr: Physical Function PCI address.
        :param vf_id: Virtual Function number.
        :type node: dict
        :type pf_pci_addr: str
        :type vf_id: int
        :returns: Virtual Function PCI address.
        :rtype: str
        :raises RuntimeError: If failed to get Virtual Function PCI address.
        """
        command = f"sh -c \"basename $(readlink " \
            f"/sys/bus/pci/devices/{pf_pci_addr}/virtfn{vf_id})\""
        message = u"Failed to get virtual function PCI address."

        stdout, _ = exec_cmd_no_error(
            node, command, timeout=30, sudo=True, message=message
        )

        return stdout.strip()

    @staticmethod
    def get_sriov_numvfs(node, pf_pci_addr):
        """Get number of SR-IOV VFs.

        :param node: DUT node.
        :param pf_pci_addr: Physical Function PCI device address.
        :type node: dict
        :type pf_pci_addr: str
        :returns: Number of VFs.
        :rtype: int
        :raises RuntimeError: If PCI device is not SR-IOV capable.
        """
        pci = pf_pci_addr.replace(u":", r"\:")
        command = f"cat /sys/bus/pci/devices/{pci}/sriov_numvfs"
        message = f"PCI device {pf_pci_addr} is not a SR-IOV device."

        for _ in range(3):
            stdout, _ = exec_cmd_no_error(
                node, command, timeout=30, sudo=True, message=message
            )
            try:
                sriov_numvfs = int(stdout)
            except ValueError:
                logger.trace(
                    f"Reading sriov_numvfs info failed on {node[u'host']}"
                )
            else:
                return sriov_numvfs

    @staticmethod
    def set_sriov_numvfs(node, pf_pci_addr, numvfs=0):
        """Init or reset SR-IOV virtual functions by setting its number on PCI
        device on DUT. Setting to zero removes all VFs.

        :param node: DUT node.
        :param pf_pci_addr: Physical Function PCI device address.
        :param numvfs: Number of VFs to initialize, 0 - removes the VFs.
        :type node: dict
        :type pf_pci_addr: str
        :type numvfs: int
        :raises RuntimeError: Failed to create VFs on PCI.
        """
        cmd = f"test -f /sys/bus/pci/devices/{pf_pci_addr}/sriov_numvfs"
        sriov_unsupported, _, _ = exec_cmd(node, cmd)
        # if sriov_numvfs doesn't exist, then sriov_unsupported != 0
        if int(sriov_unsupported):
            if numvfs == 0:
                # sriov is not supported and we want 0 VFs
                # no need to do anything
                return

            raise RuntimeError(
                f"Can't configure {numvfs} VFs on {pf_pci_addr} device "
                f"on {node[u'host']} since it doesn't support SR-IOV."
            )

        pci = pf_pci_addr.replace(u":", r"\:")
        command = f"sh -c \"echo {numvfs} | " \
            f"tee /sys/bus/pci/devices/{pci}/sriov_numvfs\""
        message = f"Failed to create {numvfs} VFs on {pf_pci_addr} device " \
            f"on {node[u'host']}"

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

    @staticmethod
    def pci_driver_unbind(node, pci_addr):
        """Unbind PCI device from current driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :raises RuntimeError: If PCI device unbind failed.
        """
        pci = pci_addr.replace(u":", r"\:")
        command = f"sh -c \"echo {pci_addr} | " \
            f"tee /sys/bus/pci/devices/{pci}/driver/unbind\""
        message = f"Failed to unbind PCI device {pci_addr} on {node[u'host']}"

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

    @staticmethod
    def unbind_pci_devices_from_other_driver(node, driver, *pci_addrs):
        """Unbind PCI devices from driver other than input driver on node.

        :param node: DUT node.
        :param driver: Driver to not unbind from. If None or empty string,
            will attempt to unbind from the current driver.
        :param pci_addrs: PCI device addresses.
        :type node: dict
        :type driver: str
        :type pci_addrs: list
        """
        for pci_addr in pci_addrs:
            cur_driver = DUTSetup.get_pci_dev_driver(node, pci_addr)
            if not cur_driver:
                return
            if not driver or cur_driver != driver:
                DUTSetup.pci_driver_unbind(node, pci_addr)

    @staticmethod
    def pci_driver_bind(node, pci_addr, driver):
        """Bind PCI device to driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :param driver: Driver to bind.
        :type node: dict
        :type pci_addr: str
        :type driver: str
        :raises RuntimeError: If PCI device bind failed.
        """
        message = f"Failed to bind PCI device {pci_addr} to {driver} " \
            f"on host {node[u'host']}"
        pci = pci_addr.replace(u":", r"\:")
        command = f"sh -c \"echo {driver} | " \
            f"tee /sys/bus/pci/devices/{pci}/driver_override\""

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

        command = f"sh -c \"echo {pci_addr} | " \
            f"tee /sys/bus/pci/drivers/{driver}/bind\""

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

        command = f"sh -c \"echo  | " \
            f"tee /sys/bus/pci/devices/{pci}/driver_override\""

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

    @staticmethod
    def pci_vf_driver_unbind(node, pf_pci_addr, vf_id):
        """Unbind Virtual Function from driver on node.

        :param node: DUT node.
        :param pf_pci_addr: PCI device address.
        :param vf_id: Virtual Function ID.
        :type node: dict
        :type pf_pci_addr: str
        :type vf_id: int
        :raises RuntimeError: If Virtual Function unbind failed.
        """
        vf_pci_addr = DUTSetup.get_virtfn_pci_addr(node, pf_pci_addr, vf_id)
        pf_pci = pf_pci_addr.replace(u":", r"\:")
        vf_path = f"/sys/bus/pci/devices/{pf_pci}/virtfn{vf_id}"

        command = f"sh -c \"echo {vf_pci_addr} | tee {vf_path}/driver/unbind\""
        message = f"Failed to unbind VF {vf_pci_addr} on {node[u'host']}"

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

    @staticmethod
    def pci_vf_driver_bind(node, pf_pci_addr, vf_id, driver):
        """Bind Virtual Function to driver on node.

        :param node: DUT node.
        :param pf_pci_addr: PCI device address.
        :param vf_id: Virtual Function ID.
        :param driver: Driver to bind.
        :type node: dict
        :type pf_pci_addr: str
        :type vf_id: int
        :type driver: str
        :raises RuntimeError: If PCI device bind failed.
        """
        vf_pci_addr = DUTSetup.get_virtfn_pci_addr(node, pf_pci_addr, vf_id)
        pf_pci = pf_pci_addr.replace(u":", r'\:')
        vf_path = f"/sys/bus/pci/devices/{pf_pci}/virtfn{vf_id}"

        message = f"Failed to bind VF {vf_pci_addr} to {driver} " \
            f"on {node[u'host']}"
        command = f"sh -c \"echo {driver} | tee {vf_path}/driver_override\""

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

        command = f"sh -c \"echo {vf_pci_addr} | " \
            f"tee /sys/bus/pci/drivers/{driver}/bind\""

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

        command = f"sh -c \"echo  | tee {vf_path}/driver_override\""

        exec_cmd_no_error(
            node, command, timeout=120, sudo=True, message=message
        )

    @staticmethod
    def get_pci_dev_driver(node, pci_addr):
        """Get current PCI device driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :returns: Driver or None
        :raises RuntimeError: If it is not possible to get the interface driver
            information from the node.
        """
        driver_path = f"/sys/bus/pci/devices/{pci_addr}/driver"
        cmd = f"test -d {driver_path}"
        ret_code, ret_val, _ = exec_cmd(node, cmd)
        if int(ret_code):
            # the directory doesn't exist which means the device is not bound
            # to any driver
            return None
        cmd = f"basename $(readlink -f {driver_path})"
        ret_val, _ = exec_cmd_no_error(node, cmd)
        return ret_val.strip()

    @staticmethod
    def verify_kernel_module(node, module, force_load=False):
        """Verify if kernel module is loaded on node. If parameter force
        load is set to True, then try to load the modules.

        :param node: Node.
        :param module: Module to verify.
        :param force_load: If True then try to load module.
        :type node: dict
        :type module: str
        :type force_load: bool
        :raises RuntimeError: If module is not loaded or failed to load.
        """
        command = f"grep -w {module} /proc/modules"
        message = f"Kernel module {module} is not loaded " \
            f"on host {node[u'host']}"

        try:
            exec_cmd_no_error(
                node, command, timeout=30, sudo=False, message=message
            )
        except RuntimeError:
            if force_load:
                # Module is not loaded and we want to load it
                DUTSetup.load_kernel_module(node, module)
            else:
                raise

    @staticmethod
    def verify_kernel_module_on_all_duts(nodes, module, force_load=False):
        """Verify if kernel module is loaded on all DUTs. If parameter force
        load is set to True, then try to load the modules.

        :param nodes: DUT nodes.
        :param module: Module to verify.
        :param force_load: If True then try to load module.
        :type nodes: dict
        :type module: str
        :type force_load: bool
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                DUTSetup.verify_kernel_module(node, module, force_load)

    @staticmethod
    def verify_uio_driver_on_all_duts(nodes):
        """Verify if uio driver kernel module is loaded on all DUTs. If module
        is not present it will try to load it.

        :param nodes: DUT nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                uio_driver = Topology.get_uio_driver(node)
                DUTSetup.verify_kernel_module(node, uio_driver, force_load=True)

    @staticmethod
    def load_kernel_module(node, module):
        """Load kernel module on node.

        :param node: DUT node.
        :param module: Module to load.
        :type node: dict
        :type module: str
        :returns: nothing
        :raises RuntimeError: If loading failed.
        """
        command = f"modprobe {module}"
        message = f"Failed to load {module} on host {node[u'host']}"

        exec_cmd_no_error(node, command, timeout=30, sudo=True, message=message)

    def running_in_container(node):
        """This method tests if topology node is running inside container.

        :param node: Topology node.
        :type node: dict
        :returns: True if running in docker container, false if not or failed
            to detect.
        :rtype: bool
        """
        command = "cat /.dockerenv"
        try:
            exec_cmd_no_error(node, command, timeout=30)
        except RuntimeError:
            return False
        return True

    @staticmethod
    def get_docker_mergeddir(node, uuid=None):
        """Get Docker overlay for MergedDir diff.

        :param node: DUT node.
        :param uuid: Docker UUID.
        :type node: dict
        :type uuid: str
        :returns: Docker container MergedDir.
        :rtype: str
        :raises RuntimeError: If getting output failed.
        """
        if not uuid:
            command = 'fgrep "hostname" /proc/self/mountinfo | cut -f 4 -d" "'
            message = "Failed to get UUID!"
            stdout, _ = exec_cmd_no_error(node, command, message=message)
            uuid = stdout.split(sep="/")[-2]
        command = (
            f"docker inspect "
            f"--format='{{{{.GraphDriver.Data.MergedDir}}}}' {uuid}"
        )
        message = f"Failed to get directory of {uuid} on host {node[u'host']}"

        stdout, _ = exec_cmd_no_error(node, command, sudo=True, message=message)
        return stdout.strip()

    @staticmethod
    def get_hugepages_info(node, hugesize=None):
        """Get number of huge pages in system.

        :param node: Node in the topology.
        :param hugesize: Size of hugepages. Default system huge size if None.
        :type node: dict
        :type hugesize: int
        :returns: Number of huge pages in system.
        :rtype: dict
        :raises RuntimeError: If reading failed.
        """
        if not hugesize:
            hugesize = "$(grep Hugepagesize /proc/meminfo | awk '{ print $2 }')"
        command = f"cat /sys/kernel/mm/hugepages/hugepages-{hugesize}kB/*"
        stdout, _ = exec_cmd_no_error(node, command)
        try:
            line = stdout.splitlines()
            return {
                "free_hugepages": int(line[0]),
                "nr_hugepages": int(line[1]),
                "nr_hugepages_mempolicy": int(line[2]),
                "nr_overcommit_hugepages": int(line[3]),
                "resv_hugepages": int(line[4]),
                "surplus_hugepages": int(line[5])
            }
        except ValueError:
            logger.trace(u"Reading huge pages information failed!")

    @staticmethod
    def check_huge_page(
            node, huge_mnt, mem_size, hugesize=2048, allocate=False):
        """Check if there is enough HugePages in system. If allocate is set to
        true, try to allocate more HugePages.

        :param node: Node in the topology.
        :param huge_mnt: HugePage mount point.
        :param mem_size: Reqeusted memory in MB.
        :param hugesize: HugePage size in KB.
        :param allocate: Whether to allocate more memory if not enough.
        :type node: dict
        :type huge_mnt: str
        :type mem_size: int
        :type hugesize: int
        :type allocate: bool
        :raises RuntimeError: Mounting hugetlbfs failed or not enough HugePages
            or increasing map count failed.
        """
        # Get huge pages information.
        hugepages = DUTSetup.get_hugepages_info(node, hugesize=hugesize)

        # Check if hugepages requested are available on node.
        if hugepages[u"nr_overcommit_hugepages"]:
            # If overcommit is used, we need to know how many additional pages
            # we can allocate
            huge_available = hugepages[u"nr_overcommit_hugepages"] - \
                hugepages[u"surplus_hugepages"]
        else:
            # Fallbacking to free_hugepages which were used before to detect.
            huge_available = hugepages[u"free_hugepages"]

        if ((mem_size * 1024) // hugesize) > huge_available:
            # If we want to allocate hugepage dynamically.
            if allocate:
                huge_needed = ((mem_size * 1024) // hugesize) - huge_available
                huge_to_allocate = huge_needed + hugepages[u"nr_hugepages"]
                max_map_count = huge_to_allocate * 4
                # Check if huge pages mount point exist.
                try:
                    exec_cmd_no_error(node, u"fgrep 'hugetlbfs' /proc/mounts")
                except RuntimeError:
                    exec_cmd_no_error(node, f"mkdir -p {huge_mnt}", sudo=True)
                    exec_cmd_no_error(
                        node,
                        f"mount -t hugetlbfs -o pagesize={hugesize}k none "
                        f"{huge_mnt}",
                        sudo=True)
                # Increase maximum number of memory map areas for process.
                exec_cmd_no_error(
                    node,
                    f"echo \"{max_map_count}\" | "
                    f"sudo tee /proc/sys/vm/max_map_count",
                    message=f"Increase map count failed on {node[u'host']}!"
                )
                # Increase hugepage count.
                exec_cmd_no_error(
                    node,
                    f"echo \"{huge_to_allocate}\" | "
                    f"sudo tee /proc/sys/vm/nr_hugepages",
                    message=f"Mount huge pages failed on {node[u'host']}!"
                )
            # If we do not want to allocate dynamically end with error.
            else:
                raise RuntimeError(
                    f"Not enough availablehuge pages: {huge_available}!"
                )
