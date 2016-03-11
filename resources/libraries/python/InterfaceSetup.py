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

"""Interface setup library."""
from ssh import SSH
from robot.api import logger
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal


class InterfaceSetup(object):
    """Interface setup utilities."""

    __UDEV_IF_RULES_FILE = '/etc/udev/rules.d/10-network.rules'

    @staticmethod
    def tg_set_interface_driver(node, pci_addr, driver):
        """Set interface driver on the TG node.

        :param node: Node to set interface driver on (must be TG node).
        :param pci_addr: PCI address of the interface.
        :param driver: Driver name.
        :type node: dict
        :type pci_addr: str
        :type driver: str
        """
        old_driver = InterfaceSetup.tg_get_interface_driver(node, pci_addr)
        if old_driver == driver:
            return

        ssh = SSH()
        ssh.connect(node)

        # Unbind from current driver
        if old_driver is not None:
            cmd = 'sh -c "echo {0} > /sys/bus/pci/drivers/{1}/unbind"'.format(
                pci_addr, old_driver)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise Exception("'{0}' failed on '{1}'".format(cmd,
                                                               node['host']))

        # Bind to the new driver
        cmd = 'sh -c "echo {0} > /sys/bus/pci/drivers/{1}/bind"'.format(
            pci_addr, driver)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception("'{0}' failed on '{1}'".format(cmd, node['host']))

    @staticmethod
    def tg_get_interface_driver(node, pci_addr):
        """Get interface driver from the TG node.

        :param node: Node to get interface driver on (must be TG node).
        :param pci_addr: PCI address of the interface.
        :type node: dict
        :type pci_addr: str
        :return: Interface driver or None if not found.
        :rtype: str

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
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'lspci -vmmks {0}'.format(pci_addr)

        (ret_code, stdout, _) = ssh.exec_command(cmd)
        if int(ret_code) != 0:
            raise Exception("'{0}' failed on '{1}'".format(cmd, node['host']))

        for line in stdout.splitlines():
            if len(line) == 0:
                continue
            (name, value) = line.split("\t", 1)
            if name == 'Driver:':
                return value

        return None

    @staticmethod
    def tg_set_interfaces_udev_rules(node):
        """Set udev rules for interfaces.

        Create udev rules file in /etc/udev/rules.d where are rules for each
        interface used by TG node, based on MAC interface has specific name.
        So after unbind and bind again to kernel driver interface has same
        name as before. This must be called after TG has set name for each
        port in topology dictionary.
        udev rule example
        SUBSYSTEM=="net", ACTION=="add", ATTR{address}=="52:54:00:e1:8a:0f",
        NAME="eth1"

        :param node: Node to set udev rules on (must be TG node).
        :type node: dict
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = 'rm -f {0}'.format(InterfaceSetup.__UDEV_IF_RULES_FILE)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise Exception("'{0}' failed on '{1}'".format(cmd, node['host']))

        for if_k, if_v in node['interfaces'].items():
            if if_k == 'mgmt':
                continue
            rule = 'SUBSYSTEM==\\"net\\", ACTION==\\"add\\", ATTR{address}' + \
                '==\\"' + if_v['mac_address'] + '\\", NAME=\\"' + \
                if_v['name'] + '\\"'
            cmd = 'sh -c "echo \'{0}\' >> {1}"'.format(
                rule, InterfaceSetup.__UDEV_IF_RULES_FILE)
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise Exception("'{0}' failed on '{1}'".format(cmd,
                                                               node['host']))

        cmd = '/etc/init.d/udev restart'
        ssh.exec_command_sudo(cmd)

    @staticmethod
    def tg_set_interfaces_default_driver(node):
        """Set interfaces default driver specified in topology yaml file.

        :param node: Node to setup interfaces driver on (must be TG node).
        :type node: dict
        """
        for if_k, if_v in node['interfaces'].items():
            if if_k == 'mgmt':
                continue
            InterfaceSetup.tg_set_interface_driver(node, if_v['pci_address'],
                                                   if_v['driver'])

    @staticmethod
    def create_vxlan_interface(node, vni, source_ip, destination_ip):
        """Create VXLAN interface and return index of created interface

        Executes "vxlan_add_del_tunnel src {src} dst {dst} vni {vni}" VAT
        command on the node.

        :param node: Node where to create VXLAN interface
        :param vni: VXLAN Network Identifier
        :param source_ip: Source IP of a VXLAN Tunnel End Point
        :param destination_ip: Destination IP of a VXLAN Tunnel End Point
        :type node: dict
        :type vni: int
        :type source_ip: str
        :type destination_ip: str
        :return: SW IF INDEX of created interface
        :rtype: int
        """

        output = VatExecutor.cmd_from_template(node, "vxlan_create.vat",
                                               src=source_ip,
                                               dst=destination_ip,
                                               vni=vni)
        output = output[0]

        if output["retval"] == 0:
            return output["sw_if_index"]
        else:
            raise RuntimeError('Unable to create VXLAN interface on node {}'.\
                               format(node))

    @staticmethod
    def create_vlan_subinterface(node, interface, vlan):
        """TBD

        :param node: Node to add subinterface on.
        :param interface: TBD
        :param vlan: TBD
        :type node: dict
        :type interface: str or int
        :type vlan: int
        :return: name and index of created subinterface
        :rtype: tuple
        """

        def _get_interface_sw_index(node, interface):
            # TODO: refactor Topology.get_interface_sw_index
            try:
                return int(interface)
            except ValueError:
                for port in node['interfaces'].values():
                    port_name = port.get('name')
                    if port_name == interface:
                        return port.get('vpp_sw_index')
                return None
        sw_if_index = _get_interface_sw_index(node, interface)

        output = VatExecutor.cmd_from_template(node, "add_vlan_subif.vat",
                                               sw_if_index=sw_if_index,
                                               vlan=vlan)
        output = output[0]

        if output["retval"] == 0:
            sw_subif_index = output["sw_if_index"]
            logger.trace('Created subif with index {}'.format(sw_subif_index))
        else:
            raise RuntimeError('Unable to create VLAN subinterface on node {}'
                               .format(node))

        with VatTerminal(node, False) as vat:
            vat.vat_terminal_exec_cmd('exec show interfaces')

        return '{}.{}'.format(interface, vlan), sw_subif_index

    @staticmethod
    def show_traces(node):
        with VatTerminal(node, False) as vat:
            vat.vat_terminal_exec_cmd('exec show trace')
            vat.vat_terminal_exec_cmd('exec show interfaces')
