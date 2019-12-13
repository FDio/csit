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
    initialize and run the CRC checker, write result consequences
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
        sys.stderr.write(
            f"{err!r}\n"
            u"\n"
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            u"\n"
            u"VPP CSIT API CHECK FAIL!\n"
            u"\n"
            u"This means the patch under test has missing messages,\n"
            u"or messages with unexpected CRCs compared to what CSIT needs.\n"
            u"Either this Change and/or its ancestors were editing .api files,\n"
            u"or your chain is not rebased upon the recent enough VPP codebase.\n"
            u"\n"
            u"Please rebase the patch to see if that fixes the problem.\n"
            u"If that fails email csit-dev@lists.fd.io for a new\n"
            u"operational branch supporting the api changes.\n"
            u"\n"
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        )
        return 1
    else:
        sys.stderr.write(
            u"\n"
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
            u"\n"
            u"VPP CSIT API CHECK PASS!\n"
            u"\n"
            u"@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        )
        return 0

if __name__ == u"__main__":
    sys.exit(main())
