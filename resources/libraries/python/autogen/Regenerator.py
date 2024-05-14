# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Module defining utilities for test directory regeneration.

TODO: How can we check each suite id is unique,
      when currently the suite generation is run on each directory separately?
"""

import copy
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
    :returns: The whole text after replacements are done.
    :rtype: str
    :raises ValueError: If number of occurrences does not match.
    """
    found = whole.count(to_replace)
    if found != how_many:
        raise ValueError(f"{in_filename}: {msg}")
    return whole.replace(to_replace, replace_with)


def get_iface_and_suite_ids(filename):
    """Get NIC code, suite ID and suite tag.

    NIC code is the part of suite name
    which should be replaced for other NIC.
    Suite ID is the part os suite name
    which is appended to test case names.
    Suite tag is suite ID without both test type and NIC driver parts.

    :param filename: Suite file.
    :type filename: str
    :returns: NIC code, suite ID, suite tag.
    :rtype: 3-tuple of str
    """
    dash_split = filename.split(u"-", 1)
    if len(dash_split[0]) <= 4:
        # It was something like "2n1l", we need one more split.
        dash_split = dash_split[1].split(u"-", 1)
    nic_code = dash_split[0]
    suite_id = dash_split[1].split(u".robot", 1)[0]
    suite_tag = suite_id.rsplit(u"-", 1)[0]
    for prefix in Constants.FORBIDDEN_SUITE_PREFIX_LIST:
        if suite_tag.startswith(prefix):
            suite_tag = suite_tag[len(prefix):]
    return nic_code, suite_id, suite_tag


def check_suite_tag(suite_tag, prolog):
    """Verify suite tag occurres once in prolog.

    Call this after all edits are done,
    to confirm the (edited) suite tag still matches the (edited) suite name.

    Currently, the edited suite tag is expect to be identical
    to the primary suite tag, but having a function is more flexible.

    The occurences are counted including "| " prefix,
    to lower the chance to match a comment.

    :param suite_tag: Part of suite name, between NIC driver and suite type.
    :param prolog: The part of .robot file content without test cases.
    :type suite_tag: str
    :type prolog: str
    :raises ValueError: If suite_tag not found exactly once.
    """
    found = prolog.count(u"| " + suite_tag)
    if found != 1:
        raise ValueError(f"Suite tag found {found} times for {suite_tag}")


def filter_and_edit_kwargs_for_astf(suite_id, kwargs):
    """Return possibly edited kwargs, or None if to be skipped.

    This is a code block used in few places.
    Kwargs is (a copy of) one item from tc_kwargs_list.
    Currently, the editable field is frame_size,
    to be increased to for tests with data (not just CPS).

    :param suite_id: Suite ID.
    :param kwargs: Key-value pairs used to construct one testcase.
    :type suite_id: str
    :type tc_kwargs_list: dict
    :returns: Edited kwargs.
    :rtype Optional[dict]
    """
    if u"-cps-" in suite_id:
        # Contrary to UDP, there is no place to affect frame size
        # in TCP CPS tests. Actual frames are close to min size.
        # UDP uses the min value too, for fairer comparison to TCP.
        if kwargs[u"frame_size"] not in MIN_FRAME_SIZE_VALUES:
            return None
    elif (u"-pps-" in suite_id or u"-tput-" in suite_id):
        if u"imix" in str(kwargs[u"frame_size"]).lower():
            # ASTF does not support IMIX (yet).
            return None
        if kwargs[u"frame_size"] in MIN_FRAME_SIZE_VALUES:
            # Minimal (TRex) TCP data frame is 80B for IPv4.
            # In future, we may want to have also IPv6 TCP.
            # UDP uses the same value, for fairer comparison to TCP.
            kwargs[u"frame_size"] = 100
    return kwargs


def add_default_testcases(
        testcase, nic_code, suite_id, file_out, tc_kwargs_list):
    """Add default testcases to file.

    :param testcase: Testcase class.
    :param nic_code: NIC code.
    :param suite_id: Suite ID.
    :param file_out: File to write testcases to.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type nic_code: str
    :type suite_id: str
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    for kwas in tc_kwargs_list:
        # We may edit framesize for ASTF, the copy should be local.
        kwargs = copy.deepcopy(kwas)
        # TODO: Is there a better way to disable some combinations?
        emit = True
        core_scale = Constants.NIC_CODE_TO_CORESCALE[nic_code]
        if u"soak" in suite_id:
            # Soak test take too long, do not risk other than tc01.
            if kwargs[u"phy_cores"] != 1:
                emit = False
            if u"reassembly" in suite_id:
                if kwargs[u"frame_size"] != 1518:
                    emit = False
            else:
                if kwargs[u"frame_size"] not in MIN_FRAME_SIZE_VALUES:
                    emit = False

        kwargs.update({'phy_cores': kwas['phy_cores']*core_scale})

        kwargs = filter_and_edit_kwargs_for_astf(suite_id, kwargs)
        if emit and kwargs is not None:
            file_out.write(testcase.generate(**kwargs))


def add_tcp_testcases(testcase, file_out, tc_kwargs_list):
    """Add TCP testcases to file.

    :param testcase: Testcase class.
    :param file_out: File to write testcases to.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    for kwargs in tc_kwargs_list:
        file_out.write(testcase.generate(**kwargs))


def add_iperf3_testcases(testcase, file_out, tc_kwargs_list):
    """Add iperf3 testcases to file.

    :param testcase: Testcase class.
    :param file_out: File to write testcases to.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    for kwargs in tc_kwargs_list:
        file_out.write(testcase.generate(**kwargs))


def add_trex_testcases(testcase, suite_id, file_out, tc_kwargs_list):
    """Add trex testcases to file.

    :param testcase: Testcase class.
    :param suite_id: Suite ID.
    :param file_out: File to write testcases to.
    :param tc_kwargs_list: Key-value pairs used to construct testcases.
    :type testcase: Testcase
    :type suite_id: str
    :type file_out: file
    :type tc_kwargs_list: dict
    """
    for kwas in tc_kwargs_list:
        # We may edit framesize for ASTF, the copy should be local.
        kwargs = copy.deepcopy(kwas)
        kwargs = filter_and_edit_kwargs_for_astf(suite_id, kwargs)
        if kwargs is not None:
            file_out.write(testcase.generate(**kwargs))


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
            in_filename, "ndrpdr", suite_type, 1,
            "File name should contain suite type once.", in_filename
        )
        tmp_prolog = replace_defensively(
            in_prolog, "ndrpdr".upper(), suite_type.upper(), 1,
            "Suite type should appear once in uppercase (as tag).",
            in_filename
        )
        tmp_prolog = replace_defensively(
            tmp_prolog,
            "Find NDR and PDR intervals using optimized search",
            Constants.PERF_TYPE_TO_KEYWORD[suite_type], 1,
            "Main search keyword should appear once in suite.",
            in_filename
        )
        tmp_prolog = replace_defensively(
            tmp_prolog,
            Constants.PERF_TYPE_TO_SUITE_DOC_VER["ndrpdr"],
            Constants.PERF_TYPE_TO_SUITE_DOC_VER[suite_type],
            1, "Exact suite type doc not found.", in_filename
        )
        tmp_prolog = replace_defensively(
            tmp_prolog,
            Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER["ndrpdr"],
            Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER[suite_type],
            1, "Exact template type doc not found.", in_filename
        )
        _, suite_id, _ = get_iface_and_suite_ids(tmp_filename)
        testcase = Testcase.default(suite_id)
        for nic_code in Constants.NIC_CODE_TO_NAME:
            nic_name = Constants.NIC_CODE_TO_NAME[nic_code]
            tmp2_filename = replace_defensively(
                tmp_filename, "10ge2p1x710", nic_code, 1,
                "File name should contain NIC code once.", in_filename
            )
            tmp2_prolog = replace_defensively(
                tmp_prolog, "Intel-X710", nic_name, 2,
                "NIC name should appear twice (tag and variable).",
                in_filename
            )
            if tmp2_prolog.count("HW_") == 2:
                # TODO CSIT-1481: Crypto HW should be read
                #      from topology file instead.
                if nic_name in Constants.NIC_NAME_TO_CRYPTO_HW:
                    tmp2_prolog = replace_defensively(
                        tmp2_prolog, "HW_DH895xcc",
                        Constants.NIC_NAME_TO_CRYPTO_HW[nic_name], 1,
                        "HW crypto name should appear.", in_filename
                    )
            iface, old_suite_id, old_suite_tag = get_iface_and_suite_ids(
                tmp2_filename
            )
            if "DPDK" in in_prolog:
                for driver in Constants.DPDK_NIC_NAME_TO_DRIVER[nic_name]:
                    out_filename = replace_defensively(
                        tmp2_filename, old_suite_id,
                        Constants.DPDK_NIC_DRIVER_TO_SUITE_PREFIX[driver] \
                            + old_suite_id,
                        1, "Error adding driver prefix.", in_filename
                    )
                    out_prolog = replace_defensively(
                        tmp2_prolog, "vfio-pci", driver, 1,
                        "Driver name should appear once.", in_filename
                    )
                    out_prolog = replace_defensively(
                        out_prolog,
                        Constants.DPDK_NIC_DRIVER_TO_TAG["vfio-pci"],
                        Constants.DPDK_NIC_DRIVER_TO_TAG[driver], 1,
                        "Driver tag should appear once.", in_filename
                    )
                    iface, suite_id, suite_tag = get_iface_and_suite_ids(
                        out_filename
                    )
                    # The next replace is probably a noop, but it is safer to
                    # maintain the same structure as for other edits.
                    out_prolog = replace_defensively(
                        out_prolog, old_suite_tag, suite_tag, 1,
                        f"Perf suite tag {old_suite_tag} should appear once.",
                        in_filename
                    )
                    check_suite_tag(suite_tag, out_prolog)
                    # TODO: Reorder loops so suite_id is finalized sooner.
                    testcase = Testcase.default(suite_id)
                    with open(out_filename, "wt") as file_out:
                        file_out.write(out_prolog)
                        add_default_testcases(
                            testcase, nic_code, suite_id, file_out, kwargs_list
                        )
                continue
            for driver in Constants.NIC_NAME_TO_DRIVER[nic_name]:
                out_filename = replace_defensively(
                    tmp2_filename, old_suite_id,
                    Constants.NIC_DRIVER_TO_SUITE_PREFIX[driver] + old_suite_id,
                    1, "Error adding driver prefix.", in_filename
                )
                out_prolog = replace_defensively(
                    tmp2_prolog, "vfio-pci", driver, 1,
                    "Driver name should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_TAG["vfio-pci"],
                    Constants.NIC_DRIVER_TO_TAG[driver], 1,
                    "Driver tag should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_PLUGINS["vfio-pci"],
                    Constants.NIC_DRIVER_TO_PLUGINS[driver], 1,
                    "Driver plugin should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_VFS["vfio-pci"],
                    Constants.NIC_DRIVER_TO_VFS[driver], 1,
                    "NIC VFs argument should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_CODE_TO_PFS["10ge2p1x710"],
                    Constants.NIC_CODE_TO_PFS[nic_code], 1,
                    "NIC PFs argument should appear once.", in_filename
                )
                iface, suite_id, suite_tag = get_iface_and_suite_ids(
                    out_filename
                )
                # The next replace is probably a noop, but it is safer to
                # maintain the same structure as for other edits.
                out_prolog = replace_defensively(
                    out_prolog, old_suite_tag, suite_tag, 1,
                    f"Perf suite tag {old_suite_tag} should appear once.",
                    in_filename
                )
                check_suite_tag(suite_tag, out_prolog)
                # TODO: Reorder loops so suite_id is finalized sooner.
                testcase = Testcase.default(suite_id)
                with open(out_filename, "wt") as file_out:
                    file_out.write(out_prolog)
                    add_default_testcases(
                        testcase, nic_code, suite_id, file_out, kwargs_list
                    )


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
    _, suite_id, _ = get_iface_and_suite_ids(in_filename)
    testcase = Testcase.default(suite_id)
    for nic_code in Constants.NIC_CODE_TO_NAME:
        nic_name = Constants.NIC_CODE_TO_NAME[nic_code]
        tmp_filename = replace_defensively(
            in_filename, u"10ge2p1x710", nic_code, 1,
            u"File name should contain NIC code once.", in_filename
        )
        tmp_prolog = replace_defensively(
            in_prolog, u"Intel-X710", nic_name, 2,
            u"NIC name should appear twice (tag and variable).",
            in_filename
        )
        if tmp_prolog.count(u"HW_") == 2:
            # TODO CSIT-1481: Crypto HW should be read
            #      from topology file instead.
            if nic_name in Constants.NIC_NAME_TO_CRYPTO_HW.keys():
                tmp_prolog = replace_defensively(
                    tmp_prolog, u"HW_DH895xcc",
                    Constants.NIC_NAME_TO_CRYPTO_HW[nic_name], 1,
                    u"HW crypto name should appear.", in_filename
                )
        iface, old_suite_id, old_suite_tag = get_iface_and_suite_ids(
            tmp_filename
        )
        for driver in Constants.NIC_NAME_TO_DRIVER[nic_name]:
            out_filename = replace_defensively(
                tmp_filename, old_suite_id,
                Constants.NIC_DRIVER_TO_SUITE_PREFIX[driver] + old_suite_id,
                1, u"Error adding driver prefix.", in_filename
            )
            out_prolog = replace_defensively(
                tmp_prolog, u"vfio-pci", driver, 1,
                u"Driver name should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_TAG[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_TAG[driver], 1,
                u"Driver tag should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_PLUGINS[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_PLUGINS[driver], 1,
                u"Driver plugin should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_VFS[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_VFS[driver], 1,
                u"NIC VFs argument should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_CODE_TO_PFS["10ge2p1x710"],
                Constants.NIC_CODE_TO_PFS[nic_code], 1,
                "NIC PFs argument should appear once.", in_filename
            )
            iface, suite_id, suite_tag = get_iface_and_suite_ids(out_filename)
            out_prolog = replace_defensively(
                out_prolog, old_suite_tag, suite_tag, 1,
                u"Perf suite tag should appear once.", in_filename
            )
            check_suite_tag(suite_tag, out_prolog)
            # TODO: Reorder loops so suite_id is finalized sooner.
            testcase = Testcase.default(suite_id)
            with open(out_filename, u"wt") as file_out:
                file_out.write(out_prolog)
                add_default_testcases(
                    testcase, iface, suite_id, file_out, kwargs_list
                )


def write_tcp_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated tcp suites.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_default_testcase.
    :type in_filename: str
    :type in_prolog: str
    :type kwargs_list: list of dict
    """
    # TODO: Generate rps from cps? There are subtle differences.
    _, suite_id, suite_tag = get_iface_and_suite_ids(in_filename)
    testcase = Testcase.tcp(suite_id)
    for nic_code in Constants.NIC_CODE_TO_NAME:
        nic_name = Constants.NIC_CODE_TO_NAME[nic_code]
        tmp_filename = replace_defensively(
            in_filename, u"10ge2p1x710", nic_code, 1,
            u"File name should contain NIC code once.", in_filename
        )
        tmp_prolog = replace_defensively(
            in_prolog, u"Intel-X710", nic_name, 2,
            u"NIC name should appear twice (tag and variable).",
            in_filename
        )
        iface, old_suite_id, old_suite_tag = get_iface_and_suite_ids(
            tmp_filename
        )
        for driver in Constants.NIC_NAME_TO_DRIVER[nic_name]:
            out_filename = replace_defensively(
                tmp_filename, old_suite_id,
                Constants.NIC_DRIVER_TO_SUITE_PREFIX[driver] + old_suite_id,
                1, u"Error adding driver prefix.", in_filename
            )
            out_prolog = replace_defensively(
                tmp_prolog, u"vfio-pci", driver, 1,
                u"Driver name should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_TAG[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_TAG[driver], 1,
                u"Driver tag should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_PLUGINS[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_PLUGINS[driver], 1,
                u"Driver plugin should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_DRIVER_TO_VFS[u"vfio-pci"],
                Constants.NIC_DRIVER_TO_VFS[driver], 1,
                u"NIC VFs argument should appear once.", in_filename
            )
            out_prolog = replace_defensively(
                out_prolog, Constants.NIC_CODE_TO_PFS["10ge2p1x710"],
                Constants.NIC_CODE_TO_PFS[nic_code], 1,
                "NIC PFs argument should appear once.", in_filename
            )
            iface, suite_id, suite_tag = get_iface_and_suite_ids(out_filename)
            out_prolog = replace_defensively(
                out_prolog, old_suite_tag, suite_tag, 1,
                u"Perf suite tag should appear once.", in_filename
            )
            check_suite_tag(suite_tag, out_prolog)
            testcase = Testcase.tcp(suite_id)
            with open(out_filename, u"wt") as file_out:
                file_out.write(out_prolog)
                add_tcp_testcases(testcase, file_out, kwargs_list)


def write_iperf3_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated iperf3 suites.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_default_testcase.
    :type in_filename: str
    :type in_prolog: str
    :type kwargs_list: list of dict
    """
    _, suite_id, suite_tag = get_iface_and_suite_ids(in_filename)
    testcase = Testcase.iperf3(suite_id)
    for nic_code in Constants.NIC_CODE_TO_NAME:
        nic_name = Constants.NIC_CODE_TO_NAME[nic_code]
        out_filename = replace_defensively(
            in_filename, u"10ge2p1x710", nic_code, 1,
            u"File name should contain NIC code once.", in_filename
        )
        out_prolog = replace_defensively(
            in_prolog, u"Intel-X710", nic_name, 2,
            u"NIC name should appear twice (tag and variable).",
            in_filename
        )
        check_suite_tag(suite_tag, out_prolog)
        with open(out_filename, u"wt") as file_out:
            file_out.write(out_prolog)
            add_iperf3_testcases(testcase, file_out, kwargs_list)


def write_trex_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated trex suites.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_trex_testcase.
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
        _, suite_id, suite_tag = get_iface_and_suite_ids(tmp_filename)
        testcase = Testcase.trex(suite_id)
        for nic_code in Constants.NIC_CODE_TO_NAME:
            nic_name = Constants.NIC_CODE_TO_NAME[nic_code]
            out_filename = replace_defensively(
                tmp_filename, u"10ge2p1x710", nic_code, 1,
                u"File name should contain NIC code once.", in_filename
            )
            out_prolog = replace_defensively(
                tmp_prolog, u"Intel-X710", nic_name, 2,
                u"NIC name should appear twice (tag and variable).",
                in_filename
            )
            check_suite_tag(suite_tag, out_prolog)
            with open(out_filename, u"wt") as file_out:
                file_out.write(out_prolog)
                add_trex_testcases(testcase, suite_id, file_out, kwargs_list)


def write_device_files(in_filename, in_prolog, kwargs_list):
    """Using given filename and prolog, write all generated suites.

    :param in_filename: Template filename to derive real filenames from.
    :param in_prolog: Template content to derive real content from.
    :param kwargs_list: List of kwargs for add_default_testcase.
    :type in_filename: str
    :type in_prolog: str
    :type kwargs_list: list of dict
    """
    for suite_type in Constants.DEVICE_TYPE_TO_KEYWORD:
        tmp_filename = replace_defensively(
            in_filename, u"scapy", suite_type, 1,
            u"File name should contain suite type once.", in_filename
        )
        _, suite_id, _ = get_iface_and_suite_ids(tmp_filename)
        testcase = Testcase.default(suite_id)
        for nic_code in Constants.NIC_CODE_TO_NAME:
            nic_name = Constants.NIC_CODE_TO_NAME[nic_code]
            tmp2_filename = replace_defensively(
                tmp_filename, u"10ge2p1x710", nic_code, 1,
                u"File name should contain NIC code once.", in_filename
            )
            tmp2_prolog = replace_defensively(
                in_prolog, u"Intel-X710", nic_name, 2,
                u"NIC name should appear twice (tag and variable).",
                in_filename
            )
            iface, old_suite_id, _ = get_iface_and_suite_ids(
                tmp2_filename
            )
            for driver in Constants.NIC_NAME_TO_DRIVER[nic_name]:
                out_filename = replace_defensively(
                    tmp2_filename, old_suite_id,
                    Constants.NIC_DRIVER_TO_SUITE_PREFIX[driver] + old_suite_id,
                    1, u"Error adding driver prefix.", in_filename
                )
                out_prolog = replace_defensively(
                    tmp2_prolog, u"vfio-pci", driver, 1,
                    u"Driver name should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_TAG[u"vfio-pci"],
                    Constants.NIC_DRIVER_TO_TAG[driver], 1,
                    u"Driver tag should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_PLUGINS[u"vfio-pci"],
                    Constants.NIC_DRIVER_TO_PLUGINS[driver], 1,
                    u"Driver plugin should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_DRIVER_TO_VFS[u"vfio-pci"],
                    Constants.NIC_DRIVER_TO_VFS[driver], 1,
                    u"NIC VFs argument should appear once.", in_filename
                )
                out_prolog = replace_defensively(
                    out_prolog, Constants.NIC_CODE_TO_PFS["10ge2p1x710"],
                    Constants.NIC_CODE_TO_PFS[nic_code], 1,
                    "NIC PFs argument should appear once.", in_filename
                )
                iface, suite_id, suite_tag = get_iface_and_suite_ids(
                    out_filename
                )
                check_suite_tag(suite_tag, out_prolog)
                # TODO: Reorder loops so suite_id is finalized sooner.
                testcase = Testcase.default(suite_id)
                with open(out_filename, u"wt") as file_out:
                    file_out.write(out_prolog)
                    add_default_testcases(
                        testcase, iface, suite_id, file_out, kwargs_list
                    )


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

        :param pattern: Glob pattern to select files. Example: \*-ndrpdr.robot
        :param protocol: String determining minimal frame size. Default: "ip4"
        :type pattern: str
        :type protocol: str
        :raises RuntimeError: If invalid source suite is encountered.
        """
        if not self.quiet:
            print(f"Regenerator starts at {getcwd()}", file=sys.stderr)

        min_frame_size = PROTOCOL_TO_MIN_FRAME_SIZE[protocol]
        default_kwargs_list = [
            {u"frame_size": 1518, u"phy_cores": 1},
            {u"frame_size": 1518, u"phy_cores": 2},
            {u"frame_size": 1518, u"phy_cores": 3},
            {u"frame_size": 1518, u"phy_cores": 4},
        ]
        hs_bps_kwargs_list = [
            {u"frame_size": 1460, u"phy_cores": 1},
        ]
        hs_quic_kwargs_list = [
            {u"frame_size": 1280, u"phy_cores": 1},
        ]
        iperf3_kwargs_list = [
            {u"frame_size": 128000, u"phy_cores": 1},
            {u"frame_size": 128000, u"phy_cores": 2},
            {u"frame_size": 128000, u"phy_cores": 4}
        ]
        # List for tests with one dataplane core
        # (and variable number of other cores).
        dp1_kwargs_list = [
            {u"frame_size": 1518, u"phy_cores": 2},
            {u"frame_size": 1518, u"phy_cores": 3},
            {u"frame_size": 1518, u"phy_cores": 4},
        ]

        http_kwargs_list = [
            {u"frame_size": 0, u"phy_cores": 1},
            {u"frame_size": 0, u"phy_cores": 2},
            {u"frame_size": 64, u"phy_cores": 1},
            {u"frame_size": 64, u"phy_cores": 2},
            {u"frame_size": 1024, u"phy_cores": 1},
            {u"frame_size": 1024, u"phy_cores": 2},
            {u"frame_size": 2048, u"phy_cores": 1},
            {u"frame_size": 2048, u"phy_cores": 2}
        ]

        device_kwargs_list = [
            {u"frame_size": min_frame_size, u"phy_cores": 0}
        ]

        trex_kwargs_list = [
            {u"frame_size": min_frame_size},
            {u"frame_size": 1518},
            {u"frame_size": 9000},
            {u"frame_size": u"IMIX_v4_1"}
        ]

        for in_filename in glob(pattern):
            if not self.quiet:
                print(
                    u"Regenerating in_filename:", in_filename, file=sys.stderr
                )
            iface, _, _ = get_iface_and_suite_ids(in_filename)
            if not iface.endswith(u"10ge2p1x710"):
                raise RuntimeError(
                    f"Error in {in_filename}: non-primary NIC found."
                )
            for prefix in Constants.FORBIDDEN_SUITE_PREFIX_LIST:
                if prefix in in_filename:
                    raise RuntimeError(
                        f"Error in {in_filename}: non-primary driver found."
                    )
            with open(in_filename, u"rt") as file_in:
                in_prolog = u"".join(
                    file_in.read().partition(u"*** Test Cases ***")[:-1]
                )
            if "-tg" in in_filename:
                write_trex_files(in_filename, in_prolog, trex_kwargs_list)
                continue
            if in_filename.endswith(u"-ndrpdr.robot"):
                if u"scheduler" in in_filename:
                    write_default_files(
                        in_filename, in_prolog, dp1_kwargs_list
                    )
                else:
                    write_default_files(
                        in_filename, in_prolog, default_kwargs_list
                    )
            elif in_filename.endswith(u"-reconf.robot"):
                write_reconf_files(in_filename, in_prolog, default_kwargs_list)
            elif in_filename.endswith(u"-rps.robot") \
                    or in_filename.endswith(u"-cps.robot"):
                write_tcp_files(in_filename, in_prolog, http_kwargs_list)
            elif in_filename.endswith(u"-bps.robot"):
                hoststack_kwargs_list = \
                    hs_quic_kwargs_list if u"quic" in in_filename \
                    else hs_bps_kwargs_list
                write_tcp_files(in_filename, in_prolog, hoststack_kwargs_list)
            elif in_filename.endswith(u"-iperf3-mrr.robot"):
                write_iperf3_files(in_filename, in_prolog, iperf3_kwargs_list)
            elif in_filename.endswith(u"-scapy.robot"):
                write_device_files(in_filename, in_prolog, device_kwargs_list)
            else:
                raise RuntimeError(
                    f"Error in {in_filename}: non-primary suite type found."
                )
        if not self.quiet:
            print(u"Regenerator ends.", file=sys.stderr)
        print(file=sys.stderr)  # To make autogen check output more readable.
