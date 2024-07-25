# Copyright (c) 2024 Cisco and/or its affiliates.
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
set +x

# This tool saves time for RCA after release.

# First argument: Jenkins job to analyze.
# Second argument: Pattern to looks for (e.g. identifying release instead of RC2).

# For each run, this script prints hints on whether skip or look deeper.

jobname="${1}"
build_pattern="${2}"
# TODO: Detect last run and go backward?
for i in {1..999}; do
    if ! curl -sf "${jobname}/${i}/console.log.gz" | zcat > "console.log"; then
        echo "${i}: failed to download. No more runs?"
        exit 0
    fi
    if ! fgrep -q "${build_pattern}" "console.log"; then
        echo "${i}: not matching the pattern, skip."
        continue
    fi
    if ! grep '.* tests, .* passed, .* failed' "console.log" > "tests.txt"; then
        echo "${i}: no tests run? suspicious."
        continue
    fi
    final=$(tail -1 "tests.txt" | tee "final.txt")
    if fgrep -q ', 0 failed' "final.txt"; then
        echo -ne "${i}: skip ${final}\t\t"
    else
        echo -ne "${i}: investigate ${final}\t\t"
    fi
    # Detecting host based on calibration wait loop.
    fgrep 'RETRYING' "console.log" | tail -1 | grep -o '\[.*\]'
done
