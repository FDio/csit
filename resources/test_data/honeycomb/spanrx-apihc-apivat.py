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

"""Test variables for spanrx apihc apivat func."""


def get_variables(node):

    interface1 = node['interfaces']['port1']['name']
    interface2 = node['interfaces']['port3']['name']
    interface3 = "local0"

    variables = {
        "interface1": interface1,
        "interface2": interface2,
        "interface3": interface3,
        "settings_1": {
            "state": "receive",
            "iface-ref": interface2,
        },

        "settings_2": {
            "state": "transmit",
            "iface-ref": interface2,
        },

        "settings_3": {
            "state": "both",
            "iface-ref": interface2,
        },

        "settings_4": {
            "state": "both",
            "iface-ref": interface3,
        },

        "tg_to_dut_if1_ip": "192.168.1.1",
        "dut_to_tg_if1_ip": "192.168.1.2",
        "prefix": 24,
    }
    return variables
