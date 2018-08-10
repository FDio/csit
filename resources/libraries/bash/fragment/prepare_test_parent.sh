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
# - VPP_DIR - Path to existing directory, parent of accessed directories.
# - BASH_FRAGMENT_DIR - Path to directory holding parser script.
# - CSIT_DIR - Path to directory with root of local CSIT git repository.
# - ARCHIVE_DIR and DOWNLOAD_DIR - Paths to directories to update.
# Directories read:
# - build_parent - Build artifacts (to test next) are copied from here.
# Directories updated:
# - csit_new - Deleted, then recreated and latest robot results copied here.
# - ${CSIT_DIR} - Subjected to git reset and git clean.
# - ${ARCHIVE_DIR} - Created if not existing (might be deleted by git clean).
# - ${DOWNLOAD_DIR} - Created after git clean, parent build atrifacts copied here.
# - csit_parent - Currently a symlink to csit/ to archive robot results.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

cd "${VPP_DIR}"
rm -rf csit_new
mkdir -p csit_new
for filename in output.xml log.html report.html; do
    mv "csit/${filename}" "csit_new/${filename}"
done
source "${BASH_FRAGMENT_DIR}/parse_bmrr_results.sh" csit_new

# TODO: Also handle archive/ and make job archive everything useful.
( cd "${CSIT_DIR}" && git reset --hard HEAD && git clean -dffx ) || {
    die 1 "Something went wrong with CSIT reset."
}
mkdir -p "${ARCHIVE_DIR}" "${DOWNLOAD_DIR}"

cp build_parent/*.deb "${DOWNLOAD_DIR}"/
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s csit csit_parent
