# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""Segment Routing over IPv6 dataplane utilities library."""

from enum import Enum

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.VatJsonUtil import VatJsonUtil
from resources.libraries.python.topology import Topology


class SRv6Behaviour(Enum):
    """Defines SRv6 endpoint functions implemented in VPP."""
    # Endpoint function
    END = 'end'
    # Endpoint function with Layer-3 cross-connect
    END_X = 'end.x'
    # Endpoint with decapsulation and Layer-2 cross-connect
    END_DX2 = 'end.dx2'
    # Endpoint with decapsulation and IPv4 cross-connect
    END_DX4 = 'end.dx4'
    # Endpoint with decapsulation and IPv4 table lookup
    END_DT4 = 'end.dt4'
    # Endpoint with decapsulation and IPv6 cross-connect
    END_DX6 = 'end.dx6'
    # Endpoint with decapsulation and IPv6 table lookup
    END_DT6 = 'end.dt6'


class SRv6(object):
    """SRv6 class."""

    def __init__(self):
        pass

    @staticmethod
    def configure_sr_localsid(node, local_sid, behavior, interface=None,
                              next_hop=None, fib_table=None):
        """Create SRv6 LocalSID and binds it to a particular behaviour on
        the given node.

        :param node: Given node to create localSID on.
        :param local_sid: LocalSID IPv6 address.
        :param behavior: SRv6 LocalSID function.
        :param interface: Interface name (Optional, required for
            L2/L3 xconnects).
        :param next_hop: Next hop IPv4/IPv6 address (Optional, required for L3
            xconnects).
        :param fib_table: FIB table for IPv4/IPv6 lookup (Optional, required for
            L3 routing).
        :type node: dict
        :type local_sid: str
        :type behavior: str
        :type interface: str
        :type next_hop: int
        :type fib_table: str
        :raises ValueError: If unsupported SRv6 LocalSID function used or
            required parameter is missing.
        """
        if behavior == SRv6Behaviour.END:
            params = ''
        elif behavior in [SRv6Behaviour.END_X, SRv6Behaviour.END_DX4,
                          SRv6Behaviour.END_DX6]:
            if interface is None or next_hop is None:
                raise ValueError('Required data missing.\ninterface:{0}\n'
                                 'next_hop:{1}'.format(interface, next_hop))
            interface_name = Topology.get_interface_name(node, interface)
            params = '{0} {1}'.format(interface_name, next_hop)
        elif behavior == SRv6Behaviour.END_DX2:
            if interface is None:
                raise ValueError('Required data missing.\ninterface:{0}\n'.
                                 format(interface))
            params = '{0}'.format(interface)
        elif behavior in [SRv6Behaviour.END_DT4, SRv6Behaviour.END_DT6]:
            if fib_table is None:
                raise ValueError('Required data missing.\nfib_table:{0}\n'.
                                 format(fib_table))
            params = '{0}'.format(fib_table)
        else:
            raise ValueError('Unsupported SRv6 LocalSID function: {0}'.
                             format(behavior))

        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_localsid_add.vat', local_sid=local_sid,
                behavior=behavior, params=params)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Create SRv6 LocalSID {0} failed on node {1}'.format(
                local_sid, node['host']))

    @staticmethod
    def delete_sr_localsid(node, local_sid):
        """Delete SRv6 LocalSID on the given node.

        :param node: Given node to delete localSID on.
        :param local_sid: LocalSID IPv6 address.
        :type node: dict
        :type local_sid: str
        """
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_localsid_del.vat', local_sid=local_sid)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Delete SRv6 LocalSID {0} failed on node {1}'.format(
                local_sid, node['host']))

    @staticmethod
    def show_sr_localsids(node):
        """Show SRv6 LocalSIDs on the given node.

        :param node: Given node to show localSIDs on.
        :type node: dict
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_localsids_show.vat')

    @staticmethod
    def configure_sr_policy(node, bsid, sid_list, mode='encap'):
        """Create SRv6 policy on the given node.

        :param node: Given node to create SRv6 policy on.
        :param bsid: BindingSID - local SID IPv6 address.
        :param sid_list: SID list.
        :param mode: Encapsulation / insertion mode.
        :type node: dict
        :type bsid: str
        :type sid_list: list
        :type mode: str
        """
        sid_conf = 'next ' + ' next '.join(sid_list)

        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_policy_add.vat', bsid=bsid,
                sid_conf=sid_conf, mode=mode)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Create SRv6 policy for BindingSID {0} failed on node '
                    '{1}'.format(bsid, node['host']))

    @staticmethod
    def delete_sr_policy(node, bsid):
        """Delete SRv6 policy on the given node.

        :param node: Given node to delete SRv6 policy on.
        :param bsid: BindingSID IPv6 address.
        :type node: dict
        :type bsid: str
        """
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_policy_del.vat', bsid=bsid)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Delete SRv6 policy for BindingSID {0} failed on node '
                    '{1}'.format(bsid, node['host']))

    @staticmethod
    def show_sr_policies(node):
        """Show SRv6 policies on the given node.

        :param node: Given node to show SRv6 policies on.
        :type node: dict
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_policies_show.vat')

    @staticmethod
    def configure_sr_steer(node, mode, bsid, interface=None, ip_addr=None,
                           mask=None):
        """Create SRv6 steering policy on the given node.

        :param node: Given node to create steering policy on.
        :param mode: Mode of operation - L2 or L3.
        :param bsid: BindingSID - local SID IPv6 address.
        :param interface: Interface name (Optional, required in case of
            L2 mode).
        :param ip_addr: IPv4/IPv6 address (Optional, required in case of L3
            mode).
        :param mask: IP address mask (Optional, required in case of L3 mode).
        :type node: dict
        :type mode: str
        :type bsid: str
        :type interface: str
        :type ip_addr: int
        :type mask: int
        :raises ValueError: If unsupported mode used or required parameter
            is missing.
        """
        if mode == 'l2':
            if interface is None:
                raise ValueError('Required data missing.\ninterface:{0}\n'.
                                 format(interface))
            interface_name = Topology.get_interface_name(node, interface)
            params = 'l2 {0}'.format(interface_name)
        elif mode == 'l3':
            if ip_addr is None or mask is None:
                raise ValueError('Required data missing.\nIP address:{0}\n'
                                 'mask:{1}'.format(ip_addr, mask))
            params = '{0}/{1}'.format(ip_addr, mask)
        else:
            raise ValueError('Unsupported mode: {0}'.format(mode))

        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_steer_add_del.vat', params=params, bsid=bsid)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Create SRv6 steering policy for BindingSID {0} failed on '
                    'node {1}'.format(bsid, node['host']))

    @staticmethod
    def delete_sr_steer(node, mode, bsid, interface=None, ip_addr=None,
                        mask=None):
        """Delete SRv6 steering policy on the given node.

        :param node: Given node to delete steering policy on.
        :param mode: Mode of operation - L2 or L3.
        :param bsid: BindingSID - local SID IPv6 address.
        :param interface: Interface name (Optional, required in case of
            L2 mode).
        :param ip_addr: IPv4/IPv6 address (Optional, required in case of L3
            mode).
        :param mask: IP address mask (Optional, required in case of L3 mode).
        :type node: dict
        :type mode: str
        :type bsid: str
        :type interface: str
        :type ip_addr: int
        :type mask: int
        :raises ValueError: If unsupported mode used or required parameter
            is missing.
        """
        params = 'del'
        if mode == 'l2':
            if interface is None:
                raise ValueError('Required data missing.\ninterface:{0}\n'.
                                 format(interface))
            interface_name = Topology.get_interface_name(node, interface)
            params += 'l2 {0}'.format(interface_name)
        elif mode == 'l3':
            if ip_addr is None or mask is None:
                raise ValueError('Required data missing.\nIP address:{0}\n'
                                 'mask:{1}'.format(ip_addr, mask))
            params += '{0}/{1}'.format(ip_addr, mask)
        else:
            raise ValueError('Unsupported mode: {0}'.format(mode))

        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_steer_add_del.vat', params=params, bsid=bsid)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Delete SRv6 policy for bsid {0} failed on node {1}'.format(
                bsid, node['host']))

    @staticmethod
    def show_sr_steering_policies(node):
        """Show SRv6 steering policies on the given node.

        :param node: Given node to show SRv6 steering policies on.
        :type node: dict
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_steer_policies_show.vat')

    @staticmethod
    def set_sr_encaps_source_address(node, ip6_addr):
        """Set SRv6 encapsulation source address on the given node.

        :param node: Given node to set SRv6 encapsulation source address on.
        :param ip6_addr: Local SID IPv6 address.
        :type node: dict
        :type ip6_addr: str
        """
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template(
                'srv6/sr_set_encaps_source.vat', ip6_addr=ip6_addr)

        VatJsonUtil.verify_vat_retval(
            resp[0],
            err_msg='Set SRv6 encapsulation source address {0} failed on node'
                    ' {1}'.format(ip6_addr, node['host']))
