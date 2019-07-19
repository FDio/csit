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

# Extract 2N suites from the global testcase list and normalize output.
suites_2n=($(printf '%s\n' "${suites_names[@]}" | \
           grep -E "^(2n1l|2n)-" | \
           sed -re "s/(2n1l|2n)-//"))
# Extract 3N suites from the global testcase list.
suites_3n=($(printf '%s\n' "${suites_names[@]}" | \
           grep -vE "^(2n1l|2n|eth2p)-"))
# Extract vpp_device suites from the global testcase list.
# Code will try to map the naming to perf by normalizing output.
suites_dev=($(printf '%s\n' "${suites_names[@]}" | \
            grep -E "^eth2p-" | \
            sed -re "s/eth2p-/10ge2p1x710-/" | \
            sed -re "s/-dev/-ndrpdr/" | \
            sed -re "s/-ethicmpv/-ethip/"))

# Compute intersection of arrays.
intersection_3n2n=($(comm -12 <(printf '%s\n' "${suites_3n[@]}" | sort) \
    <(printf '%s\n' "${suites_2n[@]}" | sort)))
intersection_3ndev=($(comm -12 <(printf '%s\n' "${suites_2n[@]}" | sort) \
    <(printf '%s\n' "${suites_dev[@]}" | sort)))

# Print the results in CSV format.
echo "Suite name;Testcase name;2n version;VPP Device version" | \
    tee -a "tc_coverage.log"
for i in "${!suites_names[@]}"; do
    if [[ ! "${suites_names[i]}" =~ ^(2n1l|2n|eth2p)-.* ]]; then
        echo -n "${suites_names[i]};${testcases_names[i]}" | \
            tee -a "tc_coverage.log"
        if [[ "${intersection_3n2n[@]}" =~ "${suites_names[i]}" ]]; then
            echo -n ";yes" | tee -a "tc_coverage.log"
        else
            echo -n ";no" | tee -a "tc_coverage.log"
        fi
        if [[ "${intersection_3ndev[@]}" =~ "${suites_names[i]}" ]]; then
            echo ";yes" | tee -a "tc_coverage.log"
        else
            echo ";no" | tee -a "tc_coverage.log"
        fi
    fi
done

set -x

echo "Count 2n: ${#suites_2n[@]}"
echo "Count 3n: ${#suites_3n[@]}"
echo "Count dev: ${#suites_dev[@]}"
echo "Coverage 2n3n: ${#intersection_3n2n[@]}"
echo "Coverage 3ndev: ${#intersection_3ndev[@]}"

warn
warn "Testcase coverage checker: PASS"
