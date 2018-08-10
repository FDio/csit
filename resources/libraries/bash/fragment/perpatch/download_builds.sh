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

# This is mostly useful only for Sandbox testing, to avoid recompilation.
#
# ARGUMENTS:
# - ${1} - URL to download VPP builds from.
# Variables read:
# - VPP_DIR - Path to WORKSPACE, parent of created directories.
# - DOWNLOAD_DIR - Path to directory where pybot takes the build to test from.
# Directories created:
# - archive - Probably ends up empty, not to be confused with ${ARCHIVE_DIR}.
# - build_new - Holding built artifacts of the patch under test (PUT).
# - built_parent - Holding built artifacts of parent of PUT.
# - csit_new - (Re)set to a symlink to archive robot results on failure.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

cd "${VPP_DIR}" || die 1 "Change directory operation failed."
rm -rf "build-root" "build_parent" "build_new" "archive" "csit_new" || {
    die 1 "Directory removal failed."
}
wget -N --progress=dot:giga "${1}" || die 1 "Wget download failed."
unzip "archive.zip" || die 1 "Archive extraction failed."
mv "archive/build_parent" ./ || die 1 "Move operation failed."
mv "archive/build_new" ./ || die 1 "Move operation failed."
cp -r "build_new"/*".deb" "${DOWNLOAD_DIR}" || die 1 "Copy operation failed."
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s "${ARCHIVE_DIR}" "csit_new" || die 1 "Symbolic link creation failed."
