#!/usr/bin/env bash

# Copyright (c) 2021 Cisco and/or its affiliates.
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


function generate_report () {

    # Generate report content
    #
    # Variable read:
    # - ${TOOLS_DIR} - Path to existing resources subdirectory "tools".
    # - ${GERRIT_BRANCH} - Path to existing resources subdirectory "tools".
    # Variables set:
    # - REPORT_EXIT_STATUS - Exit status of report generation.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${TOOLS_DIR}"/presentation || die "Pushd failed!"

    # Set default values in config array.
    typeset -A CFG
    typeset -A DIR

    DIR[WORKING]="_tmp"

    # Create working directories.
    mkdir "${DIR[WORKING]}" || die "Mkdir failed!"

    export PYTHONPATH=`pwd`:`pwd`/../../../ || die "Export failed!"

    set +e
    python pal.py \
        --specification specifications/report \
        --release "${GERRIT_BRANCH:-master}" \
        --week "28" \
        --logging INFO \
        --force

    REPORT_EXIT_STATUS="$?"
    set -e

}

function die_on_report_error () {

    # Source this fragment if you want to abort on any failure.
    #
    # Variables read:
    # - REPORT_EXIT_STATUS - Set by a report generation function.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if [[ "${REPORT_EXIT_STATUS}" != "0" ]]; then
        die "Failed to generate report!" "${REPORT_EXIT_STATUS}"
    fi
}
