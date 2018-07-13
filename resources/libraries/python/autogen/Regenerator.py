# Copyright (c) 2018 Cisco and/or its affiliates.
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

from glob import glob
from os import getcwd

from .Testcase import Testcase
from .DefaultTestcase import DefaultTestcase


class Regenerator(object):
    """Class containing file generating methods."""

    def __init__(self, testcase_class=DefaultTestcase):
        """Initialize Testcase class to use.

        TODO: See the type doc for testcase_class?
        It implies the design is wrong. Fix it.
        Easiest: Hardcode Regenerator to use DefaultTestcase only.

        :param testcase_class: Subclass of DefaultTestcase for generation.
            Default: DefaultTestcase
        :type testcase_class: subclass of DefaultTestcase accepting suite_id
        """
        self.testcase_class = testcase_class

    def regenerate_glob(self, pattern, is_ip6=False, tc_kwargs_list=None):
        """Regenerate files matching glob pattern based on arguments.

        In the current working directory, find all files matching
        the glob pattern. Use testcase template (from init) to regenerate
        test cases, autonumbering them, taking arguments from list.
        If the list is None, use default list, which depends on ip6 usage.

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

        def add_testcase(file_out, num, **kwargs):
            file_out.write(testcase.generate(num=num, **kwargs))
            return num + 1

        def add_testcases(file_out, tc_kwargs_list):
            num = 1
            for tc_kwargs in tc_kwargs_list:
                num = add_testcase(file_out, num, **tc_kwargs)

        print "Regenerator starts at {cwd}".format(cwd=getcwd())
        min_framesize = 78 if is_ip6 else 64
        kwargs_list = tc_kwargs_list if tc_kwargs_list is not None else [
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
        for filename in glob(pattern):
            with open(filename, "r") as file_in:
                text = file_in.read()
                text_prolog = "".join(text.partition("*** Test Cases ***")[:-1])
            # TODO: Make the following work for 2n suites.
            suite_id = filename.split("-", 1)[1].split(".", 1)[0]
            print "Regenerating suite_id:", suite_id
            testcase = self.testcase_class(suite_id)
            with open(filename, "w") as file_out:
                file_out.write(text_prolog)
                add_testcases(file_out, kwargs_list)
        print "Regenerator ends."
        print  # To make autogen check output more readable.
