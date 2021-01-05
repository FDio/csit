#!/usr/bin/env bash

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

# Grep of interest: We want all [0-9]{2,4}B- or IMIX- prefixed.
# Currently script assumes all variations inside to be part of either
# auto-generation or not checked at all (VIRL derivates).
r_grep="([0-9]{2,4}B|IMIX)-"
# Parse grep of interest (learn path, learn suite, learn testcase name).
r_parse='(.*)\/(.*).robot.*(([0-9]{2,4}B|IMIX)-.*)'

# CSIT Testcase naming convention rules.
# https://wiki.fd.io/view/CSIT/csit-test-naming
# Rules are defined as regular expressions in ordered array and checked in order
# in a loop, where every iteration is catenated with previous rules. This way we
# can detect where exactly the naming does not meet criteria and print error
# from rule string array. This imply that rules are defined in a way of a single
# string. First rule must start with ^ and last is terminated by $.
# Rules are written from Left to Right.
# Bash regular expression logic is used. Once the error is raised the checker is
# breaked for current Testcase marking the expected fail.
# One caveat of this solution is that we cannot proceed to check full names now
# as majority of Testcases does not meet naming criteria.
s_testc_rules=(
    'packet size or file size'
    'core combination'
    'NIC driver mode'
    'packet encapsulation on L2 layer'
    'test type'
    )
r_testc_rules=(
    '^([[:digit:]]{1,4}B|IMIX)-'
    '([[:digit:]]+c-){0,1}'
    '(avf-|1lbvpplacp-|2lbvpplacp-){0,1}'
    '(eth|dot1q|dot1ad)'
    # TODO: Packet encapsulation (here majority of TC starts failing).
    #'(ip4|ip6|ip6ip6|icmpv4|icmpv6)'
    #'(ipsec[[:digit:]]+tnlhw|ipsec[[:digit:]]+tnlsw|'
    #'srhip6|tcp|udp|lispip6|lispip4|vxlan){0,1}'
    #'(http){0,1}-'
    '(.*)-(dev|ndrpdr|bps|cps|rps|reconf)$'
    )
s_suite_rules=(
    'number of SUT nodes'
    'NIC card'
    'NIC driver mode'
    'packet encapsulation on L2 layer'
    'test type'
    )
r_suite_rules=(
    '^(2n1l|2n){0,1}-'
    '(eth2p|10ge2p1x710)-'
    '(avf-|1lbvpplacp-|2lbvpplacp-){0,1}'
    '(eth|dot1q|dot1ad)'
    # TODO: Packet encapsulation (here majority of TC starts failing).
    #'(ip4|ip6|ip6ip6|icmpv4|icmpv6)'
    #'(ipsec[[:digit:]]+tnlhw|ipsec[[:digit:]]+tnlsw|'
    #'srhip6|tcp|udp|lispip6|lispip4|vxlan){0,1}'
    #'(http){0,1}-'
    '(.*)-(dev|ndrpdr|bps|cps|rps|reconf)$'
    )

rm -f "tc_naming.log" || die

# Disabling -x: Following lines are doing too much garbage output.
set +x

# Grep interest.
grep_match=$(grep -RE "${r_grep}" tests/*) || die
# Extract data from the grep output.
suites_dirs=($(printf "${grep_match}" | sed -re "s/${r_parse}/\1/")) || die
suites_names=($(printf "${grep_match}" | sed -re "s/${r_parse}/\2/")) || die
testcases_names=($(printf "${grep_match}" | sed -re "s/${r_parse}/\3/")) || die

# Naming check.
total_failed_tc=0
total_failed_su=0
for idx in "${!testcases_names[@]}"; do
    for pass in "${!r_suite_rules[@]}"; do
        r_rule=$(printf '%s' "${r_suite_rules[@]:1:pass}")
        if [[ ! "${suites_names[idx]}" =~ ${r_rule} ]]; then
            msg=""
            msg+="${suites_dirs[idx]}/${suites_names[idx]} / "
            msg+="${testcases_names[idx]} ${s_suite_rules[pass]} "
            msg+="is not matching suite naming rule!"
            echo "${msg}" | tee -a "tc_naming.log" || die
            total_failed_su=$((total_failed_su + 1))
            break
        fi
    done
    for pass in "${!r_testc_rules[@]}"; do
        r_rule=$(printf '%s' "${r_testc_rules[@]:1:pass}")
        if [[ ! "${testcases_names[idx]}" =~ ${r_rule} ]]; then
            msg=""
            msg+="${suites_dirs[idx]}/${suites_names[idx]} / "
            msg+="${testcases_names[idx]} ${s_testc_rules[pass]} "
            msg+="is not matching testcase naming rule!"
            echo "${msg}" | tee -a "tc_naming.log" || die
            total_failed_tc=$((total_failed_tc + 1))
            break
        fi
    done
done

set -x

if [ $((total_failed_tc + total_failed_su)) != "0" ]; then
    warn
    warn "Testcase naming checker: FAIL"
    exit 1
fi

warn
warn "Testcase naming checker: PASS"
