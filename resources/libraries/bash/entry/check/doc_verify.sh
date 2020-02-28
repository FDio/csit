#!/usr/bin/env bash

# Copyright (c) 2019 Cisco and/or its affiliates.
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

set -xeuo pipefail

# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

common_dirs || die
log_file="$(pwd)/doc_verify.log" || die

# Pre-cleanup.
rm -f "${log_file}" || die
rm -f "${DOC_GEN_DIR}/csit.docs.tar.gz" || die
rm -rf "${DOC_GEN_DIR}/_build" || die

# Documentation generation.
# Here we do store only stderr to file while stdout (inlcuding Xtrace) is
# printed to console. This way we can track increased errors in future.
# We do not need to do trap as the env will be closed after tox finished the
# task.
exec 3>&1 || die
export BASH_XTRACEFD="3" || die

pushd "${DOC_GEN_DIR}" || die
source ./run_doc.sh ${GERRIT_BRANCH:-local} 2> ${log_file} || true
popd || die

if [[ ! -f "${log_file}" ]] || [[ -s "${log_file}" ]]; then
    # Output file not exists or is non empty.
    warn
    warn "Doc verify checker: FAIL"
    exit 1
fi

warn
warn "Doc verify checker: PASS"
