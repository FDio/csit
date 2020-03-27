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

"""Segment Routing over IPv6 data plane utilities library."""

from enum import IntEnum

from ipaddress import ip_address, IPv6Address

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class SRv6Behavior(IntEnum):
    """SRv6 LocalSID supported functions."""
    # Endpoint function
    END = 1
    # Endpoint function with Layer-3 cross-connect
    END_X = 2
    # Endpoint with decapsulation and Layer-2 cross-connect
    END_DX2 = 5
    # Endpoint with decapsulation and IPv6 cross-connect
    END_DX6 = 6
    # Endpoint with decapsulation and IPv4 cross-connect
    END_DX4 = 7
    # Endpoint with decapsulation and IPv6 table lookup
    END_DT6 = 8
    # Endpoint with decapsulation and IPv4 table lookup
    END_DT4 = 9
    # Endpoint to SR-unaware appliance via static proxy
    END_AS = 20
    # Endpoint to SR-unaware appliance via dynamic proxy
    END_AD = 21
    # Endpoint to SR-unaware appliance via masquerading
    END_AM = 22


class SRv6PolicySteeringTypes(IntEnum):
    """SRv6 steering types."""
    SR_STEER_L2 = 2
    SR_STEER_IPV4 = 4
    SR_STEER_IPV6 = 6


class SRv6:
    """SRv6 class."""

    @staticmethod
    def create_srv6_sid_list(sids):
        """Create SRv6 SID list object.

        :param sids: SID IPv6 addresses.
        :type sids: list
        :returns: SRv6 SID list object.
        :rtype: dict
        """
        sid_list = [IPv6Address(sid).packed for sid in sids]

        return dict(
            num_sids=len(sid_list),
            weight=1,
            sids=sid_list + (16 - len(sid_list)) * [IPv6Address(0).packed]
        )

    @staticmethod
    def configure_sr_localsid(
            node, local_sid, behavior, interface=None, next_hop=None,
            fib_table=None, out_if=None, in_if=None, src_addr=None,
            sid_list=None):
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
        :param out_if: Interface name of local interface for sending traffic
            towards the Service Function (Optional, required for SRv6 endpoint
            to SR-unaware appliance).
        :param in_if: Interface name of local interface receiving the traffic
            coming back from the Service Function (Optional, required for SRv6
            endpoint to SR-unaware appliance).
        :param src_addr: Source address on the packets coming back on in_if
            interface (Optional, required for SRv6 endpoint to SR-unaware
            appliance via static proxy).
        :param sid_list: SID list (Optional, required for SRv6 endpoint to
            SR-unaware appliance via static proxy).
        :type node: dict
        :type local_sid: str
        :type behavior: str
        :type interface: str
        :type next_hop: str
        :type fib_table: str
        :type out_if: str
        :type in_if: str
        :type src_addr: str
        :type sid_list: list
        :raises ValueError: If required parameter is missing.
        """
        beh = behavior.replace(u".", u"_").upper()
        # There is no SRv6Behaviour enum defined for functions from SRv6 plugins
        # so we need to use CLI command to configure it.
        if beh in (getattr(SRv6Behavior, u"END_AD").name,
                   getattr(SRv6Behavior, u"END_AS").name,
                   getattr(SRv6Behavior, u"END_AM").name):
            if beh == getattr(SRv6Behavior, u"END_AS").name:
                if next_hop is None or out_if is None or in_if is None or \
                        src_addr is None or sid_list is None:
                    raise ValueError(
                        f"Required parameter(s) missing.\n"
                        f"next_hop:{next_hop}\n "
                        f"out_if:{out_if}\n"
                        f"in_if:{in_if}\n"
                        f"src_addr:{src_addr}\n"
                        f"sid_list:{sid_list}"
                    )
                sid_conf = f"next {u' next '.join(sid_list)}"
                params = f"nh {next_hop} oif {out_if} iif {in_if} " \
                    f"src {src_addr} {sid_conf}"
            else:
                if next_hop is None or out_if is None or in_if is None:
                    raise ValueError(
                        f"Required parameter(s) missing.\n"
                        f"next_hop:{next_hop}\n"
                        f"out_if:{out_if}\n"
                        f"in_if:{in_if}"
                    )
                params = f"nh {next_hop} oif {out_if} iif {in_if}"

            cli_cmd = f"sr localsid address {local_sid} behavior {behavior} " \
                f"{params}"

            PapiSocketExecutor.run_cli_cmd(node, cli_cmd)
            return

        cmd = u"sr_localsid_add_del"
        args = dict(
            is_del=False,
            localsid=IPv6Address(local_sid).packed,
            end_psp=False,
            behavior=getattr(SRv6Behavior, beh).value,
            sw_if_index=Constants.BITWISE_NON_ZERO,
            vlan_index=0,
            fib_table=0,
            nh_addr=0
        )
        err_msg = f"Failed to add SR localSID {local_sid} " \
            f"host {node[u'host']}"
        if beh in (getattr(SRv6Behavior, u"END_X").name,
                   getattr(SRv6Behavior, u"END_DX4").name,
                   getattr(SRv6Behavior, u"END_DX6").name):
            if interface is None or next_hop is None:
                raise ValueError(
                    f"Required parameter(s) missing.\n"
                    f"interface:{interface}\n"
                    f"next_hop:{next_hop}"
                )
            args[u"sw_if_index"] = InterfaceUtil.get_interface_index(
                node, interface
            )
            args[u"nh_addr"] = IPAddress.create_ip_address_object(
                ip_address(next_hop)
            )
        elif beh == getattr(SRv6Behavior, u"END_DX2").name:
            if interface is None:
                raise ValueError(
                    f"Required parameter missing.\ninterface: {interface}"
                )
            args[u"sw_if_index"] = InterfaceUtil.get_interface_index(
                node, interface
            )
        elif beh in (getattr(SRv6Behavior, u"END_DT4").name,
                     getattr(SRv6Behavior, u"END_DT6").name):
            if fib_table is None:
                raise ValueError(
                    f"Required parameter missing.\n"
                    f"fib_table: {fib_table}"
                )
            args[u"fib_table"] = fib_table

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def show_sr_localsids(node):
        """Show SRv6 LocalSIDs on the given node.

        :param node: Given node to show localSIDs on.
        :type node: dict
        """
        cmd = u"sr_localsids_dump"
        PapiExecutor.dump_and_log(node, (cmd,))

    @staticmethod
    def configure_sr_policy(node, bsid, sid_list, mode=u"encap"):
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
        cmd = u"sr_policy_add"
        args = dict(
            bsid_addr=IPv6Address(bsid).packed,
            weight=1,
            is_encap=bool(mode == u"encap"),
            is_spray=False,
            sids=SRv6.create_srv6_sid_list(sid_list)
        )
        err_msg = f"Failed to add SR policy for BindingSID {bsid} " \
            f"on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def show_sr_policies(node):
        """Show SRv6 policies on the given node.

        :param node: Given node to show SRv6 policies on.
        :type node: dict
        """
        cmd = u"sr_policies_dump"
        PapiExecutor.dump_and_log(node, (cmd,))

    @staticmethod
    def _get_sr_steer_policy_args(
            node, mode, interface=None, ip_addr=None, prefix=None):
        """Return values of sw_if_index, mask_width, prefix_addr and
            traffic_type for sr_steering_add_del API.

        :param node: Given node to create/delete steering policy on.
        :param mode: Mode of operation - L2 or L3.
        :param interface: Interface name (Optional, required in case of
            L2 mode).
        :param ip_addr: IPv4/IPv6 address (Optional, required in case of L3
            mode).
        :param prefix: IP address prefix (Optional, required in case of L3
            mode).
        :type node: dict
        :type mode: str
        :type interface: str
        :type ip_addr: str
        :type prefix: int
        :returns: Values for sw_if_index, prefix and traffic_type
        :rtype: tuple
        :raises ValueError: If unsupported mode used or required parameter
            is missing.
        """
        if mode.lower() == u"l2":
            if interface is None:
                raise ValueError(
                    f"Required data missing.\n"
                    f"interface: {interface}"
                )
            sw_if_index = InterfaceUtil.get_interface_index(node, interface)
            prefix = 0
            traffic_type = getattr(
                SRv6PolicySteeringTypes, u"SR_STEER_L2"
            ).value
        elif mode.lower() == u"l3":
            if ip_addr is None or prefix is None:
                raise ValueError(
                    f"Required data missing.\n"
                    f"IP address:{ip_addr}\n"
                    f"mask:{prefix}"
                )
            sw_if_index = Constants.BITWISE_NON_ZERO
            ip_addr = ip_address(ip_addr)
            prefix = IPUtil.create_prefix_object(ip_addr, int(prefix))
            traffic_type = getattr(
                    SRv6PolicySteeringTypes, u"SR_STEER_IPV4"
                ).value if ip_addr.version == 4 else getattr(
                    SRv6PolicySteeringTypes, u"SR_STEER_IPV6"
                ).value
        else:
            raise ValueError(f"Unsupported mode: {mode}")

        return sw_if_index, prefix, traffic_type

    # TODO: Bring L1 names, arguments and defaults closer to PAPI ones.
    @staticmethod
    def configure_sr_steer(
            node, mode, bsid, interface=None, ip_addr=None, prefix=None):
        """Create SRv6 steering policy on the given node.

        :param node: Given node to create steering policy on.
        :param mode: Mode of operation - L2 or L3.
        :param bsid: BindingSID - local SID IPv6 address.
        :param interface: Interface name (Optional, required in case of
            L2 mode).
        :param ip_addr: IPv4/IPv6 address (Optional, required in case of L3
            mode).
        :param prefix: IP address prefix (Optional, required in case of L3
            mode).
        :type node: dict
        :type mode: str
        :type bsid: str
        :type interface: str
        :type ip_addr: str
        :type prefix: int
        :raises ValueError: If unsupported mode used or required parameter
            is missing.
        """
        sw_if_index, prefix, traffic_type = SRv6._get_sr_steer_policy_args(
                node, mode, interface, ip_addr, prefix
            )

        cmd = u"sr_steering_add_del"
        args = dict(
            is_del=False,
            bsid_addr=IPv6Address(str(bsid)).packed,
            sr_policy_index=0,
            table_id=0,
            prefix=prefix,
            sw_if_index=sw_if_index,
            traffic_type=traffic_type
        )
        err_msg = f"Failed to add SRv6 steering policy for BindingSID {bsid} " \
            f"on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def show_sr_steering_policies(node):
        """Show SRv6 steering policies on the given node.

        :param node: Given node to show SRv6 steering policies on.
        :type node: dict
        """
        cmd = u"sr_steering_pol_dump"
        PapiExecutor.dump_and_log(node, (cmd,))

    @staticmethod
    def set_sr_encaps_source_address(node, ip6_addr):
        """Set SRv6 encapsulation source address on the given node.

        :param node: Given node to set SRv6 encapsulation source address on.
        :param ip6_addr: Local SID IPv6 address.
        :type node: dict
        :type ip6_addr: str
        """
        cmd = u"sr_set_encap_source"
        args = dict(
            encaps_source=IPv6Address(ip6_addr).packed
        )
        err_msg = f"Failed to set SRv6 encapsulation source address " \
            f"{ip6_addr} on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
