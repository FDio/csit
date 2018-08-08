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

RESERVATION_DIR="/tmp/reservation_dir"

while true; do
    for TOPOLOGY in ${TOPOLOGIES};
    do
        python "${PYTHON_SCRIPTS_DIR}/topo_reservation.py" -t ${TOPOLOGY}
        if [[ "$?" != "0" ]]; then
            WORKING_TOPOLOGY=${TOPOLOGY}
            echo "Reserved: ${WORKING_TOPOLOGY}"
            # On script exit we clean testbed.
            trap "cancel_all ${WORKING_TOPOLOGY}" EXIT
            break
        fi
    done

    if [ -n "${WORKING_TOPOLOGY}" ]; then
        # Exit the infinite while loop if we made a reservation.
        break
    fi

    # Wait ~3minutes before next try.
    SLEEP_TIME=$[ ( $RANDOM % 20 ) + 180 ]s
    echo "Sleeping ${SLEEP_TIME}"
    sleep ${SLEEP_TIME}
done
