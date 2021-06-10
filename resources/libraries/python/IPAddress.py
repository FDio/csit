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

"""Common IP utilities library."""

from enum import IntEnum


class AddressFamily(IntEnum):
    """IP address family."""
    ADDRESS_IP4 = 0
    ADDRESS_IP6 = 1


class IPAddress:
    """Common IP address utilities"""

    @staticmethod
    def union_addr(ip_addr):
        """Creates union IP address.

        :param ip_addr: IPv4 or IPv6 address.
        :type ip_addr: IPv4Address or IPv6Address
        :returns: Union IP address.
        :rtype: dict
        """
        return dict(ip6=ip_addr.packed) if ip_addr.version == 6 \
            else dict(ip4=ip_addr.packed)

    @staticmethod
    def create_ip_address_object(ip_addr):
        """Create IP address object.

        :param ip_addr: IPv4 or IPv6 address
        :type ip_addr: IPv4Address or IPv6Address
        :returns: IP address object.
        :rtype: dict
        """
        return dict(
            af=getattr(
                AddressFamily, u"ADDRESS_IP6" if ip_addr.version == 6
                else u"ADDRESS_IP4"
            ).value,
            un=IPAddress.union_addr(ip_addr)
        )
