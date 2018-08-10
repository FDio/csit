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
# - WORKSPACE - Jenkins workspace, copy only happens if the value is not empty.
# - ARCHIVE_DIR - Path to directory with content to be copied.
# Directories updated:
# - ${WORKSPACE}/archives/ - Created if does not exist,
#   content of ${ARCHIVE_DIR}/ is copied here.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

# We will create additional archive if workspace variable is set. This way if
# script is running in jenkins all will be automatically archived to logs.fd.io.
if [[ -n "${WORKSPACE-}" ]]; then
    mkdir -p "${WORKSPACE}/archives/" || die 1 "Archives dir creation failed."
    cp -r "${ARCHIVE_DIR}"/* "${WORKSPACE}/archives/" || die 1 "Copy failed."
fi
