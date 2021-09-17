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

"""Module defining utilities creating kwargs for test case generation.

All functions have the same signature, so call sites can me more similar,
even though not all functions actually require all arguments.
"""

from resources.libraries.python.Constants import Constants


# Protocol aware tests.

def default_kwargs(protocol):
    """Return list of kwargs suitable for most performance tests.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    min_frame_size = Constants.PROTOCOL_TO_MIN_FRAME_SIZE[protocol]
    return [
        {u"frame_size": min_frame_size, u"phy_cores": 1},
        {u"frame_size": min_frame_size, u"phy_cores": 2},
        {u"frame_size": min_frame_size, u"phy_cores": 4},
        {u"frame_size": 1518, u"phy_cores": 1},
        {u"frame_size": 1518, u"phy_cores": 2},
        {u"frame_size": 1518, u"phy_cores": 4},
        {u"frame_size": 9000, u"phy_cores": 1},
        {u"frame_size": 9000, u"phy_cores": 2},
        {u"frame_size": 9000, u"phy_cores": 4},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 1},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 2},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 4},
    ]

def device_kwargs(protocol):
    """Return list of kwargs suitable for device tests.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    min_frame_size = Constants.PROTOCOL_TO_MIN_FRAME_SIZE[protocol]
    return [
        {u"frame_size": min_frame_size, u"phy_cores": 0}
    ]

def dp1_kwargs(protocol):
    """Return list of kwargs suitable for one dataplane core tests.

    Some tests (ipsec async scheduler) haw two kinds of workers.
    This list makes space for one dataplane worker
    and one or more feature workers.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    min_frame_size = Constants.PROTOCOL_TO_MIN_FRAME_SIZE[protocol]
    return [
        {u"frame_size": min_frame_size, u"phy_cores": 2},
        {u"frame_size": min_frame_size, u"phy_cores": 3},
        {u"frame_size": min_frame_size, u"phy_cores": 4},
        {u"frame_size": 1518, u"phy_cores": 2},
        {u"frame_size": 1518, u"phy_cores": 3},
        {u"frame_size": 1518, u"phy_cores": 4},
        {u"frame_size": 9000, u"phy_cores": 2},
        {u"frame_size": 9000, u"phy_cores": 3},
        {u"frame_size": 9000, u"phy_cores": 4},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 2},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 3},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 4},
    ]

def trex_kwargs(protocol):
    """Return list of kwargs suitable for stateless TG tests.

    The phy_cores field is ignored (TG tests have no DUT to use cores),
    but is kept here to simplify the interface.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    min_frame_size = Constants.PROTOCOL_TO_MIN_FRAME_SIZE[protocol]
    return [
        {u"frame_size": min_frame_size, u"phy_cores": 0},
        {u"frame_size": 1518, u"phy_cores": 0},
        {u"frame_size": 9000, u"phy_cores": 0},
        {u"frame_size": u"IMIX_v4_1", u"phy_cores": 0},
    ]

# TCP based tests, the protocol value is ignored.

def hs_bps_kwargs(protocol):
    """Return list of kwargs suitable for hoststack bps tests.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    return [
        {u"frame_size": 1460, u"phy_cores": 1},
    ]

def hs_quic_kwargs(protocol):
    """Return list of kwargs suitable for hoststack quic tests.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    return [
        {u"frame_size": 1280, u"phy_cores": 1},
    ]

def http_kwargs(protocol):
    """Return list of kwargs suitable for http tests.

    TODO: Distinguish better from other hoststack tests.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    return [
        {u"frame_size": 0, u"phy_cores": 1},
        {u"frame_size": 0, u"phy_cores": 2},
        {u"frame_size": 64, u"phy_cores": 1},
        {u"frame_size": 64, u"phy_cores": 2},
        {u"frame_size": 1024, u"phy_cores": 1},
        {u"frame_size": 1024, u"phy_cores": 2},
        {u"frame_size": 2048, u"phy_cores": 1},
        {u"frame_size": 2048, u"phy_cores": 2},
    ]

def iperf3_kwargs(protocol):
    """Return list of kwargs suitable for iperf3 tests.

    :param protocol: String determining minimal frame size.
    :type protocol: str
    :returns: Kwargs to use.
    :rtype: List of dicts, each with "frame_size" and "phy_cores" keys.
    """
    return [
        {u"frame_size": 128000, u"phy_cores": 1},
        {u"frame_size": 128000, u"phy_cores": 2},
        {u"frame_size": 128000, u"phy_cores": 4},
    ]
