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
import re

from resources.libraries.python.VppPCIUtil import VppPCIUtil
from resources.libraries.python.VppHugePageUtil import VppHugePageUtil
from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.VppGrubUtil import VppGrubUtil
from resources.libraries.python.VPPUtil import VPPUtil
from resources.libraries.python.QemuUtils import QemuUtils
from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import Topology

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
        """
        Returns the nodes dictionary.

        :returns: The nodes
        :rtype: dictionary
        """

        return self._nodes

    @staticmethod
    def _autoconfig_backup_file(ssh, filename):
        """
        Create a backup file.

        :param ssh: ssh class
        :param filename: The file to backup
        """

        # Does a copy of the file exist, if not create one
        ofile = filename + '.orig'
        (ret, stdout, stderr) = ssh.exec_command('ls {}'.format(ofile))
        if ret != 0:
            logging.debug(stderr)
            if stdout.strip('\n') != ofile:
                cmd = 'sudo cp {} {}'.format(filename, ofile)
                (ret, stdout, stderr) = ssh.exec_command(cmd)
                if ret != 0:
                    logging.debug(stderr)

    @staticmethod
    def _ask_user_range(question, first, last, default):
        """
        Asks the user for a number within a range.
        default is returned if return is entered.

        :param question: Text of a question.
        :param first: First number in the range
        :param last: Last number in the range
        :param default: The value returned when return is entered
        :type question: string
        :type first: int
        :type last: int
        :type default: int
        :returns: The answer to the question
        :rtype: int
        """

        while True:
            answer = raw_input(question)
            if len(answer) == 0:
                answer = default
                break
            if re.findall(r'[0-9+]', answer):
                if int(answer) in range(first, last + 1):
                    break
                else:
                    print "Please a value between {} and {} or Return.". \
                        format(first, last)
            else:
                print "Please a number between {} and {} or Return.". \
                    format(first, last)

        return int(answer)

    @staticmethod
    def _ask_user_yn(question, default):
        """
        Asks the user for a yes or no question.

        :param question: Text of a question.
        :param default: The value returned when return is entered
        :type question: string
        :type default: string
        :returns: The answer to the question
        :rtype: string
        """

        input_valid = False
        default = default.lower()
        answer = ''
        while not input_valid:
            answer = raw_input(question)
            if len(answer) == 0:
                answer = default
            if re.findall(r'[YyNn]', answer):
                input_valid = True
                answer = answer[0].lower()
            else:
                print "Please answer Y, N or Return."

        return answer

    def _loadconfig(self):
        """
        Load the testbed configuration, given the auto configuration file.

        """

        # Get the Topology, from the topology layout file
        with open(self._autoconfig_filename, 'r') as stream:
            try:
                topo = yaml.load(stream)
                if 'metadata' in topo:
                    self._metadata = topo['metadata']
                if 'nodes' in topo:
                    self._nodes = topo['nodes']
            except yaml.YAMLError as exc:
                print exc

    def _updateconfig(self):
        """
        Update the testbed configuration, given the auto configuration file.
        We will write the system configuration file with the current node
        information

        """

        # Initialize the yaml data
        ydata = {'metadata': self._metadata, 'nodes': self._nodes}

        # Write the system config file
        if 'system_config_file' in self._metadata:
            filename = self._metadata['system_config_file']
        else:
            filename = DEFAULT_SYSTEM_CONFIG_FILENAME
        with open(filename, 'w') as yamlfile:
            yaml.dump(ydata, yamlfile, default_flow_style=False)

    def _update_auto_config(self):
        """
        Write the auto configuration file with the new configuration data,
        input from the user.

        """

        # Initialize the yaml data
        nodes = {}
        with open(self._autoconfig_filename, 'r') as stream:
            try:
                ydata = yaml.load(stream)
                if 'nodes' in ydata:
                    nodes = ydata['nodes']
            except yaml.YAMLError as exc:
                print exc
                return

        for i in nodes.items():
            key = i[0]
            node = i[1]

            # Interfaces
            node['interfaces'] = {}
            for item in self._nodes[key]['interfaces'].items():
                port = item[0]
                interface = item[1]

                node['interfaces'][port] = {}
                node['interfaces'][port]['pci_address'] = \
                    interface['pci_address']
                if 'mac_address' in interface:
                    node['interfaces'][port]['mac_address'] = \
                        interface['mac_address']

            if 'total_other_cpus' in self._nodes[key]['cpu']:
                node['cpu']['total_other_cpus'] = \
                    self._nodes[key]['cpu']['total_other_cpus']
            if 'total_vpp_cpus' in self._nodes[key]['cpu']:
                node['cpu']['total_vpp_cpus'] = \
                    self._nodes[key]['cpu']['total_vpp_cpus']
            if 'reserve_vpp_main_core' in self._nodes[key]['cpu']:
                node['cpu']['reserve_vpp_main_core'] = \
                    self._nodes[key]['cpu']['reserve_vpp_main_core']
            if 'total_buffers_per_queue' in self._nodes[key]['cpu']:
                node['cpu']['total_buffers_per_queue'] = \
                    self._nodes[key]['cpu']['total_buffers_per_queue']

            # Huge pages
            node['hugepages']['total'] = self._nodes[key]['hugepages']['total']

        # Write the auto config config file
        with open(self._autoconfig_filename, 'w') as yamlfile:
            yaml.dump(ydata, yamlfile, default_flow_style=False)

    def apply_huge_pages(self):
        """
        Apply the huge page config

        """

        for i in self._nodes.items():
            node = i[1]

            hpg = VppHugePageUtil(node)
            hpg.hugepages_dryrun_apply()

    @staticmethod
    def _apply_vpp_unix(node):
        """
        Apply the VPP Unix config

        :param node: Node dictionary with cpuinfo.
        :type node: dict
        """

        unix = '  nodaemon\n'
        if 'unix' not in node['vpp']:
            return ''

        unixv = node['vpp']['unix']
        if 'interactive' in unixv:
            interactive = unixv['interactive']
            if interactive is True:
                unix = '  interactive\n'

        return unix.rstrip('\n')

    @staticmethod
    def _apply_vpp_cpu(node):
        """
        Apply the VPP cpu config

        :param node: Node dictionary with cpuinfo.
        :type node: dict
        """

        # Get main core
        cpu = '\n'
        vpp_main_core = node['cpu']['vpp_main_core']
        if vpp_main_core is not 0:
            cpu += '  main-core {}\n'.format(vpp_main_core)

        # Get workers
        vpp_workers = node['cpu']['vpp_workers']
        if len(vpp_workers) > 0:
            vpp_worker_str = ''
            for i, worker in enumerate(vpp_workers):
                if i > 0:
                    vpp_worker_str += ','
                if worker[0] == worker[1]:
                    vpp_worker_str += "{}".format(worker[0])
                else:
                    vpp_worker_str += "{}-{}".format(worker[0], worker[1])

            cpu += '  corelist-workers {}\n'.format(vpp_worker_str)

        return cpu

    @staticmethod
    def _apply_vpp_devices(node):
        """
        Apply VPP PCI Device configuration to vpp startup.

        :param node: Node dictionary with cpuinfo.
        :type node: dict
        """

        devices = ''
        ports_per_numa = node['cpu']['ports_per_numa']
        total_mbufs = node['cpu']['total_mbufs']

        for item in ports_per_numa.items():
            value = item[1]
            interfaces = value['interfaces']

            # if 0 was specified for the number of vpp workers, use 1 queue
            num_rx_queues = None
            num_tx_queues = None
            if 'rx_queues' in value:
                num_rx_queues = value['rx_queues']
            if 'tx_queues' in value:
                num_tx_queues = value['tx_queues']

            num_rx_desc = None
            num_tx_desc = None
            if 'rx_desc_entries' in value:
                num_rx_desc = value['rx_desc_entries']
            if 'tx_desc_entries' in value:
                num_tx_desc = value['tx_desc_entries']

            # Create the devices string
            for interface in interfaces:
                pci_address = interface['pci_address']
                pci_address = pci_address.lstrip("'").rstrip("'")
                devices += '\n'
                devices += '  dev {} {{ \n'.format(pci_address)
                if num_rx_queues:
                    devices += '    num-rx-queues {}\n'.format(num_rx_queues)
                else:
                    devices += '    num-rx-queues {}\n'.format(1)
                if num_tx_queues:
                    devices += '    num-tx-queues {}\n'.format(num_tx_queues)
                if num_rx_desc:
                    devices += '    num-rx-desc {}\n'.format(num_rx_desc)
                if num_tx_desc:
                    devices += '    num-tx-desc {}\n'.format(num_tx_desc)
                devices += '  }'

        if total_mbufs is not 0:
            devices += '\n  num-mbufs {}'.format(total_mbufs)

        return devices

    @staticmethod
    def _calc_vpp_workers(node, vpp_workers, numa_node,
                          other_cpus_end, total_vpp_workers,
                          reserve_vpp_main_core):
        """
        Calculate the VPP worker information

        :param node: Node dictionary
        :param vpp_workers: List of VPP workers
        :param numa_node: Numa node
        :param other_cpus_end: The end of the cpus allocated for cores
        other than vpp
        :param total_vpp_workers: The number of vpp workers needed
        :param reserve_vpp_main_core: Is there a core needed for
        the vpp main core
        :type node: dict
        :type numa_node: int
        :type other_cpus_end: int
        :type total_vpp_workers: int
        :type reserve_vpp_main_core: bool
        :returns: Is a core still needed for the vpp main core
        :rtype: bool
        """

        # Can we fit the workers in one of these slices
        cpus = node['cpu']['cpus_per_node'][numa_node]
        for cpu in cpus:
            start = cpu[0]
            end = cpu[1]
            if start <= other_cpus_end:
                start = other_cpus_end + 1

            if reserve_vpp_main_core:
                start += 1

            workers_end = start + total_vpp_workers - 1
            if workers_end <= end:
                if reserve_vpp_main_core:
                    node['cpu']['vpp_main_core'] = start - 1
                reserve_vpp_main_core = False
                if total_vpp_workers:
                    vpp_workers.append((start, workers_end))
                break

        # We still need to reserve the main core
        if reserve_vpp_main_core:
            node['cpu']['vpp_main_core'] = other_cpus_end + 1

        return reserve_vpp_main_core

    @staticmethod
    def _calc_desc_and_queues(node, total_ports,
                              total_ports_per_numa,
                              total_vpp_cpus,
                              ports_per_numa_value):
        """
        Calculate the number of descriptors and queues

        :param node: Node dictionary
        :param total_ports: The total number of ports to be used by vpp
        :param total_ports_per_numa: The total number of ports for this
        numa node
        :param total_vpp_cpus: The total number of cpus to allocate for vpp
        :param ports_per_numa_value: The value from the ports_per_numa
        dictionary
        :type node: dict
        :type total_ports: int
        :type total_ports_per_numa: int
        :type total_vpp_cpus: int
        :type ports_per_numa_value: dict
        :returns The total number of message buffers
        :returns: The total number of vpp workers
        :rtype: int
        :rtype: int
        """

        total_vpp_workers = int(float(total_vpp_cpus) *
                                (float(total_ports_per_numa) /
                                 float(total_ports)))
        ports_per_numa_value['total_vpp_workers'] = total_vpp_workers

        # Get the descriptor entries
        desc_entries = max(1, total_vpp_workers) * \
            node['cpu']['total_buffers_per_queue'] * \
            total_ports
        ports_per_numa_value['rx_desc_entries'] = desc_entries
        ports_per_numa_value['tx_desc_entries'] = desc_entries
        total_mbufs = desc_entries * 2
        ports_per_numa_value['rx_queues'] = max(1, total_vpp_workers / 2)
        ports_per_numa_value['tx_queues'] = max(1, total_vpp_workers / 2)

        return total_mbufs, total_vpp_workers

    @staticmethod
    def _create_ports_per_numa(node, interfaces):
        """
        Create a dictionary or ports per numa node
        :param node: Node dictionary
        :param interfaces: All the interfaces to be used by vpp
        :type node: dict
        :type interfaces: dict
        :returns: The ports per numa dictionary
        :rtype: dict
        """

        # Make a list of ports by numa node
        ports_per_numa = {}
        for item in interfaces.items():
            i = item[1]
            if i['numa_node'] not in ports_per_numa:
                ports_per_numa[i['numa_node']] = {'interfaces': []}
                ports_per_numa[i['numa_node']]['interfaces'].append(i)
            else:
                ports_per_numa[i['numa_node']]['interfaces'].append(i)
        node['cpu']['ports_per_numa'] = ports_per_numa

        return ports_per_numa

    def calculate_cpu_parameters(self):
        """
        Calculate the cpu configuration.

        """

        # Calculate the cpu parameters, needed for the
        # vpp_startup and grub configuration
        for i in self._nodes.items():
            node = i[1]

            # get total number of nic ports
            interfaces = node['interfaces']

            # Make a list of ports by numa node
            ports_per_numa = self._create_ports_per_numa(node, interfaces)

            # Get the number of cpus to skip, we never use the first cpu
            other_cpus_start = 1
            other_cpus_end = other_cpus_start + \
                node['cpu']['total_other_cpus'] - 1
            other_workers = None
            if other_cpus_end is not 0:
                other_workers = (other_cpus_start, other_cpus_end)
            node['cpu']['other_workers'] = other_workers

            # Allocate the VPP main core and workers
            vpp_workers = []
            reserve_vpp_main_core = node['cpu']['reserve_vpp_main_core']
            total_vpp_cpus = node['cpu']['total_vpp_cpus']

            # If total_vpp_cpus is 0 or is less than the numa nodes with ports
            #  then we shouldn't get workers
            total_with_main = total_vpp_cpus
            if reserve_vpp_main_core:
                total_with_main += 1
            total_mbufs = 0
            if total_with_main is not 0:
                for item in ports_per_numa.items():
                    numa_node = item[0]
                    value = item[1]

                    # Get the number of descriptors and queues
                    mbufs, total_vpp_workers = self._calc_desc_and_queues(
                        node, len(interfaces), len(value['interfaces']),
                        total_vpp_cpus, value)
                    total_mbufs += mbufs

                    # Get the VPP workers
                    reserve_vpp_main_core = self._calc_vpp_workers(
                        node, vpp_workers, numa_node, other_cpus_end,
                        total_vpp_workers, reserve_vpp_main_core)

            # Save the info
            node['cpu']['vpp_workers'] = vpp_workers
            node['cpu']['total_mbufs'] = total_mbufs

        # Write the config
        self._updateconfig()

    def apply_vpp_startup(self):
        """
        Apply the vpp startup configration
        Returns the diffs of 2 files.

        """

        # Apply the VPP startup configruation
        for i in self._nodes.items():
            node = i[1]

            ssh = SSH()
            ssh.connect(node)

            # Get the startup file
            sfile = node['vpp']['startup_config_file']

            # Get the devices
            devices = self._apply_vpp_devices(node)

            # Get the CPU config
            cpu = self._apply_vpp_cpu(node)

            # Get the unix config
            unix = self._apply_vpp_unix(node)

            # Make a backup if needed
            self._autoconfig_backup_file(ssh, sfile)

            # Get the template
            tfile = sfile + '.template'
            (ret, stdout, stderr) = \
                ssh.exec_command('cat {}'.format(tfile))
            if ret != 0:
                raise RuntimeError('Executing cat command failed to node {}'.
                                   format(node['host']))
            startup = stdout.format(unix=unix,
                                    cpu=cpu,
                                    devices=devices)

            (ret, stdout, stderr) = \
                ssh.exec_command('rm {}'.format(sfile))
            if ret != 0:
                logging.debug(stderr)

            cmd = "sudo cat > {0} << EOF\n{1}\n".format(sfile, startup)
            (ret, stdout, stderr) = ssh.exec_command(cmd)
            if ret != 0:
                raise RuntimeError('Writing config failed node {}'.
                                   format(node['host']))

    def apply_grub_cmdline(self):
        """
        Apply the grub cmdline

        """

        for i in self._nodes.items():
            node = i[1]

            # Get the isolated CPUs
            other_workers = node['cpu']['other_workers']
            vpp_workers = node['cpu']['vpp_workers']
            vpp_main_core = node['cpu']['vpp_main_core']
            all_workers = []
            if other_workers is not None:
                all_workers = [other_workers]
            if vpp_main_core is not 0:
                all_workers += [(vpp_main_core, vpp_main_core)]
            all_workers += vpp_workers
            isolated_cpus = ''
            for idx, worker in enumerate(all_workers):
                if worker is None:
                    continue
                if idx > 0:
                    isolated_cpus += ','
                if worker[0] == worker[1]:
                    isolated_cpus += "{}".format(worker[0])
                else:
                    isolated_cpus += "{}-{}".format(worker[0], worker[1])

            vppgrb = VppGrubUtil(node)
            current_cmdline = vppgrb.get_current_cmdline()
            if 'grub' not in node:
                node['grub'] = {}
            node['grub']['current_cmdline'] = current_cmdline
            node['grub']['default_cmdline'] =\
                vppgrb.apply_cmdline(node, isolated_cpus)

        self._updateconfig()

    def get_hugepages(self):
        """
        Get the hugepage configuration

        """

        for i in self._nodes.items():
            node = i[1]

            hpg = VppHugePageUtil(node)
            max_map_count, shmmax = hpg.get_huge_page_config()
            node['hugepages']['max_map_count'] = max_map_count
            node['hugepages']['shmax'] = shmmax
            total, free, size = hpg.get_actual_huge_pages()
            node['hugepages']['actual_total'] = total
            node['hugepages']['free'] = free
            node['hugepages']['size'] = size

        self._updateconfig()

    def get_grub(self):
        """
        Get the grub configuration

        """

        for i in self._nodes.items():
            node = i[1]

            vppgrb = VppGrubUtil(node)
            current_cmdline = vppgrb.get_current_cmdline()
            default_cmdline = vppgrb.get_default_cmdline()

            # Get the total number of isolated CPUs
            current_iso_cpus = 0
            iso_cpur = re.findall(r'isolcpus=[\w+\-,]+', current_cmdline)
            if len(iso_cpur):
                iso_cpu_str = iso_cpur[0]
                iso_cpu_str = iso_cpu_str.split('=')[1]
                iso_cpul = iso_cpu_str.split(',')
                for iso_cpu in iso_cpul:
                    isocpuspl = iso_cpu.split('-')
                    if len(isocpuspl) is 1:
                        current_iso_cpus += 1
                    else:
                        first = int(isocpuspl[0])
                        second = int(isocpuspl[1])
                        if first == second:
                            current_iso_cpus += 1
                        else:
                            current_iso_cpus += second - first

            if 'grub' not in node:
                node['grub'] = {}
            node['grub']['current_cmdline'] = current_cmdline
            node['grub']['default_cmdline'] = default_cmdline
            node['grub']['current_iso_cpus'] = current_iso_cpus

        self._updateconfig()

    def get_device(self):
        """
        Get the device configuration

        """

        for i in self._nodes.items():
            node = i[1]
            # Update the interface data

            vpp = VppPCIUtil(node)
            vpp.get_all_devices()

            # Save the device information
            node['devices'] = {}
            node['devices']['dpdk_devices'] = vpp.get_dpdk_devices()
            node['devices']['kernel_devices'] = vpp.get_kernel_devices()
            node['devices']['other_devices'] = vpp.get_other_devices()
            node['devices']['linkup_devices'] = vpp.get_link_up_devices()

        self._updateconfig()

    @staticmethod
    def get_cpu_layout(node):
        """
        Get the cpu layout

        using lscpu -p get the cpu layout.
        Returns a list with each item representing a single cpu.

        :param node: Node dictionary.
        :type node: dict
        :returns: The cpu layout
        :rtype: list
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = 'lscpu -p'
        (ret, stdout, stderr) = ssh.exec_command(cmd)
        if ret != 0:
            raise RuntimeError('{} failed on node {} {}'.
                               format(cmd, node['host'], stderr))

        pcpus = []
        lines = stdout.split('\n')
        for line in lines:
            if len(line) == 0 or line[0] == '#':
                continue
            linesplit = line.split(',')
            layout = {'cpu': linesplit[0], 'core': linesplit[1],
                      'socket': linesplit[2], 'node': linesplit[3]}

            # cpu, core, socket, node
            pcpus.append(layout)

        return pcpus

    def get_cpu(self):
        """
        Get the cpu configuration

        """

        # Get the CPU layout
        CpuUtils.get_cpu_layout_from_all_nodes(self._nodes)

        for i in self._nodes.items():
            node = i[1]

            # Get the cpu layout
            layout = self.get_cpu_layout(node)
            node['cpu']['layout'] = layout

            cpuinfo = node['cpuinfo']
            smt_enabled = CpuUtils.is_smt_enabled(cpuinfo)
            node['cpu']['smt_enabled'] = smt_enabled

            # We don't want to write the cpuinfo
            node['cpuinfo'] = ""

        # Write the config
        self._updateconfig()

    def discover(self):
        """
        Get the current system configuration.

        """

        # Get the Huge Page configuration
        self.get_hugepages()

        # Get the device configuration
        self.get_device()

        # Get the CPU configuration
        self.get_cpu()

        # Get the current grub cmdline
        self.get_grub()

    def _modify_cpu_questions(self, node, total_cpus, numa_nodes):
        """
        Ask the user questions related to the cpu configuration.

        :param node: Node dictionary
        :param total_cpus: The total number of cpus in the system
        :param interfaces: The list of numa nodes in the system
        :type node: dict
        :type total_cpus: int
        :type numa_nodes: list
        """

        interfaces = node['interfaces']
        total_nic_ports = len(interfaces)

        print "\nYour system has {} CPUs and {} Numa Nodes.". \
            format(total_cpus, len(numa_nodes))
        print "You want to use {} ports.".format(total_nic_ports)
        print "\nYou can devote between 0 and {} cpu cores to VPP" \
              "and other processes.".format(total_cpus - 1)
        print "To begin, we suggest not devoting any CPUs, then \
        reconfigure as needed."

        question = '\nHow many CPUs do you want to reserve for processes \
other than VPP? [0-{}][0]? '.format(str(total_cpus - 1))
        total_other_cpus = self._ask_user_range(question, 0,
                                                total_cpus - 1, 0)
        node['cpu']['total_other_cpus'] = total_other_cpus

        max_vpp_cpus = total_cpus - total_other_cpus - 1
        total_vpp_cpus = 0
        if max_vpp_cpus > 0:
            question = "How many CPU(s) shall we use with VPP [0-{}][0]? ". \
                format(max_vpp_cpus)
            total_vpp_cpus = self._ask_user_range(question, 0, max_vpp_cpus, 0)
            node['cpu']['total_vpp_cpus'] = total_vpp_cpus

        max_main_cpus = max_vpp_cpus - total_vpp_cpus
        reserve_vpp_main_core = False
        if max_main_cpus > 0:
            question = "Should we reserve 1 cpu for the VPP Main thread? "
            question += "[y/N]? "
            answer = self._ask_user_yn(question, 'n')
            if answer == 'y':
                reserve_vpp_main_core = True
            node['cpu']['reserve_vpp_main_core'] = reserve_vpp_main_core
            node['cpu']['vpp_main_core'] = 0

        question = "How many rx/tx buffers per queue do you want? "
        question += "[512-8192][512]? "
        total_buffers_per_queue = self._ask_user_range(question, 512, 8192, 512)
        node['cpu']['total_buffers_per_queue'] = total_buffers_per_queue

    def modify_cpu(self):
        """
        Modify the cpu configuration, asking for the user for the values.

        """

        # Get the CPU layout
        CpuUtils.get_cpu_layout_from_all_nodes(self._nodes)

        for i in self._nodes.items():
            node = i[1]
            total_cpus = 0
            total_cpus_per_slice = 0
            cpus_per_node = {}
            numa_nodes = []
            cores = []
            cpu_layout = self.get_cpu_layout(node)

            # Assume the number of cpus per slice is always the same as the
            # first slice
            first_node = '0'
            for cpu in cpu_layout:
                if cpu['node'] != first_node:
                    break
                total_cpus_per_slice += 1

            # Get the total number of cpus, cores, and numa nodes from the
            # cpu layout
            for cpul in cpu_layout:
                numa_node = cpul['node']
                core = cpul['core']
                cpu = cpul['cpu']
                total_cpus += 1

                if numa_node not in cpus_per_node:
                    cpus_per_node[numa_node] = []
                cpuperslice = int(cpu) % total_cpus_per_slice
                if cpuperslice == 0:
                    cpus_per_node[numa_node].append((int(cpu), int(cpu) +
                                                     total_cpus_per_slice - 1))
                if numa_node not in numa_nodes:
                    numa_nodes.append(numa_node)
                if core not in cores:
                    cores.append(core)
            node['cpu']['cpus_per_node'] = cpus_per_node

            # Ask the user some questions
            self._modify_cpu_questions(node, total_cpus, numa_nodes)

            # Populate the interfaces with the numa node
            ikeys = node['interfaces'].keys()
            Topology.get_interfaces_numa_node(node, *tuple(ikeys))

            # We don't want to write the cpuinfo
            node['cpuinfo'] = ""

        # Write the configs
        self._update_auto_config()
        self._updateconfig()

    def _modify_other_devices(self, node,
                              other_devices, kernel_devices, dpdk_devices):
        """
        Modify the devices configuration, asking for the user for the values.

        """

        if len(other_devices) > 0:
            print "\nThese device(s) are currently NOT being used",
            print "by VPP or the OS.\n"
            VppPCIUtil.show_vpp_devices(other_devices)
            question = "\nWould you like to give any of these devices"
            question += "back to the OS [y/N]? "
            answer = self._ask_user_yn(question, 'N')
            if answer == 'y':
                vppd = {}
                for dit in other_devices.items():
                    dvid = dit[0]
                    device = dit[1]
                    question = "Would you like to use device {} for".\
                        format(dvid)
                    question += " the OS [y/N]? "
                    answer = self._ask_user_yn(question, 'n')
                    if answer == 'y':
                        driver = device['unused'].split(',')[0]
                        VppPCIUtil.bind_vpp_device(node, driver, dvid)
                        vppd[dvid] = device
                for dit in vppd.items():
                    dvid = dit[0]
                    device = dit[1]
                    kernel_devices[dvid] = device
                    del other_devices[dvid]

        if len(other_devices) > 0:
            print "\nThese device(s) are still NOT being used ",
            print "by VPP or the OS.\n"
            VppPCIUtil.show_vpp_devices(other_devices)
            question = "\nWould you like use any of these for VPP [y/N]? "
            answer = self._ask_user_yn(question, 'N')
            if answer == 'y':
                vppd = {}
                for dit in other_devices.items():
                    dvid = dit[0]
                    device = dit[1]
                    question = "Would you like to use device {} ".format(dvid)
                    question += "for VPP [y/N]? "
                    answer = self._ask_user_yn(question, 'n')
                    if answer == 'y':
                        vppd[dvid] = device
                for dit in vppd.items():
                    dvid = dit[0]
                    device = dit[1]
                    dpdk_devices[dvid] = device
                    del other_devices[dvid]

    def modify_devices(self):
        """
        Modify the devices configuration, asking for the user for the values.

        """

        for i in self._nodes.items():
            node = i[1]
            devices = node['devices']
            other_devices = devices['other_devices']
            kernel_devices = devices['kernel_devices']
            dpdk_devices = devices['dpdk_devices']

            self._modify_other_devices(node, other_devices,
                                       kernel_devices, dpdk_devices)

            if len(kernel_devices) > 0:
                print "\nThese devices have kernel interfaces, but appear\
 to be safe to use with VPP.\n"
                VppPCIUtil.show_vpp_devices(kernel_devices)
                question = \
                    "\nWould you like to use any of these device(s) for \
VPP [y/N]? "
                answer = self._ask_user_yn(question, 'n')
                if answer == 'y':
                    vppd = {}
                    for dit in kernel_devices.items():
                        dvid = dit[0]
                        device = dit[1]
                        question = "Would you like to use device {} \
for VPP [y/N]? ".format(dvid)
                        answer = self._ask_user_yn(question, 'n')
                        if answer == 'y':
                            vppd[dvid] = device
                    for dit in vppd.items():
                        dvid = dit[0]
                        device = dit[1]
                        dpdk_devices[dvid] = device
                        del kernel_devices[dvid]

            if len(dpdk_devices) > 0:
                print "\nThese device(s) will be used by VPP.\n"
                VppPCIUtil.show_vpp_devices(dpdk_devices)
                question = "\nWould you like to remove any of "
                question += "these device(s) [y/N]? "
                answer = self._ask_user_yn(question, 'n')
                if answer == 'y':
                    vppd = {}
                    for dit in dpdk_devices.items():
                        dvid = dit[0]
                        device = dit[1]
                        question = "Would you like to remove {} [y/N]? ". \
                            format(dvid)
                        answer = self._ask_user_yn(question, 'n')
                        if answer == 'y':
                            vppd[dvid] = device
                    for dit in vppd.items():
                        dvid = dit[0]
                        device = dit[1]
                        kernel_devices[dvid] = device
                        del dpdk_devices[dvid]

            interfaces = {}
            for dit in dpdk_devices.items():
                dvid = dit[0]
                device = dit[1]
                VppPCIUtil.vpp_create_interface(interfaces, dvid, device)
            node['interfaces'] = interfaces

            print "\nThese device(s) will be used by VPP, please rerun\
 this option if this is incorrect.\n"
            VppPCIUtil.show_vpp_devices(dpdk_devices)

        self._update_auto_config()
        self._updateconfig()

    def modify_huge_pages(self):
        """
        Modify the huge page configuration, asking for the user for the values.

        """

        for i in self._nodes.items():
            node = i[1]

            total = node['hugepages']['actual_total']
            free = node['hugepages']['free']
            size = node['hugepages']['size']
            print "\nThere currently {} {} huge pages free.". \
                format(free, size)
            answer = self._ask_user_yn("Do you want to reconfigure the \
number of huge pages [y/N]? ", 'N')
            if answer == 'n':
                continue

            print "\nThere currently a total of {} huge pages.". \
                format(total)
            question = \
                "How many huge pages do you want [1024 - 65536][1024]? "
            answer = self._ask_user_range(question, 1024, 65536, 1024)
            node['hugepages']['total'] = str(answer)

        # Update auto-config.yaml
        self._update_auto_config()

        # Rediscover just the hugepages
        self.get_hugepages()

    def patch_qemu(self):
        """
        Patch qemu with the correct patches.

        """

        for i in self._nodes.items():
            node = i[1]

            print '\nWe are patching the node "{}":\n'.format(node['host'])

            qmu = QemuUtils()
            qmu.build_qemu(node, force_install=False, apply_patch=True)

    @staticmethod
    def cpu_info(node):
        """
        print the CPU information

        """

        cpu = CpuUtils.get_cpu_info_per_node(node)

        item = 'Model name'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'CPU(s)'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'Thread(s) per core'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'Core(s) per socket'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'Socket(s)'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'NUMA node(s)'
        numa_nodes = 0
        if item in cpu:
            numa_nodes = int(cpu[item])
        for i in xrange(0, numa_nodes):
            item = "NUMA node{} CPU(s)".format(i)
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'CPU max MHz'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])
        item = 'CPU min MHz'
        if item in cpu:
            print "{:>20}:    {}".format(item, cpu[item])

        if node['cpu']['smt_enabled']:
            smt = 'Enabled'
        else:
            smt = 'Disabled'
        print "{:>20}:    {}".format('SMT', smt)

        # VPP Processes
        print "\nVPP Processes: (Process Name: Cpu Number)"
        vpp_processes = cpu['vpp_processes']
        for i in vpp_processes.items():
            print "  {:10}: {:4}".format(i[0], i[1])

    @staticmethod
    def device_info(node):
        """
        Show the device information.

        """

        # devices = node['devices']
        # VppPCIUtil.show_vpp_devices(devices['dpdk_devices'])
        interfaces = VPPUtil.get_hardware(node)
        if interfaces == {}:
            return

        print "{:30} {:6} {:4} {:7} {:4} {:7}".\
            format('Name', 'Socket', 'RXQs',
                   'RXDescs', 'TXQs', 'TXDescs')
        for intf in sorted(interfaces.items()):
            name = intf[0]
            value = intf[1]
            if name == 'local':
                continue
            socket = rx_qs = rx_ds = tx_qs = tx_ds = ''
            if 'cpu socket' in value:
                socket = value['cpu socket']
            if 'rx queues' in value:
                rx_qs = value['rx queues']
            if 'rx descs' in value:
                rx_ds = value['rx descs']
            if 'tx queues' in value:
                tx_qs = value['tx queues']
            if 'tx descs' in value:
                tx_ds = value['tx descs']
            print "{:30} {:>6} {:>4} {:>7} {:>4} {:>7}".format(
                name, socket, rx_qs, rx_ds, tx_qs, tx_ds)

    @staticmethod
    def hugepage_info(node):
        """
        Show the huge page information.

        """

        hpg = VppHugePageUtil(node)
        hpg.show_huge_pages()

    def sys_info(self):
        """
        Print the system information

        """

        for i in self._nodes.items():
            print "\n=============================="
            name = i[0]
            node = i[1]

            print "NODE: {}\n".format(name)

            # CPU
            print "CPU:"
            self.cpu_info(node)

            # Grub
            print "\nGrub Command Line:"
            if 'grub' in node:
                print \
                    "  Current: {}".format(
                        node['grub']['current_cmdline'])
                print \
                    "  Configured: {}".format(
                        node['grub']['default_cmdline'])

            # Huge Pages
            print "\nHuge Pages:"
            self.hugepage_info(node)

            # Devices
            print "\nDevices:"
            self.device_info(node)
            print "\n=============================="
