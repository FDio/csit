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

"""
Script that fails if .api.json files downloaded to a hardcoded place
do not match CRC checksusms currently supported by CSIT.

No executable flag, nor shebang, as most users do not have .api.json
files downloaded to the correct place.
"""

import os.path as op
import sys

from resources.libraries.python.VppApiCrc import VppApiCrcChecker


def edit_file(error):
    """Based on CRC mismatch detected, edit the CSIT CRC list file.

    A new file with .log extension is created in the same directory.

    :param error: The error raised by CRC checker.
    :type error: RuntimeError with particularly formatted message.
    """
    file_name = u"supported_crcs.yaml"
    file_dir = op.normpath(op.join(
        op.dirname(op.abspath(__file__)), u"..", u"..", u"..",
        u"resources", u"api", u"vpp"))
    file_in_path = op.join(file_dir, file_name)
    file_out_path = op.join(file_dir, file_name + u".log")
    # Remove prolog, epilog and intros, including outside double-quotes.
    changes = str(error)[43:-3].split(u'",\n "')
    len_changes = len(changes)
    with open(file_in_path, u"r") as fin, open(file_out_path, u"w") as fout:
        index = 0
        # Remove inside double-quotes
        message, new_crc = changes[index].split(u'":"')
        for line in fin:
            if message and message in line:
                # CRC is the thing between single quotes.
                _, old_crc, _ = line.split(u"'")
                line = line.replace(old_crc, new_crc)
                index += 1
                if index < len_changes:
                    message, new_crc = changes[index].split(u'":"')
                else:
                    # Signal no other changes are to be done.
                    message = u""
            fout.write(line)


def main():
    """Execute the logic, return the return code.

    From current location, construct path to .api file subtree,
    initialize and run the CRC checker, print result consequences
    to stderr, return the return code to return from the script.

    :returns: Return code to return. 0 if OK, 1 if CRC mismatch.
    :rtype: int
    """

    # TODO: Read FDIO_VPP_DIR environment variable, or some other input,
    # instead of using hardcoded relative path?

    api_dir = op.normpath(op.join(
        op.dirname(op.abspath(__file__)), u"..", u"..", u"..", u"..",
        u"build-root", u"install-vpp-native", u"vpp", u"share", u"vpp",
        u"api"
    ))
    checker = VppApiCrcChecker(api_dir)
    try:
        checker.report_initial_conflicts(report_missing=True)
    except RuntimeError as err:
        stderr_lines = [
            f"{err!r}",
            u"",
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
            u"",
            u"VPP CSIT API CHECK FAIL!",
            u"",
            u"This means the patch under test has missing messages,",
            u"or messages with unexpected CRCs compared to what CSIT needs.",
            u"Either this Change and/or its ancestors were editing .api files,",
            u"or your chain is not rebased upon a recent enough VPP codebase.",
            u"",
            u"In the former case, please consult the following document",
            u"to see how to make CSIT accept the .api editing change.",
            u"https://github.com/FDio/csit/blob/master/docs/"
            u"automating_vpp_api_flag_day.rst",
            u"For the latter case, please rebase the patch to see",
            u"if that fixes the problem. If repeated rebases do not help",
            u"send and email to csit-dev@lists.fd.io asking to investigate.",
            u"",
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
        ]
        edit_file(err)
        ret_code = 1
    else:
        stderr_lines = [
            u"",
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
            u"",
            u"VPP CSIT API CHECK PASS!",
            u"",
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
        ]
        ret_code = 0
    for stderr_line in stderr_lines:
        print(stderr_line, file=sys.stderr)
    return ret_code

if __name__ == u"__main__":
    sys.exit(main())
