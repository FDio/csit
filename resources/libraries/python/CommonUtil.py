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


class ObjIncrement(object):
    """
    An iterator class used to generate values in each iteration.
    """
    def __init__(self, current_value, increment):
        self._current_value = None
        self._next_value = current_value
        self._increment = increment
        super(ObjIncrement, self).__init__()

    def _incr(self):
        """
        The iteration that will be called in each PAPI/VAT config.
        """
        self._current_value = self._next_value
        self._next_value = self._next_value + self._increment

    def __next__(self):
        """
        Each iteration returns an object (with new values in each iteration)
        that can be used to configure VPP using PAPI calls.
        """
        self._incr()
        return self._current_value

    def __iter__(self):
        return self

    def _str_fmt(self):
        return str(self._current_value)

    def vat_str(self):
        """
        Increment the current value and return a string representation used
        in vat cli commands.
        """
        self._incr()
        return self._str_fmt()


class NetworkIncrement(ObjIncrement):
    """
    An iterator object which accepts a network range and returns a new network
    incremented by the increment each time it's incremented.
    """
    def _incr(self):
        """
        Increment the network, e.g.:
        '30.0.0.0/24' incremented by 1 (the next network) is '30.0.1.0/24'.
        '30.0.0.0/24' incremented by 2 is '30.0.2.0/24'.
        """
        self._current_value = self._next_value

        if self._increment > 0:
            prefix_len = self._current_value.prefixlen
            addr = self._current_value.network_address
            host_len = self._current_value.max_prefixlen - prefix_len
            self._next_value = ip_network(
                f"{addr + self._increment * (1 << host_len)}"
                f"/{prefix_len}"
            )

    def _str_fmt(self):
        """
        The string representation of the network is
        '<ip_address_start> - <ip_address_stop>' for the purposes of the
        'ipsec policy add spd' cli.
        """
        return f"{self._current_value.network_address} - " \
               f"{self._current_value.broadcast_address}"
