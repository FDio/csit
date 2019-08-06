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

from __future__ import print_function

from glob import glob
from os import getcwd
import sys

from .DefaultTestcase import DefaultTestcase
from resources.libraries.python.Constants import Constants


# Copied from https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs):
    """Print to stderr."""
    print(*args, file=sys.stderr, **kwargs)


class Regenerator(object):
    """Class containing file generating methods."""

    def __init__(self, testcase_class=DefaultTestcase, quiet=True):
        """Initialize Testcase class to use.

        TODO: See the type doc for testcase_class?
        It implies the design is wrong. Fix it.
        Easiest: Hardcode Regenerator to use DefaultTestcase only.

        :param testcase_class: Subclass of DefaultTestcase for generation.
            Default: DefaultTestcase
        :param quiet: Reduce log prints (to stderr) when True (default).
        :type testcase_class: subclass of DefaultTestcase accepting suite_id
        :type quiet: boolean
        """
        self.testcase_class = testcase_class
        self.quiet = quiet

    def regenerate_glob(self, pattern, protocol="ip4", tc_kwargs_list=None):
        """Regenerate files matching glob pattern based on arguments.

        In the current working directory, find all files matching
        the glob pattern. Use testcase template (from init) to regenerate
        test cases, autonumbering them, taking arguments from list.
        If the list is None, use default list, which depends on ip6 usage.

        Log-like prints are emited to sys.stderr.

        :param pattern: Glob pattern to select files. Example: *-ndrpdr.robot
        :param is_ip6: Flag determining minimal frame size. Default: False
        :param tc_kwargs_list: Arguments defining the testcases. Default: None
            When None, default list is used.
            List item is a dict, argument names are keys.
            The initialized testcase_class should accept those, and "num".
            DefaultTestcase accepts "frame_size" and "phy_cores".
        :type pattern: str
        :type is_ip6: boolean
        :type tc_kwargs_list: list of tuple or None
        """

        protocol_to_min_frame_size = {
            "ip4": 64,
            "ip6": 78,
            "ethip4vxlan": 114,  # What is the real minimum for latency stream?
            "dot1qip4": 68,
            "dot1qip4vxlan": 118
        }
        min_frame_size_values = protocol_to_min_frame_size.values()

        def get_iface_and_suite_id(filename):
            """Get interface and suite ID.

            :param filename: Suite file.
            :type filename: str
            :returns: Interface ID, Suite ID.
            :rtype: tuple
            """
            dash_split = filename.split("-", 1)
            if len(dash_split[0]) <= 4:
                # It was something like "2n1l", we need one more split.
                dash_split = dash_split[1].split("-", 1)
            return dash_split[0], dash_split[1].split(".", 1)[0]

        def add_testcase(testcase, iface, suite_id, file_out, num, **kwargs):
            """Add testcase to file.

            :param testcase: Testcase class.
            :param iface: Interface.
            :param suite_id: Suite ID.
            :param file_out: File to write testcases to.
            :param num: Testcase number.
            :param kwargs: Key-value pairs used to construct testcase.
            :type testcase: Testcase
            :type iface: str
            :type suite_id: str
            :type file_out: file
            :type num: int
            :type kwargs: dict
            :returns: Next testcase number.
            :rtype: int
            """
            # TODO: Is there a better way to disable some combinations?
            emit = True
            if kwargs["frame_size"] == 9000:
                if "vic1227" in iface:
                    # Not supported in HW.
                    emit = False
                if "vic1385" in iface:
                    # Not supported in HW.
                    emit = False
            if "-16vm2t-" in suite_id or "-16dcr2t-" in suite_id:
                if kwargs["phy_cores"] > 3:
                    # CSIT lab only has 28 (physical) core processors,
                    # so these test would fail when attempting to assign cores.
                    emit = False
            if "-24vm1t-" in suite_id or "-24dcr1t-" in suite_id:
                if kwargs["phy_cores"] > 3:
                    # CSIT lab only has 28 (physical) core processors,
                    # so these test would fail when attempting to assign cores.
                    emit = False
            if "soak" in suite_id:
                # Soak test take too long, do not risk other than tc01.
                if kwargs["phy_cores"] != 1:
                    emit = False
                if kwargs["frame_size"] not in min_frame_size_values:
                    emit = False
            if emit:
                file_out.write(testcase.generate(num=num, **kwargs))
            # We bump tc number in any case, so that future enables/disables
            # do not affect the numbering of other test cases.
            return num + 1

        def add_testcases(testcase, iface, suite_id, file_out, tc_kwargs_list):
            """Add testcases to file.

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
            num = 1
            for tc_kwargs in tc_kwargs_list:
                num = add_testcase(
                    testcase, iface, suite_id, file_out, num, **tc_kwargs)

        def replace_defensively(
                whole, to_replace, replace_with, how_many, msg, in_filename):
            """Replace substrings while checking the number of occurences.

            Return edited copy of the text (so original string is not affected).

            :param whole: The text to perform replacements on.
            :param to_replace: Substring occurences of which to replace.
            :param replace_with: Substring to replace occurences with.
            :param how_many: Number of occurences to expect.
            :param msg: Error message to raise.
            :param in_filename: File name in which the error occured.
            :type whole: str
            :type to_replace: str
            :type replace_with: str
            :type how_many: int
            :type msg: str
            :type in_filename: str
            :return: The whole text after replacements are done.
            :rtype: str
            :raise ValueError: If number of occurences does not match.
            """
            found = whole.count(to_replace)
            if found != how_many:
                raise ValueError(in_filename + ": " + msg)
            return whole.replace(to_replace, replace_with)

        def write_files(in_filename, in_prolog, kwargs_list):
            """Using given filename and prolog, write all generated suites.

            :param in_filename: Template filename to derive real filenames from.
            :param in_prolog: Template content to derive real content from.
            :param kwargs_list: List of kwargs for add_testcase.
            :type in_filename: str
            :type in_prolog: str
            :type kwargs_list: list of dict
            """
            for suite_type in Constants.PERF_TYPE_TO_KEYWORD.keys():
                tmp_filename = replace_defensively(
                    in_filename, "ndrpdr", suite_type, 1,
                    "File name should contain suite type once.", in_filename)
                tmp_prolog = replace_defensively(
                    in_prolog, "ndrpdr".upper(), suite_type.upper(), 1,
                    "Suite type should appear once in uppercase (as tag).",
                    in_filename)
                tmp_prolog = replace_defensively(
                    tmp_prolog,
                    "Find NDR and PDR intervals using optimized search",
                    Constants.PERF_TYPE_TO_KEYWORD[suite_type], 1,
                    "Main search keyword should appear once in suite.",
                    in_filename)
                tmp_prolog = replace_defensively(
                    tmp_prolog,
                    Constants.PERF_TYPE_TO_SUITE_DOC_VER["ndrpdr"],
                    Constants.PERF_TYPE_TO_SUITE_DOC_VER[suite_type],
                    1, "Exact suite type doc not found.", in_filename)
                tmp_prolog = replace_defensively(
                    tmp_prolog,
                    Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER["ndrpdr"],
                    Constants.PERF_TYPE_TO_TEMPLATE_DOC_VER[suite_type],
                    1, "Exact template type doc not found.", in_filename)
                _, suite_id = get_iface_and_suite_id(tmp_filename)
                testcase = self.testcase_class(suite_id)
                for nic_name in Constants.NIC_NAME_TO_CODE.keys():
                    out_filename = replace_defensively(
                        tmp_filename, "10ge2p1x710",
                        Constants.NIC_NAME_TO_CODE[nic_name], 1,
                        "File name should contain NIC code once.", in_filename)
                    out_prolog = replace_defensively(
                        tmp_prolog, "Intel-X710", nic_name, 2,
                        "NIC name should appear twice (tag and variable).",
                        in_filename)
                    if out_prolog.count("HW_") == 2:
                        # TODO CSIT-1481: Crypto HW should be read
                        # from topology file instead.
                        if nic_name in Constants.NIC_NAME_TO_CRYPTO_HW.keys():
                            out_prolog = replace_defensively(
                                out_prolog, "HW_DH895xcc",
                                Constants.NIC_NAME_TO_CRYPTO_HW[nic_name], 1,
                                "HW crypto name should appear.", in_filename)
                    iface, suite_id = get_iface_and_suite_id(out_filename)
                    with open(out_filename, "w") as file_out:
                        file_out.write(out_prolog)
                        add_testcases(
                            testcase, iface, suite_id, file_out, kwargs_list)

        if not self.quiet:
            eprint("Regenerator starts at {cwd}".format(cwd=getcwd()))
        min_frame_size = protocol_to_min_frame_size[protocol]
        kwargs_list = tc_kwargs_list if tc_kwargs_list else [
            {"frame_size": min_frame_size, "phy_cores": 1},
            {"frame_size": min_frame_size, "phy_cores": 2},
            {"frame_size": min_frame_size, "phy_cores": 4},
            {"frame_size": 1518, "phy_cores": 1},
            {"frame_size": 1518, "phy_cores": 2},
            {"frame_size": 1518, "phy_cores": 4},
            {"frame_size": 9000, "phy_cores": 1},
            {"frame_size": 9000, "phy_cores": 2},
            {"frame_size": 9000, "phy_cores": 4},
            {"frame_size": "IMIX_v4_1", "phy_cores": 1},
            {"frame_size": "IMIX_v4_1", "phy_cores": 2},
            {"frame_size": "IMIX_v4_1", "phy_cores": 4}
        ]
        for in_filename in glob(pattern):
            if not self.quiet:
                eprint("Regenerating in_filename:", in_filename)
            if not in_filename.endswith("ndrpdr.robot"):
                eprint("Error in {fil}: non-primary suite type encountered."
                       .format(fil=in_filename))
                sys.exit(1)
            iface, _ = get_iface_and_suite_id(in_filename)
            if not iface.endswith("10ge2p1x710"):
                eprint("Error in {fil}: non-primary NIC encountered."
                       .format(fil=in_filename))
                sys.exit(1)
            with open(in_filename, "r") as file_in:
                in_prolog = "".join(
                    file_in.read().partition("*** Test Cases ***")[:-1])
            write_files(in_filename, in_prolog, kwargs_list)
        if not self.quiet:
            eprint("Regenerator ends.")
        eprint()  # To make autogen check output more readable.
