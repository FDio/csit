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
from resources.libraries.python.topology import Topology
from resources.libraries.python.VppConfigGenerator import VppConfigGenerator
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
    We will rewrite the auto configuration file and the current node information
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
    _get_new_vpp_devices:

    Given a list of pci devices, ask the user for new ones
    '''

    @staticmethod
    def _get_new_vpp_device_list(self, devices):

        vpp_devices = []
        vpp_devices_removed = []
        for d in devices:
            print("\nDo you want to use this device for FDIO:")
            if 'interface' in d:
                print("{}  {}  {}".format(d['id'], d['interface'], d['description']))
            else:
                print("{}  {}".format(d['id'], d['description']))
            a = self._ask_user_yn("")
            if a == 'y':
                vpp_devices.append(d)
            else:
                vpp_devices_removed.append(d)

        return vpp_devices, vpp_devices_removed

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

    def apply_vpp_startup(self):

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
            original_cmdline = vppgrb.get_actual_cmdline()
            grub_file = node['cpu']['grub_config_file']
            vpp_cmdline = vppgrb.apply_cmdline(grub_file)
            node['grub']['original_cmdline'] = original_cmdline
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
            original_cmdline = vppgrb.get_actual_cmdline()

            isolated_cpus = ''
            if 'list' in node['cpu']:
                isolated_cpus = node['cpu']['list']
            vpp_cmdline = vppgrb.create_cmdline(isolated_cpus)

            if 'grub' not in node:
                node['grub'] = {}
            node['grub']['original_cmdline'] = original_cmdline
            node['grub']['vpp_cmdline'] = vpp_cmdline

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

        # Apply the Huge pages
        self.apply_hugepages()

        # Apply the vpp startup, vpp will be restarted
        self.apply_vpp_startup()

    '''
    write_new_config:

    Write the new configuration data.
    '''

    def write_new_config(self):

        # Initialize the yaml data
        yl = {'metadata': self._metadata, 'nodes': self._nodes}

        for key in self._nodes.keys():

            new_devices = []
            for d in self._vpp_devices_node[key]:
                new_devices.append('{}'.format(d['id']))

            if 'vpp' not in yl['nodes'][key]:
                yl['nodes'][key]['vpp'] = {}
            if 'dpdk' not in yl['nodes'][key]['vpp']:
                yl['nodes'][key]['vpp']['dpdk'] = []
            yl['nodes'][key]['vpp']['dpdk']['devices'] = new_devices

            if 'vpp' not in self._nodes[key]:
                yl['nodes'][key]['vpp'] = {}
            if 'dpdk' not in self._nodes[key]['vpp']:
                yl['nodes'][key]['vpp']['dpdk'] = []
            self._nodes[key]['vpp']['dpdk']['devices'] = new_devices

        # Update the config file
        self._updateconfig()

    '''
    pci_devices:

    Conigure the PCI devices.
    '''

    def pci_devices(self):

        for i in self._nodes.items():
            key = i[0]
            node = i[1]

            print "\nWe are configuring the node \"{}\":\n".format(node['host'])
            vpp = VppPCIUtil(node)

            devices_used = vpp.get_dpdk_devices()
            devices_not_used = vpp.get_kernel_devices()
            devices_not_used += vpp.get_other_devices()
            devices_link_up = vpp.get_link_up_devices()
            a = ''
            while a != 'n':
                print("These devices are currently being used by the DPDK:\n")
                vpp.show_vpp_devices(devices_used)

                a = self._ask_user_yn("Do you want to change any device(s) currently being used by FDIO ")
                if a == 'y':
                    devices_used, devices_removed = self._get_new_vpp_device_list(self, devices_used)
                    devices_not_used += devices_removed

                print("\nThese device(s) are being used (link up) by the kernel and can NOT be used by FDIO:\n")
                vpp.show_vpp_devices(devices_link_up)

                print("\nThese device(s) are NOT currently being used by FDIO:\n")
                vpp.show_vpp_devices(devices_not_used)
                a = self._ask_user_yn("Do you want to use any of these devices for FDIO ")
                if a == 'y':
                    devices_to_be_used, devices_not_used = self._get_new_vpp_device_list(self, devices_not_used)
                    devices_used += devices_to_be_used

            if len(devices_used) > 0:
                print("\nThe Devices that VPP will use:\n")
                vpp.show_vpp_devices(devices_used)
            else:
                print("\nVPP is NOT configured to use any devices.")
            print("\n")

            # Save the new devices
            self._vpp_devices_node[key] = devices_used

    '''
    huge_pages:

    Configure the Huge pages.
    '''

    def huge_pages(self):

        for i in self._nodes.items():
            node = i[1]

            logging.info("\nWe are configuring the node \"{}\":\n".format(node['host']),
                         also_console=True)
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
