# Copyright (c) 2023 Cisco and/or its affiliates.
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

set -xuo pipefail

logs_fd_io="dc7f1y83kdjnx.cloudfront.net"
JOB_NAME="csit-vpp-perf-verify-master-2n-clx"
URL_BASE="https://${logs_fd_io}/vex-yul-rot-jenkins-1/$JOB_NAME"
wget -N "${URL_BASE}"
for run in `grep -o '"[0-9]*/index\.html"' "${JOB_NAME}" | cut -d '"' -f 2 | cut -d '/' -f 1 | sort -un`; do
    if [[ $run -le 1119 ]]; then
        continue
    fi
    mkdir -p "${run}"
    pushd "${run}"
    if [[ ! -f "console-timestamp.log.gz" ]]; then
        wget -N "${URL_BASE}/${run}/console-timestamp.log.gz" || true
    fi
    if [[ ! -f "timing.txt" ]]; then
        if [[ -f "console-timestamp.log.gz" && ! -f "console-timestamp.log" ]]; then
            gunzip -k "console-timestamp.log.gz"
        fi
        if [[ -f "console-timestamp.log" ]]; then
            grep 'Checking out Revision\|B-1c-rdma-\|DR_LOWER: \|packets\|established\|Minimal load is an upper bound' console-timestamp.log > "timing.txt"
        fi
    fi
    if [[ -f "console-timestamp.log" ]]; then
        rm "console-timestamp.log"
    fi
    popd
done
