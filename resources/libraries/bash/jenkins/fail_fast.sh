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

# Source this fragment if you want to abort on any failed test case.
#
# Variables read:
# - PYBOT_RETURN_STATUS - Set by pybot running fragment.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

if [[ "${PYBOT_RETURN_STATUS}" != "0" ]]; then
    die "${PYBOT_RETURN_STATUS}" "Test failures are present!"
fi
