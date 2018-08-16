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
# - TEST_CODE - String affecting test selection, usually jenkins job name.
# - BASH_FRAGMENT_DIR - Path to directory holding specialized gather scripts.
# Variables set:
# - DUT - CSIT test/ subdirectory containing suites to execute.
# Directories updated:
# - ${DOWNLOAD_DIR} - Files needed by tests are gathered here.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh
# Multiple other side effects are possible,
# see fragments sourced from here for their current description.

pushd "${DOWNLOAD_DIR}"
case "$TEST_CODE" in
    *hc2vpp*)
        DUT="hc2vpp"
        ;;
    *vpp*)
        DUT="vpp"
        source "${BASH_FRAGMENT_DIR}/verify/gather_vpp.sh"
        ;;
    *ligato*)
        DUT="kubernetes"
        source "${BASH_FRAGMENT_DIR}/verify/gather_ligato.sh"
        ;;
    *dpdk*)
        DUT="dpdk"
        source "${BASH_FRAGMENT_DIR}/verify/gather_dpdk.sh"
        ;;
    *)
        die 1 "Unable to identify DUT type from: ${TEST_CODE}!"
        ;;
esac
popd
