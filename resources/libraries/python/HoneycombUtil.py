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

from json import loads
from enum import Enum, unique

from robot.api import logger

from resources.libraries.python.HTTPRequest import HTTPRequest
from resources.libraries.python.constants import Constants as Const


@unique
class DataRepresentation(Enum):
    """Representation of data sent by PUT and POST requests."""
    NO_DATA = 0
    JSON = 1
    XML = 2
    TXT = 3


# Headers used in requests. Key - content representation, value - header.
HEADERS = {DataRepresentation.NO_DATA:
               {},  # Must be empty.
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

        :param msg: Message to be displayed and logged
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
    def parse_json_response(response, path=None):
        """Parse data from response string in JSON format according to given
        path.

        :param response: JSON formatted string.
        :param path: Path to navigate down the data structure.
        :type response: string
        :type path: tuple
        :return: JSON dictionary/list tree.
        :rtype: list
        """
        data = loads(response)

        if path:
            data = HoneycombUtil._parse_json_tree(data, path)
            if not isinstance(data, list):
                data = [data, ]

        return data

    @staticmethod
    def _parse_json_tree(data, path):
        """Retrieve data addressed by path from python representation of JSON
        object.

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
        :param url_file: URL file. The argument contains only the name of file
        without extension, not the full path.
        :type node: dict
        :type url_file: str
        :return: Status code and content of response.
        :rtype tuple
        """

        path = HoneycombUtil.read_path_from_url_file(url_file)
        return HTTPRequest.get(node, path)

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
        :type data: str
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
        :type data: str
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
        print(data_representation)
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
