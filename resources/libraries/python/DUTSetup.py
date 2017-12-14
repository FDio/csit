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

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.VPPUtil import VPPUtil


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
    def show_vpp_version_on_all_duts(nodes):
        """Show VPP version verbose on all DUTs.

        :param nodes: VPP nodes
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                DUTSetup.vpp_show_version_verbose(node)

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
        :returns: PID
        :rtype: int
        :raises RuntimeError if it is not possible to get the PID.
        """

        ssh = SSH()
        ssh.connect(node)

        for i in range(3):
            logger.trace('Try {}: Get VPP PID'.format(i))
            ret_code, stdout, stderr = ssh.exec_command('pidof vpp')

            if int(ret_code) != 0:
                raise RuntimeError('Not possible to get PID of VPP process '
                                   'on node: {0}\n {1}'.
                                   format(node['host'], stdout + stderr))

            if len(stdout.splitlines()) == 1:
                return int(stdout)
            elif len(stdout.splitlines()) == 0:
                logger.debug("No VPP PID found on node {0}".
                             format(node['host']))
                continue
            else:
                logger.debug("More then one VPP PID found on node {0}".
                             format(node['host']))
                ret_list = list()
                for line in stdout.splitlines():
                    ret_list.append(int(line))
                return ret_list

        return None

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
        :returns: nothing
        :raises RuntimeError: If QAT is not initialized or failed to initialize.
        """

        ssh = SSH()
        ssh.connect(node)

        cryptodev = Topology.get_cryptodev(node)
        cmd = 'cat /sys/bus/pci/devices/{0}/sriov_numvfs'.\
            format(cryptodev.replace(':', r'\:'))

        # Try to read number of VFs from PCI address of QAT device
        for _ in range(3):
            ret_code, stdout, _ = ssh.exec_command(cmd)
            if int(ret_code) == 0:
                try:
                    sriov_numvfs = int(stdout)
                except ValueError:
                    logger.trace('Reading sriov_numvfs info failed on {0}'.
                                 format(node['host']))
                else:
                    if sriov_numvfs != numvfs:
                        if force_init:
                            # QAT is not initialized and we want to initialize
                            # with numvfs
                            DUTSetup.crypto_device_init(node, numvfs)
                        else:
                            raise RuntimeError('QAT device {0} is not '
                                               'initialized to {1} on host {2}'
                                               .format(cryptodev, numvfs,
                                                       node['host']))
                    break

    @staticmethod
    def crypto_device_init(node, numvfs):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :param numvfs: Number of VFs to initialize, 0 - disable the VFs.
        :type node: dict
        :type numvfs: int
        :returns: nothing
        :raises RuntimeError: If failed to stop VPP or QAT failed to initialize.
        """
        cryptodev = Topology.get_cryptodev(node)

        # QAT device must be re-bound to kernel driver before initialization
        driver = 'dh895xcc'
        kernel_module = 'qat_dh895xcc'
        current_driver = DUTSetup.get_pci_dev_driver(
            node, cryptodev.replace(':', r'\:'))

        DUTSetup.kernel_module_verify(node, kernel_module, force_load=True)

        VPPUtil.stop_vpp_service(node)
        if current_driver is not None:
            DUTSetup.pci_driver_unbind(node, cryptodev)
        DUTSetup.pci_driver_bind(node, cryptodev, driver)

        ssh = SSH()
        ssh.connect(node)

        # Initialize QAT VFs
        if numvfs > 0:
            cmd = 'echo "{0}" | tee /sys/bus/pci/devices/{1}/sriov_numvfs'.\
                format(numvfs, cryptodev.replace(':', r'\:'), timeout=180)
            ret_code, _, _ = ssh.exec_command_sudo("sh -c '{0}'".format(cmd))

            if int(ret_code) != 0:
                raise RuntimeError('Failed to initialize {0} VFs on QAT device '
                                   ' on host {1}'.format(numvfs, node['host']))

    @staticmethod
    def pci_driver_unbind(node, pci_addr):
        """Unbind PCI device from current driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :returns: nothing
        :raises RuntimeError: If PCI device unbind failed.
        """

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command_sudo(
            "sh -c 'echo {0} | tee /sys/bus/pci/devices/{1}/driver/unbind'"
            .format(pci_addr, pci_addr.replace(':', r'\:')), timeout=180)

        if int(ret_code) != 0:
            raise RuntimeError('Failed to unbind PCI device {0} from driver on '
                               'host {1}'.format(pci_addr, node['host']))

    @staticmethod
    def pci_driver_bind(node, pci_addr, driver):
        """Bind PCI device to driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :param driver: Driver to bind.
        :type node: dict
        :type pci_addr: str
        :type driver: str
        :returns: nothing
        :raises RuntimeError: If PCI device bind failed.
        """

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command_sudo(
            "sh -c 'echo {0} | tee /sys/bus/pci/drivers/{1}/bind'".format(
                pci_addr, driver), timeout=180)

        if int(ret_code) != 0:
            raise RuntimeError('Failed to bind PCI device {0} to {1} driver on '
                               'host {2}'.format(pci_addr, driver,
                                                 node['host']))

    @staticmethod
    def get_pci_dev_driver(node, pci_addr):
        """Get current PCI device driver on node.

        :param node: DUT node.
        :param pci_addr: PCI device address.
        :type node: dict
        :type pci_addr: str
        :returns: Driver or None
        :raises RuntimeError: If PCI rescan or lspci command execution failed.
        """
        ssh = SSH()
        ssh.connect(node)

        for i in range(3):
            logger.trace('Try {0}: Get interface driver'.format(i))
            cmd = 'sh -c "echo 1 > /sys/bus/pci/rescan"'
            ret_code, _, _ = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise RuntimeError("'{0}' failed on '{1}'"
                                   .format(cmd, node['host']))

            cmd = 'lspci -vmmks {0}'.format(pci_addr)
            ret_code, stdout, _ = ssh.exec_command(cmd)
            if int(ret_code) != 0:
                raise RuntimeError("'{0}' failed on '{1}'"
                                   .format(cmd, node['host']))

            for line in stdout.splitlines():
                if len(line) == 0:
                    continue
                name = None
                value = None
                try:
                    name, value = line.split("\t", 1)
                except ValueError:
                    if name == "Driver:":
                        return None
                if name == 'Driver:':
                    return value
        else:
            return None

    @staticmethod
    def kernel_module_verify(node, module, force_load=False):
        """Verify if kernel module is loaded on all DUTs. If parameter force
        load is set to True, then try to load the modules.

        :param node: DUT node.
        :param module: Module to verify.
        :param force_load: If True then try to load module.
        :type node: dict
        :type module: str
        :type force_load: bool
        :returns: nothing
        :raises RuntimeError: If module is not loaded or failed to load.
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = 'grep -w {0} /proc/modules'.format(module)
        ret_code, _, _ = ssh.exec_command(cmd)

        if int(ret_code) != 0:
            if force_load:
                # Module is not loaded and we want to load it
                DUTSetup.kernel_module_load(node, module)
            else:
                raise RuntimeError('Kernel module {0} is not loaded on host '
                                   '{1}'.format(module, node['host']))

    @staticmethod
    def kernel_module_load(node, module):
        """Load kernel module on node.

        :param node: DUT node.
        :param module: Module to load.
        :type node: dict
        :type module: str
        :returns: nothing
        :raises RuntimeError: If loading failed.
        """

        ssh = SSH()
        ssh.connect(node)

        ret_code, _, _ = ssh.exec_command_sudo("modprobe {0}".format(module))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to load {0} kernel module on host {1}'.
                               format(module, node['host']))
