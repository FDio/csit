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

from resources.libraries.python.autogen.edit_state import EditState
from resources.libraries.python.autogen.split_write import write_files
from resources.libraries.python.autogen.suite_subtype import SuiteSubtype
from resources.libraries.python.Constants import Constants

def generate_recursively(verbose=False):
    """Entry point for suite generation.

    The code visits every directory from current working directory
    and attempts to generate files based on every .robot file encountered.

    If the same filename repeats, fail.
    (Suite tags and IDs may repeat, as they do not copntain NIC code.)

    :param verbose: Reduce log prints (to stderr) when False (default).
    :type quiet: boolean
    :raises RuntimeError: If generation fails, e.g. on non-primary input.
    """
    cwd = os.getcwd()
    if verbose:
        print(f"Regenerator starts at {cwd}", file=sys.stderr)
    no_files = 0
    filename_set = set()
    for visit_dir, _, files in os.walk(cwd):
        for filename in files:
            if filename == u"__init__.robot" or not filename.endswith(u"robot"):
                continue
            if verbose:
                print(f"Regenerating {filename}:", file=sys.stderr)
            iface, _, _ = EditState.get_iface_and_suite_ids(filename)
            # Early fail conditions, move to separate function if too long.
            if not iface.endswith(u"10ge2p1x710"):
                raise RuntimeError(f"{filename}: non-primary NIC found.")
            for prefix in Constants.FORBIDDEN_SUITE_PREFIX_LIST:
                if prefix in filename:
                    raise RuntimeError(f"{filename}: non-primary driver found.")
            # Read file content.
            with open(os.path.join(visit_dir, filename), u"rt") as file_in:
                prolog = u"".join(
                    file_in.read().partition(u"*** Test Cases ***")[:-1]
                )
            # It is easier to temporarily change working directory
            # instead of passing visit_dir argument everywhere.
            try:
                os.chdir(visit_dir)
                no_files += classify_and_handle(filename, prolog, filename_set)
            finally:
                os.chdir(cwd)
    if verbose:
        print(u"Regenerator ends.", file=sys.stderr)
    print(f"{no_files} files written", file=sys.stderr)
    print(file=sys.stderr)  # To make autogen check output more readable.


def classify_and_handle(filename, prolog, filename_set):
    """Detect test type and proceed with the logic specialized to it.

    At the end, the logic will write several new files,
    overwriting the original one the generator found.

    We keep directory and filename separated, as usually
    only the filename is edited during generation.

    :param filename: File name of the file found at generation start.
    :param prolog: Most of suite content, except test cases.
    :param filename_set: Filenames generated so far.
    :type filename: str
    :type prolog: str
    :type filename_set: Set[str]
    :return: How many files were written.
    :rtype: int
    :raises RuntimeError: On forbidden or malformed input or repeated filename.
    """
    subtype = SuiteSubtype.from_filename(filename)
    state = EditState(filename, prolog, subtype)
    return write_files(state, filename_set)
