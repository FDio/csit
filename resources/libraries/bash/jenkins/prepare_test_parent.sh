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

# Bash script fragment, to be sourced from main.sh

set -exuo pipefail

cd "${VPP_DIR}"
rm -rf csit_new
mkdir -p csit_new
for filename in output.xml log.html report.html; do
    mv "csit/${filename}" "csit_new/${filename}"
done
source "${BASH_LIBRARY_DIR}/parse_bmrr_results.sh" csit_new

# TODO: Also handle archive/ and make job archive everything useful.
( cd "${CSIT_DIR}" && git reset --hard HEAD && git clean -dffx )
mkdir -p "${ARCHIVE_DIR}" "${DOWNLOAD_DIR}"

cp build_parent/*.deb "${DOWNLOAD_DIR}"
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s csit csit_parent
