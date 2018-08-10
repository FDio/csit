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

function common_dirs () {

    set -exuo pipefail

    # Written variables:
    # - BASH_FRAGMENT_DIR - Path to existing directory this file is located in.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - RESOURCES_DIR - Path to existing CSIT subdirectory "resources".
    # - TOOLS_DIR - Path to existing resources subdirectory "tools".
    # - PYTHON_SCRIPTS_DIR - Path to existing tools subdirectory "scripts".
    # - ARCHIVE_DIR - Path to created CSIT subdirectory "archive".
    # - DOWNLOAD_DIR - Path to created CSIT subdirectory "download_dir".

    # We rely on "set -e", as definition of "die" is not sourced yet.
    BASH_FRAGMENT_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
    CSIT_DIR=$(readlink -e "${BASH_FRAGMENT_DIR}/../../../..")
    RESOURCES_DIR=$(readlink -e "${CSIT_DIR}/resources")
    TOOLS_DIR=$(readlink -e "${RESOURCES_DIR}/tools")
    PYTHON_SCRIPTS_DIR=$(readlink -e "${TOOLS_DIR}/scripts")

    ARCHIVE_DIR=$(readlink -f "${CSIT_DIR}/archive")
    mkdir -p "${ARCHIVE_DIR}"
    DOWNLOAD_DIR=$(readlink -f "${CSIT_DIR}/download_dir")
    mkdir -p "${DOWNLOAD_DIR}"
}
