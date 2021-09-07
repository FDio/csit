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

"""Classes for IP addresses and networks, with multiple serialization options.

Some usage (PAPI) wants to serialize as dicts,
other (VAT2, CLI) prefer serialization to human readable strings.

Classes subclassed from dict and with __str__ method cover both usages.
Also, several factory methods are added to simplify call sites.
False address arguments are converted to 0.0.0.0 (all zero bytes for PAPI).

TODO: Add (optional) checking of dict-like constructor kwargs.
TODO: Investigate speed in scale tests, add special quick functions if needed.
"""

from enum import IntEnum
from ipaddress import (
    ip_address, ip_network, IPv4Address, IPv6Address, IPv4Network, IPv6Network
)


class AddressFamily(IntEnum):
    """IP address family."""
    ADDRESS_IP4 = 0
    ADDRESS_IP6 = 1

class AddressUnion(dict):
    """In VPP .api the fields of this type are vl_api_address_union_t.

    Main definition:
    https://github.com/FDio/vpp/blob/v21.06/src/vnet/ip/ip_types.api#L91-L94
    For PAPI, this is a dict with key "ip4" xor "ip6", value ip_address.
    For VAT2, this is str(ip_address).
    """
    # Inherited constructor, as we do no checks yet.

    def __str__(self):
        """Return human readable string suitable for VAT2.

        :returns: Human readable form, based on ip_address "compressed".
        :rtype: str
        """
        for address in self.values():
            return str(address)

    def is_ip6(self):
        """Return whether the address is IPv6.

        Useful for call sites that want to compute their desired prefix length.

        :returns: True if the address is IPv6, false otherwise (assumin IPv4).
        :rtype: bool
        """
        return u"ip6" in self

    @classmethod
    def of(cls, address):
        """Factory to convert from multiple types.

        None, empty string and other falses are understood as 0.0.0.0.

        Currently supported imput types:
        IPv4Address, IPv6Address, str, AddressUnion, Address, AddressWithPrefix.
        The returned value can come from argument internals,
        so modify it on your own risk.

        :param address: IP address to convert from.
        :type address: object
        :returns: An instance storing the address.
        :rtype: cls
        """
        if isinstance(address, AddressWithPrefix):
            address = address[u"address"]
        if isinstance(address, Address):
            address = address[u"un"]
        if isinstance(address, AddressUnion):
            return address
        address = address if address else ip_address(u"0.0.0.0")
        if not isinstance(address, (IPv4Address, IPv6Address)):
            address = ip_address(address)
        if isinstance(address, IPv6Address):
            return cls(ip6=address)
        # Assuming IP4.
        return cls(ip4=address)


class Address(dict):
    """In VPP .api the fields of this type are vl_api_address_t.

    Main definition:
    https://github.com/FDio/vpp/blob/v21.06/src/vnet/ip/ip_types.api#L96-L99
    For PAPI, this is a dict with keys "af" and "un", value ip_address.
    For VAT2, this is str(ip_address) of the "un" part.
    """
    # Inherited constructor, as we do no checks yet.

    def __str__(self):
        """Return human readable string suitable for VAT2.

        :returns: Human readable form, based on ip_address "compressed".
        :rtype: str
        """
        for address in self[u"un"].values():
            return str(address)

    def is_ip6(self):
        """Return whether the address is IPv6.

        Useful for call sites that want to compute their desired prefix length.

        :returns: True if the address is IPv6, false otherwise (assumin IPv4).
        :rtype: bool
        """
        return self[u"af"] == AddressFamily.ADDRESS_IP6

    @classmethod
    def of(cls, address):
        """Factory to convert from multiple types.

        None, empty string and other falses are understood as 0.0.0.0.

        Currently supported imput types:
        IPv4Address, IPv6Address, str, AddressUnion, Address, AddressWithPrefix.
        The returned value can come from argument internals,
        so modify it on your own risk.

        :param address: IP address to convert from.
        :type address: Union[IPv4Address, IPv6Address, None]
        :returns: New instance storing the address.
        :rtype: cls
        """
        if isinstance(address, AddressWithPrefix):
            address = address[u"address"]
        if isinstance(address, Address):
            return address
        if not isinstance(address, AddressUnion):
            address = AddressUnion.of(address)
        if address.is_ip6():
            af = AddressFamily.ADDRESS_IP6
        else:
            af = AddressFamily.ADDRESS_IP4
        return cls(af=af, un=address)


class AddressWithPrefix(dict):
    """In VPP .api the fields of this type are vl_api_prefix_t,
    or vl_api_address_with_prefix_t.

    Main definition:
    https://github.com/FDio/vpp/blob/v21.06/src/vnet/ip/ip_types.api#L101-L104
    For PAPI, this is a dict with keys "address" and "len",
    value ip_address and int.
    For VAT2, this is str(ip_network), elsewhere known as "slash" format.
    """
    # Inherited constructor, as we do no checks yet.

    def __str__(self):
        """Return human readable string suitable for VAT2.

        :returns: Human readable form, based on ip_network "compressed".
        :rtype: str
        """
        for address in self[u"address"][u"un"].values():
            return f"{address}/{self[u'len']}"

    def is_ip6(self):
        """Return whether the address part is IPv6.

        Useful for call sites that want to compute their desired prefix length.

        :returns: True if the address is IPv6, false otherwise (assumin IPv4).
        :rtype: bool
        """
        return self[u"address"].is_ip6()

    @classmethod
    def of(cls, address, plen=None):
        """Factory to convert from various input types.

        The address part does not have to be aligned.
        None, empty string and other falses are understood as 0.0.0.0.

        If the first argument is ip_network, AddressWithPrefix or
        string in slash format, second argument is ignored.
        Else, the first argument is converted to Address.

        :param address: IP network to convert from.
        :param plen: Prefix length, if not contained in first argument.
        :type address: object
        :type plen: Union[int, str]
        :returns: New instance storing the address.
        :rtype: cls
        """
        if isinstance(address, AddressWithPrefix):
            return address
        if isinstance(address, str) and u"/" in address:
            address = ip_network(address)
        if isinstance(address, (IPv4Network, IPv6Network)):
            plen = address.prefixlen
            address = address.network_address
        return cls(address=Address.of(address), len=int(plen))
