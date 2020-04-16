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

"""
Script that fails if .api.json files downloaded to a hardcoded place
do not match CRC checksusms currently supported by CSIT.

No executable flag, nor shebang, as most users do not have .api.json
files downloaded to the correct place.
"""

import os.path as op
import sys

from resources.libraries.python.VppApiCrc import VppApiCrcChecker


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
            u"https://github.com/FDio/csit/blob/master/docs/automating_vpp_api_flag_day.rst"
            u"",
            u"For the latter case, please rebase the patch to see",
            u"if that fixes the problem. If even repeated rebases do not help",
            u"send and email to csit-dev@lists.fd.io asking to investigate.",
            u"",
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@",
        ]
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
