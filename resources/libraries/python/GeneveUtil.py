# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""VPP GENEVE Plugin utilities library."""

from ipaddress import ip_address

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology
from resources.libraries.python.VPPUtil import VPPUtil


class GeneveUtil:
    """VPP GENEVE Plugin Keywords."""

    @staticmethod
    def add_geneve_tunnel(
            node, local_address, remote_address, vni, multicast_if=None,
            encap_vrf=0, l3_mode=False):
        """Add GENEVE tunnel on the specified VPP node.

        :param node: Topology node.
        :param local_address: Local IP address.
        :param remote_address: Remote IP address.
        :param vni: Virtual network ID.
        :param multicast_if: Interface key of multicast interface; used only if
            remote is multicast. (Default value = None)
        :param encap_vrf: The FIB ID for sending unicast GENEVE encap packets or
            receiving multicast packets. (Default value = 0)
        :param l3_mode: Use geneve tunnel in L3 mode (ip routing) if Tue else in
            L2 mode (L2 switching). (Default value = False)
        :type node: dict
        :type local_address: str
        :type remote_address: str
        :type vni: int
        :type multicast_if: str
        :type encap_vrf: int
        :type l3_mode: bool
        :returns: SW interface index of created geneve tunnel.
        :rtype: int
        :raises RuntimeError: if no NSIM features are enabled or
                vpp papi command fails.
        """
        cmd = u"geneve_add_del_tunnel2"
        args = dict(
            is_add=True,
            local_address=IPAddress.create_ip_address_object(
                ip_address(local_address)
            ),
            remote_address=IPAddress.create_ip_address_object(
                ip_address(remote_address)
            ),
            mcast_sw_if_index=Topology.get_interface_sw_index(
                node, multicast_if
            ) if multicast_if else Constants.BITWISE_NON_ZERO,
            encap_vrf_id=int(encap_vrf),
            decap_next_index=VPPUtil.vpp_add_node_next(
                node, node_name=u"geneve4-input", next_name=u"ethernet-input"
            ) if l3_mode else Constants.BITWISE_NON_ZERO,
            vni=int(vni),
            l3_mode=l3_mode
        )
        err_msg = f"Failed to configure GENEVE tunnel on host {node[u'host']}!"
        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        if_key = Topology.add_new_port(node, u"geneve_tunnel")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)
        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        return sw_if_index
