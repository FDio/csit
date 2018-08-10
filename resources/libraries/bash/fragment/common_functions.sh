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
# - PYTHON_SCRIPTS_DIR - Path to directory holding Python scripts.
# Functions defined:
# - warn
# - die
# - cancel_all

function warn () {
    # Prints the message to standard error.
    echo "$@" >&2
}

function die () {
    # Prints the message to standard error end exit with error code specified
    # by first argument.
    set -x
    set +eu
    status="$1"
    shift
    warn "$@"
    exit "${status}"
}

function cancel_all () {
    # Trap function to get into consistent state.
    set -xo pipefail
    set +eu  # We do not want to exit early in a "teardown".
    python "${PYTHON_SCRIPTS_DIR}/topo_cleanup.py" -t "$1"
    python "${PYTHON_SCRIPTS_DIR}/topo_reservation.py" -c -t "$1"
    set -eu
}
