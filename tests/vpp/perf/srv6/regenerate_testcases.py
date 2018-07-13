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
        file_out.write(testcase.generate(num=1, framesize=78, cores=1))
        file_out.write(testcase.generate(num=2, framesize=78, cores=2))
        file_out.write(testcase.generate(num=3, framesize=78, cores=4))
        file_out.write(testcase.generate(num=4, framesize=1518, cores=1))
        file_out.write(testcase.generate(num=5, framesize=1518, cores=2))
        file_out.write(testcase.generate(num=6, framesize=1518, cores=4))
        file_out.write(testcase.generate(num=7, framesize=9000, cores=1))
        file_out.write(testcase.generate(num=8, framesize=9000, cores=2))
        file_out.write(testcase.generate(num=9, framesize=9000, cores=4))
        file_out.write(testcase.generate(num=7, framesize="IMIX_v4_1", cores=1))
        file_out.write(testcase.generate(num=8, framesize="IMIX_v4_1", cores=2))
        file_out.write(testcase.generate(num=9, framesize="IMIX_v4_1", cores=4))
