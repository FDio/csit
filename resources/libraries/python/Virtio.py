# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Virtio feature flags library."""

from enum import IntEnum


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


class Virtio:

    @staticmethod
    def create_virtio_feature_mask(**kwargs):
        """Create virtio feature mask with feature bits set according to kwargs.
        :param kwargs: Key-value pairs of feature names and it's state
        :type kwargs: dict
        """
        virtion_feature_mask = 0

        for feature_name, enabled in kwargs.items():
            virtio_feature_name = "VIRTIO_NET_F_API_" + feature_name.upper()
            if virtio_feature_name not in VirtioFeaturesFlags.__members__:
                raise ValueError("Unsupported virtio feature flag name")
            elif enabled:
                virtion_feature_mask |= \
                    1 << VirtioFeaturesFlags[virtio_feature_name].value

        return virtion_feature_mask

    @staticmethod
    def is_virtio_feature_enabled(virtio_feature_mask, virtio_feature_flag):
        """Checks if concrete virtion feature is enabled inside
         virtio_feature_mask
        :param virtio_feature_mask: Mask of enabled virtio features
        :param feature_name: Name of checked feature
        :type virtio_feature_mask: int
        :type feature_name: str
        """
        feature_flag_bit = 1 << virtio_feature_flag.value
        return (virtio_feature_mask & feature_flag_bit) > 0
