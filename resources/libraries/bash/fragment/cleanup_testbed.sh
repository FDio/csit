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
# - PYTHON_SCRIPTS_DIR - Path to directory containing the cleanup script.
# - WORKING_TOPOLOGY - Path to topology yaml file of the reserved testbed.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

python "${PYTHON_SCRIPTS_DIR}/topo_cleanup.py" -t "${WORKING_TOPOLOGY}" || {
    die 1 "Cleanup script failed."
}
