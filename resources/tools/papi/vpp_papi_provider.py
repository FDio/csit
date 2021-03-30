#!/usr/bin/env python3

# Copyright (c) 2020 Cisco and/or its affiliates.
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

r"""CSIT PAPI Provider

TODO: Add description.

Examples:
---------

Request/reply or dump:

    vpp_papi_provider.py \
        --method request \
        --data '[{"api_name": "show_version", "api_args": {}}]'

VPP-stats:

    vpp_papi_provider.py \
        --method stats \
        --data '[["^/if", "/err/ip4-input", "/sys/node/ip4-input"], ["^/if"]]'
"""

import argparse
import json
import os
import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Client name
CLIENT_NAME = u"csit_papi"


# Sphinx creates auto-generated documentation by importing the python source
# files and collecting the docstrings from them. The NO_VPP_PAPI flag allows
# the vpp_papi_provider.py file to be importable without having to build
# the whole vpp api if the user only wishes to generate the test documentation.

try:
    do_import = bool(not os.getenv(u"NO_VPP_PAPI") == u"1")
except KeyError:
    do_import = True

if do_import:

    # Find the directory where the modules are installed. The directory depends
    # on the OS used.
    # TODO: Find a better way to import papi modules.

    modules_path = None
    for root, dirs, files in os.walk(u"/usr/lib"):
        for name in files:
            if name == u"vpp_papi.py":
                modules_path = os.path.split(root)[0]
                break
    if modules_path:
        sys.path.append(modules_path)
        from vpp_papi import VPPApiClient
        from vpp_papi.vpp_stats import VPPStats
    else:
        raise RuntimeError(u"vpp_papi module not found")


def _convert_reply(api_r):
    """Process API reply / a part of API reply for smooth converting to
    JSON string.

    It is used only with 'request' and 'dump' methods.

    Apply binascii.hexlify() method for string values.

    TODO: Implement complex solution to process of replies.

    :param api_r: API reply.
    :type api_r: Vpp_serializer reply object (named tuple)
    :returns: Processed API reply / a part of API reply.
    :rtype: dict
    """
    unwanted_fields = [u"count", u"index", u"context"]

    def process_value(val):
        """Process value.

        :param val: Value to be processed.
        :type val: object
        :returns: Processed value.
        :rtype: dict or str or int
        """
        if isinstance(val, dict):
            for val_k, val_v in val.items():
                val[str(val_k)] = process_value(val_v)
            return val
        elif isinstance(val, list):
            for idx, val_l in enumerate(val):
                val[idx] = process_value(val_l)
            return val
        elif isinstance(val, bytes):
            val.hex()
        elif hasattr(val, u"__int__"):
            return int(val)
        elif hasattr(val, "__str__"):
            return str(val).encode(encoding=u"utf-8").hex()
        # Next handles parameters not supporting preferred integer or string
        # representation to get it logged
        elif hasattr(val, u"__repr__"):
            return repr(val)
        else:
            return val

    reply_dict = dict()
    reply_key = repr(api_r).split(u"(")[0]
    reply_value = dict()
    for item in dir(api_r):
        if not item.startswith(u"_") and item not in unwanted_fields:
            reply_value[item] = process_value(getattr(api_r, item))
    reply_dict[reply_key] = reply_value
    return reply_dict


def process_json_request(args):
    """Process the request/reply and dump classes of VPP API methods.

    :param args: Command line arguments passed to VPP PAPI Provider.
    :type args: ArgumentParser
    :returns: JSON formatted string.
    :rtype: str
    :raises RuntimeError: If PAPI command error occurs.
    """

    try:
        vpp = VPPApiClient()
    except Exception as err:
        raise RuntimeError(f"PAPI init failed:\n{err!r}")

    reply = list()

    def process_value(val):
        """Process value.

        :param val: Value to be processed.
        :type val: object
        :returns: Processed value.
        :rtype: dict or str or int
        """
        if isinstance(val, dict):
            for val_k, val_v in val.items():
                val[str(val_k)] = process_value(val_v)
            return val
        elif isinstance(val, list):
            for idx, val_l in enumerate(val):
                val[idx] = process_value(val_l)
            return val
        elif isinstance(val, str):
            return bytes.fromhex(val).decode(encoding=u"utf-8")
        elif isinstance(val, int):
            return val
        else:
            return str(val)

    json_data = json.loads(args.data)
    vpp.connect(CLIENT_NAME)
    for data in json_data:
        api_name = data[u"api_name"]
        api_args_unicode = data[u"api_args"]
        api_reply = dict(api_name=api_name)
        api_args = dict()
        for a_k, a_v in api_args_unicode.items():
            api_args[str(a_k)] = process_value(a_v)
        try:
            papi_fn = getattr(vpp.api, api_name)
            rep = papi_fn(**api_args)

            if isinstance(rep, list):
                converted_reply = list()
                for r in rep:
                    converted_reply.append(_convert_reply(r))
            else:
                converted_reply = _convert_reply(rep)

            api_reply[u"api_reply"] = converted_reply
            reply.append(api_reply)
        except (AttributeError, ValueError) as err:
            vpp.disconnect()
            raise RuntimeError(
                f"PAPI command {api_name}({api_args}) input error:\n{err!r}"
            )
        except Exception as err:
            vpp.disconnect()
            raise RuntimeError(
                f"PAPI command {api_name}({api_args}) error:\n{err!r}"
            )
    vpp.disconnect()

    return json.dumps(reply)


def process_stats(args):
    """Process the VPP Stats.

    :param args: Command line arguments passed to VPP PAPI Provider.
    :type args: ArgumentParser
    :returns: JSON formatted string.
    :rtype: str
    :raises RuntimeError: If PAPI command error occurs.
    """

    try:
        stats = VPPStats(args.socket)
    except Exception as err:
        raise RuntimeError(f"PAPI init failed:\n{err!r}")

    json_data = json.loads(args.data)

    reply = list()

    eprint(f"json_data: {json_data!r}")
    for path in json_data:
        eprint(f"path: {path!r}")
        directory = stats.ls(path)
        eprint(f"directory: {directory!r}")
        data = stats.dump(directory)
        eprint(f"data: {data!r}")
        reply.append(data)

    try:
        return json.dumps(reply)
    except UnicodeDecodeError as err:
        raise RuntimeError(f"PAPI reply {reply} error:\n{err!r}")


def process_stats_request(args):
    """Process the VPP Stats requests.

    :param args: Command line arguments passed to VPP PAPI Provider.
    :type args: ArgumentParser
    :returns: JSON formatted string.
    :rtype: str
    :raises RuntimeError: If PAPI command error occurs.
    """

    try:
        stats = VPPStats(args.socket)
    except Exception as err:
        raise RuntimeError(f"PAPI init failed:\n{err!r}")

    try:
        json_data = json.loads(args.data)
    except ValueError as err:
        raise RuntimeError(f"Input json string is invalid:\n{err!r}")

    papi_fn = getattr(stats, json_data[u"api_name"])
    reply = papi_fn(**json_data.get(u"api_args", {}))

    return json.dumps(reply)


def main():
    """Main function for the Python API provider.
    """

    # The functions which process different types of VPP Python API methods.
    process_request = dict(
        request=process_json_request,
        dump=process_json_request,
        stats=process_stats,
        stats_request=process_stats_request
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__
    )
    parser.add_argument(
        u"-m", u"--method", required=True,
        choices=[str(key) for key in process_request.keys()],
        help=u"Specifies the VPP API methods: "
             u"1. request - simple request / reply; "
             u"2. dump - dump function;"
             u"3. stats - VPP statistics."
    )
    parser.add_argument(
        u"-d", u"--data", required=True,
        help=u"If the method is 'request' or 'dump', data is a JSON string "
             u"(list) containing API name(s) and its/their input argument(s). "
             u"If the method is 'stats', data is a JSON string containing t"
             u"he list of path(s) to the required data."
    )
    parser.add_argument(
        u"-s", u"--socket", default=u"/var/run/vpp/stats.sock",
        help=u"A file descriptor over the VPP stats Unix domain socket. "
             u"It is used only if method=='stats'."
    )

    args = parser.parse_args()

    return process_request[args.method](args)


if __name__ == u"__main__":
    sys.stdout.write(main())
    sys.stdout.flush()
    sys.exit(0)
