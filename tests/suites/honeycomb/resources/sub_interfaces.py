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

"""Test variables for Honeycomb sub-interface test suite."""

# Bridge domain name.
bd_name = 'test-sub-bd'

# Bridge domain configuration used while adding the bridge domain to a
# sub-interface.
sub_bd_settings = {
    'bridge-domain': bd_name,
    'split-horizon-group': '0',
    'bridged-virtual-interface': 'False'
}

# Rewrite tag parameters used while setting the rewrite tag.
rw_params = {
    'rewrite-operation': 'pop-1',
    'first-pushed': '802dot1ad',
    'tag1': '1',
    'tag2': '2'
}

# Rewrite tag parameters used while editing the rewrite tag.
rw_params_edited = {
    'rewrite-operation': 'push-1',
    'first-pushed': '802dot1q',
    'tag1': '12',
    'tag2': '22'
}

# Rewrite tag parameters when it is disabled.
rw_params_disabled = {
    'rewrite-operation': 'disabled',
    'first-pushed': '802dot1ad'
}

# Rewrite tag parameters - wrong value of 'rewrite-operation' parameter.
# Used in negative test.
rw_params_wrong_op = {
    'rewrite-operation': 'WRONG_OP',
    'first-pushed': '802dot1q',
    'tag1': '1',
    'tag2': '2'
}

# Rewrite tag parameters - wrong value of 'first-pushed' parameter.
# Used in negative test.
rw_params_wrong_pushed = {
    'rewrite-operation': 'pop-1',
    'first-pushed': 'WRONG_PUSHED',
    'tag1': '1',
    'tag2': '2'
}

# Second bridge domain name.
bd2_name = 'test-sub-bd2'
bd2_settings = {
    'bridge-domain': bd2_name,
    'split-horizon-group': '0',
    'bridged-virtual-interface': 'False'
}

# Second bridge domain configuration used while adding the bridge domain to a
# sub-interface.
bd2_conf = {
    'flood': True,
    'forward': True,
    'learn': True,
    'unknown-unicast-flood': True,
    'arp-termination': True
}

# Parameters of a bridge domain with rewrite tag.
bd_rw_settings = {
    'bridge-domain': bd2_name,
    'split-horizon-group': '0',
    'bridged-virtual-interface': 'False',
    'vlan-tag-rewrite': rw_params
}
