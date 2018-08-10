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

# Variables set:
# - DUT - CSIT test/ subdirectory containing suites to execute.
# - TAGS - Array of processed tag boolean expressions.
# Hardcoded values:
# - List of tag expressions selecting few suites.
# - Prefix, selecting test type and NIC.

DUT="vpp"

# Hardcoded for perpatch. TODO: Make this configurable.
test_tag_array=("l2xcbaseAND1cAND64b"
                "l2bdbaseAND1cAND64b"
                "ip4baseAND1cAND64b"
                "ip6baseAND1cAND78b")
TAGS=()
# We will prefix with perftest to prevent running other tests
# (e.g. Functional).
prefix="perftestAND"
# Automatic prefixing for VPP jobs to limit the NIC used and
# traffic evaluation to MRR.
prefix="${prefix}mrrANDnic_intel-x710AND"
for TAG in "${test_tag_array[@]}"; do
    if [[ ${TAG} == "!"* ]]; then
        # Exclude tags are not prefixed.
        TAGS+=("${TAG}")
    else
        TAGS+=("${prefix}${TAG}")
    fi
done
