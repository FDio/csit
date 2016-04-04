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

"""Implements keywords used with Honeycomb."""

import os.path
from json import loads

from robot.api import logger

from resources.libraries.python.topology import NodeType
from resources.libraries.python.HTTPRequest import HTTPRequest
from resources.libraries.python.constants import Constants as C


class HoneycombUtil(object):
    """Implements keywords used with Honeycomb."""

    def __init__(self):
        pass

    def get_configured_topology(self, nodes):
        """Retrieves topology node IDs from each honeycomb node.

        :param nodes: all nodes in topology
        :type nodes: dict
        :return: list of string IDs such as ['vpp1', 'vpp2']
        :rtype list
        """

        url_file = os.path.join(C.RESOURCES_TPL_HC, "config_topology.url")
        with open(url_file) as template:
            path = template.readline()

        data = []
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                _, ret = HTTPRequest.get(node, path)
                logger.debug('return: {0}'.format(ret))
                data.append(self.parse_json_response(ret, ("topology",
                                                           "node", "node-id")))

        return data

    def parse_json_response(self, response, path=None):
        """Parse data from response string in JSON format according to given
        path.

        :param response: JSON formatted string
        :param path: Path to navigate down the data structure
        :type response: string
        :type path: tuple
        :return: JSON dictionary/list tree
        :rtype: dict
        """
        data = loads(response)

        if path:
            data = self._parse_json_tree(data, path)
            while isinstance(data, list) and len(data) == 1:
                data = data[0]

        return data

    def _parse_json_tree(self, data, path):
        """Retrieve data from python representation of JSON object.

        :param data: parsed JSON dictionary tree
        :param path: Path to navigate down the dictionary tree
        :type data: dict
        :type path: tuple
        :return: data from specified path
        :rtype: list or str
        """

        count = 0
        for key in path:
            if isinstance(data, dict):
                data = data[key]
                count += 1
            elif isinstance(data, list):
                result = []
                for item in data:
                    result.append(self._parse_json_tree(item, path[count:]))
                    return result

        return data
