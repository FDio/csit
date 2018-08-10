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

function unreserve_testbed () {

    set -exuo pipefail

    # Variables read:
    # - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
    # Trap unregistered:
    # - EXIT
    # Functions called:
    # - cancel_all - Call unregistration script, defined in common_functions.sh
    # - die - Print to stderr and exit, defined in common_functions.sh

    trap - EXIT || echo "Trap deactivation failed, continuing anyway."
    cancel_all "${WORKING_TOPOLOGY}" || die 2 "UNRESERVE FAILED. REPAIR MANUALLY."
}
