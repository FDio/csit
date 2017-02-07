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

"""NAT utilities library."""

from resources.libraries.python.VatExecutor import VatExecutor


class NATUtil(object):
    """NAT utilities."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_get_nat_static_mappings(node):
        """Get NAT static mappings from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: List of static mappings.
        :rtype: list
        :raises RuntimeError: If the output is not as expected.
        """

        vat = VatExecutor()
        # JSON output not supported for this command
        vat.execute_script('snat/snat_mapping_dump.vat', node, json_out=False)

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
    def vpp_get_nat_interfaces(node):
        """Get list of interfaces configured with NAT from VPP node.

        :param node: VPP node.
        :type node: dict
        :returns: List of interfaces on the node that are configured with NAT.
        :rtype: list
        :raises RuntimeError: If the output is not as expected.
        """

        vat = VatExecutor()
        # JSON output not supported for this command
        vat.execute_script('snat/snat_interface_dump.vat', node,
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
