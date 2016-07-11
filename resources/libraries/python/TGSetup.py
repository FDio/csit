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

"""TG Setup library."""

from resources.libraries.python.topology import NodeType
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class TGSetup(object):  # pylint: disable=too-few-public-methods
    """TG setup before test."""

    @staticmethod
    def all_tgs_set_interface_default_driver(nodes):
        """Setup interfaces default driver for all TGs in given topology.

        :param nodes: Nodes in topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.TG:
                InterfaceUtil.tg_set_interfaces_default_driver(node)
