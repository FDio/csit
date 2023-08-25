# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""IP4 Topology Library."""

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.IPUtil import IPUtil


class IPTopology:
    """IP4 Topology Library."""

    @staticmethod
    def initialize_ipv4_forwarding(nodes, count=1):
        """"""
        topology = BuiltIn().get_variable_value("&{topology_info}")
        dut = topology["duts"][-1]
        int = BuiltIn().get_variable_value("${int}")

        for i in range(1):
            DUT1_int1 = BuiltIn().get_variable_value(f"${{DUT1_{int}1}}[0]")
            DUT1_int2 = BuiltIn().get_variable_value(f"${{DUT1_{int}2}}[0]")
            DUT_int1 = BuiltIn().get_variable_value(f"${{{dut}_{int}1}}[0]")
            DUT_int2 = BuiltIn().get_variable_value(f"${{{dut}_{int}2}}[0]")

            IPUtil.vpp_add_ip_neighbor(
                nodes["DUT1"], DUT1_int1, "1.1.1.1", topology["TG_pf1_mac"]
            )
            if dut == "DUT2":
                DUT_mac1 = BuiltIn().get_variable_value(f"${{{dut}_{int}1_mac}}[0]")
                IPUtil.vpp_add_ip_neighbor(
                    nodes["DUT1"], DUT1_int2, "2.2.2.2", DUT_mac1
                )
                DUT_mac2 = BuiltIn().get_variable_value(f"${{DUT1_{int}2_mac}}[0]")
                IPUtil.vpp_add_ip_neighbor(
                    nodes["DUT2"], DUT_int1, "2.2.2.1", DUT_mac2
                )
            IPUtil.vpp_add_ip_neighbor(
                nodes[dut], DUT_int2, "3.3.3.1", topology["TG_pf2_mac"]
            )

            IPUtil.vpp_interface_set_ip_address(
                nodes["DUT1"], DUT1_int1, "1.1.1.2", 30
            )
            if dut == "DUT2":
                IPUtil.vpp_interface_set_ip_address(
                    nodes["DUT1"], DUT1_int2, "2.2.2.1", 30
                )
                IPUtil.vpp_interface_set_ip_address(
                    nodes["DUT2"], DUT_int1, "2.2.2.2", 30
                )
            IPUtil.vpp_interface_set_ip_address(
                nodes[dut], DUT_int2, "3.3.3.2", 30
            )

            IPUtil.vpp_route_add(
                nodes["DUT1"], "10.0.0.0", 32, gateway="1.1.1.1",
                interface=DUT1_int1, count=count
            )
            if dut == "DUT2":
                IPUtil.vpp_route_add(
                    nodes["DUT1"], "20.0.0.0", 32, gateway="2.2.2.2",
                    interface=DUT1_int2, count=count
                )
                IPUtil.vpp_route_add(
                    nodes["DUT2"], "10.0.0.0", 32, gateway="2.2.2.1",
                    interface=DUT_int1, count=count
                )
            IPUtil.vpp_route_add(
                nodes[dut], "20.0.0.0", 32, gateway="3.3.3.1",
                interface=DUT_int2, count=count
            )
