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
# - DOWNLOAD_DIR - Path to directory where Robot takes builds to test from.
# Directories read:
# - build-root - Existing directory with built VPP artifacts (including DPDK).
# Directories updated:
# - build_parent - Old directory removed, build-root moved to become this.
# - ${DOWNLOAD_DIR} - Old content removed, files from build_new copied here.
# - csit_new - Currently a symlink to csit/ to archive robot results on failure.

cd ${VPP_DIR}
rm -rf build_parent
mv build-root build_parent
rm -rf "${DOWNLOAD_DIR}"/*
cp build_new/*.deb "${DOWNLOAD_DIR}"
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s csit csit_new
