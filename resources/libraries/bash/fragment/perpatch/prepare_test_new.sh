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

function prepare_test_new () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to existing directory, parent of accessed directories.
    # - DOWNLOAD_DIR - Path to directory where Robot takes builds to test from.
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # Directories read:
    # - build-root - Existing directory with built VPP artifacts (also DPDK).
    # Directories updated:
    # - build_parent - Old directory removed, build-root moved to become this.
    # - ${DOWNLOAD_DIR} - Old content removed, files from build_new copied here.
    # - csit_new - Currently a symlink to to archive robot results on failure.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    cd "${VPP_DIR}" || die 1 "Change directory operationf failed."
    rm -rf "build_parent" "csit_new" "${DOWNLOAD_DIR}"/* || die 1 "Rm failed."
    mkdir -p "build_parent" || die 1 "Directory creation operation failed."
    mv "build-root"/*".deb" "build_parent"/ || die 1 "Move operation failed."
    cp "build_new"/*".deb" "${DOWNLOAD_DIR}" || die 1 "Copy operation failed."
    # Create symlinks so that if job fails on robot, results can be archived.
    ln -s "${ARCHIVE_DIR}" "csit_new" || die 1 "Symbolic link creation failed."
}
