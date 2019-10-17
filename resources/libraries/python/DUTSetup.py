# Copyright (c) 2018 Cisco and/or its affiliates.
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

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class DUTSetup(object):
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
            command = ('echo $(< /tmp/*supervisor*.log)')
        else:
            command = ('journalctl --no-pager --unit={name} '
                       '--since="$(echo `systemctl show -p '
                       'ActiveEnterTimestamp {name}` | '
                       'awk \'{{print $2 $3}}\')"'.
                       format(name=service))
        message = 'Node {host} failed to get logs from unit {name}'.\
            format(host=node['host'], name=service)

        exec_cmd_no_error(node, command, timeout=30, sudo=True,
                          message=message)

    @staticmethod
    def get_service_logs_on_all_duts(nodes, service):
        """Get specific service unit logs from all DUTs.

        :param nodes: Nodes in the topology.
        :param service: Service unit name.
        :type nodes: dict
        :type service: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
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
            command = 'supervisorctl restart {name}'.format(name=service)
        else:
            command = 'service {name} restart'.format(name=service)
        message = 'Node {host} failed to restart service {name}'.\
            format(host=node['host'], name=service)

        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message)

        DUTSetup.get_service_logs(node, service)

    @staticmethod
    def restart_service_on_all_duts(nodes, service):
        """Restart the named service on all DUTs.

        :param node: Nodes in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.restart_service(node, service)

    @staticmethod
    def start_service(node, service):
        """Start up the named service on node.

        :param node: Node in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        # TODO: change command to start once all parent function updated.
        if DUTSetup.running_in_container(node):
            command = 'supervisorctl restart {name}'.format(name=service)
        else:
            command = 'service {name} restart'.format(name=service)
        message = 'Node {host} failed to start service {name}'.\
            format(host=node['host'], name=service)

        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message)

        DUTSetup.get_service_logs(node, service)

    @staticmethod
    def start_service_on_all_duts(nodes, service):
        """Start up the named service on all DUTs.

        :param node: Nodes in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.start_service(node, service)

    @staticmethod
    def stop_service(node, service):
        """Stop the named service on node.

        :param node: Node in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        if DUTSetup.running_in_container(node):
            command = 'supervisorctl stop {name}'.format(name=service)
        else:
            command = 'service {name} stop'.format(name=service)
        message = 'Node {host} failed to stop service {name}'.\
            format(host=node['host'], name=service)

        exec_cmd_no_error(
            node, command, timeout=180, sudo=True, message=message)

        DUTSetup.get_service_logs(node, service)

    @staticmethod
    def stop_service_on_all_duts(nodes, service):
        """Stop the named service on all DUTs.

        :param node: Nodes in the topology.
        :param service: Service unit name.
        :type node: dict
        :type service: str
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.stop_service(node, service)

    @staticmethod
    def get_vpp_pid(node):
        """Get PID of running VPP process.

        :param node: DUT node.
        :type node: dict
        :returns: PID
        :rtype: int or list of int
        :raises RuntimeError: If it is not possible to get the PID.
        """
        cmd = 'pidof vpp | grep .'
        message = 'Failed to get PID of VPP process on node: {host}'.format(
            host=node['host'])
        stdout, _ = exec_cmd_no_error(
            node, cmd, retries=2, message=message, include_reason=True)
        pid_list = stdout.split()
        if len(pid_list) == 1:
            return int(stdout)
        logger.debug("More than one VPP PID found on node {host}".format(
            host=node['host']))
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
            if node['type'] == NodeType.DUT:
                pids[node['host']] = DUTSetup.get_vpp_pid(node)
        return pids

    @staticmethod
    def crypto_device_verify(node, crypto_type, numvfs, force_init=False):
        """Verify if Crypto QAT device virtual functions are initialized on all
        DUTs. If parameter force initialization is set to True, then try to
        initialize or remove VFs on QAT.

        :param node: DUT node.
        :crypto_type: Crypto device type - HW_DH895xcc or HW_C3xxx.
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
                raise RuntimeError('QAT device failed to create VFs on {host}'.
                                   format(host=node['host']))

    @staticmethod
    def crypto_device_init(node, crypto_type, numvfs):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :crypto_type: Crypto device type - HW_DH895xcc or HW_C3xxx.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :type node: dict
        :type crypto_type: string
        :type numvfs: int
        :returns: nothing
        :raises RuntimeError: If failed to stop VPP or QAT failed to initialize.
        """
        if crypto_type == "HW_DH895xcc":
            kernel_mod = "qat_dh895xcc"
            kernel_drv = "dh895xcc"
        elif crypto_type == "HW_C3xxx":
            kernel_mod = "qat_c3xxx"
            kernel_drv = "c3xxx"
        else:
            raise RuntimeError('Unsupported crypto device type on {host}'.
                               format(host=node['host']))

        pci_addr = Topology.get_cryptodev(node)

        # QAT device must be re-bound to kernel driver before initialization.
        DUTSetup.verify_kernel_module(node, kernel_mod, force_load=True)

        # Stop VPP to prevent deadlock.
        DUTSetup.stop_service(node, Constants.VPP_UNIT)

        current_driver = DUTSetup.get_pci_dev_driver(
            node, pci_addr.replace(':', r'\:'))
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
        :rtype: int
        :raises RuntimeError: If failed to get Virtual Function PCI address.
        """
        command = "sh -c "\
            "'basename $(readlink /sys/bus/pci/devices/{pci}/virtfn{vf_id})'".\
            format(pci=pf_pci_addr, vf_id=vf_id)
        message = 'Failed to get virtual function PCI address.'

        stdout, _ = exec_cmd_no_error(node, command, timeout=30, sudo=True,
                                      message=message)

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
        command = 'cat /sys/bus/pci/devices/{pci}/sriov_numvfs'.\
            format(pci=pf_pci_addr.replace(':', r'\:'))
        message = 'PCI device {pci} is not a SR-IOV device.'.\
            format(pci=pf_pci_addr)

        for _ in range(3):
            stdout, _ = exec_cmd_no_error(node, command, timeout=30, sudo=True,
                                          message=message)
            try:
                sriov_numvfs = int(stdout)
            except ValueError:
                logger.trace('Reading sriov_numvfs info failed on {host}'.
                             format(host=node['host']))
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
        command = "sh -c "\
            "'echo {num} | tee /sys/bus/pci/devices/{pci}/sriov_numvfs'".\
            format(num=numvfs, pci=pf_pci_addr.replace(':', r'\:'))
        message = 'Failed to create {num} VFs on {pci} device on {host}'.\
            format(num=numvfs, pci=pf_pci_addr, host=node['host'])

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

    @staticmethod
    def pci_driver_unbind(node, pci_addr):
        """Unbind PCI device from current driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :raises RuntimeError: If PCI device unbind failed.
        """
        command = "sh -c "\
            "'echo {pci} | tee /sys/bus/pci/devices/{pcie}/driver/unbind'".\
            format(pci=pci_addr, pcie=pci_addr.replace(':', r'\:'))
        message = 'Failed to unbind PCI device {pci} on {host}'.\
            format(pci=pci_addr, host=node['host'])

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

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
        message = 'Failed to bind PCI device {pci} to {driver} on host {host}'.\
            format(pci=pci_addr, driver=driver, host=node['host'])

        command = "sh -c "\
            "'echo {driver} | tee /sys/bus/pci/devices/{pci}/driver_override'".\
            format(driver=driver, pci=pci_addr.replace(':', r'\:'))

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

        command = "sh -c "\
            "'echo {pci} | tee /sys/bus/pci/drivers/{driver}/bind'".\
            format(pci=pci_addr, driver=driver)

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

        command = "sh -c "\
            "'echo  | tee /sys/bus/pci/devices/{pci}/driver_override'".\
            format(pci=pci_addr.replace(':', r'\:'))

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

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
        vf_path = "/sys/bus/pci/devices/{pf_pci_addr}/virtfn{vf_id}".\
            format(pf_pci_addr=pf_pci_addr.replace(':', r'\:'), vf_id=vf_id)

        command = "sh -c "\
            "'echo {vf_pci_addr} | tee {vf_path}/driver/unbind'".\
            format(vf_pci_addr=vf_pci_addr, vf_path=vf_path)

        message = 'Failed to unbind VF {vf_pci_addr} to on {host}'.\
            format(vf_pci_addr=vf_pci_addr, host=node['host'])

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

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
        vf_path = "/sys/bus/pci/devices/{pf_pci_addr}/virtfn{vf_id}".\
            format(pf_pci_addr=pf_pci_addr.replace(':', r'\:'), vf_id=vf_id)

        message = 'Failed to bind VF {vf_pci_addr} to {driver} on {host}'.\
            format(vf_pci_addr=vf_pci_addr, driver=driver, host=node['host'])

        command = "sh -c "\
            "'echo {driver} | tee {vf_path}/driver_override'".\
            format(driver=driver, vf_path=vf_path)

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

        command = "sh -c "\
            "'echo {vf_pci_addr} | tee /sys/bus/pci/drivers/{driver}/bind'".\
            format(vf_pci_addr=vf_pci_addr, driver=driver)

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

        command = "sh -c "\
            "'echo  | tee {vf_path}/driver_override'".\
            format(vf_path=vf_path)

        exec_cmd_no_error(node, command, timeout=120, sudo=True,
                          message=message)

    @staticmethod
    def get_pci_dev_driver(node, pci_addr):
        """Get current PCI device driver on node.

        .. note::
            # lspci -vmmks 0000:00:05.0
            Slot:   00:05.0
            Class:  Ethernet controller
            Vendor: Red Hat, Inc
            Device: Virtio network device
            SVendor:        Red Hat, Inc
            SDevice:        Device 0001
            PhySlot:        5
            Driver: virtio-pci

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :returns: Driver or None
        :raises RuntimeError: If PCI rescan or lspci command execution failed.
        :raises RuntimeError: If it is not possible to get the interface driver
            information from the node.
        """
        cmd = ('lspci -vmmks {pci_addr} | grep Driver: '
               '|| {{ echo 1 > /sys/bus/pci/rescan ; false ; }}'.format(
                   pci_addr=pci_addr))
        stdout, _ = exec_cmd_no_error(node, cmd, sudo=True, retries=2)
        return stdout.split(":", 1)[-1].strip() or None

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
        command = 'grep -w {module} /proc/modules'.format(module=module)
        message = 'Kernel module {module} is not loaded on host {host}'.\
            format(module=module, host=node['host'])

        try:
            exec_cmd_no_error(node, command, timeout=30, sudo=False,
                              message=message)
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

        :param node: DUT nodes.
        :param module: Module to verify.
        :param force_load: If True then try to load module.
        :type node: dict
        :type module: str
        :type force_load: bool
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.verify_kernel_module(node, module, force_load)

    @staticmethod
    def verify_uio_driver_on_all_duts(nodes):
        """Verify if uio driver kernel module is loaded on all DUTs. If module
        is not present it will try to load it.

        :param node: DUT nodes.
        :type node: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
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
        command = 'modprobe {module}'.format(module=module)
        message = 'Failed to load {module} on host {host}'.\
            format(module=module, host=node['host'])

        exec_cmd_no_error(node, command, timeout=30, sudo=True, message=message)

    @staticmethod
    def install_vpp_on_all_duts(nodes, vpp_pkg_dir):
        """Install VPP on all DUT nodes. Start the VPP service in case of
        systemd is not available or does not support autostart.

        :param nodes: Nodes in the topology.
        :param vpp_pkg_dir: Path to directory where VPP packages are stored.
        :type nodes: dict
        :type vpp_pkg_dir: str
        :raises RuntimeError: If failed to remove or install VPP.
        """
        for node in nodes.values():
            message = 'Failed to install VPP on host {host}!'.\
                format(host=node['host'])
            if node['type'] == NodeType.DUT:
                command = 'ln -s /dev/null /etc/sysctl.d/80-vpp.conf || true'
                exec_cmd_no_error(node, command, sudo=True)

                command = '. /etc/lsb-release; echo "${DISTRIB_ID}"'
                stdout, _ = exec_cmd_no_error(node, command)

                if stdout.strip() == 'Ubuntu':
                    exec_cmd_no_error(node, 'apt-get purge -y "*vpp*" || true',
                                      timeout=120, sudo=True)
                    exec_cmd_no_error(node, 'dpkg -i --force-all {dir}*.deb'.
                                      format(dir=vpp_pkg_dir), timeout=120,
                                      sudo=True, message=message)
                    exec_cmd_no_error(node, 'dpkg -l | grep vpp', sudo=True)
                    if DUTSetup.running_in_container(node):
                        DUTSetup.restart_service(node, Constants.VPP_UNIT)
                else:
                    exec_cmd_no_error(node, 'yum -y remove "*vpp*" || true',
                                      timeout=120, sudo=True)
                    exec_cmd_no_error(node, 'rpm -ivh {dir}*.rpm'.
                                      format(dir=vpp_pkg_dir), timeout=120,
                                      sudo=True, message=message)
                    exec_cmd_no_error(node, 'rpm -qai *vpp*', sudo=True)
                    DUTSetup.restart_service(node, Constants.VPP_UNIT)

    @staticmethod
    def running_in_container(node):
        """This method tests if topology node is running inside container.

        :param node: Topology node.
        :type node: dict
        :returns: True if running in docker container, false if not or failed
        to detect.
        :rtype: bool
        """
        command = "fgrep docker /proc/1/cgroup"
        message = 'Failed to get cgroup settings.'
        try:
            exec_cmd_no_error(node, command, timeout=30, sudo=False,
                              message=message)
        except RuntimeError:
            return False
        return True

    @staticmethod
    def get_docker_mergeddir(node, uuid):
        """Get Docker overlay for MergedDir diff.

        :param node: DUT node.
        :param uuid: Docker UUID.
        :type node: dict
        :type uuid: str
        :returns: Docker container MergedDir.
        :rtype: str
        :raises RuntimeError: If getting output failed.
        """
        command = "docker inspect --format='"\
            "{{{{.GraphDriver.Data.MergedDir}}}}' {uuid}".format(uuid=uuid)
        message = 'Failed to get directory of {uuid} on host {host}'.\
            format(uuid=uuid, host=node['host'])

        stdout, _ = exec_cmd_no_error(node, command, sudo=True, message=message)
        return stdout.strip()

    @staticmethod
    def get_huge_page_size(node):
        """Get default size of huge pages in system.

        :param node: Node in the topology.
        :type node: dict
        :returns: Default size of free huge pages in system.
        :rtype: int
        :raises RuntimeError: If reading failed for three times.
        """

        cmd = "sed -n '/Hugepagesize/s/[^0-9]//gp' /proc/meminfo | grep ."
        message = 'Getting huge page size information failed.'
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, retries=2, message=message)
        return int(stdout)

    @staticmethod
    def get_huge_page_free(node, huge_size):
        """Get number of free huge pages in system.

        :param node: Node in the topology.
        :param huge_size: Size of hugepages.
        :type node: dict
        :type huge_size: int
        :returns: Number of free huge pages in system.
        :rtype: int
        :raises RuntimeError: If reading failed for three times.
        """
        # TODO: add numa aware option
        cmd = ('grep "[0-9]" '
               '/sys/kernel/mm/hugepages/hugepages-{size}kB/free_hugepages'
               .format(size=huge_size))
        message = 'Getting free huge pages information failed'
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, retries=2, message=message)
        return int(stdout)

    @staticmethod
    def get_huge_page_total(node, huge_size):
        """Get total number of huge pages in system.

        :param node: Node in the topology.
        :param huge_size: Size of hugepages.
        :type node: dict
        :type huge_size: int

        :returns: Total number of huge pages in system.
        :rtype: int
        :raises RuntimeError: If reading failed for three times.
        """
        # TODO: add numa aware option
        cmd = ('grep "[0-9]" '
               '/sys/kernel/mm/hugepages/hugepages-{size}kB/nr_hugepages'
               .format(size=huge_size))
        message = 'Getting total huge pages information failed.'
        stdout, _ = exec_cmd_no_error(
            node, cmd, sudo=True, retries=2, message=message)
        return int(stdout)

    @staticmethod
    def has_huge_page_mounted(node, huge_mnt):
        """Return whether a mount point for huge pages exists on node.

        :param node: Node in the topology
        :param huge_mnt: HugePage mount point
        :type node: dict
        :type huge_mnt: str
        :returns: whether there is hugepagefs mounted at mount point
        :rtype: bool
        :raises RuntimeError: remote command execution failed
        """
        cmd = "grep -e '{huge_mnt}.*hugetlbfs' /proc/mounts".format(
            huge_mnt=huge_mnt)
        ret_code, _, _ = exec_cmd(node, cmd)
        return ret_code == 0

    @staticmethod
    def create_huge_page_mount(node, huge_mnt):
        """Return whether a mount point for huge pages exists on node.

        :param node: Node in the topology
        :param huge_mnt: HugePage mount point
        :type node: dict
        :type huge_mnt: str
        :raises RuntimeError: remote command execution failed
        """
        # TODO why is 2048 hardcoded here
        cmd = ('mkdir -p {mnt} && '
               'mount -t hugetlbfs -o pagesize=2048k none {mnt}'
               .format(mnt=huge_mnt))
        message = 'Mount huge pages failed on {host}'.format(host=node['host'])
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

    @staticmethod
    def set_huge_page_max_map_count(node, max_map_count):
        """Set maximum number of memory map areas a process may have on node.

        :param node: Node in the topology
        :param max_map_count: Max number of memory map areas
        :type node: dict
        :type max_map_count: int
        :raises RuntimeError: remote command execution failed
        """
        cmd = 'echo "{max_map_count}" | tee /proc/sys/vm/max_map_count'.format(
            max_map_count=max_map_count)
        message = 'Set map count failed on {host}'.format(host=node['host'])
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

    @staticmethod
    def set_huge_page_count(node, page_count):
        """Set hugepage count on node.

        :param node: Node in the topology
        :param page_count: HugePage count
        :type node: dict
        :type page_count: int
        :raises RuntimeError: remote command execution failed
        """
        cmd = 'echo "{page_count}" | tee /proc/sys/vm/nr_hugepages'.format(
            page_count=page_count)
        message = 'Set huge page count failed on {host}'.format(
            host=node['host'])
        exec_cmd_no_error(node, cmd, sudo=True, message=message)

    @staticmethod
    def check_huge_page(node, huge_mnt, mem_size, allocate=False):
        """Check if there is enough HugePages in system. If allocate is set to
        true and there isn't enough currently, try to allocate more HugePages.

        :param node: Node in the topology.
        :param huge_mnt: HugePage mount point.
        :param mem_size: Requested memory in MB.
        :param allocate: Whether to allocate more memory if not enough.
        :type node: dict
        :type huge_mnt: str
        :type mem_size: str
        :type allocate: bool

        :raises RuntimeError: Mounting hugetlbfs failed or not enough HugePages
        or increasing map count failed.
        """
        # Get huge pages information
        huge_size = DUTSetup.get_huge_page_size(node)
        huge_free = DUTSetup.get_huge_page_free(node, huge_size)
        huge_total = DUTSetup.get_huge_page_total(node, huge_size)

        # Check if memory requested is available on host
        if (mem_size * 1024) > (huge_free * huge_size):
            # If we want to allocate hugepage dynamically
            if allocate:
                mem_needed = (mem_size * 1024) - (huge_free * huge_size)
                huge_to_allocate = ((mem_needed / huge_size) * 2) + huge_total
                max_map_count = huge_to_allocate * 4
                DUTSetup.set_huge_page_max_map_count(node, max_map_count)
                DUTSetup.set_huge_page_count(node, huge_to_allocate)
            # If we do not want to allocate dynamicaly end with error
            else:
                raise RuntimeError('Not enough free huge pages: {0}, {1} MB'.
                                   format(huge_free, huge_free * huge_size))

        # If huge page mount point does not exist create one
        if not DUTSetup.has_huge_page_mounted(node, huge_mnt):
            DUTSetup.create_huge_page_mount(node, huge_mnt)
