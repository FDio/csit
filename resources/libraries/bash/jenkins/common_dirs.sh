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

# Typically this cripts is sourced from another script:
# source "${BASH_LIBRARY_DIR}/common_dirs.sh"

BASH_LIBRARY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
CSIT_DIR=$(readlink -e "${BASH_LIBRARY_DIR}/../../../..")
RESOURCES_DIR=$(readlink -e "${CSIT_DIR}/resources")
TOOLS_DIR=$(readlink -e "${RESOURCES_DIR}/tools")
PYTHON_SCRIPTS_DIR=$(readlink -e "${TOOLS_DIR/scripts")

ARCHIVE_DIR=$(readlink -e "${CSIT_DIR}/archives")
mkdir -p "${ARCHIVE_DIR}"
