#!/usr/bin/env bash

# Copyright (c) 2019 Cisco and/or its affiliates.
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

# This is a launcher script, to be called from Jenkins.
# It runs tox at $CSIT_DIR (after activating virtualenv with its requirements).
# Exit code of tox is propagated.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs || die
cd "${CSIT_DIR}" || die
activate_virtualenv "${CSIT_DIR}" "${CSIT_DIR}/tox-requirements.txt" || die
# Verbosity is increased so console output shows any unwanted downloads.
tox -vv  # Return code is turned into Jenkins job vote.
