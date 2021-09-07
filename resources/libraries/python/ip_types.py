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

    def is_ip6(self):
        """Return whether the address is IPv6.

        Useful for call sites that want to compute their desired prefix length.

        :returns: True if the address is IPv6, false otherwise (assumin IPv4).
        :rtype: bool
        """
        return u"ip6" in self

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

    def is_ip6(self):
        """Return whether the address is IPv6.

        Useful for call sites that want to compute their desired prefix length.

        :returns: True if the address is IPv6, false otherwise (assumin IPv4).
        :rtype: bool
        """
        return self[u"af"] == AddressFamily.ADDRESS_IP6

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
                af=AddressFamily.ADDRESS_IP6,
                un=AddressUnion.from_ip_address(address),
            )
        # Assuming IP4.
        return cls(
            af=AddressFamily.ADDRESS_IP4,
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
    def from_str_network(cls, network):
        """Factory to convert from string formatted network.

        The address part does not have to be aligned.

        :param address: IP network to convert from (slash format).
        :type address: str
        :returns: New instance storing the address.
        :rtype: cls
        """
        return cls.from_ip_network(ip_network(network))

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
