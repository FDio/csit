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


# TODO: Read FDIO_VPP_DIR environment variable, or some other input,
# instead of using hardcoded relative path?
API_DIR = op.normpath(op.join(
    op.dirname(op.abspath(__file__)), "..", "..", "..", "..",
    "build-root", "install-vpp-native", "vpp", "share", "vpp", "api"))

def edit_file(error):
    """Based on CRC mismatch detected, edit the CSIT CRC list file.

    A new file with .log extension is created in the same directory.

    :param error: The error raised by CRC checker.
    :type error: RuntimeError with particularly formatted message.
    """
    file_name = "supported_crcs.yaml"
    file_dir = op.normpath(op.join(
        op.dirname(op.abspath(__file__)), "..", "..", "..",
        "resources", "api", "vpp"))
    file_in_path = op.join(file_dir, file_name)
    file_out_path = op.join(file_dir, file_name + ".log")
    # Remove prolog, epilog and intros, including outside double-quotes.
    changes = error.message[43:-3].split('",\n "')
    sys.stderr.write(repr(changes) + '\n')
    len_changes = len(changes)
    with open(file_in_path, "r") as fin, open(file_out_path, "w") as fout:
        index = 0
        # Remove inside double-quotes
        message, new_crc = changes[index].split('":"')
        sys.stderr.write("message: " + message + ", crc: " new_crc + '\n')
        for line in fin:
            if message in line:
                sys.stderr.write("Found in line: " + line + '\n')
                _, _, _, old_crc, _ = line.split('"')
                line = line.replace(old_crc, new_crc)
                sys.stderr.write("New line: " + line + '\n')
                index += 1
                if index >= len_changes:
                    break
                message, new_crc = changes[index][1:-1].split('":"')
                sys.stderr.write("message: " + message + ", crc: " new_crc + '\n')
            fout.write(line + '\n')
            sys.stderr.write("Written line: " + line + '\n')

CHECKER = VppApiCrcChecker(API_DIR)
try:
    CHECKER.report_initial_conflicts(report_missing=True)
except RuntimeError as err:
    sys.stderr.write("{err!r}\n".format(err=err))
    sys.stderr.write(
        "\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        "\n"
        "VPP CSIT API CHECK FAIL!\n"
        "\n"
        "This means the patch under test has missing messages,\n"
        "or messages with unexpected CRCs compared to what CSIT needs.\n"
        "Either this Change and/or its ancestors were editing .api files,\n"
        "or your chain is not rebased upon the recent enough VPP codebase.\n"
        "\n"
        "Please rebase the patch to see if that fixes the problem.\n"
        "If that fails email csit-dev@lists.fd.io for a new\n"
        "operational branch supporting the api changes.\n"
        "\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
    )
    edit_file(err)
    sys.exit(1)
else:
    sys.stderr.write(
        "\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
        "\n"
        "VPP CSIT API CHECK PASS!\n"
        "\n"
        "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@\n"
    )
