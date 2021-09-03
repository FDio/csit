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
from ipaddress import ip_address, IPv6Address


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

    @classmethod
    def from_ip_address(cls, address):
        """Factory to convert from ip_address.

        None, empty string and other falses are understood as 0.0.0.0.

        :param address: IP address to convert from.
        :type address: Union[IPv4Address, IPv6Address, None]
        :returns: New instance storing the address.
        :rtype: cls
        """
        address = address if address else ip_address(u"0.0.0.0")
        if isinstance(address, IPv6Address):
            return cls(ip6=address)
        # Assuming IP4.
        return cls(ip4=address)

    @classmethod
    def from_str_address(cls, address):
        """Factory to convert from string address via ip_address.

        The current implementation happens to work when address is ip_address.
        None, empty string and other falses are understood as 0.0.0.0.

        :param address: Readable IP address to convert from.
        :type address: Optional[str]
        :returns: New instance storing the address.
        :rtype: cls
        """
        address = address if address else u"0.0.0.0"
        return cls.from_ip_address(ip_address(address))


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

    @classmethod
    def from_ip_address(cls, address):
        """Factory to convert from ip_address.

        None, empty string and other falses are understood as 0.0.0.0.

        :param address: IP address to convert from.
        :type address: Union[IPv4Address, IPv6Address, None]
        :returns: New instance storing the address.
        :rtype: cls
        """
        address = address if address else ip_address(u"0.0.0.0")
        if isinstance(address, IPv6Address):
            return cls(
                af=AddressFamily.ADDRESS_IP6.value,
                un=AddressUnion.from_ip_address(address),
            )
        # Assuming IP4.
        return cls(
            af=AddressFamily.ADDRESS_IP4.value,
            un=AddressUnion.from_ip_address(address),
        )

    @classmethod
    def from_str_address(cls, address):
        """Factory to convert from string address via ip_address.

        The current implementation happens to work when address is ip_address.
        None, empty string and other falses are understood as 0.0.0.0.

        :param address: Readable IP address to convert from.
        :type address: Optional[str]
        :returns: New instance storing the address.
        :rtype: cls
        """
        address = address if address else u"0.0.0.0"
        return cls.from_ip_address(ip_address(address))


class AddressWithPrefix(dict):
    """In VPP .api the fields of this type are vl_api_prefix_t,
    or vl_api_address_with_prefix_t.

    As the ability to add int to ip_network is really convenient,
    we override __add__ and also add some properties to access results.

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

    @classmethod
    def from_ip_network(cls, network):
        """Factory to convert from ip_network.

        The address part does not have to be aligned.

        :param address: IP network to convert from.
        :type address: Union[IPv4Network, IPv6Network]
        :returns: New instance storing the address.
        :rtype: cls
        """
        return cls(
            address=Address.from_ip_address(network.network_address),
            len=network.prefixlen,
        )

    @classmethod
    def from_str_network(cls, network, strict=False):
        """Factory to convert from string network.

        The address part alignment is checked when strict is True.

        :param address: Network in {address}/{plen} format.
        :param strict: If true, fail on misaligned start address.
        :type address: str
        :type strict: bool
        :returns: New instance storing the address.
        :rtype: cls
        """
        return cls.from_ip_network(ip_network(network, strict))

    @classmethod
    def from_ip_address_and_plen(cls, address, plen):
        """Factory to convert from ip_address and prefix length.

        String plen is converted to int as decimal.
        None, empty string and other falses are understood as 0.0.0.0.

        :param address: IP address to convert from.
        :param plen: Prefix length.
        :type address: Union[IPv4Address, IPv6Address, None]
        :type plen: Union[int, str]
        :returns: New instance storing the address.
        :rtype: cls
        """
        address = address if address else ip_address(u"0.0.0.0")
        return cls(
            address=Address.from_ip_address(address),
            len=int(plen),
        )

    @classmethod
    def from_str_address_and_plen(cls, address, plen):
        """Factory to convert from string address via ip_address.

        String plen is converted to int as decimal.
        The current implementation happens to work when address is ip_address.
        None, empty string and other falses are understood as 0.0.0.0.

        :param address: Readable IP address to convert from.
        :param plen: Prefix length.
        :type address: Optional[str]
        :type plen: Union[int, str]
        :returns: New instance storing the address.
        :rtype: cls
        """
        address = address if address else u"0.0.0.0"
        return cls.from_ip_address_and_plen(ip_address(address), plen)

    @property
    def address(self):
        """Return the address part.

        :returns: The address part of the network, can be unaligned.
        :rtype: Union[IPv4Address, IPv6Address]
        """
        return self[u"address"]

    @property
    def plen(self):
        """Return the prefix length part.

        :returns: The prefix length part of the network.
        :rtype: int
        """
        return self[u"len"]

    def __add__(self, increment):
        """Increase address by the "increment" network sizes.

        This makes it easy to use ObjIncrement to iterate over
        adjacent networks.

        Decimal string is also accepted as increment value.

        :param increment: How many networks sizes to add, can be negative.
        :type increment: Union[int, str]
        :returns: New instance with increased address.
        :rtype: self.__class__
        """
        host_len = self.address.max_prefixlen - self.plen
        new_address = self.address + increment * (1 << host_len)
        return self.__class__.from_ip_address_and_plen(new_address, self.plen)

%%%% HERE %%%%
# IPsecUtil.vpp_ipsec_add_spd_entry wants start and end address,
# Duck type AddressWithPrefix to offer network_address and broadcast_address
# and unify with range_str. Then delete convert_to_ip_network.
    
    def range_str(self):
        """Return string representation some VAT commands need.

        The implementation uses broadcast address, so the output is correct
        only if the start address was properly aligned.

        :returns: Start address, dash, end address.
        :rtype: str
        """
        return f"{self.address.network_address} - " \
               f"{self.address.broadcast_address}"


def convert_to_ip_network(obj, strict=True):
    """Convert to ip_network from multiple argument types.

    Sometimes we have IP network as human readable string,
    sometimes as ip_network, sometimes as AddressWithPrefix.
    This converts anything known to ip_network.
    Checking for alignment happens only when strict
    and only when obj is not ip_network already.

    :param obj: Value to convert from.
    :param strict: If true, fail on misaligned start address.
    :type obj: Union[str, IPv4Network, IPv6Network, AddressWithPrefix]
    :type strict: bool
    :returns: New instance, or obj if already ip_network.
    :rtype: Union[IPv4Network, IPv6Network]
    """
    if isinstance(obj, (IPv4Network, IPv6Network)):
        return obj
    if isinstance(obj, AddressWithPrefix):
        return ip_network((obj.address, obj.plen), strict=strict)
    return ip_network(obj, strict=strict)
