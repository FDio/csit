# Copyright (c) 2021 PANTHEON.tech s.r.o.
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

"""Common utilities library."""

from ipaddress import ip_network


class _Increment(object):
    """
    An informal interface iterator class used to generate values in each
    iteration.
    """
    def __next__(self):
        """
        Each iteration returns an object (with new values in each iteration)
        that can be used to configure VPP. PAPI calls will just use the object
        itself or extract the needed values from the object.
        """
        raise NotImplemented

    def __iter__(self):
        return self

    def __str__(self):
        """
        String representation used in vat cli commands.
        """
        raise NotImplemented


class ObjIncrement(_Increment):
    """
    An iterator object which returns the input object incremented by increment
    each time it's iterated. This implies that the object must support the +
    binary operator with the used increment.
    """
    def __init__(self, current_value, increment):
        self._current_value = current_value
        self._increment = increment
        super(ObjIncrement, self).__init__()

    def __next__(self):
        current_value = self._current_value
        self._current_value += self._increment
        return current_value

    def __str__(self):
        return str(self._current_value)


class NetworkIncrement(_Increment):
    """
    An iterator object which accepts a network range and returns a new network
    incremented by the increment each time it's incremented.
    """
    def __init__(self, current_network, increment):
        self._current_network = ip_network(current_network)
        self._increment = increment
        super(NetworkIncrement, self).__init__()

    def __next__(self):
        """
        Return the next network incremented by increment.
        For example, network '30.0.0.0/24' incremented by 1 (i.e. the next
        network) is '30.0.1.0/24'.
        """
        current_network = self._current_network
        if self._increment > 0:
            prefix_len = self._current_network.prefixlen
            addr = self._current_network.network_address
            self._current_network = ip_network(
                f"{addr + (1 << 32 - prefix_len)}/{prefix_len}"
            )
        return current_network

    def __str__(self):
        """
        The string representation of the object is
        '<ip_address_start> - <ip_address_stop>' for the purposes of the
        'ipsec policy add spd' cli.
        """
        return f"{self._current_network.network_address} - " \
               f"{self._current_network.broadcast_address}"
