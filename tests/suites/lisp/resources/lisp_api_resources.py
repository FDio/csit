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

"""Test variables for Lisp API test suite."""

"""Lisp status example test data."""
lisp_status = [{"gpe_status":"disabled",
                "feature_status":"disabled"},
               {"gpe_status":"enabled",
                "feature_status":"enabled"}]

"""Example lisp local eid we want set to VPP
and then check if is set correct."""
eid_table = [{'eid': '192.168.0.1',
              'vni': 0,
              'eid-prefix-len': 24,
              'locator-set': 'ls1'},
             {'eid': '192.168.1.1',
              'vni': 0,
              'eid-prefix-len': 24,
              'locator-set': 'ls1'},
             {'eid': '192.168.2.1',
              'vni': 0,
              'eid-prefix-len': 24,
              'locator-set': 'ls1'},
             {'eid': '192.168.3.1',
              'vni': 0,
              'eid-prefix-len': 24,
              'locator-set': 'ls1'},
             {'eid': '10:1::1',
              'vni': 0,
              'eid-prefix-len': 32,
              'locator-set': 'ls1'},
             {'eid': '10:2::1',
              'vni': 0,
              'eid-prefix-len': 32,
              'locator-set': 'ls1'},
             {'eid': '10:3::1',
              'vni': 0,
              'eid-prefix-len': 32,
              'locator-set': 'ls1'}]

"""Example lisp map resolvers data we want set to VPP
and then check if is set correct."""
map_resolver = [{'map resolver': '192.169.0.1'},
                {'map resolver': '192.169.1.1'},
                {'map resolver': '192.169.2.1'},
                {'map resolver': '12:1::1'},
                {'map resolver': '12:2::1'}]
