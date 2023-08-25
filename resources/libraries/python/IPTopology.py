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
    def initialize_ipv4_forwarding(nodes, count=1, links=1):
        """
        xxx.xxx.xxx.xxx
         |   |   |   |
        SEG.LNK.INT.HOST

        Where:
            - SEG: Topology segment (1-TG/DUT, [2-DUT/TG], 3-DUT/DUT).
            - LNK: Link within topology segment.
            - INT: Interface on the NIC.
            - HOST: Host in subnet within link.
        """
        topology = BuiltIn().get_variable_value("&{topology_info}")
        dut = topology["duts"][-1]
        ifl = BuiltIn().get_variable_value("${int}")

        for l,i in zip(range(links), range(1,links*2,2)):
            DUT1_int1 = BuiltIn().get_variable_value(f"${{DUT1_{ifl}{i}}}[0]")
            DUT1_int2 = BuiltIn().get_variable_value(f"${{DUT1_{ifl}{i+1}}}[0]")
            DUT_int1 = BuiltIn().get_variable_value(f"${{{dut}_{ifl}{i}}}[0]")
            DUT_int2 = BuiltIn().get_variable_value(f"${{{dut}_{ifl}{i+1}}}[0]")
            print(topology["TG_pf1_mac"])
            IPUtil.vpp_add_ip_neighbor(
                nodes["DUT1"], DUT1_int1, f"1.{l}.{i}.1",
                topology["TG_pf1_mac"][0]
            )
            if dut == "DUT2":
                DUT_mac1 = BuiltIn().get_variable_value(
                    f"${{{dut}_{ifl}{i}_mac}}[0]"
                )
                IPUtil.vpp_add_ip_neighbor(
                    nodes["DUT1"], DUT1_int2, f"3.{l}.{i+1}.2", DUT_mac1
                )
                DUT_mac2 = BuiltIn().get_variable_value(
                    f"${{DUT1_{ifl}{i+1}_mac}}[0]"
                )
                IPUtil.vpp_add_ip_neighbor(
                    nodes["DUT2"], DUT_int1, f"3.{l}.{i}.1", DUT_mac2
                )
            IPUtil.vpp_add_ip_neighbor(
                nodes[dut], DUT_int2, f"2.{l}.{i+1}.1",
                topology["TG_pf2_mac"][0]
            )

            IPUtil.vpp_interface_set_ip_address(
                nodes["DUT1"], DUT1_int1, f"1.{l}.{i}.2", 30
            )
            if dut == "DUT2":
                IPUtil.vpp_interface_set_ip_address(
                    nodes["DUT1"], DUT1_int2, f"3.{l}.{i+1}.1", 30
                )
                IPUtil.vpp_interface_set_ip_address(
                    nodes["DUT2"], DUT_int1, f"3.{l}.{i}.2", 30
                )
            IPUtil.vpp_interface_set_ip_address(
                nodes[dut], DUT_int2, f"2.{l}.{i+1}.2", 30
            )

            IPUtil.vpp_route_add(
                nodes["DUT1"], "10.0.0.0", 32, gateway=f"1.{l}.{i}.1",
                interface=DUT1_int1, count=count
            )
            if dut == "DUT2":
                IPUtil.vpp_route_add(
                    nodes["DUT1"], "20.0.0.0", 32, gateway=f"3.{l}.{i+1}.2",
                    interface=DUT1_int2, count=count
                )
                IPUtil.vpp_route_add(
                    nodes["DUT2"], "10.0.0.0", 32, gateway=f"3.{l}.{i}.1",
                    interface=DUT_int1, count=count
                )
            IPUtil.vpp_route_add(
                nodes[dut], "20.0.0.0", 32, gateway=f"2.{l}.{i+1}.1",
                interface=DUT_int2, count=count
            )
