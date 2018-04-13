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

"""NAT utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal, VatExecutor


class NATUtil(object):
    """This class defines the methods to set NAT."""

    def __init__(self):
        pass

    @staticmethod
    def set_nat44_interfaces(node, int_in, int_out):
        """Set inside and outside interfaces for NAT44.

        :param node: DUT node.
        :param int_in: Inside interface.
        :param int_out: Outside interface.
        :type node: dict
        :type int_in: str
        :type int_out: str
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If setting of inside and outside interfaces for
            NAT44 fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat44_set_interfaces.vat',
                    int_in=int_in, int_out=int_out)
                return response
        except:
            raise RuntimeError("Setting of inside and outside interfaces for "
                               "NAT failed!")

    @staticmethod
    def set_nat44_deterministic(node, ip_in, subnet_in, ip_out, subnet_out):
        """Set deterministic behaviour of NAT44.

        :param node: DUT node.
        :param ip_in: Inside IP.
        :param subnet_in: Inside IP subnet.
        :param ip_out: Outside IP.
        :param subnet_out: Outside IP subnet.
        :type node: dict
        :type ip_in: str
        :type subnet_in: str or int
        :type ip_out: str
        :type subnet_out: str or int
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If setting of deterministic behaviour of NAT44
            fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat44_set_deterministic.vat',
                    ip_in=ip_in, subnet_in=subnet_in,
                    ip_out=ip_out, subnet_out=subnet_out)
                return response
        except:
            raise RuntimeError("Setting of deterministic behaviour of NAT "
                               "failed!")

    @staticmethod
    def set_nat_workers(node, lcores):
        """Set NAT workers.

        :param node: DUT node.
        :param lcores: List of cores, format: range e.g. 1-5 or list of ranges
            e.g.: 1-5,18-22.
        :type node: dict
        :type lcores: str
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If setting of NAT workers fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat_set_workers.vat', lcores=lcores)
                return response
        except:
            raise RuntimeError("Setting of NAT workers failed!")

    @staticmethod
    def show_nat(node):
        """Show the NAT settings.

        :param node: DUT node.
        :type node: dict
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If getting of NAT settings fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat_show_nat.vat')
                return response
        except:
            raise RuntimeError("Getting of NAT settings failed!")

    @staticmethod
    def show_nat44_deterministic_forward(node, ip_addr):
        """Show forward IP address and port(s).

        :param node: DUT node.
        :param ip_addr: IP address.
        :type node: dict
        :type ip_addr: str
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If command 'exec snat deterministic forward'
            fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat44_deterministic_forward.vat', ip=ip_addr)
                return response
        except:
            raise RuntimeError("Command 'exec nat44 deterministic forward {ip}'"
                               " failed!".format(ip=ip_addr))

    @staticmethod
    def show_nat44_deterministic_reverse(node, ip_addr, port):
        """Show reverse IP address.

        :param node: DUT node.
        :param ip_addr: IP address.
        :param port: Port.
        :type node: dict
        :type ip_addr: str
        :type port: str or int
        :returns: Response of the command.
        :rtype: str
        :raises RuntimeError: If command 'exec snat deterministic reverse'
            fails.
        """

        try:
            with VatTerminal(node, json_param=False) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'nat/nat44_deterministic_reverse.vat',
                    ip=ip_addr, port=port)
                return response
        except:
            raise RuntimeError(
                "Command 'exec nat44 deterministic reverse {ip}:{port}'"
                " failed!".format(ip=ip_addr, port=port))

    @staticmethod
    def get_nat_static_mappings(node):
        """Get NAT static mappings from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: List of static mappings.
        :rtype: list
        :raises RuntimeError: If the output is not as expected.
        """

        vat = VatExecutor()
        # JSON output not supported for this command
        vat.execute_script('nat/snat_mapping_dump.vat', node, json_out=False)

        stdout = vat.get_script_stdout()
        lines = stdout.split("\n")

        data = []
        # lines[0,1] are table and column headers
        for line in lines[2::]:
            # Ignore extra data after NAT table
            if "snat_static_mapping_dump error: Misc" in line or "vat#" in line:
                continue
            items = line.split(" ")
            while "" in items:
                items.remove("")
            if len(items) == 0:
                continue
            elif len(items) == 4:
                # no ports were returned
                data.append({
                    "local_address": items[0],
                    "remote_address": items[1],
                    "vrf": items[2],
                    "protocol": items[3]
                })
            elif len(items) == 6:
                data.append({
                    "local_address": items[0],
                    "local_port": items[1],
                    "remote_address": items[2],
                    "remote_port": items[3],
                    "vrf": items[4],
                    "protocol": items[5]
                })
            else:
                raise RuntimeError("Unexpected output from snat_mapping_dump.")

        return data

    @staticmethod
    def get_nat_interfaces(node):
        """Get list of interfaces configured with NAT from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: List of interfaces on the node that are configured with NAT.
        :rtype: list
        :raises RuntimeError: If the output is not as expected.
        """

        vat = VatExecutor()
        # JSON output not supported for this command
        vat.execute_script('nat/snat_interface_dump.vat', node,
                           json_out=False)

        stdout = vat.get_script_stdout()
        lines = stdout.split("\n")

        data = []
        for line in lines:
            items = line.split(" ")
            for trash in ("", "vat#"):
                while trash in items:
                    items.remove(trash)
            if len(items) == 0:
                continue
            elif len(items) == 3:
                data.append({
                    # items[0] is the table header - "sw_if_index"
                    "sw_if_index": items[1],
                    "direction": items[2]
                })
            else:
                raise RuntimeError(
                    "Unexpected output from snat_interface_dump.")

        return data
