#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
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



sudo apt-get -y install python-virtualenv

virtualenv --system-site-packages env
. env/bin/activate
pip install -r requirements.txt

cat > mock.robot <<EOF
*** test cases ***
| Temoporary placeholder test for multilink
| | log | nothing here to see
EOF

pybot mock.robot


exit 0
