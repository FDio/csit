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
    def crypto_device_verify(node, force_init=False):
        """Verify if Crypto QAT device virtual functions are initialized on all
        DUTs. If parameter force initialization is set to True, then try to
        initialize.

        :param node: DUT node.
        :param force_init: If True then try to initialize.
        :type node: dict
        :type force_init: bool
        :return: nothing
        :raises RuntimeError if QAT is not initialized or failed to initialize.
        """

        ssh = SSH()
        ssh.connect(node)

        cryptodev = Topology.get_cryptodev(node)

        ret_code, stdout, _ = ssh.exec_command('lspci -vmms {}'.format(
            cryptodev))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to retrieve lscpi information on host: '
                               '{}'.format(node['host']))

        if not stdout:
            if force_init:
                DUTSetup.crypto_device_init(node)
            else:
                raise RuntimeError('Crypto device is not initialized on host: '
                                   '{}'.format(node['host']))

    @staticmethod
    def crypto_device_init(node):
        """Init Crypto QAT device virtual functions on DUT.

        :param node: DUT node.
        :type node: dict
        :return: nothing
        :raises RuntimeError if QAT failed to initialize.
        """

        ssh = SSH()
        ssh.connect(node)

        cryptodev = Topology.get_cryptodev(node)
        cryptodev_addr = '{0}:{1}:00.0'.format(cryptodev.split(':')[0],
                                               cryptodev.split(':')[1])
        cryptodev_path = r'{0}\:{1}\:00.0'.format(cryptodev.split(':')[0],
                                                  cryptodev.split(':')[1])

        ret_code, _, _ = ssh.exec_command(
            "sudo sh -c 'echo {} | tee /sys/bus/pci/devices/{}/driver/unbind'"
            .format(cryptodev_addr, cryptodev_path))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to unbind QAT device on '
                               'host: {}'.format(node['host']))

        ret_code, _, _ = ssh.exec_command(
            "sudo sh -c 'echo {} | tee /sys/bus/pci/drivers/dh895xcc/bind'"
            .format(cryptodev_addr))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to bind QAT device to kernel driver on '
                               'host: {}'.format(node['host']))

        ret_code, _, _ = ssh.exec_command(
            "sudo sh -c 'echo 32 | tee /sys/bus/pci/devices/{}/sriov_numvfs'"
            .format(cryptodev_path))

        if int(ret_code) != 0:
            raise RuntimeError('Failed to initialize VFs on QAT device on '
                               'host: {}'.format(node['host']))

