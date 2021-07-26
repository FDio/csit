# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""Vhost-user interfaces library."""

from enum import IntEnum

from robot.api import logger

from resources.libraries.python.CpuUtils import CpuUtils
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology


class VirtioFeaturesFlags(IntEnum):
    """Virtio Features Flags."""
    VIRTIO_NET_F_API_CSUM = 0
    VIRTIO_NET_F_API_GUEST_CSUM = 1
    VIRTIO_NET_F_API_GSO = 6
    VIRTIO_NET_F_API_GUEST_TSO4 = 7
    VIRTIO_NET_F_API_GUEST_TSO6 = 8
    VIRTIO_NET_F_API_GUEST_UFO = 10
    VIRTIO_NET_F_API_HOST_TSO4 = 11
    VIRTIO_NET_F_API_HOST_TSO6 = 12
    VIRTIO_NET_F_API_HOST_UFO = 14
    VIRTIO_NET_F_API_MRG_RXBUF = 15
    VIRTIO_NET_F_API_CTRL_VQ = 17
    VIRTIO_NET_F_API_GUEST_ANNOUNCE = 21
    VIRTIO_NET_F_API_MQ = 22
    VIRTIO_F_API_ANY_LAYOUT = 27
    VIRTIO_F_API_INDIRECT_DESC = 28


class VhostUser:
    """Vhost-user interfaces L1 library."""

    @staticmethod
    def vpp_create_vhost_user_interface(
            node, socket, is_server=False, virtio_feature_mask=None):
        """Create Vhost-user interface on VPP node.

        :param node: Node to create Vhost-user interface on.
        :param socket: Vhost-user interface socket path.
        :param is_server: Server side of connection. Default: False
        :param virtio_feature_mask: Mask of virtio features to be enabled.
        :type node: dict
        :type socket: str
        :type is_server: bool
        :type virtio_feature_mask: int
        :returns: SW interface index.
        :rtype: int
        """
        cmd = u"create_vhost_user_if"
        err_msg = f"Failed to create Vhost-user interface " \
            f"on host {node[u'host']}"
        if virtio_feature_mask is None:
            enable_gso = False
        else:
            enable_gso = VirtioFeatureMask.is_feature_enabled(
                virtio_feature_mask, VirtioFeaturesFlags.VIRTIO_NET_F_API_GSO
            )
        args = dict(
            is_server=bool(is_server),
            sock_filename=str(socket),
            enable_gso=bool(enable_gso)
        )

        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        # Update the Topology:
        if_key = Topology.add_new_port(node, u"vhost")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)

        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        ifc_mac = InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)

        Topology.update_interface_vhost_socket(node, if_key, socket)

        return sw_if_index

    @staticmethod
    def get_vhost_user_if_name_by_sock(node, socket):
        """Get Vhost-user interface name by socket.

        :param node: Node to get Vhost-user interface name on.
        :param socket: Vhost-user interface socket path.
        :type node: dict
        :type socket: str
        :returns: Interface name or None if not found.
        :rtype: str
        """
        for interface in node[u"interfaces"].values():
            if interface.get(u"socket") == socket:
                return interface.get(u"name")
        return None

    @staticmethod
    def get_vhost_user_mac_by_sw_index(node, sw_if_index):
        """Get Vhost-user l2_address for the given interface from actual
        interface dump.

        :param node: VPP node to get interface data from.
        :param sw_if_index: SW index of the specific interface.
        :type node: dict
        :type sw_if_index: str
        :returns: l2_address of the given interface.
        :rtype: str
        """
        return InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)

    @staticmethod
    def show_vpp_vhost_on_all_duts(nodes):
        """Show Vhost-user on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VhostUser.vhost_user_dump(node)

    @staticmethod
    def vhost_user_dump(node):
        """Get vhost-user data for the given node.

        :param node: VPP node to get interface data from.
        :type node: dict
        :returns: List of dictionaries with all vhost-user interfaces.
        :rtype: list
        """
        cmd = u"sw_interface_vhost_user_dump"
        err_msg = f"Failed to get vhost-user dump on host {node['host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        logger.debug(f"Vhost-user details:\n{details}")
        return details

    @staticmethod
    def vhost_user_affinity(node, pf_key, skip_cnt=0):
        """Set vhost-user affinity for the given node.

        :param node: Topology node.
        :param pf_key: Interface key to compute numa location.
        :param skip_cnt: Skip first "skip_cnt" CPUs.
        :type node: dict
        :type pf_key: str
        :type skip_cnt: int
        """
        pids, _ = exec_cmd_no_error(
            node, f"grep -h vhost /proc/*/comm | uniq | xargs pidof")

        affinity = CpuUtils.get_affinity_vhost(
            node, pf_key, skip_cnt=skip_cnt, cpu_cnt=len(pids.split(" ")))

        for cpu, pid in zip(affinity, pids.split(" ")):
            exec_cmd_no_error(node, f"taskset -pc {cpu} {pid}", sudo=True)


class VirtioFeatureMask:
    """Virtio features utilities"""

    @staticmethod
    def create_virtio_feature_mask(**kwargs):
        """Create virtio feature mask with feature bits set according to kwargs.
        :param kwargs: Key-value pairs of feature names and it's state
        :type kwargs: dict
        """
        virtio_feature_mask = 0

        if u"all" in kwargs and kwargs[u"all"] is True:
            for virtio_feature_flag in VirtioFeaturesFlags:
                virtio_feature_mask |= 1 << virtio_feature_flag.value
        else:
            for feature_name, enabled in kwargs.items():
                virtio_feature_name = \
                    u"VIRTIO_NET_F_API_" + feature_name.upper()
                if virtio_feature_name not in VirtioFeaturesFlags.__members__:
                    raise ValueError(u"Unsupported virtio feature flag name")
                if enabled:
                    virtio_feature_mask |= \
                        1 << VirtioFeaturesFlags[virtio_feature_name].value

        return virtio_feature_mask

    @staticmethod
    def is_feature_enabled(virtio_feature_mask, virtio_feature_flag):
        """Checks if concrete virtio feature is enabled within
         virtio_feature_mask
        :param virtio_feature_mask: Mask of enabled virtio features
        :param virtio_feature_flag: Checked virtio feature
        :type virtio_feature_mask: int
        :type virtio_feature_flag: VirtioFeaturesFlags
        """
        feature_flag_bit = 1 << virtio_feature_flag.value
        return (virtio_feature_mask & feature_flag_bit) > 0
