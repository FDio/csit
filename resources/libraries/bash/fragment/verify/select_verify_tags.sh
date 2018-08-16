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

# Variables read:
# - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
# - TEST_CODE - String affecting test selection, usually jenkins job name.
# - TEST_TAG_STRING - String selecting tags, from gerrit comment. Can be unset.
# Variables set:
# - TAGS - Array of processed tag boolean expressions.

# NIC SELECTION
# All topologies NICs
available_nics=($(grep -hoPR "model: \K.*" topologies/available/* | sort -u))
# Selected topology NICs
reserved_nics=($(grep -hoPR "model: \K.*" ${WORKING_TOPOLOGY} | sort -u))
# All topologies NICs - Selected topology NICs
exclude_nics=($(comm -13 <(printf '%s\n' "${reserved_nics[@]}") <(printf '%s\n' "${available_nics[@]}")))

case "$TEST_CODE" in
    # Select specific performance tests based on jenkins job type variable.
    *ndrpdr-weekly* )
        test_tag_array=("ndrpdrANDnic_intel-x520-da2AND1c"
                        "ndrpdrANDnic_intel-x520-da2AND2c"
                        "ndrpdrAND1cANDipsec"
                        "ndrpdrAND2cANDipsec")
        ;;
    *ndrpdr-timed* )
        ;;
    *mrr-daily* )
        test_tag_array=("mrrAND64bAND1c"
                        "mrrAND64bAND2c"
                        "mrrAND64bAND4c"
                        "mrrAND78bAND1c"
                        "mrrAND78bAND2c"
                        "mrrAND78bAND4c"
                        "mrrANDimixAND1cANDvhost"
                        "mrrANDimixAND2cANDvhost"
                        "mrrANDimixAND4cANDvhost"
                        "mrrANDimixAND1cANDmemif"
                        "mrrANDimixAND2cANDmemif"
                        "mrrANDimixAND4cANDmemif")
        ;;
    * )
        if [[ -z "${TEST_TAG_STRING-}" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            test_tag_array=("mrrANDnic_intel-x710AND1cAND64bANDip4base"
                            "mrrANDnic_intel-x710AND1cAND78bANDip6base"
                            "mrrANDnic_intel-x710AND1cAND64bANDl2bdbase")
        else
            # If trigger contains tags, split them into array.
            test_tag_array=(${TEST_TAG_STRING//:/ })
        fi
        ;;
esac

# We will add excluded NICs.
test_tag_array+=("${exclude_nics[@]/#/!NIC_}")

TAGS=()

# We will prefix with perftest to prevent running other tests
# (e.g. Functional).
prefix="perftestAND"
if [[ ${TEST_CODE} == vpp-* ]]; then
    # Automatic prefixing for VPP jobs to limit the NIC used and
    # traffic evaluation to MRR.
    prefix="${prefix}mrrANDnic_intel-x710AND"
fi
for TAG in "${test_tag_array[@]}"; do
    if [[ ${TAG} == "!"* ]]; then
        # Exclude tags are not prefixed.
        TAGS+=("${TAG}")
    else
        TAGS+=("$prefix${TAG}")
    fi
done
