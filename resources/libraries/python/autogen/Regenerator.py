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
            DefaultTestcase accepts "framesize" and "phy_cores".
        :type pattern: str
        :type is_ip6: boolean
        :type tc_kwargs_list: list of tuple or None
        """

        protocol_to_min_framesize = {
            "ip4": 64,
            "ip6": 78,
            "vxlan+ip4": 114  # What is the real minimum for latency stream?
        }
        min_framesize_values = protocol_to_min_framesize.values()
        nic_names = Constants.NIC_NAME_TO_CODE.keys()
        primary_name = "Intel-X710"
        primary_code = Constants.NIC_NAME_TO_CODE[primary_name]
        len_primary_code = len(primary_code)
        primary_type = "ndrpdr"
        primary_keyword = Constants.SUITE_TYPE_TO_KEYWORD[primary_type]
        suite_types = Constants.SUITE_TYPE_TO_KEYWORD.keys()

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
            if kwargs["framesize"] == 9000:
                if "vic1227" in iface:
                    # Not supported in HW.
                    emit = False
                if "avf" in suite_id:
                    # Not supported by AVF driver.
                    # https://git.fd.io/vpp/tree/src/plugins/avf/README.md
                    emit = False
            if "-16vm-" in suite_id or "-16dcr-" in suite_id:
                if kwargs["phy_cores"] > 3:
                    # CSIT lab only has 28 (physical) core processors,
                    # so these test would fail when attempting to assign cores.
                    emit = False
            if "soak" in suite_id:
                # Soak test take too long, do not risk other than tc01.
                if kwargs["phy_cores"] != 1:
                    emit = False
                if kwargs["framesize"] not in min_framesize_values:
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

        def replace_defensively(whole, to_replace, replace_with, how_many):
            """Replace substrings while checking the number of occurences.

            Return edited copy of the text (so original string is not affected).

            :param whole: The text to perform replacements on.
            :param to_replace: Substring occurences of which to replace.
            :param replace_with: Substring to replace occurences with.
            :param how_many: Number of occurences to expect.
            :type whole: str
            :type to_replace: str
            :type replace_with: str
            :type how_many: int
            :return: The whole text after replacements are done.
            :rtype: str
            :raise ValueError: If number of occurences does not match.
            """
            found = whole.count(to_replace)
            if found != how_many:
                raise ValueError("Number of occurences does not match.")
            return whole.replace(to_replace, replace_with)

        if not self.quiet:
            eprint("Regenerator starts at {cwd}".format(cwd=getcwd()))
        min_framesize = protocol_to_min_framesize[protocol]
        kwargs_list = tc_kwargs_list if tc_kwargs_list else [
            {"framesize": min_framesize, "phy_cores": 1},
            {"framesize": min_framesize, "phy_cores": 2},
            {"framesize": min_framesize, "phy_cores": 4},
            {"framesize": 1518, "phy_cores": 1},
            {"framesize": 1518, "phy_cores": 2},
            {"framesize": 1518, "phy_cores": 4},
            {"framesize": 9000, "phy_cores": 1},
            {"framesize": 9000, "phy_cores": 2},
            {"framesize": 9000, "phy_cores": 4},
            {"framesize": "IMIX_v4_1", "phy_cores": 1},
            {"framesize": "IMIX_v4_1", "phy_cores": 2},
            {"framesize": "IMIX_v4_1", "phy_cores": 4}
        ]
        for in_filename in glob(pattern):
            if not self.quiet:
                eprint("Regenerating in_filename:", in_filename)
            if not in_filename.endswith(primary_type + ".robot"):
                eprint("Error: non-primary suite type encountered.")
                sys.exit(1)
            iface, suite_id = get_iface_and_suite_id(in_filename)
            if not iface.endswith(primary_code):
                eprint("Error: non-primary NIC encountered.")
                sys.exit(1)
            with open(in_filename, "r") as file_in:
                text = file_in.read()
            in_prolog = "".join(text.partition("*** Test Cases ***")[:-1])
            for suite_type in suite_types:
                tmp_filename = replace_defensively(
                    in_filename, primary_type, suite_type, 1)
                suite_keyword = Constants.SUITE_TYPE_TO_KEYWORD[suite_type]
                tmp_prolog = replace_defensively(
                    in_prolog, primary_keyword, suite_keyword, 1)
                iface, suite_id = get_iface_and_suite_id(tmp_filename)
                testcase = self.testcase_class(suite_id)
                for nic_name in nic_names:
                    nic_code = Constants.NIC_NAME_TO_CODE[nic_name]
                    out_filename = replace_defensively(
                        tmp_filename, primary_code, nic_code, 1)
                    out_prolog = replace_defensively(
                        tmp_prolog, primary_name, nic_name, 2)
                    iface, suite_id = get_iface_and_suite_id(out_filename)
                    with open(out_filename, "w") as file_out:
                        file_out.write(out_prolog)
                        add_testcases(
                            testcase, iface, suite_id, file_out, kwargs_list)
        if not self.quiet:
            eprint("Regenerator ends.")
        eprint()  # To make autogen check output more readable.
