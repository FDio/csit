#!/usr/bin/env bash

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

# This file does not have executable flag nor shebang.
# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.

set -exu

set +e
PYTHONPATH=`pwd` pylint --rcfile=pylint.cfg resources/ tests/ > pylint.log
STATUS="$?"
set -e

if [ "$STATUS" != "0" ]; then
    echo "Pylint exited with nonzero status: $STATUS"
    ## TODO: Enable when output size does more good than harm.
    # cat pylint.log
    echo
    echo "Pylint checker: FAIL"
    exit 1
fi

echo
echo "Pylint checker: PASS"
