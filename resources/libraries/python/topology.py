# Copyright (c) 2015 Cisco and/or its affiliates.
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

#Defines nodes and topology structure.

__all__ = ["DICT__nodes"]


class NodeType(object):
    #Device Under Test (this node has VPP running on it)
    DUT = 'DUT'
    #Traffic Generator (this node has traffic generator on it)
    TG = 'TG'

MOCK_DATA_FOR_NOW = {
        'nodes' : {
            'DUT1' : {
                'type' : NodeType.DUT,
                'host' : '',
                'port' : 22,
                'username' : '',
                'password' : '',
                'priv_key' : 'file_path',
                'interfaces' : {
                    'port1' : 'eth1',
                    'port2' : 'Gigabit.fds.fas',
                    }
                },
            'DUT2' : {
                'type' : NodeType.DUT,
                'host' : '',
                'port' : 22,
                'username' : '',
                'password' : '',
                },
            'TG' : {
                'type' : NodeType.TG,
                'host' : '',
                'port' : 22,
                'username' : '',
                'password' : '',
                },
            }
        }

DICT__nodes = MOCK_DATA_FOR_NOW['nodes']

