# Copyright (c) 2021 Cisco and/or its affiliates.
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

# This file should be executed from tox, as the assumed working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# This script checks if the number of tests in a job specification is the same
# as declared at the beginning of the file.
# It counts the lines not starting with '#' so it can also detect redundant
# empty lines, or lines which should not be in the job specification.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

# Disabling -x: Following lines are doing too much garbage output.
set +x

job_spec_dir="docs/job_specs/"
rm -f "job_spec.log" || die
violations=0

for f in $(find ${job_spec_dir} -type f | grep -v perf_tests_job_specs); do
    declared=$(fgrep "### tests" $f | tr -dc '0-9')
    present=$(fgrep -v '#' $f | wc -l)
    if [ "${declared}" != "${present}" ]; then
        echo "Wrong number of tests detected in ${f}: \
declared: ${declared} / present: ${present}" | tee -a job_spec.log
        violations=$((violations+1))
    fi
done

if [ "${violations}" != "0" ]; then
    warn
    warn "Number of tests in job spec checker: FAIL"
    exit 1
fi

warn
warn "Number of tests in job spec checker: PASS"
