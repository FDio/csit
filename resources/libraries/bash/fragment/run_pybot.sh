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

# Currently, VPP-1361 causes occasional test failures.
# If real result is more important than time, we can retry few times.
# TODO: We should be retrying on test case level instead.

# Arguments:
# - $1 - Number of pybot invocations to attempt to avoid failures. Default: 1.
# Variables read:
# - CSIT_DIR - Path to directory with root of local CSIT git repository.
# - ARCHIVE_DIR - Path to store robot result files in.
# - PYBOT_ARGS, EXPANDED_TAGS - See compose_pybot_arguments.sh
# Variables set:
# - PYBOT_EXIT_STATUS - Exit status of most recent pybot invocation.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

tries="${1:-1}"

while true; do
    if [[ "${tries}" -le 0 ]]; then
        break
    else
        tries=$((${tries} - 1))
    fi
    set +e  # Although, allegedly sub-shell invocation does not trigger -e.
    # TODO: Make robot tests not to require "$(pwd)" == "${CSIT_DIR}".
    pushd "${CSIT_DIR}" || die 1 "Change directory operation failed."
    pybot --outputdir ${ARCHIVE_DIR} ${PYBOT_ARGS}${EXPANDED_TAGS[@]} ${CSIT_DIR}/tests/
    PYBOT_EXIT_STATUS=$(echo "$?")
    popd || die 1 "Change directory operation failed."
    set -e
    if [[ "${PYBOT_EXIT_STATUS}" == "0" ]]; then
        break
    fi
done
