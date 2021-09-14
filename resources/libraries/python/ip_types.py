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
Several methods are added to make the instance usable instead of results of
ip_address and ip_network.

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

    @classmethod
    def for_version(cls, version):
        """Return instance suitable for give IP version.

        :param version: IP version, 4 or 6.
        :type version: int
        :returns: ADDRESS_IP4 or ADDRESS_IP6
        :rtype: cls
        :raises ValueError: If version is not 4 nor 6.
        """
        if version == 4:
            return cls.ADDRESS_IP4
        if version == 6:
            return cls.ADDRESS_IP6
        raise ValueError(f"Unsupported IP version: {version}")


class AddressUnion(dict):
    """In VPP .api the fields of this type are vl_api_address_union_t.

    Main definition:
    https://github.com/FDio/vpp/blob/v21.06/src/vnet/ip/ip_types.api#L91-L94
    For PAPI, this is a dict with key "ip4" xor "ip6", value ip_address.
    For VAT2, this is str(ip_address).
    """
    # Intentionally changing constructor signature,
    # be careful when subclassing.
    def __init__(self, address):
        """Dict factory to convert from multiple types.

        None, empty string and other falses are understood as 0.0.0.0.

        Currently supported imput types:
        IPv4Address, IPv6Address, str, AddressUnion, Address, AddressWithPrefix.
        The returned value can come from argument internals,
        so modify it on your own risk.

        :param address: IP address to convert from.
        :type address: object
        """
        if isinstance(address, AddressWithPrefix):
            address = address[u"address"]
        if isinstance(address, Address):
            address = address[u"un"]
        if isinstance(address, AddressUnion):
            super().__init__(address)
            return
        address = address if address else ip_address(u"0.0.0.0")
        if not isinstance(address, (IPv4Address, IPv6Address)):
            address = ip_address(address)
        if isinstance(address, IPv6Address):
            super().__init__(ip6=address)
            return
        # Assuming IP4.
        super().__init__(ip4=address)

    def __str__(self):
        """Return human readable string suitable for VAT2.

        :returns: Human readable form, based on ip_address "compressed".
        :rtype: str
        """
        return str(self.ip_address)

    @property
    def version(self):
        """Return IP version of the address.

        If version is not detected to be 6, it is assumed to be 4.

        :returns: 4 or 6, depending on address value.
        :rtype: int
        """
        return 6 if u"ip6" in self else 4

    @property
    def ip_address(self):
        """Return the address converted as in ip_address.

        :returns: Converted address.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        for address in self.values():
            return address


class Address(dict):
    """In VPP .api the fields of this type are vl_api_address_t.

    Main definition:
    https://github.com/FDio/vpp/blob/v21.06/src/vnet/ip/ip_types.api#L96-L99
    For PAPI, this is a dict with keys "af" and "un", value ip_address.
    For VAT2, this is str(ip_address) of the "un" part.
    """
    # Intentionally changing constructor signature,
    # be careful when subclassing.
    def __init__(self, address):
        """Dict factory to convert from multiple types.

        None, empty string and other falses are understood as 0.0.0.0.

        Currently supported imput types:
        IPv4Address, IPv6Address, str, AddressUnion, Address, AddressWithPrefix.
        The returned value can come from argument internals,
        so modify it on your own risk.

        :param address: IP address to convert from.
        :type address: Union[IPv4Address, IPv6Address, None]
        """
        if isinstance(address, AddressWithPrefix):
            address = address[u"address"]
        if isinstance(address, Address):
            super().__init__(address)
            return
        if not isinstance(address, AddressUnion):
            address = AddressUnion(address)
        super().__init__(
            af=AddressFamily.for_version(address.version),
            un=address,
        )

    def __str__(self):
        """Return human readable string suitable for VAT2.

        :returns: Human readable form, based on ip_address "compressed".
        :rtype: str
        """
        for address in self[u"un"].values():
            return str(address)

    @property
    def version(self):
        """Return IP version of the address.

        If version is not detected to be 6, it is assumed to be 4.

        :returns: 4 or 6, depending on address value.
        :rtype: int
        """
        return self[u"un"].version

    @property
    def ip_address(self):
        """Return the address converted as in ip_address.

        :returns: Converted address.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        return self[u"un"].ip_address

    def __add__(self, increment):
        """Return new address increased by "increment" addresses.

        This makes it possible to use Address instances in ObjIncrement.

        :param increment: How many addresses to add. Can be zero or negative.
        :type increment: int
        :returns: New incremented address.
        :rtype: self.__class__
        """
        return self.__class__(self.ip_address + increment)


class AddressWithPrefix(dict):
    """In VPP .api the fields of this type are vl_api_prefix_t,
    or vl_api_address_with_prefix_t.

    Main definition:
    https://github.com/FDio/vpp/blob/v21.06/src/vnet/ip/ip_types.api#L101-L104
    For PAPI, this is a dict with keys "address" and "len",
    value ip_address and int.
    For VAT2, this is str(ip_network), elsewhere known as "slash" format.
    """
    # Intentionally changing constructor signature,
    # be careful when subclassing.
    def __init__(self, address, plen=None):
        """Dict factory to convert from various input types.

        The address part does not have to be aligned.
        None, empty string and other falses are understood as 0.0.0.0.

        If the first argument is ip_network, AddressWithPrefix or
        string in slash format, second argument is ignored.
        Else, the first argument is converted to Address.

        :param address: IP network to convert from.
        :param plen: Prefix length, if not contained in first argument.
        :type address: object
        :type plen: Union[int, str]
        """
        if isinstance(address, AddressWithPrefix):
            super().__init__(address)
            return
        if isinstance(address, str) and u"/" in address:
            address = ip_network(address)
        if isinstance(address, (IPv4Network, IPv6Network)):
            plen = address.prefixlen
            address = address.network_address
        super().__init__(address=Address(address), len=int(plen))

    def __str__(self):
        """Return human readable string suitable for VAT2.

        :returns: Human readable form, based on ip_network "compressed".
        :rtype: str
        """
        for address in self[u"address"][u"un"].values():
            return f"{address}/{self[u'len']}"

    @property
    def version(self):
        """Return IP version of the address.

        If version is not detected to be 6, it is assumed to be 4.

        :returns: 4 or 6, depending on address value.
        :rtype: int
        """
        return self[u"address"][u"un"].version

    @property
    def network_address(self):
        """Return the address part, converted as in ip_address.

        :returns: Converted address part.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        return self[u"address"].ip_address

    @property
    def prefixlen(self):
        """Return the prefix length of this network.

        :returns: Prefix length.
        :rtype: int
        """
        return self[u"len"]

    def __add__(self, increment):
        """Return new address increased by "increment" network sizes.

        This makes it possible to use AddressWithPlen instances in ObjIncrement,
        without the need to compute network size for address increment.

        :param increment: How many networks to add. Can be zero or negative.
        :type increment: int
        :returns: New incremented network.
        :rtype: self.__class__
        """
        plen = self.prefixlen
        network_size = 1 << (self.network_address.max_prefixlen - plen)
        new_address = self.network_address + increment * network_size
        return self.__class__(new_address, plen)
