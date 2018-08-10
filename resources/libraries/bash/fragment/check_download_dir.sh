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

function check_download_dir () {

    set -exuo pipefail

    # Fail if there are no files visible in ${DOWNLOAD_DIR}.
    #
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # Directories read:
    # - ${DOWNLOAD_DIR} - Has to be non-empty to proceed.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    if [[ ! "$(ls -A ${DOWNLOAD_DIR})" ]]; then
        die 1 "No artifacts downloaded!"
    fi
}
