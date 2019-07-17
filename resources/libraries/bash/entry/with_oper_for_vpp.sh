#!/usr/bin/env bash

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

set -exuo pipefail

# Typical usage:
# $ source "./with_oper_for_vpp.sh" "per_patch_perf.sh"
#
# This wrapper is mostly useful for Jenkins invocation,
# because in manual testing people usually already have checked out
# the branches they want to test (which might not yet be available in Gerrit).
#
# Assumptions:
# + There is a directory holding initial CSIT code to use, this script is there.
# + First argument is filename of next entry script to execute.
#   TODO: Support relative paths? Relative to BASH_ENTRY_DIR?
# Consequences:
# + A csit branch name is computed.
# + Possibly overriden, based on CSIT_REF value.
# + The computed or overriden CSIT refspec is checked out.
# + The argument entry script is sourced, with arguments shifted.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs || die
source "${BASH_FUNCTION_DIR}/branch.sh" || die "Source failed."
checkout_csit_for_vpp "${GERRIT_BRANCH}" || die
cmd="${1}"
shift
pwd
ls -l .
ls -l csit
ls -l csit/resources
ls -l csit/resources/libraries
ls -l csit/resources/libraries/bash
ls -l csit/resources/libraries/bash/entry
ls -l csit/resources/libraries/bash/entry/check_crc.sh
source "${BASH_ENTRY_DIR}/${cmd}" "$@"
