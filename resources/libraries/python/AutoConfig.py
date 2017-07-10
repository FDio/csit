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

"""Library that supports Auto Configuration."""

import yaml
import logging

from resources.libraries.python.VppPCIUtil import VppPCIUtil
from resources.libraries.python.VppHugePageUtil import VppHugePageUtil
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.VppGrubUtil import VppGrubUtil
from resources.libraries.python.VhostUser import VhostUser
from resources.libraries.python.topology import Topology
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
from resources.libraries.python.QemuUtils import QemuUtils
from resources.libraries.python.ssh import SSH

'''
This module includes methods and classes that can be used by the auto configuration utility.

The classes and methods are related to Configuring the system under test.
 
'''

"""Auto Configuration tools."""

__all__ = ["AutoConfig"]

DEFAULT_SYSTEM_CONFIG_FILENAME = "./system-config.yaml"


class AutoConfig(object):
    """Auto Configuration Tools"""

    def __init__(self, autoconfig_filename):
        self._autoconfig_filename = autoconfig_filename
        self._metadata = {}
        self._nodes = {}
        self._vpp_devices_node = {}
        self._hugepage_config = ""
        self._loadconfig()

    def get_nodes(self):
        return self._nodes

    '''
    _ask_user_yn:

    Ask the user yes or no
    '''

    @staticmethod
    def _ask_user_yn(question):

        a = ''
        while a != 'y' or a != 'n':
            a = raw_input("\n{}[y/n]? ".format(question))
            a = a[0].lower()

            if a == 'y' or a == 'n':
                return a
            else:
                print("Please answer yes or no.")

    '''
    _loadconfig:

    Load the testbed configuration, given the auto configuration file.
    '''

    def _loadconfig(self):
        # Get the Topology, from the topology layout file
        with open(self._autoconfig_filename, 'r') as stream:
            try:
                yl = yaml.load(stream)
                if 'metadata' in yl:
                    self._metadata = yl['metadata']
                if 'nodes' in yl:
                    self._nodes = yl['nodes']
            except yaml.YAMLError as exc:
                print(exc)

    '''
    _updateconfig:

    Update the testbed configuration, given the auto configuration file.
    We will write the system configuration file with the current node information
    '''

    def _updateconfig(self):

        # Initialize the yaml data
        yl = {'metadata': self._metadata, 'nodes': self._nodes}

        # Write the system config file
        if 'system_config_file' in self._metadata:
            filename = self._metadata['system_config_file']
        else:
            filename = DEFAULT_SYSTEM_CONFIG_FILENAME
        with open(filename, 'w') as f:
            yaml.dump(yl, f, default_flow_style=False)

    '''
    update_auto_config:

    Write the auto configuration file with the new configuration data.
    '''

    def _update_auto_config(self):

        # Initialize the yaml data
        nodes = []
        with open(self._autoconfig_filename, 'r') as stream:
            try:
                yl = yaml.load(stream)
                if 'nodes' in yl:
                    nodes = yl['nodes']
            except yaml.YAMLError as exc:
                print(exc)
                return

        for i in nodes.items():
            key = i[0]
            node = i[1]

            interfaces = {}
            if 'devices' in self._nodes[key]:
                devices = self._nodes[key]['devices']
                for j in range(len(devices)):
                    p = 'port{}'.format(j)
                    interfaces[p] = {}
                    interfaces[p]['pci_address'] = devices[j]['id']
                    macs = devices[j]['l2_addr']
                    interfaces[p]['mac_address'] = devices[j]['l2_addr'][0]
                    for k in range(len(macs)):
                        if k > 0:
                            m = "mac_address_{}".format(k+1)
                            interfaces[p][m] = {}
                            interfaces[p][m] = '{}'.format(macs[k])
            node['interfaces'] = interfaces

        # Write the auto config config file
        with open(self._autoconfig_filename, 'w') as f:
            yaml.dump(yl, f, default_flow_style=False)

    '''
    _get_new_vpp_devices:

    Given a list of devices owned by the kernel, get a list of devices to use
    '''

    @staticmethod
    def _get_new_vpp_device_list(self, kernel_devices, devices_to_be_used=None):

        vpp_devices = []
        for d in kernel_devices:
            if devices_to_be_used is None:
                print("\nDo you want to use this device for FDIO:")
                if 'interface' in d:
                    print("{}  {}  {}".format(d['id'], d['interface'], d['description']))
                else:
                    print("{}  {}".format(d['id'], d['description']))
                a = self._ask_user_yn("")
                if a == 'y':
                    vpp_devices.append(d)
            else:
                d2 = filter(lambda x: x['id'] == d['id'], devices_to_be_used)
                if d2:
                    vpp_devices.append(d)

        return vpp_devices

    '''
    apply_vpp_cpu:

    Apply the VPP cpu config
    '''

    @staticmethod
    def apply_vpp_cpu(cfggen):

        node = cfggen.get_node()

        vpp_main_core = node['cpu']['vpp_main_core']
        cfggen.add_cpu_main_core(vpp_main_core)

        vpp_worker_list = node['cpu']['vpp_worker_list']
        cfggen.add_cpu_corelist_workers(vpp_worker_list)

    '''
    apply_vpp_unix:

    Apply the VPP Unix config
    '''

    @staticmethod
    def apply_vpp_unix(cfggen, vpp):

        if 'unix' not in vpp:
            return
        unix = vpp['unix']

        if 'log' in unix:
            cfggen.add_unix_log(unix['log'])
        if 'cli-listen' in unix:
            cfggen.add_unix_cli_listen(unix['cli-listen'])
        if ('nodaemon' in unix) and (unix['nodaemon'] is True):
            cfggen.add_unix_nodaemon()
        if ('interactive' in unix) and (unix['interactive'] is True):
            cfggen.add_unix_interactive()
        if ('full-coredump' in unix) and (unix['full-coredump'] is True):
            cfggen.add_unix_full_coredump()

    '''
    apply_device:

    Apply VPP PCI Device configuration.
    '''

    @staticmethod
    def apply_vpp_devices(cfggen):

        node = cfggen.get_node()

        if 'interfaces' not in node:
            return

        interfaces = node['interfaces']
        devices = []
        for i in interfaces.values():
            devices.append(i['pci_address'])

        dt = tuple(devices)
        cfggen.add_dpdk_dev(*dt)

    '''
    apply_hugepage:
    
    Apply the hugepage configuration
    '''

    def apply_hugepages(self):

        for i in self._nodes.items():
            node = i[1]

            vppcfg = VppHugePageUtil(node)
            vppcfg.hugepage_apply_config()

    '''
    apply_vpp_startup:

    Apply the vpp startup configration
    '''

    def apply_vpp_startup(self, apply_cpu=False):

        # Apply the VPP startup configruation
        for i in self._nodes.items():
            node = i[1]

            cfggen = VppConfigGenerator()
            cfggen.set_node(node)

            if 'vpp' in node:
                vpp = node['vpp']

                # Apply some basics
                if 'startup_config_file' in vpp:
                    cfggen.set_config_filename(node['vpp']['startup_config_file'])

                if ('api-trace' in vpp) and vpp['api-trace'] is True:
                    cfggen.add_api_trace()

                    if ('api-segment' in vpp) and ('gid' in vpp['api-segment']):
                        cfggen.add_api_segment_gid()

                # Apply the number of receive queues
                if ('dpdk' in vpp) and ('rx-queues' in vpp['dpdk']):
                    cfggen.add_dpdk_dev_default_rxq('2')

                # Apply the unix config
                self.apply_vpp_unix(cfggen, vpp)

                # Apply the device configuration
                self.apply_vpp_devices(cfggen)

                # Apply cpu
                if apply_cpu is True:
                    self.apply_vpp_cpu(cfggen)

            # Write the startup file, restarts vpp
            cfggen.apply_config()

    '''
    apply_grub:

    Apply the grub configuration startup configration
    '''

    def apply_grub(self):

        for i in self._nodes.items():
            node = i[1]

            vppgrb = VppGrubUtil(node)
            vpp_cmdline = vppgrb.apply_cmdline(node)

            node['grub']['vpp_cmdline'] = vpp_cmdline

        self._updateconfig()

    '''
    get_hugepages:

    Get the hugepage configuration
    '''

    def get_hugepages(self):

        for i in self._nodes.items():
            node = i[1]

            vppcfg = VppHugePageUtil(node)
            total, max_map_count, shmmax = vppcfg.get_huge_page_config()
            node['hugepages']['total'] = total
            node['hugepages']['max_map_count'] = max_map_count
            node['hugepages']['shmax'] = shmmax

        self._updateconfig()

    '''
    get_grub:

    Get the grub configuration
    '''

    def get_grub(self):

        for i in self._nodes.items():
            node = i[1]

            vppgrb = VppGrubUtil(node)
            current_cmdline = vppgrb.get_current_cmdline()
            default_cmdline = vppgrb.get_default_cmdline()

            if 'grub' not in node:
                node['grub'] = {}
            node['grub']['current_cmdline'] = current_cmdline
            node['grub']['default_cmdline'] = default_cmdline

        self._updateconfig()

    '''
    get_device:

    Get the device configuration
    '''

    def get_device(self):

        # Update the interface data
        InterfaceUtil.update_all_interface_data_on_all_nodes(self._nodes, numa_node=True)
        self._updateconfig()

    '''
    get_cpu:

    Get the cpu configuration
    '''

    def get_cpu(self):

        # Get the CPU layout
        CpuUtils.get_cpu_layout_from_all_nodes(self._nodes)

        for i in self._nodes.items():
            node = i[1]

            cpuinfo = node['cpuinfo']
            smt_enabled = CpuUtils.is_smt_enabled(cpuinfo)
            cpu_node_count = CpuUtils.cpu_node_count(node)
            vpp_worker_cores = node['cpu']['vpp_worker_cores']
            skip_cnt = node['cpu']['skip_cores']
            isolated_cores = node['cpu']['isolated_cores']
            cpu_cnt = isolated_cores / cpu_node_count
            vpp_worker_cnt = vpp_worker_cores / cpu_node_count

            ikeys = node['interfaces'].keys()
            numa_node_highest_interfaces_cnt = Topology.get_interfaces_numa_node(node, *tuple(ikeys))

            # Get a list of all the cores
            cpu_list = CpuUtils.cpu_range_per_node_str(node, numa_node_highest_interfaces_cnt,
                                                       skip_cnt=skip_cnt,
                                                       cpu_cnt=cpu_cnt,
                                                       smt_used=smt_enabled)
            node['cpu']['list'] = cpu_list

            # Get 2 core 1 for vpp main thread and 1 for qemu
            core_list = CpuUtils.cpu_slice_of_list_per_node(node,
                                                            numa_node_highest_interfaces_cnt,
                                                            skip_cnt=skip_cnt,
                                                            cpu_cnt=1,
                                                            smt_used=smt_enabled)
            node['cpu']['vpp_main_core'] = core_list[0]
            node['cpu']['qemu_core'] = core_list[1]
            node['cpu']['smt_enabled'] = smt_enabled

            # Allocate cores for the vpp workers
            if smt_enabled:
                skip_cnt += 1
            else:
                skip_cnt += 2
            # Get a list of all the cores
            vpp_worker_list = CpuUtils.cpu_range_per_node_str(node, numa_node_highest_interfaces_cnt,
                                                              skip_cnt=skip_cnt,
                                                              cpu_cnt=vpp_worker_cnt,
                                                              smt_used=smt_enabled)
            node['cpu']['vpp_worker_list'] = vpp_worker_list

            # We don't want to write the cpuinfo
            node['cpuinfo'] = ""

        # Write the config
        self._updateconfig()

    '''
    discover:

    Get the current system configuration.
    '''

    def discover(self):

        # Get the Huge Page configuration
        self.get_hugepages()

        # Get the device configuration
        self.get_device()

        # Get the CPU configuration
        self.get_cpu()

        # Get the current grub cmdline
        self.get_grub()

    '''
    apply_preboot:

    Apply the config that is needed before rebooting.
    '''

    def apply_preboot(self):

        # Apply Huge Pages
        self.apply_hugepages()

        # Partially Apply the VPP startup
        self.apply_vpp_startup(apply_cpu=False)

        # Discover the basic config
        self.discover()

        # Apply the grub configuration
        self.apply_grub()

        # reboot
        a = self._ask_user_yn("Your system(s) have been reconfigured are you ready to reboot ")
        if a == 'y':

            for i in self._nodes.items():
                node = i[1]

                ssh = SSH()
                ssh.connect(node)

                cmd = "sudo reboot -n"
                (ret, stdout, stderr) = ssh.exec_command(cmd)
                if ret != 0:
                    raise RuntimeError('Executing update-grub failed to node {}'.format(node['hostname']))

    '''
    apply_postboot:

    Apply the config that is needed after rebooting.
    '''

    def apply_postboot(self):

        # Discover the system config
        self.discover()

        # Apply the Huge pages
        self.apply_hugepages()

        # Apply the vpp startup, vpp will be restarted
        self.apply_vpp_startup(apply_cpu=True)

    '''
    devices_update:

    Update the auto config with the information from the devices already set.
    '''

    def devices_update(self, node, vpp, devices_to_be_used):
        print("Devices Update")

        devices_to_rebind = devices_to_be_used + vpp.get_other_devices()
        vpp.rebind_vpp_devices(node, devices_to_rebind)

        vpp = VppPCIUtil(node)
        kernel_devices = vpp.get_kernel_devices()

        for d in kernel_devices:
            d2 = filter(lambda x: x['id'] == d['id'], kernel_devices)[0]
            print d2

        print kernel_devices

    '''
    devices_interactive:

    Configure the PCI devices interactively.
    '''

    def devices_interactive(self):

        for i in self._nodes.items():
            node = i[1]

            print "\nWe are configuring the node \"{}\":\n".format(node['host'])
            vpp = VppPCIUtil(node)
            devices_currently_being_used = vpp.get_dpdk_devices()
            devices_to_be_used = None

            if len(devices_currently_being_used) > 0:
                print("These devices are being used by the FDIO:\n")
                vpp.show_vpp_devices(devices_currently_being_used)

                a = self._ask_user_yn("Do you want to use these devices ")
                if a == 'y':
                    devices_to_be_used = devices_currently_being_used

            # Reset the devices
            devices_to_rebind = devices_currently_being_used + vpp.get_other_devices()
            vpp.rebind_vpp_devices(node, devices_to_rebind)

            # Get the new device list
            vpp = VppPCIUtil(node)
            kernel_devices = vpp.get_kernel_devices()

            if devices_to_be_used is None:
                print("These devices are available:\n")
                vpp.show_vpp_devices(kernel_devices)

            devices = self._get_new_vpp_device_list(self, kernel_devices, devices_to_be_used)
            node['devices'] = devices

        self._update_auto_config()

    '''
    huge_pages:

    Configure the Huge pages.
    '''

    def huge_pages(self):

        for i in self._nodes.items():
            node = i[1]
            vpp = VppHugePageUtil(node)

            # Get the configured number of huge pages
            if ('hugepages' in node) and ('total' in node['hugepages']):
                print("Our current Huge Page Configuration is as follows:")
                vpp.show_huge_pages()
                print("\nWe are going to config a total of {} Huge Pages".format(node['hugepages']['total']))
                a = self._ask_user_yn("Is this OK ")
                if a != 'y':
                    print(
                        "\nAdd the total number of hugepages you want in the file {}".format(self._autoconfig_filename))
                    print("Use the something like:\n    hugepages:\n      total: 4096\n")
                    return
            else:
                print("\nAdd the total number of hugepages you want in the file {}".format(self._autoconfig_filename))
                print("Use the something like:\n    hugepages:\n      total: 4096\n")
                return

    '''
    patch_qemu:

    Patch qemu with the cotrrect patches.
    '''

    def patch_qemu(self):

        for i in self._nodes.items():
            node = i[1]

            logging.debug("\nWe are patching the node \"{}\":\n".format(node['host']))

            qu = QemuUtils()
            qu.build_qemu(node, force_install=True, apply_patch=True)

    '''
    system information functions

    '''

    @staticmethod
    def cpu_info(node):

        cpu = CpuUtils.get_cpu_info_per_node(node)

        item = 'Model name'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'CPU(s)'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'Thread(s) per core'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'Core(s) per socket'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'Socket(s)'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'NUMA node(s)'
        numa_nodes = 0
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
            numa_nodes = int(cpu[item])
        for i in xrange(0, numa_nodes):
            item = "NUMA node{} CPU(s)".format(i)
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'CPU max MHz'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))
        item = 'CPU min MHz'
        if item in cpu:
            print("{:>20}:    {}".format(item, cpu[item]))

        if cpu['smt_enabled']:
            smt = 'Enabled'
        else:
            smt = 'Disabled'
        print("{:>20}:    {}".format('SMT', smt))

        # VPP Processes
        print("\nVPP Processes: (Process Name: Cpu Number)")
        vpp_processes = cpu['vpp_processes']
        for i in vpp_processes.items():
            print("  {:10}: {:4}".format(i[0], i[1]))

    @staticmethod
    def device_info(node):

        vpp = VppPCIUtil(node)

        devices_used = vpp.get_dpdk_devices()
        devices_not_used = vpp.get_kernel_devices()
        devices_not_used += vpp.get_other_devices()

        print("These devices are currently being used by the FDIO:\n")
        vpp.show_vpp_devices(devices_used)

    @staticmethod
    def hugepage_info(node):

        vpp = VppHugePageUtil(node)
        if ('hugepages' in node) and ('total' in node['hugepages']):
            vpp.show_huge_pages()

    def sys_info(self):

        for i in self._nodes.items():
            print("\n==============================")
            name = i[0]
            node = i[1]

            print("NODE: {}\n".format(name))

            # CPU
            print("CPU:")
            self.cpu_info(node)

            # Grub
            # print("\nGrub Command Line:")
            # if 'grub' in node:
                # print("     Current: {}".format(node['grub']['original_cmdline']))
                # print("  Configured: {}".format(node['grub']['vpp_cmdline']))

            # Huge Pages
            print("\nHuge Pages:")
            self.hugepage_info(node)

            # Devices
            print("\nDevices:")
            self.device_info(node)
            print("\n==============================")

    def vpp_test(self):

        for i in self._nodes.items():
            print("\n==============================")
            name = i[0]
            node = i[1]

            print("NODE: {}\n".format(name))

            vh = VhostUser()

            vh.vpp_create_vhost_user_interface(node, '/tmp/vpp_test_sock1')
