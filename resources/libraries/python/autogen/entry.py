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

"""Module defining top level logic for test suite regeneration."""

import os
import sys


def generate_recursively(verbose=False):
    """Entry point for suite generation.

    The code visits every directory from current working directory
    and attempts to generate files based on every .robot file encountered.

    :param verbose: Reduce log prints (to stderr) when False (default).
    :type quiet: boolean
    :raises RuntimeError: If generation fails, e.g. on non-primary input.
    """
    cwd = og.getcwd()
    if verbose:
        print(f"Regenerator starts at {cwd}", file=sys.stderr)
    suite_ids = set()
    for visit_dir, subdirs, files in os.walk(cwd):
        for in_filename in files:
            if not in_filename.endswith(u".robot"):
                continue
            if verbose:
                print(
                    u"Regenerating in_filename:", in_filename, file=sys.stderr
                )
            iface, _, _ = util.get_iface_and_suite_ids(in_filename)
            # Early fail conditions, move to separate function if too long.
            if not iface.endswith(u"10ge2p1x710"):
                raise RuntimeError(
                    f"Error in {in_filename}: non-primary NIC found."
                )
            for prefix in Constants.FORBIDDEN_SUITE_PREFIX_LIST:
                if prefix in in_filename:
                    raise RuntimeError(
                        f"Error in {in_filename}: non-primary driver found."
                    )
            # Read file content.
            with open(os.join(visit_dir, in_filename), u"rt") as file_in:
                in_prolog = u"".join(
                    file_in.read().partition(u"*** Test Cases ***")[:-1]
                )
            # It is easier to temporarily change working directory
            # instead of passing visit_dir argument everywhere.
            try:
                os.chdir(visit_dir)
                classify_and_handle(in_filename, in_prolog, suite_id_list)
            finally:
                os.chdir(cwd)
    if verbose:
        print(u"Regenerator ends.", file=sys.stderr)
    print(file=sys.stderr)  # To make autogen check output more readable.


def classify_and_handle(in_filename, in_prolog, suite_ids):
    """Detect test type and proceed with the logic specialized to it.

    At the end, the logic will write several new files,
    overwriting the original one the generator found.

    We keep directory and filename separated, as usually
    only the filename is edited during generation.

    :param in_filename: File name of the file found at generation start.
    :param in_prolog: Most of suite content, except test cases.
    :param suite_ids: Suite IDs generated so far.
    :type in_filename: str
    :type in_prolog: str
    :type suite_id_list: Set[str]
    :raises RuntimeError: On forbidden or malformed input or repeated suite ID.
    """
    subtype = TestSubtype.from_filename(in_filename)
    state = EditState(in_filename, in_prolog, subtype)
    write_files(state, suite_ids)
