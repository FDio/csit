# Copyright (c) 2022 Cisco and/or its affiliates.
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

# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# This script starts with copying ${CSIT_DIR}/docs/model/current/schema
# to a temporary directory, then it calls yaml2json.py there,
# and finally it uses diff to see if the content is different
# from the original schema. If the diff (logged into yaml2json.log)
# is non-empty, the checker fails.

# In the future we may have more instances of json generated from yaml
# (e.g. not only for model schemas), so the checker does not mention schema,
# even though that is the only currently checked target directory.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs
work_dir="$(pwd)" || die
trap "cd '${work_dir}'" EXIT || die

origdir="${CSIT_DIR}/docs/model/current/schema"
tmpdir="${GENERATED_DIR}/schema_tmp"
logf="${CSIT_DIR}/yaml2json.log"
rm -rf "${tmpdir}" || die "Failed to remove existing temporary directory."
mkdir -p "${tmpdir}" || die "Failed to create temporary directory."
pushd "${tmpdir}" || die
    cp -r "${origdir}/"* "." || die "Failed to copy from schema directory."
    python3 "./yaml2json.py" || die "Failed to call yaml2json script."
    # Diff returns RC=1 if output is nonzero.
    lines="$(diff -pudr "${origdir}" "." | tee "${logf}" | wc -l || true)"
popd || die
rm -rf "${tmpdir}" || die "Failed to remove used temporary directory."
if [ "${lines}" != "0" ]; then
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Yaml2json conflict, diff sees nonzero lines: ${lines}"
    # TODO: Disable if output size does more harm than good.
    cat "${logf}" >&2 || die
    warn
    warn "Yaml2json checker: FAIL"
    exit 1
fi

warn
warn "Yaml2json checker: PASS"
