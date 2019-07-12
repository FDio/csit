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

set -euo pipefail

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
# auto-generation or not checked at all.
r_grep="tc01-"
# Parse grep of interest (learn path, learn suite, learn testcase name).
r_parse='(.*)\/(.*).robot.*(tc[[:digit:]]{2}-.*)'

# CSIT Testcase naming convention 1st pass.
# https://wiki.fd.io/view/CSIT/csit-test-naming
r_testc_check=''
r_testc_check+='^tc[[:digit:]]{2}-'
# Packet size.
r_testc_check+='([[:digit:]]{2,4}B|IMIX)-'
# Core combination is optional.
r_testc_check+='([[:digit:]]+c-){0,1}'
# NIC settings.
r_testc_check+='(avf-|1lbvpplacp-|2lbvpplacp-){0,1}'
# TODO: Traffic description (here majority of TC are failing).
#r_testc_check+='(eth|dot1q|dot1ad)'
#r_testc_check+='(ip4|ip6|ip6ip6)'
#r_testc_check+='(ipsec[[:digit:]]+tnlhw|ipsec[[:digit:]]+tnlsw|icmpv4|icmpv6|'
#r_testc_check+='srhip6|tcp|udp|lispip6|lispip4|vxlan){0,1}'
#r_testc_check+='(http){0,1}-'
# Test type at the end.
r_testc_check+='(.*)-(dev|ndrpdr|cps)$'

# Grep interest.
grep_match=$(grep -RE "${r_grep}" tests/*) || die
# Extract data from the grep output.
suites_dirs=($(printf "${grep_match}" | sed -re "s/${r_parse}/\1/")) || die
suites_names=($(printf "${grep_match}" | sed -re "s/${r_parse}/\2/")) || die
testcases_names=($(printf "${grep_match}" | sed -re "s/${r_parse}/\3/")) || die

# Naming check
failed=0
for i in "${!testcases_names[@]}"; do
    [[ "${testcases_names[i]}" =~ ${r_testc_check} ]]  || \
        echo "${suites_names[i]}" / "${testcases_names[i]}" \
            "is not matching naming convention!"
        ((failed++))
done

if [ "${failed}" != "0" ]; then
    warn
    warn "Testcase naming checker: FAIL"
    exit 1
fi

warn
warn "Testcase naming checker: PASS"
