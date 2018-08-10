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

function activate_virtualenv () {

    set -exuo pipefail

    # Arguments:
    # - ${1} - Non-empty path to existing directory for creating virtualenv in.
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - ENV_DIR - Path to the created virtualenv subdirectory.
    # Variables exported:
    # - PYTHONPATH - CSIT_DIR, as CSIT Python scripts usually need this.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    if [[ "${1-}" == "" ]]; then
        die 1 "Root location of virtualenv to create is not specified."
    fi
    ENV_DIR="${1}/env"
    rm -rf "${ENV_DIR}" || die 1 "Failed to clean previous virtualenv."

    pip install --upgrade virtualenv || {
        die 1 "Virtualenv package install failed."
    }
    virtualenv --system-site-packages "${ENV_DIR}" || {
        die 1 "Virtualenv creation failed."
    }
    set +u
    source "${ENV_DIR}/bin/activate" || die 1 "Virtualenv activation failed."
    set -u
    pip install -r "${CSIT_DIR}/requirements.txt" || {
        die 1 "CSIT requirements installation failed."
    }

    # Most CSIT Python scripts assume PYTHONPATH is set and exported.
    export PYTHONPATH="${CSIT_DIR}" || die 1 "Export failed."
}
