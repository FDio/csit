# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <https://www.gnu.org/licenses/>.

"""
This module define some constants.
"""

class SFCConstants(object):
    """
    Define some constants for the test filed verify.
    """

    DEF_SRC_PORT = 1234
    DEF_DST_PORT = 5678
    UDP_PROTOCOL = 17
    VxLAN_UDP_PORT = 4789
    VxLANGPE_UDP_PORT = 4790
    VxLAN_FLAGS = 0x8
    VxLAN_DEFAULT_VNI = 1
    VxLANGPE_FLAGS = 0xc
    VxLANGPE_NEXT_PROTOCOL = 0x4
    VxLANGPE_DEFAULT_VNI = 9
    NSH_HEADER_LENGTH = 0x6
    NSH_DEFAULT_MDTYPE = 0x1
    NSH_NEXT_PROTOCOL = 0x3
    NSH_DEFAULT_NSP = 185
    NSH_DEFAULT_NSI = 255
    NSH_DEFAULT_C1 = 3232248395
    NSH_DEFAULT_C2 = 9
    NSH_DEFAULT_C3 = 3232248392
    NSH_DEFAULT_C4 = 50336437
