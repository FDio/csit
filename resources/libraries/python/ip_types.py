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

TODO: Investigate speed in scale tests, add special quick functions if needed.
"""

from enum import IntEnum
from ipaddress import (
    ip_address, ip_network, IPv4Address, IPv6Address, IPv4Network, IPv6Network
)


def incrementator(start_value, increment=1):
    """Return an iterator which starts at given value.

    There is iterutils.count doing exactly this,
    but it only works for numeric arguments.

    This also work for carious other objects, e.g. IPv4Address,
    the only requirement is __add__ function returning the same type
    and accepting the increment object (may not be numeric either).

    :param start_value: First iteration will return this value.
    :param increment: What to add each iteration, can also be zero or negative.
    :type start_value: Any object with appropriate __add__ method.
    :type invrement: Object accepted by the __add__ method.
    """
    current_value = start_value
    while 1:
        yield current_value
        current_value += increment


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
        IPv4Address, IPv6Address, str, int,
        AddressUnion, Address, AddressWithPrefix.
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

    def __int__(self):
        """Return binary form of address packed as int.

        :returns: Integer form of the address.
        :rtype: str
        """
        return int(self.ip_address)

    @property
    def version(self):
        """Return IP version of the address.

        If version is not detected to be 6, it is assumed to be 4.

        :returns: 4 or 6, depending on address value.
        :rtype: int
        """
        return 6 if u"ip6" in self else 4

    @property
    def max_prefixlen(self):
        """Return the maximal prefix length for addresses of this version.

        :returns: Maximal prefix length.
        :rtype: int
        """
        return self.ip_address.max_prefixlen

    @property
    def ip_address(self):
        """Return the address converted as in ip_address.

        :returns: Converted address.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        for address in self.values():
            return address

    def __add__(self, increment):
        """Return new address increased by "increment" addresses.

        This makes it possible to use AddressUnion instances in ObjIncrement.

        :param increment: How many addresses to add. Can be zero or negative.
        :type increment: int
        :returns: New incremented address.
        :rtype: self.__class__
        """
        return self.__class__(self.ip_address + increment)


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
        IPv4Address, IPv6Address, str, int,
        AddressUnion, Address, AddressWithPrefix.
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

    def __int__(self):
        """Return binary form of address packed as int.

        :returns: Integer form of the address.
        :rtype: str
        """
        return int(self.ip_address)

    @property
    def version(self):
        """Return IP version of the address.

        If version is not detected to be 6, it is assumed to be 4.

        :returns: 4 or 6, depending on address value.
        :rtype: int
        """
        return self[u"un"].version

    @property
    def max_prefixlen(self):
        """Return the maximal prefix length for addresses of this version.

        :returns: Maximal prefix length.
        :rtype: int
        """
        return self.ip_address.max_prefixlen

    @property
    def ip_address(self):
        """Return the address converted as in ip_address.

        :returns: Converted address.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        return self[u"address"].ip_address

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
        If plen is None, maximal prefix length is used.

        If the first argument is ip_network, AddressWithPrefix or
        string in slash format, second argument is ignored.
        Else, the first argument is converted to Address.

        :param address: IP network to convert from.
        :param plen: Prefix length, if not contained in first argument.
        :type address: object
        :type plen: Union[int, str]
        """
        network = address
        if isinstance(network, AddressWithPrefix):
            super().__init__(network)
            return
        if isinstance(network, str) and u"/" in network:
            network = ip_network(network, strict=True)
        if isinstance(network, (IPv4Network, IPv6Network)):
            address = network.network_address
            plen = network.prefixlen
        address=Address(address)
        if plen is None:
            plen = address.max_prefixlen
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
    def prefixlen(self):
        """Return the prefix length of this network.

        :returns: Prefix length.
        :rtype: int
        """
        return self[u"len"]

    @property
    def network_address(self):
        """Return the address part, converted as in ip_address.

        :returns: Converted address part.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        return self[u"address"].ip_address

    @property
    def broadcast_address(self):
        """Return broadcast (end) address of this network.

        :returns: Broadcast address.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        return ip_network(self.network_address, self[u"len"]).broadcast_address

    def __add__(self, increment):
        """Return new address increased by "increment" network sizes.

        This makes it possible to use AddressWithPlen instances in ObjIncrement,
        without the need to compute network size for address increment.

        :param increment: How many networks to add. Can be zero or negative.
        :type increment: int
        :returns: New incremented network.
        :rtype: self.__class__
        """
        addr = self.network_address
        new_addr = addr + 1 << (addr.max_prefixlen - self.prefixlen) * increment
        return self.__class__(new_addr, self.prefixlen)

    def range_str(self):
        """Return string representation some VAT/CLI commands need.

        The implementation uses broadcast address, so the output is correct
        only if the start address was properly aligned.

        :returns: Start address, dash, end address.
        :rtype: str
        """
        return f"{self.network_address} - {self.broadcast_address}"
