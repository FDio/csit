# Copyright (c) 2022 Cisco and/or its affiliates.
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

"""URL decoding and parsing and URL encoding.
"""

import logging

from base64 import urlsafe_b64encode, urlsafe_b64decode
from urllib.parse import urlencode, urlunparse, urlparse, parse_qs
from zlib import compress, decompress
from zlib import error as ZlibErr
from binascii import Error as BinasciiErr


def url_encode(params: dict) -> str:
    """Encode the URL parameters and zip them and create the whole URL using
    given data.

    :param params: All data necessary to create the URL:
        - scheme,
        - network location,
        - path,
        - query,
        - parameters.
    :type params: dict
    :returns: Encoded URL.
    :rtype: str
    """

    url_params = params.get("params", None)
    if url_params:
        encoded_params = urlsafe_b64encode(
            compress(urlencode(url_params).encode("utf-8"), level=9)
        ).rstrip(b"=").decode("utf-8")
    else:
        encoded_params = str()

    return urlunparse((
        params.get("scheme", "http"),
        params.get("netloc", str()),
        params.get("path", str()),
        str(),  # params
        params.get("query", str()),
        encoded_params
    ))


def url_decode(url: str) -> dict:
    """Parse the given URL and decode the parameters.

    :param url: URL to be parsed and decoded.
    :type url: str
    :returns: Paresed URL.
    :rtype: dict
    """

    try:
        parsed_url = urlparse(url)
    except ValueError as err:
        logging.warning(f"\nThe url {url} is not valid, ignoring.\n{repr(err)}")
        return None

    if parsed_url.fragment:
        try:
            padding = b"=" * (4 - (len(parsed_url.fragment) % 4))
            params = parse_qs(decompress(
                urlsafe_b64decode(
                    (parsed_url.fragment.encode("utf-8") + padding)
                )).decode("utf-8")
            )
        except (BinasciiErr, UnicodeDecodeError, ZlibErr) as err:
            logging.warning(
                f"\nNot possible to decode the parameters from url: {url}"
                f"\nEncoded parameters: '{parsed_url.fragment}'"
                f"\n{repr(err)}"
            )
            return None
    else:
        params = None

    return {
        "scheme": parsed_url.scheme,
        "netloc": parsed_url.netloc,
        "path":  parsed_url.path,
        "query":  parsed_url.query,
        "fragment":  parsed_url.fragment,
        "params": params
    }
