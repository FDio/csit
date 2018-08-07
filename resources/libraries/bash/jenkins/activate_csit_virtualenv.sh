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

ENV_DIR="${CSIT_DIR}/env"
rm -rf "${ENV_DIR}"

pip install --upgrade virtualenv || {
    die 1 "Failed to install virtual env!"
}
virtualenv --system-site-packages "${ENV_DIR}" || {
    die 1 "Failed to create virtual env!"
}
set +u
source "${ENV_DIR}/bin/activate" || {
    die 1 "Failed to activate virtual env!"
}
set -u
pip install -r "${CSIT_DIR}/requirements.txt" || {
    die 1 "Failed to install requirements to virtual env!"
}

# Robot related scripts assume PYTONPATCH is set and exported.
export PYTHONPATH="${CSIT_DIR}"
