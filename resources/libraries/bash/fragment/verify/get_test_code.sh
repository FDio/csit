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

# Arguments (inherited from the caller, otherwise shift would not work):
# - ${1} - Test code value if not specified from environment.
# Variables read:
# - JOB_NAME - String affecting test selection, usually jenkins job name.
# Variables set:
# - TEST_CODE - The test selection string from environment or argument.
# - NODENESS - Node multiplicity of desired testbed.
# - FLAVOR - Node flavor string, usually describing the processor.

TEST_CODE="${JOB_NAME-}"
if [[ -z "${TEST_CODE}" ]]; then
    TEST_CODE="${1}" || die 1 "Reading first argument failed."
    shift || die 1 "Shift failed."
fi

case "$TEST_CODE" in
    *2n-skx*)
        NODENESS="2n"
        FLAVOR="skx"
        ;;
    *3n-skx*)
        NODENESS="3n"
        FLAVOR="skx"
        ;;
    *)
        # Fallback to 3-node Haswell by default (backward compatibility)
        NODENESS="3n"
        FLAVOR="hsw"
        ;;
esac
