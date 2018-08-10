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
# - TOPOLOGIES - Array of paths to topology yaml to attempt reservation on.
# - PYTHON_SCRIPTS_DIR - Path to directory holding the reservation script.
# Variables set:
# - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh
# Traps registered:
# - EXIT - Calls cancel_all defined in common_functions.sh

while true; do
    for topology in "${TOPOLOGIES[@]}"; do
        set +e
        python "${PYTHON_SCRIPTS_DIR}/topo_reservation.py" -t "${topology}"
        result="$?"
        set -e
        if [[ "${result}" == "0" ]]; then
            WORKING_TOPOLOGY="${topology}"
            echo "Reserved: ${WORKING_TOPOLOGY}"
            # On script exit we clean testbed.
            trap "cancel_all ${WORKING_TOPOLOGY}" EXIT || {
                die 2 "SIGNAL TRAP FAILED. UNRESERVE TESTBED MANUALLY."
            }
            break
        fi
    done

    if [[ -n "${WORKING_TOPOLOGY-}" ]]; then
        # Exit the infinite while loop if we made a reservation.
        break
    fi

    # Wait ~3minutes before next try.
    sleep_time=$[ ( $RANDOM % 20 ) + 180 ]s || die 1 "Sleep calculation failed."
    echo "Sleeping ${sleep_time}"
    sleep ${sleep_time} || die 1 "Sleep failed."
done
