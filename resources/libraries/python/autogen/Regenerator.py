# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Module defining utilities for test directory regeneration."""

import sys

from glob import glob
from io import open
from os import getcwd


from resources.libraries.python.Constants import Constants
from resources.libraries.python.autogen.Testcase import Testcase


PROTOCOL_TO_MIN_FRAME_SIZE = {
    u"ip4": 64,
    u"ip6": 78,
    u"ethip4vxlan": 114,  # What is the real minimum for latency stream?
    u"dot1qip4vxlan": 118
}
MIN_FRAME_SIZE_VALUES = list(PROTOCOL_TO_MIN_FRAME_SIZE.values())


def replace_defensively(
        whole, to_replace, replace_with, how_many, msg, in_filename):
    """Replace substrings while checking the number of occurrences.

    Return edited copy of the text. Assuming "whole" is really a string,
    or something else with .replace not affecting it.

    :param whole: The text to perform replacements on.
    :param to_replace: Substring occurrences of which to replace.
    :param replace_with: Substring to replace occurrences with.
    :param how_many: Number of occurrences to expect.
    :param msg: Error message to raise.
    :param in_filename: File name in which the error occurred.
    :type whole: str
    :type to_replace: str
    :type replace_with: str
    :type how_many: int
    :type msg: str
    :type in_filename: str
    :return: The whole text after replacements are done.
    :rtype: str
    :raise ValueError: If number of occurrences does not match.
    """
    found = whole.count(to_replace)
    if found != how_many:
        raise ValueError(f"{in_filename}: {msg}")
    return whole.replace(to_replace, replace_with)


def get_iface_and_suite_id(filename):
    """Get interface and suite ID.

    Interface ID is the part of suite name
    which should be replaced for other NIC.
    Suite ID is the part os suite name
    which si appended to test case names.

    :param filename: Suite file.
    :type filename: str
    :returns: Interface ID, Suite ID.
    :rtype: (str, str)
    """
    dash_split = filename.split(u"-", 1)
    if len(dash_split[0]) <= 4:
        # It was something like "2n1l", we need one more split.
        dash_split = dash_split[1].split(u"-", 1)
    return dash_split[0], dash_split[1].split(u".", 1)[0]


def add_default_testcases(testcase, iface, suite_id, file_out, tc_kwargs_list):
    """Add default testcases to file.

    :param testcase: Testcase class.
    :param iface: Interface.
    :param suite_id: Suite ID.
    :param file_out: File to write testcases to.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type iface: str
    :type suite_id: str
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    # We bump tc number in any case, so that future enables/disables
    # do not affect the numbering of other test cases.
    for num, kwargs in enumerate(tc_kwargs_list, start=1):
        # TODO: Is there a better way to disable some combinations?
        emit = True
        if kwargs[u"frame_size"] == 9000:
            if u"vic1227" in iface:
                # Not supported in HW.
                emit = False
            if u"vic1385" in iface:
                # Not supported in HW.
                emit = False
            if u"ipsec" in suite_id:
                # IPsec code does not support chained buffers.
                # Tracked by Jira ticket VPP-1207.
                emit = False
        if u"-16vm2t-" in suite_id or u"-16dcr2t-" in suite_id:
            if kwargs[u"phy_cores"] > 3:
                # CSIT lab only has 28 (physical) core processors,
                # so these test would fail when attempting to assign cores.
                emit = False
        if u"-24vm1t-" in suite_id or u"-24dcr1t-" in suite_id:
            if kwargs[u"phy_cores"] > 3:
                # CSIT lab only has 28 (physical) core processors,
                # so these test would fail when attempting to assign cores.
                emit = False
        if u"soak" in suite_id:
            # Soak test take too long, do not risk other than tc01.
            if kwargs[u"phy_cores"] != 1:
                emit = False
            if kwargs[u"frame_size"] not in MIN_FRAME_SIZE_VALUES:
                emit = False
        if emit:
            file_out.write(testcase.generate(num=num, **kwargs))


def add_tcp_testcases(testcase, file_out, tc_kwargs_list):
    """Add TCP testcases to file.

    :param testcase: Testcase class.
    :param file_out: File to write testcases to.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    for num, kwargs in enumerate(tc_kwargs_list, start=1):
        file_out.write(testcase.generate(num=num, **kwargs))


def write_default_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated suites.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_default_testcase.
    :type in_filename: str
    :type in_prolog: str
    :type kwargs_list: list of dict
    """
    for suite_type in Constants.PERF_TYPE_TO_KEYWORD:
        tmp_filename = replace_defensively(
            in_filename, u"ndrpdr", suite_type, 1,
            u"File name should contain suite type once.", in_filename
        )
        tmp_prolog = replace_defensively(
            in_prolog, u"ndrpdr".upper(), suite_type.upper(), 1,
            u"Suite type should appear once in uppercase (as tag).",
            in_filename
        )
        tmp_prolog = replace_defensively(
            tmp_prolog,
            u"Find NDR and PDR intervals using optimized search",
            Constants.PERF_TYPE_TO_KEYWORD[suite_type], 1,
            u"Main search keyword should appear once in suite.",
            in_filename
        )
        tmp_prolog = replace_defensively(
            tmp_prolog,
            Constants.PERF_TYPE_TO_SUITE_DOC_VER[u"ndrpdr"],
            Constants.PERF_TYPE_TO_SUITE_DOC_VER[suite_type],
            1, u"Exact suite type doc not found.", in_filename
        )
        tmp_prolog = replace_defensively(
            tmp_prolog,
            Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER[u"ndrpdr"],
            Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER[suite_type],
            1, u"Exact template type doc not found.", in_filename
        )
        _, suite_id = get_iface_and_suite_id(tmp_filename)
        testcase = Testcase.default(suite_id)
        for nic_name in Constants.NIC_NAME_TO_CODE:
            tmp2_filename = replace_defensively(
                tmp_filename, u"10ge2p1x710",
                Constants.NIC_NAME_TO_CODE[nic_name], 1,
                u"File name should contain NIC code once.", in_filename)
            tmp2_prolog = replace_defensively(
                tmp_prolog, u"Intel-X710", nic_name, 2,
                u"NIC name should appear twice (tag and variable).",
                in_filename)
            if tmp2_prolog.count(u"HW_") == 2:
                # TODO CSIT-1481: Crypto HW should be read
                # from topology file instead.
                if nic_name in Constants.NIC_NAME_TO_CRYPTO_HW:
                    tmp2_prolog = replace_defensively(
                        tmp2_prolog, u"HW_DH895xcc",
                        Constants.NIC_NAME_TO_CRYPTO_HW[nic_name], 1,
                        u"HW crypto name should appear.", in_filename)
            iface, old_suite_id = get_iface_and_suite_id(tmp2_filename)
            if u"DPDK" in in_prolog:
                with open(tmp2_filename, u"wt") as file_out:
                    file_out.write(tmp2_prolog)
                    add_default_testcases(
                        testcase, iface, old_suite_id, file_out, kwargs_list)
                return
            for driver in Constants.NIC_NAME_TO_DRIVER[nic_name]:
                out_filename = replace_defensively(
                    tmp2_filename, old_suite_id,
                    Constants.NIC_DRIVER_TO_SUITE_PREFIX[driver] + old_suite_id,
                    1, u"Error adding driver prefix.", in_filename)
                out_prolog = replace_defensively(
                    tmp2_prolog, u"vfio-pci", driver, 1,
                    u"Driver name should appear once.", in_filename)
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_TAG[u"vfio-pci"],
                    Constants.NIC_DRIVER_TO_TAG[driver], 1,
                    u"Driver tag should appear once.", in_filename)
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_PLUGINS[u"vfio-pci"],
                    Constants.NIC_DRIVER_TO_PLUGINS[driver], 1,
                    u"Driver plugin should appear once.", in_filename)
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_SETUP_ARG[u"vfio-pci"],
                    Constants.NIC_DRIVER_TO_SETUP_ARG[driver], 1,
                    u"Perf setup argument should appear once.", in_filename)
                iface, suite_id = get_iface_and_suite_id(out_filename)
                # TODO: Reorder loops so suite_id is finalized sooner.
                testcase = Testcase.default(suite_id)
                with open(out_filename, u"wt") as file_out:
                    file_out.write(out_prolog)
                    add_default_testcases(
                        testcase, iface, suite_id, file_out, kwargs_list)


def write_reconf_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated reconf suites.

    Use this for suite type reconf, as its local template
    is incompatible with mrr/ndrpdr/soak local template,
    while test cases are compatible.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_testcase.
    :type in_filename: str
    :type in_prolog: str
    :type kwargs_list: list of dict
    """
    _, suite_id = get_iface_and_suite_id(in_filename)
    testcase = Testcase.default(suite_id)
    for nic_name in Constants.NIC_NAME_TO_CODE:
        tmp_filename = replace_defensively(
            in_filename, u"10ge2p1x710",
            Constants.NIC_NAME_TO_CODE[nic_name], 1,
            u"File name should contain NIC code once.", in_filename)
        tmp_prolog = replace_defensively(
            in_prolog, u"Intel-X710", nic_name, 2,
            u"NIC name should appear twice (tag and variable).",
            in_filename)
        if tmp_prolog.count(u"HW_") == 2:
            # TODO CSIT-1481: Crypto HW should be read
            # from topology file instead.
            if nic_name in Constants.NIC_NAME_TO_CRYPTO_HW.keys():
                tmp_prolog = replace_defensively(
                    tmp_prolog, u"HW_DH895xcc",
                    Constants.NIC_NAME_TO_CRYPTO_HW[nic_name], 1,
                    u"HW crypto name should appear.", in_filename)
        iface, old_suite_id = get_iface_and_suite_id(tmp_filename)
        for driver in Constants.NIC_NAME_TO_DRIVER[nic_name]:
            out_filename = replace_defensively(
                tmp_filename, old_suite_id,
                Constants.NIC_DRIVER_TO_SUITE_PREFIX[driver] + old_suite_id,
                1, u"Error adding driver prefix.", in_filename)
            out_prolog = replace_defensively(
                tmp_prolog, u"vfio-pci", driver, 1,
                u"Driver name should appear once.", in_filename)
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_TAG[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_TAG[driver], 1,
                u"Driver tag should appear once.", in_filename)
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_PLUGINS[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_PLUGINS[driver], 1,
                u"Driver plugin should appear once.", in_filename)
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_SETUP_ARG[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_SETUP_ARG[driver], 1,
                u"Perf setup argument should appear once.", in_filename)
            iface, suite_id = get_iface_and_suite_id(out_filename)
            # TODO: Reorder loops so suite_id is finalized sooner.
            testcase = Testcase.default(suite_id)
            with open(out_filename, u"wt") as file_out:
                file_out.write(out_prolog)
                add_default_testcases(
                    testcase, iface, suite_id, file_out, kwargs_list)


def write_tcp_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated tcp suites.

    TODO: Suport drivers.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_default_testcase.
    :type in_filename: str
    :type in_prolog: str
    :type kwargs_list: list of dict
    """
    # TODO: Generate rps from cps? There are subtle differences.
    _, suite_id = get_iface_and_suite_id(in_filename)
    testcase = Testcase.tcp(suite_id)
    for nic_name in Constants.NIC_NAME_TO_CODE:
        out_filename = replace_defensively(
            in_filename, u"10ge2p1x710",
            Constants.NIC_NAME_TO_CODE[nic_name], 1,
            u"File name should contain NIC code once.", in_filename
        )
        out_prolog = replace_defensively(
            in_prolog, u"Intel-X710", nic_name, 2,
            u"NIC name should appear twice (tag and variable).",
            in_filename
        )
        with open(out_filename, u"wt") as file_out:
            file_out.write(out_prolog)
            add_tcp_testcases(testcase, file_out, kwargs_list)


class Regenerator:
    """Class containing file generating methods."""

    def __init__(self, quiet=True):
        """Initialize the instance.

        :param quiet: Reduce log prints (to stderr) when True (default).
        :type quiet: boolean
        """
        self.quiet = quiet

    def regenerate_glob(self, pattern, protocol=u"ip4"):
        """Regenerate files matching glob pattern based on arguments.

        In the current working directory, find all files matching
        the glob pattern. Use testcase template to regenerate test cases
        according to suffix, governed by protocol, autonumbering them.
        Also generate suites for other NICs and drivers.

        Log-like prints are emitted to sys.stderr.

        :param pattern: Glob pattern to select files. Example: *-ndrpdr.robot
        :param protocol: String determining minimal frame size. Default: "ip4"
        :type pattern: str
        :type protocol: str
        :raises RuntimeError: If invalid source suite is encountered.
        """
        if not self.quiet:
            print(f"Regenerator starts at {getcwd()}", file=sys.stderr)

        min_frame_size = PROTOCOL_TO_MIN_FRAME_SIZE[protocol]
        default_kwargs_list = [
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
            {u"frame_size": u"IMIX_v4_1", u"phy_cores": 4}
        ]
        tcp_kwargs_list = [
            {u"phy_cores": i, u"frame_size": 0} for i in (1, 2, 4)
        ]
        forbidden = [v for v in Constants.NIC_DRIVER_TO_SUITE_PREFIX.values()
                     if v]
        for in_filename in glob(pattern):
            if not self.quiet:
                print(
                    u"Regenerating in_filename:", in_filename, file=sys.stderr
                )
            iface, _ = get_iface_and_suite_id(in_filename)
            if not iface.endswith(u"10ge2p1x710"):
                raise RuntimeError(
                    f"Error in {in_filename}: non-primary NIC found.")
            for prefix in forbidden:
                if prefix in in_filename:
                    raise RuntimeError(
                        f"Error in {in_filename}: non-primary driver found.")
            with open(in_filename, u"rt") as file_in:
                in_prolog = u"".join(
                    file_in.read().partition(u"*** Test Cases ***")[:-1])
            if in_filename.endswith(u"-ndrpdr.robot"):
                write_default_files(in_filename, in_prolog, default_kwargs_list)
            elif in_filename.endswith(u"-reconf.robot"):
                write_reconf_files(in_filename, in_prolog, default_kwargs_list)
            elif in_filename[-10:] in (u"-cps.robot", u"-rps.robot"):
                write_tcp_files(in_filename, in_prolog, tcp_kwargs_list)
            else:
                raise RuntimeError(
                    f"Error in {in_filename}: non-primary suite type found."
                )
        if not self.quiet:
            print(u"Regenerator ends.", file=sys.stderr)
        print(file=sys.stderr)  # To make autogen check output more readable.
