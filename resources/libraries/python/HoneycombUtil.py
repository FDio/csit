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

"""Implements low level functionality used in communication with Honeycomb."""

import os.path
from json import loads

from robot.api import logger

from resources.libraries.python.HTTPRequest import HTTPRequest
from resources.libraries.python.constants import Constants as Const


class HoneycombUtil(object):
    """Implements low level functionality used in communication with Honeycomb.
    """

    def __init__(self):
        pass

    @staticmethod
    def read_path_from_url_file(url_file):
        """Read path from *.url file.

        The *.url file is a text file (encoding utf-8) with a path to a resource
        on honeycomb. There is only one line in each file.
        :param url_file: A text file with url without IP and port on one line,
        e.g.: /restconf/config/v3po:vpp/bridge-domains.
        The argument contains only the name of file without extension, not the
        full path.
        :type url_file: str
        :return: Requested path.
        :rtype: str
        """
        url = os.path.join(Const.RESOURCES_TPL_HC, "{}.url".format(url_file))
        with open(url) as template:
            path = template.readline()
        return path

    @staticmethod
    def parse_json_response(response, path=None):
        """Parse data from response string in JSON format according to given
        path.

        :param response: JSON formatted string.
        :param path: Path to navigate down the data structure.
        :type response: string
        :type path: tuple
        :return: JSON dictionary/list tree.
        :rtype: list, dict or str
        """
        data = loads(response)

        if path:
            data = HoneycombUtil._parse_json_tree(data, path)

        return data

    @staticmethod
    def _parse_json_tree(data, path):
        """Retrieve data from python representation of JSON object.

        :param data: Parsed JSON dictionary tree.
        :param path: Path to navigate down the dictionary tree.
        :type data: dict
        :type path: tuple
        :return: Data from specified path.
        :rtype: list, dict or str
        """

        count = 0
        for key in path:
            if isinstance(data, dict):
                data = data[key]
                count += 1
            elif isinstance(data, list):
                result = []
                for item in data:
                    result.append(HoneycombUtil._parse_json_tree(item,
                                                                 path[count:]))
                    return result
        return data

    @staticmethod
    def get_honeycomb_data(node, url_file):
        """Retrieve data from Honeycomb according to given URL.

        :param node: Honeycomb node.
        :param url_file: Text file with url without IP and port on one line,
        e.g.: /restconf/config/v3po:vpp/bridge-domains.
        The argument contains only the name of file without extension, not the
        full path.
        :type node: dict
        :type url_file: str
        :return: Requested information.
        :rtype list
        """

        path = HoneycombUtil.read_path_from_url_file(url_file)
        status_code, resp = HTTPRequest.get(node, path)

        logger.debug('return: {0}'.format(resp))

        return status_code, resp

    @staticmethod
    def set_honeycomb_data(node, url_file, data):
        """Send configuration data using PUT request and return the status code
        and response.

        :param node: Honeycomb node.
        :param url_file: Text file with url without IP and port on one line,
        e.g.: /restconf/config/v3po:vpp/bridge-domains.
        The argument contains only the name of file without extension, not the
        full path.
        :param data: Configuration data to be sent to honeycomb.
        :type node: dict
        :type url_file: str
        :type data: JSON formatted string.
        :return: Status code and content of response.
        :rtype: tuple
        """

        logger.debug(data)

        path = HoneycombUtil.read_path_from_url_file(url_file)
        headers = {"Content-Type": "application/json",
                   'Accept': 'text/plain'}

        status_code, resp = HTTPRequest.put(node=node, path=path,
                                            headers=headers, payload=data)
        return status_code, resp

    @staticmethod
    def delete_honeycomb_data(node, url_file):
        """Delete data from Honeycomb according to given URL.

        :param node: Honeycomb node.
        :param url_file: Text file with url without IP and port on one line,
        e.g.: /restconf/config/v3po:vpp/bridge-domains.
        The argument contains only the name of file without extension, not the
        full path.
        :type node: dict
        :type url_file: str
        :return: Status code and response.
        :rtype tuple
        """

        path = HoneycombUtil.read_path_from_url_file(url_file)
        status_code, resp = HTTPRequest.delete(node, path)

        logger.debug('Return: {0}.'.format(resp))

        return status_code, resp
