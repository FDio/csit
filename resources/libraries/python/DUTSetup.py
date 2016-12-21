# Copyright (c) 2016 Cisco and/or its affiliates.
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

from resources.libraries.python.topology import NodeType
from resources.libraries.python.topology import Topology
from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.VatExecutor import VatExecutor


class DUTSetup(object):
    """Contains methods for setting up DUTs."""
    @staticmethod
    def start_vpp_service_on_all_duts(nodes):
        """Start up the VPP service on all nodes."""
        ssh = SSH()
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                ssh.connect(node)
                (ret_code, stdout, stderr) = \
                    ssh.exec_command_sudo('service vpp restart', timeout=120)
                if int(ret_code) != 0:
                    logger.debug('stdout: {0}'.format(stdout))
                    logger.debug('stderr: {0}'.format(stderr))
                    raise Exception('DUT {0} failed to start VPP service'.
                                    format(node['host']))

    @staticmethod
    def vpp_show_version_verbose(node):
        """Run "show version verbose" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_version_verbose.vat", node, json_out=False)

    @staticmethod
    def vpp_api_trace_save(node):
        """Run "api trace save" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("api_trace_save.vat", node, json_out=False)

    @staticmethod
    def vpp_api_trace_dump(node):
        """Run "api trace custom-dump" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("api_trace_dump.vat", node, json_out=False)

    @staticmethod
    def setup_all_duts(nodes):
        """Prepare all DUTs in given topology for test execution."""
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.setup_dut(node)

    @staticmethod
    def setup_dut(node):
        """Run script over SSH to setup the DUT node.

        :param node: DUT node to set up.
        :type node: dict

        :raises Exception: If the DUT setup fails.
        """
        ssh = SSH()
        ssh.connect(node)

        (ret_code, stdout, stderr) = \
            ssh.exec_command('sudo -Sn bash {0}/{1}/dut_setup.sh'.
                             format(Constants.REMOTE_FW_DIR,
                                    Constants.RESOURCES_LIB_SH), timeout=120)
        logger.trace(stdout)
        logger.trace(stderr)
        if int(ret_code) != 0:
            logger.debug('DUT {0} setup script failed: "{1}"'.
                         format(node['host'], stdout + stderr))
            raise Exception('DUT test setup script failed at node {}'.
                            format(node['host']))

    @staticmethod
    def get_vpp_pid(node):
        """Get PID of running VPP process.

        :param node: DUT node.
        :type node: dict
        :return: PID
        :rtype: int
        :raises RuntimeError if it is not possible to get the PID.
        """

        ssh = SSH()
        ssh.connect(node)
        ret_code, stdout, stderr = ssh.exec_command('pidof vpp')

        logger.trace(stdout)
        logger.trace(stderr)

        if int(ret_code) != 0:
            logger.debug('Not possible to get PID of VPP process on node: '
                         '{0}\n {1}'.format(node['host'], stdout + stderr))
            raise RuntimeError('Not possible to get PID of VPP process on node:'
                               ' {}'.format(node['host']))

        if len(stdout.splitlines()) != 1:
            raise RuntimeError("More then one VPP PID found on node {0}".
                               format(node['host']))
        return int(stdout)

    @staticmethod
    def get_vpp_pids(nodes):
        """Get PID of running VPP process on all DUTs.

        :param nodes: DUT nodes.
        :type nodes: dict
        :return: PIDs
        :rtype: dict
        """

        pids = dict()
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                pids[node['host']] = DUTSetup.get_vpp_pid(node)
        return pids

    @staticmethod
    def vpp_show_crypto_device_mapping(node):
        """Run "show crypto device mapping" CLI command.

        :param node: Node to run command on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_crypto_device_mapping.vat", node,
                           json_out=False)

    @staticmethod
    def crypto_device_verify(node, force_init=False, numvfs=32):
        """Verify if Crypto QAT device virtual functions are initialized on all
        DUTs. If parameter force initialization is set to True, then try to
        initialize or disable QAT.

        :param node: DUT node.
        :param force_init: If True then try to initialize to specific value.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :type node: dict
        :type force_init: bool
        :type numvfs: int
        :return: nothing
        :raises RuntimeError if QAT is not initialized or failed to initialize.
        """

        ssh = SSH()
        ssh.connect(node)

        cryptodev = Topology.get_cryptodev(node)
        cmd = 'cat /sys/bus/pci/devices/{}/sriov_numvfs'.format(
            cryptodev.replace(':', r'\:'))

        # Try to read number of VFs from PCI address of QAT device
        for _ in range(3):
            ret_code, stdout, _ = ssh.exec_command(cmd)
            if int(ret_code) == 0:
                try:
                    sriov_numvfs = int(stdout)
                except ValueError:
                    logger.trace('Reading sriov_numvfs info failed on: {}'\
                        .format(node['host']))
                else:
                    if sriov_numvfs != numvfs:
                        if force_init:
                            # QAT is not initialized and we want to initialize
                            # with numvfs
                            DUTSetup.crypto_device_init(node, numvfs)
                        else:
                            raise RuntimeError('QAT device {} is not '\
                                'initialized to {} on host: {}'.format(\
                                cryptodev, numvfs, node['host']))
                    break

    @staticmethod
    def crypto_device_init(node, numvfs):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :type node: dict
        :type numvfs: int
        :return: nothing
        :raises RuntimeError if QAT failed to initialize.
        """

        ssh = SSH()
        ssh.connect(node)

        cryptodev = Topology.get_cryptodev(node)

        # QAT device must be bind to kernel driver before initialization
        DUTSetup.pci_driver_unbind(node, cryptodev)
        DUTSetup.pci_driver_bind(node, cryptodev, "dh895xcc")

        # Initialize QAT VFs
        ret_code, _, _ = ssh.exec_command(
            "sudo sh -c 'echo {} | tee /sys/bus/pci/devices/{}/sriov_numvfs'"
            .format(numvfs, cryptodev.replace(':', r'\:')))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to initialize {} VFs on QAT device on '
                               'host: {}'.format(numvfs, node['host']))

    @staticmethod
    def pci_driver_unbind(node, pci_addr):
        """Unbind PCI device from current driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :return: nothing
        :raises RuntimeError if PCI device unbind failed.
        """

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command(
            "sudo sh -c 'echo {} | tee /sys/bus/pci/devices/{}/driver/unbind'"
            .format(pci_addr, pci_addr.replace(':', r'\:')))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to unbind PCI device from driver on '
                               'host: {}'.format(node['host']))

    @staticmethod
    def pci_driver_bind(node, pci_addr, driver):
        """Bind PCI device to driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :param driver: Driver to bind.
        :type node: dict
        :type pci_addr: str
        :type driver: str
        :return: nothing
        :raises RuntimeError if PCI device bind failed.
        """

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command(
            "sudo sh -c 'echo {} | tee /sys/bus/pci/drivers/{}/bind'"
            .format(pci_addr, driver))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to bind PCI device to {} driver on '
                               'host: {}'.format(driver, node['host']))

    @staticmethod
    def kernel_module_verify(node, module, force_load=False):
        """Verify if kernel module is loaded on all DUTs. If parameter force
        load is set to True, then try to load the modules.

        :param node: DUT node.
        :param module: Module to verify.
        :param force_load: If True then try to load module.
        :type node: dict
        :type module: str
        :type force_init: bool
        :return: nothing
        :raises RuntimeError if module is not loaded or failed to load.
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = 'grep -w {} /proc/modules'.format(module)
        ret_code, _, _ = ssh.exec_command(cmd)

        if int(ret_code) != 0:
            if force_load:
                # Module is not loaded and we want to load it
                DUTSetup.kernel_module_load(node, module)
            else:
                raise RuntimeError('Kernel module {} is not loaded on host: '\
                    '{}'.format(module, node['host']))

    @staticmethod
    def kernel_module_load(node, module):
        """Load kernel module on node.

        :param node: DUT node.
        :param module: Module to load.
        :type node: dict
        :type module: str
        :return: nothing
        :raises RuntimeError if loading failed.
        """

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command_sudo("modprobe {}".format(module))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to load {} kernel module on host: '\
                '{}'.format(module, node['host']))
