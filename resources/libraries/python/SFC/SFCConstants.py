#!/usr/bin/env python
# Copyright (c) 2017 Cisco and/or its affiliates.
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
    NSH_FLAGS = 0x0
    NSH_HEADER_LENGTH = 0x6
    NSH_DEFAULT_MDTYPE = 0x1
    NSH_NEXT_PROTOCOL = 0x3
    NSH_DEFAULT_NSP = 185
    NSH_DEFAULT_NSI = 255
    NSH_DEFAULT_C1 = 3232248395
    NSH_DEFAULT_C2 = 9
    NSH_DEFAULT_C3 = 3232248392
    NSH_DEFAULT_C4 = 50336437
