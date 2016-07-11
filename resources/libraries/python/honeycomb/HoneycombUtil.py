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

"""Implementation of low level functionality used in communication with
Honeycomb.

Exception HoneycombError is used in all methods and in all modules with
Honeycomb keywords.

Class HoneycombUtil implements methods used by Honeycomb keywords. They must not
be used directly in tests. Use keywords implemented in the module
HoneycombAPIKeywords instead.
"""

from json import loads, dumps
from enum import Enum, unique

from robot.api import logger

from resources.libraries.python.HTTPRequest import HTTPRequest
from resources.libraries.python.constants import Constants as Const


@unique  # pylint: disable=too-few-public-methods
class DataRepresentation(Enum):
    """Representation of data sent by PUT and POST requests."""
    NO_DATA = 0
    JSON = 1
    XML = 2
    TXT = 3


# Headers used in requests. Key - content representation, value - header.
HEADERS = {DataRepresentation.NO_DATA:
               {},  # It must be empty dictionary.
           DataRepresentation.JSON:
               {"Content-Type": "application/json",
                "Accept": "text/plain"},
           DataRepresentation.XML:
               {"Content-Type": "application/xml",
                "Accept": "text/plain"},
           DataRepresentation.TXT:
               {"Content-Type": "text/plain",
                "Accept": "text/plain"}
          }


class HoneycombError(Exception):

    """Exception(s) raised by methods working with Honeycomb.

    When raising this exception, put this information to the message in this
    order:
     - short description of the encountered problem (parameter msg),
     - relevant messages if there are any collected, e.g., from caught
       exception (optional parameter details),
     - relevant data if there are any collected (optional parameter details).
     The logging is performed on two levels: 1. error - short description of the
     problem; 2. debug - detailed information.
    """

    def __init__(self, msg, details='', enable_logging=True):
        """Sets the exception message and enables / disables logging.

        It is not wanted to log errors when using these keywords together
        with keywords like "Wait until keyword succeeds". So you can disable
        logging by setting enable_logging to False.

        :param msg: Message to be displayed and logged.
        :param enable_logging: When True, logging is enabled, otherwise
        logging is disabled.
        :type msg: str
        :type enable_logging: bool
        """
        super(HoneycombError, self).__init__()
        self._msg = "{0}: {1}".format(self.__class__.__name__, msg)
        self._details = details
        if enable_logging:
            logger.error(self._msg)
            logger.debug(self._details)

    def __repr__(self):
        return repr(self._msg)

    def __str__(self):
        return str(self._msg)


class HoneycombUtil(object):
    """Implements low level functionality used in communication with Honeycomb.

    There are implemented methods to get, put and delete data to/from Honeycomb.
    They are based on functionality implemented in the module HTTPRequests which
    uses HTTP requests GET, PUT, POST and DELETE to communicate with Honeycomb.

    It is possible to PUT the data represented as XML or JSON structures or as
    plain text.
    Data received in the response of GET are always represented as a JSON
    structure.

    There are also two supportive methods implemented:
    - read_path_from_url_file which reads URL file and returns a path (see
      docs/honeycomb_url_files.rst).
    - parse_json_response which parses data from response in JSON representation
      according to given path.
    """

    def __init__(self):
        pass

    @staticmethod
    def read_path_from_url_file(url_file):
        """Read path from *.url file.

        For more information about *.url file see docs/honeycomb_url_files.rst
        :param url_file: URL file. The argument contains only the name of file
        without extension, not the full path.
        :type url_file: str
        :return: Requested path.
        :rtype: str
        """

        url_file = "{0}/{1}.url".format(Const.RESOURCES_TPL_HC, url_file)
        with open(url_file) as template:
            path = template.readline()
        return path

    @staticmethod
    def find_item(data, path):
        """Find a data item (single leaf or sub-tree) in data received from
        Honeycomb REST API.

        Path format:
        The path is a tuple with items navigating to requested data. The items
        can be strings or tuples:
        - string item represents a dictionary key in data,
        - tuple item represents list item in data.

        Example:
        data = \
        {
            "interfaces": {
                "interface": [
                    {
                        "name": "GigabitEthernet0/8/0",
                        "enabled": "true",
                        "type": "iana-if-type:ethernetCsmacd",
                    },
                    {
                        "name": "local0",
                        "enabled": "false",
                        "type": "iana-if-type:ethernetCsmacd",
                    }
                ]
            }
        }

        path = ("interfaces", ("interface", "name", "local0"), "enabled")
        This path points to "false".

        The tuple ("interface", "name", "local0") consists of:
        index 0 - dictionary key pointing to a list,
        index 1 - key which identifies an item in the list, it is also marked as
                  the key in corresponding yang file.
        index 2 - key value.

        :param data: Data received from Honeycomb REST API.
        :param path: Path to data we want to find.
        :type data: dict
        :type path: tuple
        :return: Data represented by path.
        :rtype: str, dict, or list
        :raises HoneycombError: If the data has not been found.
        """

        for path_item in path:
            try:
                if isinstance(path_item, str):
                    data = data[path_item]
                elif isinstance(path_item, tuple):
                    for data_item in data[path_item[0]]:
                        if data_item[path_item[1]] == path_item[2]:
                            data = data_item
            except KeyError as err:
                raise HoneycombError("Data not found: {0}".format(err))

        return data

    @staticmethod
    def remove_item(data, path):
        """Remove a data item (single leaf or sub-tree) in data received from
        Honeycomb REST API.

        :param data: Data received from Honeycomb REST API.
        :param path: Path to data we want to remove.
        :type data: dict
        :type path: tuple
        :return: Original data without removed part.
        :rtype: dict
        """

        origin_data = previous_data = data
        try:
            for path_item in path:
                previous_data = data
                if isinstance(path_item, str):
                    data = data[path_item]
                elif isinstance(path_item, tuple):
                    for data_item in data[path_item[0]]:
                        if data_item[path_item[1]] == path_item[2]:
                            data = data_item
        except KeyError as err:
            logger.debug("Data not found: {0}".format(err))
            return origin_data

        if isinstance(path[-1], str):
            previous_data.pop(path[-1])
        elif isinstance(path[-1], tuple):
            previous_data[path[-1][0]].remove(data)
            if not previous_data[path[-1][0]]:
                previous_data.pop(path[-1][0])

        return origin_data

    @staticmethod
    def set_item_value(data, path, new_value):
        """Set or change the value (single leaf or sub-tree) in data received
        from Honeycomb REST API.

        If the item is not present in the data structure, it is created.

        :param data: Data received from Honeycomb REST API.
        :param path: Path to data we want to change or create.
        :param new_value: The value to be set.
        :type data: dict
        :type path: tuple
        :type new_value: str, dict or list
        :return: Original data with the new value.
        :rtype: dict
        """

        origin_data = data
        for path_item in path[:-1]:
            if isinstance(path_item, str):
                try:
                    data = data[path_item]
                except KeyError:
                    data[path_item] = {}
                    data = data[path_item]
            elif isinstance(path_item, tuple):
                try:
                    flag = False
                    index = 0
                    for data_item in data[path_item[0]]:
                        if data_item[path_item[1]] == path_item[2]:
                            data = data[path_item[0]][index]
                            flag = True
                            break
                        index += 1
                    if not flag:
                        data[path_item[0]].append({path_item[1]: path_item[2]})
                        data = data[path_item[0]][-1]
                except KeyError:
                    data[path_item] = []

        if not path[-1] in data.keys():
            data[path[-1]] = {}

        if isinstance(new_value, list) and isinstance(data[path[-1]], list):
            for value in new_value:
                data[path[-1]].append(value)
        else:
            data[path[-1]] = new_value

        return origin_data

    @staticmethod
    def get_honeycomb_data(node, url_file):
        """Retrieve data from Honeycomb according to given URL.

        :param node: Honeycomb node.
        :param url_file: URL file. The argument contains only the name of file
        without extension, not the full path.
        :type node: dict
        :type url_file: str
        :return: Status code and content of response.
        :rtype tuple
        """

        path = HoneycombUtil.read_path_from_url_file(url_file)
        status_code, resp = HTTPRequest.get(node, path)
        return status_code, loads(resp)

    @staticmethod
    def put_honeycomb_data(node, url_file, data,
                           data_representation=DataRepresentation.JSON):
        """Send configuration data using PUT request and return the status code
        and response content.

        :param node: Honeycomb node.
        :param url_file: URL file. The argument contains only the name of file
        without extension, not the full path.
        :param data: Configuration data to be sent to Honeycomb.
        :param data_representation: How the data is represented.
        :type node: dict
        :type url_file: str
        :type data: dict, str
        :type data_representation: DataRepresentation
        :return: Status code and content of response.
        :rtype: tuple
        :raises HoneycombError: If the given data representation is not defined
        in HEADERS.
        """

        try:
            header = HEADERS[data_representation]
        except AttributeError as err:
            raise HoneycombError("Wrong data representation: {0}.".
                                 format(data_representation), repr(err))
        if data_representation == DataRepresentation.JSON:
            data = dumps(data)

        logger.trace(data)

        path = HoneycombUtil.read_path_from_url_file(url_file)
        return HTTPRequest.put(node=node, path=path, headers=header,
                               payload=data)

    @staticmethod
    def post_honeycomb_data(node, url_file, data=None,
                            data_representation=DataRepresentation.JSON,
                            timeout=10):
        """Send a POST request and return the status code and response content.

        :param node: Honeycomb node.
        :param url_file: URL file. The argument contains only the name of file
        without extension, not the full path.
        :param data: Configuration data to be sent to Honeycomb.
        :param data_representation: How the data is represented.
        :param timeout: How long to wait for the server to send data before
        giving up.
        :type node: dict
        :type url_file: str
        :type data: dict, str
        :type data_representation: DataRepresentation
        :type timeout: int
        :return: Status code and content of response.
        :rtype: tuple
        :raises HoneycombError: If the given data representation is not defined
        in HEADERS.
        """

        try:
            header = HEADERS[data_representation]
        except AttributeError as err:
            raise HoneycombError("Wrong data representation: {0}.".
                                 format(data_representation), repr(err))
        if data_representation == DataRepresentation.JSON:
            data = dumps(data)

        path = HoneycombUtil.read_path_from_url_file(url_file)
        return HTTPRequest.post(node=node, path=path, headers=header,
                                payload=data, timeout=timeout)

    @staticmethod
    def delete_honeycomb_data(node, url_file):
        """Delete data from Honeycomb according to given URL.

        :param node: Honeycomb node.
        :param url_file: URL file. The argument contains only the name of file
        without extension, not the full path.
        :type node: dict
        :type url_file: str
        :return: Status code and content of response.
        :rtype tuple
        """

        path = HoneycombUtil.read_path_from_url_file(url_file)
        return HTTPRequest.delete(node, path)
