# Copyright (c) 2020 Cisco and/or its affiliates.
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

"""Module defining utilities for clasifying different kinds of suites.

Each classifying function takes one argument,
in general it could be a file name, suite id or suite tag.
"""

# Keep the functions ordered alphabetically, please.

def is_suite_bps(name):
    """Return true iff the name belongs to a BPS suite (including quic).

    BPS suites are a subtype of hoststack suites,
    they use a particular testcase template.

    :param name: Identifier of the suite (file name, suite id or suite tag).
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    return u"-ldpreload-" in name or "-vppecho-" in name

def is_suite_dpdk(name):
    """Return true iff the name belongs to a DPDK (not VPP) suite.

    DPDK suites do not support different NIC drivers.

    :param name: Identifier of the suite (file name, suite id or suite tag).
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    # Looking for "| DPDK" in prolog is more reliable,
    # but for now classifying just from name is better, even if brittle.
    return u"l2xcbase-testpmd" in name or u"ip4base-l3fwd" in name

def is_suite_hoststack(name):
    """Return true iff the name belongs to a hoststack suite.

    Hoststack suites use testcase templates different from throughput ones.

    :param name: Identifier of the suite.
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    return is_suite_bps(name) or is_suite_http(name)

def is_suite_http(name):
    """Return true iff the name belongs to a HTTP suite.

    HTTP suites use a subtype of hoststack suites,
    they use a particular testcase template.

    :param name: Identifier of the suite (file name, suite id or suite tag).
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    return u"http-wrk" in name

def is_suite_ndrpdr(name):
    """Return true iff the name belongs to a ndrpdr suite.

    Mrr and soak suites have to be generated from ndrpdr suites,
    but ndrpdr suites are valid input.

    Name cannot be a suite tag, as that does not differ regularly enough
    from reconf suite tags.

    :param name: Identifier of the suite (file name or suite id).
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    return u"-ndrpdr" in name

def is_suite_quic(name):
    """Return true iff the name belongs to a quick suite.

    Quic suites are a subtype of BPS suites,
    they use particular testcase argument values.

    :param name: Identifier of the suite (file name, suite id or suite tag).
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    return u"udpquic" in name

def is_suite_reconf(name):
    """Return true iff the name belongs to a reconf suite.

    Reconf suites have content so different from ndrpdr suites
    that they cannot be generated from them (nor vice versa).

    Name cannot be a suite tag, as that does not differ regularly enough
    from ndrpdr suite tags.

    :param name: Identifier of the suite (file name or suite id).
    :type name: str
    :returns: Whether the suite is DPDK.
    :rtype: bool
    """
    return u"-reconf" in name

# Keep the functions ordered alphabetically, please.
