# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Utils for MAP feature."""


def map_port_ranges(psid, length, offset=6):
    """Return list of port ranges for given PSID in tuple <min, max>.

    :param psid: PSID.
    :param length: PSID length.
    :param offset: PSID offset.
    :type psid: int
    :type length: int
    :type offset: int
    :return: List of (min, max) port range tuples inclusive.
    :rtype: list

                      0                   1
                      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
                     +-----------+-----------+-------+
       Ports in      |     A     |    PSID   |   j   |
    the CE port set  |    > 0    |           |       |
                     +-----------+-----------+-------+
                     |  a bits   |  k bits   |m bits |
    """

    port_field_len = 16
    port_field_min = int('0x0000', 16)
    port_field_max = int('0xffff', 16)

    a = offset
    k = length
    m = port_field_len - offset - length
    km = k + m
    j_max = port_field_max >> a + k

    port_ranges = []
    for A in range(1, (port_field_max >> km) + 1):
        port_ranges.append((((A << k) | psid) << m,
                            ((A << k) | psid) << m | j_max))

    return port_ranges


for i in map_port_ranges(52, 8, 6):
    print '{0}, {1}'.format(*i)
