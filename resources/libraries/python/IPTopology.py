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

"""IP Topology Library."""

from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.IPUtil import IPUtil


class IPTopology:
    """IP Topology Library."""

    @staticmethod
    def initialize_ipv4_forwarding(count=1, pfs=2):
        """
        Custom setup of IPv4 forwarding with scalability of IP routes on all
        DUT nodes in 2-node / 3-node circular topology.

        :param count: Number of routes to configure.
        :param pfs: Number of physical interfaces to configure.
        :type count: int
        :type pfs: int
        """
        topology = BuiltIn().get_variable_value("&{topology_info}")
        dut = topology["duts"][-1]
        ifl = BuiltIn().get_variable_value("${int}")

        for l, i in zip(range(pfs // 2), range(1, pfs, 2)):
            dut1_int1 = BuiltIn().get_variable_value(f"${{DUT1_{ifl}{i}}}[0]")
            dut1_int2 = BuiltIn().get_variable_value(f"${{DUT1_{ifl}{i+1}}}[0]")
            dut_int1 = BuiltIn().get_variable_value(f"${{{dut}_{ifl}{i}}}[0]")
            dut_int2 = BuiltIn().get_variable_value(f"${{{dut}_{ifl}{i+1}}}[0]")

            IPUtil.vpp_add_ip_neighbor(
                topology["DUT1"], dut1_int1, f"1.{l}.1.1",
                topology[f"TG_pf{i}_mac"][0]
            )
            if dut == "DUT2":
                dut_mac1 = BuiltIn().get_variable_value(
                    f"${{{dut}_{ifl}{i}_mac}}[0]"
                )
                IPUtil.vpp_add_ip_neighbor(
                    topology["DUT1"], dut1_int2, f"3.{l}.3.2", dut_mac1
                )
                dut_mac2 = BuiltIn().get_variable_value(
                    f"${{DUT1_{ifl}{i+1}_mac}}[0]"
                )
                IPUtil.vpp_add_ip_neighbor(
                    topology["DUT2"], dut_int1, f"3.{l}.3.1", dut_mac2
                )
            IPUtil.vpp_add_ip_neighbor(
                topology[dut], dut_int2, f"2.{l}.2.1",
                topology[f"TG_pf{i+1}_mac"][0]
            )

            IPUtil.vpp_interface_set_ip_address(
                topology["DUT1"], dut1_int1, f"1.{l}.1.2", 30
            )
            if dut == "DUT2":
                IPUtil.vpp_interface_set_ip_address(
                    topology["DUT1"], dut1_int2, f"3.{l}.3.1", 30
                )
                IPUtil.vpp_interface_set_ip_address(
                    topology["DUT2"], dut_int1, f"3.{l}.3.2", 30
                )
            IPUtil.vpp_interface_set_ip_address(
                topology[dut], dut_int2, f"2.{l}.2.2", 30
            )

            IPUtil.vpp_route_add(
                topology["DUT1"], f"{i}0.0.0.0", 32, gateway=f"1.{l}.1.1",
                interface=dut1_int1, count=count
            )
            if dut == "DUT2":
                IPUtil.vpp_route_add(
                    topology["DUT1"], f"{i+1}0.0.0.0", 32, gateway=f"3.{l}.3.2",
                    interface=dut1_int2, count=count
                )
                IPUtil.vpp_route_add(
                    topology["DUT2"], f"{i}0.0.0.0", 32, gateway=f"3.{l}.3.1",
                    interface=dut_int1, count=count
                )
            IPUtil.vpp_route_add(
                topology[dut], f"{i+1}0.0.0.0", 32, gateway=f"2.{l}.2.1",
                interface=dut_int2, count=count
            )


    @staticmethod
    def initialize_ipv6_forwarding(count=1, pfs=2):
        """
        Custom setup of IPv6 forwarding with scalability of IP routes on all
        DUT nodes in 2-node / 3-node circular topology.

        :param count: Number of routes to configure.
        :param pfs: Number of physical interfaces to configure.
        :type count: int
        :type pfs: int
        """
        topology = BuiltIn().get_variable_value("&{topology_info}")
        dut = topology["duts"][-1]
        ifl = BuiltIn().get_variable_value("${int}")

        for l, i in zip(range(pfs // 2), range(1, pfs, 2)):
            dut1_int1 = BuiltIn().get_variable_value(f"${{DUT1_{ifl}{i}}}[0]")
            dut1_int2 = BuiltIn().get_variable_value(f"${{DUT1_{ifl}{i+1}}}[0]")
            dut_int1 = BuiltIn().get_variable_value(f"${{{dut}_{ifl}{i}}}[0]")
            dut_int2 = BuiltIn().get_variable_value(f"${{{dut}_{ifl}{i+1}}}[0]")

            IPUtil.vpp_add_ip_neighbor(
                topology["DUT1"], dut1_int1, f"2001:{l}::1",
                topology[f"TG_pf{i}_mac"][0]
            )
            if dut == "DUT2":
                dut_mac1 = BuiltIn().get_variable_value(
                    f"${{{dut}_{ifl}{i}_mac}}[0]"
                )
                IPUtil.vpp_add_ip_neighbor(
                    topology["DUT1"], dut1_int2, f"2003:{l}::2", dut_mac1
                )
                dut_mac2 = BuiltIn().get_variable_value(
                    f"${{DUT1_{ifl}{i+1}_mac}}[0]"
                )
                IPUtil.vpp_add_ip_neighbor(
                    topology["DUT2"], dut_int1, f"2003:{l}::1", dut_mac2
                )
            IPUtil.vpp_add_ip_neighbor(
                topology[dut], dut_int2, f"2002:{l}::1",
                topology[f"TG_pf{i+1}_mac"][0]
            )

            IPUtil.vpp_interface_set_ip_address(
                topology["DUT1"], dut1_int1, f"2001:{l}::2", 64
            )
            if dut == "DUT2":
                IPUtil.vpp_interface_set_ip_address(
                    topology["DUT1"], dut1_int2, f"2003:{l}::1", 64
                )
                IPUtil.vpp_interface_set_ip_address(
                    topology["DUT2"], dut_int1, f"2003:{l}::2", 64
                )
            IPUtil.vpp_interface_set_ip_address(
                topology[dut], dut_int2, f"2002:{l}::2", 64
            )

            IPUtil.vpp_route_add(
                topology["DUT1"], f"2{i}00::0", 64,
                gateway=f"2001:{l}::1", interface=dut1_int1, count=count
            )
            if dut == "DUT2":
                IPUtil.vpp_route_add(
                    topology["DUT1"], f"2{i+1}00::0", 64,
                    gateway=f"2003:{l}::2", interface=dut1_int2, count=count
                )
                IPUtil.vpp_route_add(
                    topology["DUT2"], f"2{i}00::0", 64,
                    gateway=f"2003:{l}::1", interface=dut_int1, count=count
                )
            IPUtil.vpp_route_add(
                topology[dut], f"2{i+1}00::0", 64,
                gateway=f"2002:{l}::1", interface=dut_int2, count=count
            )