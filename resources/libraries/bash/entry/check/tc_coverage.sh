#!/usr/bin/env bash

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

set -xeuo pipefail

# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

# Grep of interest: We want all tc01- prefixed (skip TC variations for now).
# Currently script assumes all variations inside to be part of either
# auto-generation or not checked at all (VIRL derivates).
r_grep="tc01-"
# Parse grep of interest (learn path, learn suite, learn testcase name).
r_parse='(.*)\/(.*).robot.*(tc[[:digit:]]{2}-.*)'

rm -f "tc_coverage.log" || die

# Disabling -x: Following lines are doing too much garbage output.
set +x

# Grep interest.
grep_match=$(grep -RE "${r_grep}" tests/*) || die
# Extract data from the grep output.
suites_dirs=($(printf "${grep_match}" | sed -re "s/${r_parse}/\1/")) || die
suites_names=($(printf "${grep_match}" | sed -re "s/${r_parse}/\2/")) || die
testcases_names=($(printf "${grep_match}" | sed -re "s/${r_parse}/\3/")) || die

# Coverage check
# ==============

set -x

echo "Count 2n: ${#suites_2n[@]}"
echo "Count 3n: ${#suites_3n[@]}"
echo "Count dev: ${#suites_dev[@]}"
echo "Coverage 2n3n: ${#intersection_3n2n[@]}"
echo "Coverage 3ndev: ${#intersection_3ndev[@]}"

warn
warn "Testcase naming checker: PASS"
