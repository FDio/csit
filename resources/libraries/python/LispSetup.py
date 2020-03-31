# Copyright (c) 2016-2020 Cisco and/or its affiliates.
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

"""Library to set up Lisp in topology."""

from enum import IntEnum

from ipaddress import ip_address

from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class EidType(IntEnum):
    """EID types."""
    PREFIX = 0
    MAC = 1
    NSH = 2


class LispEid:
    """Class for lisp eid."""

    @staticmethod
    def create_eid(eid, prefix_len):
        """Create lisp eid object.

        :param eid: Eid value.
        :param prefix_len: prefix len if the eid is IP address.
        :type eid: str
        :type prefix_len: int
        """
        eid_addr = dict(prefix=IPUtil.create_prefix_object(
            ip_address(eid), prefix_len)
        ) if prefix_len else dict(mac=str(eid))

        return dict(
            type=getattr(
                EidType, u"PREFIX" if prefix_len else u"MAC"
            ).value,
            address=eid_addr
        )


class LispRemoteLocator:
    """Class for lisp remote locator."""

    @staticmethod
    def create_rloc(ip_addr, prio=0, weight=0):
        """Create lisp remote locator object.

        :param ip_addr: IP/IPv6 address.
        :param prio: Priority.
        :param weight: Weight.
        :type ip_addr: str
        :type prio: int
        :type weight: int
        """
        return [
            dict(
                priority=prio,
                weight=weight,
                ip_address=ip_address(ip_addr)
            )
        ]


class LispStatus:
    """Class for lisp API."""

    @staticmethod
    def vpp_lisp_enable_disable(node, state):
        """Enable/Disable lisp in the VPP node in topology.

        :param node: Node of the test topology.
        :param state: State of the lisp, enable or disable.
        :type node: dict
        :type state: str
        """
        args = dict(is_enable=bool(state == u"enable"))
        cmd = u"lisp_enable_disable"
        err_msg = f"Failed to set LISP status on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispRemoteMapping:
    """Class for lisp remote mapping API."""

    @staticmethod
    def vpp_add_lisp_remote_mapping(
            node, vni, deid, deid_prefix, seid, seid_prefix, rloc,
            is_mac=False):
        """Add lisp remote mapping on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :param rloc: Receiver locator.
        :param is_mac: Set to True if the deid/seid is MAC address.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        :type rloc: str
        :type is_mac: bool
        """
        args = dict(
            is_add=True,
            is_src_dst=True,
            vni=int(vni),
            deid=LispEid.create_eid(deid, deid_prefix if not is_mac else None),
            seid=LispEid.create_eid(seid, seid_prefix if not is_mac else None),
            rloc_num=1,
            rlocs=LispRemoteLocator.create_rloc(rloc)
        )
        cmd = u"lisp_add_del_remote_mapping"
        err_msg = f"Failed to add remote mapping on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_lisp_remote_mapping(
            node, vni, deid, deid_prefix, seid, seid_prefix, rloc):
        """Delete lisp remote mapping on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :param rloc: Receiver locator.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        :type rloc: str
        """
        # used only with IPs
        args = dict(
            is_add=False,
            is_src_dst=True,
            vni=int(vni),
            deid=LispEid.create_eid(deid, deid_prefix),
            seid=LispEid.create_eid(seid, seid_prefix),
            rloc_num=1,
            rlocs=LispRemoteLocator.create_rloc(rloc)
        )
        cmd = u"lisp_add_del_remote_mapping"
        err_msg = f"Failed to delete remote mapping on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispAdjacency:
    """Class for lisp adjacency API."""

    @staticmethod
    def vpp_add_lisp_adjacency(
            node, vni, deid, deid_prefix, seid, seid_prefix, is_mac=False):
        """Add lisp adjacency on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :param is_mac: Set to True if the deid/seid is MAC address.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        :type is_mac: bool
        """
        args = dict(
            is_add=True,
            vni=int(vni),
            reid=LispEid.create_eid(deid, deid_prefix if not is_mac else None),
            leid=LispEid.create_eid(seid, seid_prefix if not is_mac else None)
        )
        cmd = u"lisp_add_del_adjacency"
        err_msg = f"Failed to add lisp adjacency on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_lisp_adjacency(
            node, vni, deid, deid_prefix, seid, seid_prefix):
        """Delete lisp adjacency on the VPP node in topology.

        :param node: VPP node.
        :param vni: Vni.
        :param deid: Destination eid address.
        :param deid_prefix: Destination eid address prefix_len.
        :param seid: Source eid address.
        :param seid_prefix: Source eid address prefix_len.
        :type node: dict
        :type vni: int
        :type deid: str
        :type deid_prefix: int
        :type seid: str
        :type seid_prefix: int
        """
        # used only with IPs
        args = dict(
            is_add=False,
            vni=int(vni),
            eid=LispEid.create_eid(deid, deid_prefix),
            leid=LispEid.create_eid(seid, seid_prefix)
        )
        cmd = u"lisp_add_del_adjacency"
        err_msg = f"Failed to delete lisp adjacency on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispGpeStatus:
    """Class for LISP GPE status manipulation."""

    @staticmethod
    def vpp_lisp_gpe_enable_disable(node, state):
        """Change the state of LISP GPE - enable or disable.

        :param node: VPP node.
        :param state: Requested state - enable or disable.
        :type node: dict
        :type state: str
        """
        args = dict(is_enable=bool(state == u"enable"))
        cmd = u"gpe_enable_disable"
        err_msg = f"Failed to set LISP GPE status on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispLocalEid:
    """Class for Lisp local eid API."""

    @staticmethod
    def vpp_add_lisp_local_eid(
            node, locator_set_name, vni, eid, prefix_len=None):
        """Set lisp eid address on the VPP node in topology.

        :param node: VPP node.
        :param locator_set_name: Name of the locator_set.
        :param vni: vni value.
        :param eid: Eid value.
        :param prefix_len: prefix len if the eid is IP address.
        :type node: dict
        :type locator_set_name: str
        :type vni: int
        :type eid: str
        :type prefix_len: int
        """
        args = dict(
            is_add=True,
            eid=LispEid.create_eid(eid, prefix_len),
            prefix_len=prefix_len,
            locator_set_name=locator_set_name,
            vni=int(vni)
        )
        cmd = u"lisp_add_del_local_eid"
        err_msg = f"Failed to add local eid on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_lisp_local_eid(
            node, locator_set_name, vni, eid, prefix_len=None):
        """Set lisp eid address on the VPP node in topology.

        :param node: VPP node.
        :param locator_set_name: Name of the locator_set.
        :param vni: vni value.
        :param eid: Eid value.
        :param prefix_len: prefix len if the eid is IP address.
        :type node: dict
        :type locator_set_name: str
        :type vni: int
        :type eid: str
        :type prefix_len: int
        """
        args = dict(
            is_add=False,
            eid=LispEid.create_eid(eid, prefix_len),
            prefix_len=prefix_len,
            locator_set_name=locator_set_name,
            vni=int(vni)
        )
        cmd = u"lisp_add_del_local_eid"
        err_msg = f"Failed to delete local eid on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispLocator:
    """Class for the Lisp Locator API."""

    @staticmethod
    def vpp_add_lisp_locator(node, locator_name, sw_if_index, priority, weight):
        """Set lisp locator on the VPP node in topology.

        :param node: VPP node.
        :param locator_name: Name of the locator_set.
        :param sw_if_index: sw_if_index if the interface.
        :param priority: priority of the locator.
        :param weight: weight of the locator.
        :type node: dict
        :type locator_name: str
        :type sw_if_index: int
        :type priority: int
        :type weight: int
        """

        args = dict(
            is_add=True,
            locator_set_name=locator_name,
            sw_if_index=sw_if_index,
            priority=priority,
            weight=weight
        )
        cmd = u"lisp_add_del_locator"
        err_msg = f"Failed to add locator on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_lisp_locator(node, locator_name, sw_if_index, priority, weight):
        """Unset lisp locator on the VPP node in topology.

        :param node: VPP node.
        :param locator_name: Name of the locator_set.
        :param sw_if_index: sw_if_index if the interface.
        :param priority: priority of the locator.
        :param weight: weight of the locator.
        :type node: dict
        :type locator_name: str
        :type sw_if_index: int
        :type priority: int
        :type weight: int
        """
        args = dict(
            is_add=False,
            locator_set_name=locator_name,
            sw_if_index=sw_if_index,
            priority=priority,
            weight=weight
        )
        cmd = u"lisp_add_del_locator"
        err_msg = f"Failed to delete locator on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispLocatorSet:
    """Class for Lisp Locator Set API."""

    @staticmethod
    def vpp_add_lisp_locator_set(node, name):
        """Add lisp locator_set on VPP.

        :param node: VPP node.
        :param name: VPP locator name.
        :type node: dict
        :type name: str
        """
        args = dict(
            is_add=True,
            locator_set_name=name,
            locator_num=0,
            locators=[]
        )
        cmd = u"lisp_add_del_locator_set"
        err_msg = f"Failed to add locator set on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_del_lisp_locator_set(node, name):
        """Del lisp locator_set on VPP.

        :param node: VPP node.
        :param name: VPP locator name.
        :type node: dict
        :type name: str
        """
        args = dict(
            is_add=False,
            locator_set_name=name,
            locator_num=0,
            locators=[]
        )
        cmd = u"lisp_add_del_locator_set"
        err_msg = f"Failed to delete locator set on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)


class LispEidTableMap:
    """
    Class for EID table map.
    """

    @staticmethod
    def vpp_lisp_eid_table_mapping(node, vni, bd_id=None, vrf=None):
        """
        Map LISP VNI to either bridge domain ID, or VRF ID.

        :param node: VPP node.
        :param vni: Lisp VNI.
        :param bd_id: Bridge domain ID.
        :param vrf: VRF id.
        :type node: dict
        :type vni: int
        :type bd_id: int
        :type vrf: int
        """
        # adding default mapping vni=0, vrf=0 needs to be skipped
        if bd_id is not None or int(vrf if vrf else 0) or int(vni):
            args = dict(
                is_add=True,
                vni=int(vni),
                dp_table=int(bd_id) if bd_id is not None else int(vrf),
                is_l2=bool(bd_id is not None)
            )
            cmd = u"lisp_eid_table_add_del_map"
            err_msg = f"Failed to add eid table map on host {node[u'host']}"

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args).get_reply(err_msg)
