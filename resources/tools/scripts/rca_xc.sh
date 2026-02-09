# Copyright (c) 2026 Cisco and/or its affiliates.
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

# Example usage:
# export job="csit-vpp-perf-report-iterative-2602-2n-aws"; bash rca_xc.sh "${job}" "26.02-rc1" | tee "{job}.txt"

# For each run, this script prints hints on whether skip or look deeper.
# Also testbeds are printed, to see possible correlations with failures.

job_name="${1}"
build_pattern="${2}"
url_prefix="https://logs.fd.io/vex-yul-rot-jenkins-1"
job_url="${url_prefix}/${job_name}"
cdir=`readlink -e .`
rm -f "index.html"
curl -sf "${job_url}/index.html" > "index.html"
for i in `grep -o '"[0-9]\+/index.html' index.html | cut -d '"' -f 2- | cut -d '/' -f 1 | sort -n`; do
    cd "${cdir}"
    target_dir="${cdir}/${job_name}/${i}"
    mkdir -p "${target_dir}"
    run_url="${job_url}/${i}"
    if [ -f "${target_dir}/console.log" ]; then
        continue
        #echo "Not skipping downloaded log during script debugging."
    fi
    job_id=$(gh api repos/FDio/CSIT/actions/runs/${i}/jobs --jq '.jobs[] | select(.name | contains("'"${job_name}"'")) | .id')
    if [[ "" == "${job_id}" ]]; then
        echo "Did not detect job id. What is wrong?"
        gh api repos/FDio/CSIT/actions/runs/${i}/jobs
        exit 1
    fi
    if ! gh run view --verbose --repo "FDio/csit" --job "${job_id}" --log > "${target_dir}/console.log"; then
        echo "${i}: failed to download console log. Aborted run?"
        continue
    fi
    if ! fgrep -q "${build_pattern}" "${target_dir}/console.log"; then
        echo "${i}: not matching the pattern. Skip."
        continue
    fi
    if ! grep '.* tests, .* passed, .* failed' "${target_dir}/console.log" > "${target_dir}/tests.txt"; then
        echo "${i}: no tests executed? Suspicious."
        continue
    fi

    #pushd "${target_dir}"
    #if ! curl -sf "${run_url}/log.html.gz" | zcat > "${target_dir}/log.html"; then
    #    echo "${i}: failed to download html log. Rebot crashed on out of memory?"
    #    popd
    #    continue
    #fi
    #python3 "${cdir}/tober.py" > "/dev/null"
    #popd

    final=$(tail -1 "${target_dir}/tests.txt" | tee "final.txt")
    if fgrep -q ', 0 failed' "final.txt"; then
        echo -ne "${i}: skip ${final}\t\t"
    else
        echo
        awk '
            /\| FAIL \|/ {
                if ($0 !~ /Tests/) {
                    print
                    getline
                    while ($0 !~ / [-=]+$/) {
                        last_line = $0
                        getline
                    }
                    print last_line
                }
            }
        ' "${target_dir}/console.log"
        echo -ne "${i}: investigate ${final}\t\t"
    fi

    # TODO: Simplify this topology detection.
    line=$(grep 'TOPOLOGY_PATH:' "${target_dir}/console.log")
    topology_path=`echo "$line" | sed -n 's/.*TOPOLOGY_PATH:\([^ ]*\).*/\1/p'`
    topology_name=$(basename "$topology_path" | sed 's/\.[^.]*$//')
    echo "$topology_name"
done
