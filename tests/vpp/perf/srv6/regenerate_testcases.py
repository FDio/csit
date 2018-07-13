#!/usr/bin/env python

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

import glob

from resources.libraries.python.autogen.DefaultTestcase import DefaultTestcase

def add_testcase(file_out, num, framesize, cores):
    file_out.write(testcase.generate(num, framesize, cores))
    return num + 1

def add_testcases(file_out, tc_args_list):
    num = 1
    for tc_args in tc_args_list:
        num = add_testcase(file_out, num, *tc_args)

for filename in glob.glob("*-ndrpdr.robot"):
    with open(filename, "r") as file_in:
        text = file_in.read()
        text_prolog = "".join(text.partition("*** Test Cases ***")[:-1])
    suite_id = filename.split("-", 1)[1].split(".", 1)[0]
    print "Regenerating suite_id:", suite_id
    testcase = DefaultTestcase(suite_id)
    with open(filename, "w") as file_out:
        file_out.write(text_prolog)
        # TODO: testcase.write()?
        num = 1
        add_testcases(file_out, [
            (78, 1),
            (78, 2),
            (78, 4),
            (1518, 1),
            (1518, 2),
            (1518, 4),
            (9000, 1),
            (9000, 2),
            (9000, 4),
            ("IMIX_v4_1", 1),
            ("IMIX_v4_1", 2),
            ("IMIX_v4_1", 4)
        ])
