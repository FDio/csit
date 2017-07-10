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

"""VPP PCI Utility libraries"""

import re

from robot.api import logger

from resources.libraries.python.ssh import SSH

DPDK_SCRIPT = "./dpdk-devbind.py"

# PCI Device id regular expresssion
PCI_DEV_ID_REGEX = '[0-9A-Fa-f]+:[0-9A-Fa-f]+:[0-9A-Fa-f]+.[0-9A-Fa-f]+'


class VppPCIUtil(object):

    @staticmethod
    def _create_device_list(device_string):
        devices = []

        ids = re.findall(PCI_DEV_ID_REGEX, device_string)
        descriptions = re.findall('\'([\s\S]*?)\'', device_string)
        drivers = re.findall('drv=[\w,]+', device_string)
        unuseds = re.findall('unused=[\w,]+', device_string)
        interfaces = re.findall('if=[\w,]+', device_string)

        for i in range(len(ids)):
            device = {'id': ids[i], 'description': descriptions[i]}
            if len(drivers) > 0:
                device['driver'] = drivers[i].split('=')[1]
            device['unused'] = unuseds[i].split('=')[1]
            if len(interfaces) > 0:
                device['interface'] = interfaces[i].split('=')[1]
            devices.append(device)

        return devices

    def __init__(self, node):

        ssh = SSH()
        ssh.connect(node)

        (ret, stdout, stderr) = ssh.exec_command(DPDK_SCRIPT + ' --status')
        if ret != 0:
            logger.debug('Could not execute DPDK script on {}'.format(node['host']))
            logger.debug('stdout: {}'.format(stdout))
            logger.debug('stderr: {}'.format(stderr))
            raise RuntimeError('Could not execute DPDK script on node {}'.format(node['host']))

        # Get the network devices using the DPDK
        # First get everything after using DPDK
        stda = stdout.split('Network devices using DPDK-compatible driver')[1]
        # Then get everything before using kernel driver
        using_dpdk = stda.split('Network devices using kernel driver')[0]
        self._dpdk_devices = self._create_device_list(using_dpdk)

        # Get the network devices using the kernel
        stda = stdout.split('Network devices using kernel driver')[1]
        using_kernel = stda.split('Other network devices')[0]
        self._kernel_devices = self._create_device_list(using_kernel)

        # Get the other network devices
        stda = stdout.split('Other network devices')[1]
        other = stda.split('Crypto devices using DPDK-compatible driver')[0]
        self._other_devices = self._create_device_list(other)

        # Get the crypto devices using the DPDK
        stda = stdout.split('Crypto devices using DPDK-compatible driver')[1]
        crypto_using_dpdk = stda.split('Crypto devices using kernel driver')[0]
        self._crypto_dpdk_devices = self._create_device_list(crypto_using_dpdk)

        # Get the network devices using the kernel
        stda = stdout.split('Crypto devices using kernel driver')[1]
        crypto_using_kernel = stda.split('Other crypto devices')[0]
        self._crypto_kernel_devices = self._create_device_list(crypto_using_kernel)

        # Get the other network devices
        crypto_other = stdout.split('Other crypto devices')[1]
        self._crypto_other_devices = self._create_device_list(crypto_other)

        # Get the devices used by the kernel
        self._link_up_devices = []
        for d in self._kernel_devices:
            for i in d['interface'].split(','):
                cmd = "ip addr show " + i
                (ret, stdout, stderr) = ssh.exec_command(cmd)
                if ret != 0:
                    logger.debug('Could not execute DPDK script on {}'.format(node['host']))
                    logger.debug('stdout: {}'.format(stdout))
                    logger.debug('stderr: {}'.format(stderr))
                    raise RuntimeError('Could not execute DPDK script on node {}'.format(node['host']))
                lstate = re.findall(r'state \w+', stdout)[0].split(' ')[1]

                # Take care of the links that are UP
                if lstate == 'UP':
                    d['linkup'] = True
                    self._link_up_devices.append(d)

        for d in self._link_up_devices:
            self._kernel_devices.remove(d)

    def get_dpdk_devices(self):
        return self._dpdk_devices

    def get_kernel_devices(self):
        return self._kernel_devices

    def get_other_devices(self):
        return self._other_devices

    def get_crypto_dpdk_devices(self):
        return self._dpdk_devices

    def get_crypto_kernel_devices(self):
        return self._kernel_devices

    def get_crypto_other_devices(self):
        return self._other_devices

    def get_link_up_devices(self):
        return self._link_up_devices

    '''
    show_vpp_devices:

    Show the devices being used by vpp.
    '''

    @staticmethod
    def show_vpp_devices(devices):

        header = "{:15} {:25} {:50}".format("PCI ID", "Kernel Interface", "Description")
        dashseparator = ("-" * (len(header) - 2))

        print(header)
        print(dashseparator)
        for d in devices:
            if 'interface' in d:
                interface = d['interface']
            else:
                interface = 'NA'
            print("{:15} {:25} {:50}".format(d['id'], interface, d['description']))
