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

function set_perpatch_vpp_dir () {

    set -exuo pipefail

    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - VPP_DIR - Path to existing root of local VPP git repository.

    # In perpatch, CSIT is cloned inside VPP clone.
    VPP_DIR=$(readlink -e "${CSIT_DIR}/..") || die 1 "Readlink failed."
}
