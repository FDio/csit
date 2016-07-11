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

"""Implementation of HTTP requests GET, PUT, POST and DELETE used in
communication with Honeycomb.

The HTTP requests are implemented in the class HTTPRequest which uses
requests.request.
"""

from enum import IntEnum, unique

from robot.api.deco import keyword
from robot.api import logger

from requests import request, RequestException, Timeout, TooManyRedirects, \
    HTTPError, ConnectionError
from requests.auth import HTTPBasicAuth


@unique
class HTTPCodes(IntEnum):
    """HTTP status codes"""
    OK = 200  # pylint: disable=invalid-name
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class HTTPRequestError(Exception):
    """Exception raised by HTTPRequest objects.

    When raising this exception, put this information to the message in this
    order:
    - short description of the encountered problem,
    - relevant messages if there are any collected, e.g., from caught
      exception,
    - relevant data if there are any collected.
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
        super(HTTPRequestError, self).__init__()
        self._msg = "{0}: {1}".format(self.__class__.__name__, msg)
        self._details = details
        if enable_logging:
            logger.error(self._msg)
            logger.debug(self._details)

    def __repr__(self):
        return repr(self._msg)

    def __str__(self):
        return str(self._msg)


class HTTPRequest(object):
    """A class implementing HTTP requests GET, PUT, POST and DELETE used in
    communication with Honeycomb.

    The communication with Honeycomb and processing of all exceptions is done in
    the method _http_request which uses requests.request to send requests and
    receive responses. The received status code and content of response are
    logged on the debug level.
    All possible exceptions raised by requests.request are also processed there.

    The other methods (get, put, post and delete) use _http_request to send
    corresponding request.

    These methods must not be used as keywords in tests. Use keywords
    implemented in the module HoneycombAPIKeywords instead.
    """

    def __init__(self):
        pass

    @staticmethod
    def create_full_url(ip_addr, port, path):
        """Creates full url including host, port, and path to data.

        :param ip_addr: Server IP.
        :param port: Communication port.
        :param path: Path to data.
        :type ip_addr: str
        :type port: str or int
        :type path: str
        :return: Full url.
        :rtype: str
        """
        return "http://{ip}:{port}{path}".format(ip=ip_addr, port=port,
                                                 path=path)

    @staticmethod
    def _http_request(method, node, path, enable_logging=True, **kwargs):
        """Sends specified HTTP request and returns status code and response
        content.

        :param method: The method to be performed on the resource identified by
        the given request URI.
        :param node: Honeycomb node.
        :param path: URL path, e.g. /index.html.
        :param enable_logging: Used to suppress errors when checking Honeycomb
        state during suite setup and teardown.
        :param kwargs: Named parameters accepted by request.request:
            params -- (optional) Dictionary or bytes to be sent in the query
            string for the Request.
            data -- (optional) Dictionary, bytes, or file-like object to
            send in the body of the Request.
            json -- (optional) json data to send in the body of the Request.
            headers -- (optional) Dictionary of HTTP Headers to send with
            the Request.
            cookies -- (optional) Dict or CookieJar object to send with the
            Request.
            files -- (optional) Dictionary of 'name': file-like-objects
            (or {'name': ('filename', fileobj)}) for multipart encoding upload.
            timeout (float or tuple) -- (optional) How long to wait for the
            server to send data before giving up, as a float, or a (connect
            timeout, read timeout) tuple.
            allow_redirects (bool) -- (optional) Boolean. Set to True if POST/
            PUT/DELETE redirect following is allowed.
            proxies -- (optional) Dictionary mapping protocol to the URL of
            the proxy.
            verify -- (optional) whether the SSL cert will be verified.
            A CA_BUNDLE path can also be provided. Defaults to True.
            stream -- (optional) if False, the response content will be
            immediately downloaded.
            cert -- (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
        :type method: str
        :type node: dict
        :type path: str
        :type enable_logging: bool
        :type kwargs: dict
        :return: Status code and content of response.
        :rtype: tuple
        :raises HTTPRequestError: If
        1. it is not possible to connect,
        2. invalid HTTP response comes from server,
        3. request exceeded the configured number of maximum re-directions,
        4. request timed out,
        5. there is any other unexpected HTTP request exception.
        """
        timeout = kwargs["timeout"]
        url = HTTPRequest.create_full_url(node['host'],
                                          node['honeycomb']['port'],
                                          path)
        try:
            auth = HTTPBasicAuth(node['honeycomb']['user'],
                                 node['honeycomb']['passwd'])
            rsp = request(method, url, auth=auth, **kwargs)

            logger.debug("Status code: {0}".format(rsp.status_code))
            logger.debug("Response: {0}".format(rsp.content))

            return rsp.status_code, rsp.content

        except ConnectionError as err:
            # Switching the logging on / off is needed only for
            # "requests.ConnectionError"
            raise HTTPRequestError("Not possible to connect to {0}:{1}.".
                                   format(node['host'],
                                          node['honeycomb']['port']),
                                   repr(err), enable_logging=enable_logging)
        except HTTPError as err:
            raise HTTPRequestError("Invalid HTTP response from {0}.".
                                   format(node['host']), repr(err))
        except TooManyRedirects as err:
            raise HTTPRequestError("Request exceeded the configured number "
                                   "of maximum re-directions.", repr(err))
        except Timeout as err:
            raise HTTPRequestError("Request timed out. Timeout is set to {0}.".
                                   format(timeout), repr(err))
        except RequestException as err:
            raise HTTPRequestError("Unexpected HTTP request exception.",
                                   repr(err))

    @staticmethod
    @keyword(name="HTTP Get")
    def get(node, path, headers=None, timeout=10, enable_logging=True):
        """Sends a GET request and returns the response and status code.

        :param node: Honeycomb node.
        :param path: URL path, e.g. /index.html.
        :param headers: Dictionary of HTTP Headers to send with the Request.
        :param timeout: How long to wait for the server to send data before
        giving up, as a float, or a (connect timeout, read timeout) tuple.
        :param enable_logging: Used to suppress errors when checking Honeycomb
        state during suite setup and teardown. When True, logging is enabled,
        otherwise logging is disabled.
        :type node: dict
        :type path: str
        :type headers: dict
        :type timeout: float or tuple
        :type enable_logging: bool
        :return: Status code and content of response.
        :rtype: tuple
        """

        return HTTPRequest._http_request('GET', node, path,
                                         enable_logging=enable_logging,
                                         headers=headers, timeout=timeout)

    @staticmethod
    @keyword(name="HTTP Put")
    def put(node, path, headers=None, payload=None, json=None, timeout=10):
        """Sends a PUT request and returns the response and status code.

        :param node: Honeycomb node.
        :param path: URL path, e.g. /index.html.
        :param headers: Dictionary of HTTP Headers to send with the Request.
        :param payload: Dictionary, bytes, or file-like object to send in
        the body of the Request.
        :param json: JSON formatted string to send in the body of the Request.
        :param timeout: How long to wait for the server to send data before
        giving up, as a float, or a (connect timeout, read timeout) tuple.
        :type node: dict
        :type path: str
        :type headers: dict
        :type payload: dict, bytes, or file-like object
        :type json: str
        :type timeout: float or tuple
        :return: Status code and content of response.
        :rtype: tuple
        """
        return HTTPRequest._http_request('PUT', node, path, headers=headers,
                                         data=payload, json=json,
                                         timeout=timeout)

    @staticmethod
    @keyword(name="HTTP Post")
    def post(node, path, headers=None, payload=None, json=None, timeout=10):
        """Sends a POST request and returns the response and status code.

        :param node: Honeycomb node.
        :param path: URL path, e.g. /index.html.
        :param headers: Dictionary of HTTP Headers to send with the Request.
        :param payload: Dictionary, bytes, or file-like object to send in
        the body of the Request.
        :param json: JSON formatted string to send in the body of the Request.
        :param timeout: How long to wait for the server to send data before
        giving up, as a float, or a (connect timeout, read timeout) tuple.
        :type node: dict
        :type path: str
        :type headers: dict
        :type payload: dict, bytes, or file-like object
        :type json: str
        :type timeout: float or tuple
        :return: Status code and content of response.
        :rtype: tuple
        """
        return HTTPRequest._http_request('POST', node, path, headers=headers,
                                         data=payload, json=json,
                                         timeout=timeout)

    @staticmethod
    @keyword(name="HTTP Delete")
    def delete(node, path, timeout=10):
        """Sends a DELETE request and returns the response and status code.

        :param node: Honeycomb node.
        :param path: URL path, e.g. /index.html.
        :param timeout: How long to wait for the server to send data before
        giving up, as a float, or a (connect timeout, read timeout) tuple.
        :type node: dict
        :type path: str
        :type timeout: float or tuple
        :return: Status code and content of response.
        :rtype: tuple
        """
        return HTTPRequest._http_request('DELETE', node, path, timeout=timeout)
