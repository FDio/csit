#!/usr/bin/env python

# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Python API provider.
"""

import argparse
import binascii
import fnmatch
import json
import os
import sys

sys.path.append('/tmp/openvpp-testing')
try:
    from resources.libraries.python.PapiErrors import *
except:
    raise

# Sphinx creates auto-generated documentation by importing the python source
# files and collecting the docstrings from them. The NO_VPP_PAPI flag allows
# the vpp_papi_provider.py file to be importable without having to build
# the whole vpp api if the user only wishes to generate the test documentation.
do_import = True
try:
    no_vpp_papi = os.getenv("NO_VPP_PAPI")
    if no_vpp_papi == "1":
        do_import = False
except:
    pass

if do_import:
    # TODO: run os.walk once per whole suite and store the path in environmental
    # variable
    modules_path = None
    for root, dirs, files in os.walk('/usr/lib'):
        for name in files:
            if name == 'vpp_papi.py':
                modules_path = os.path.split(root)[0]
                break
    if modules_path:
        sys.path.append(modules_path)
        from vpp_papi import VPP
    else:
        raise PapiInitError('vpp_papi module not found')

# client name
CLIENT_NAME = 'csit_papi'


def papi_init(vpp_json_dir='/usr/share/vpp/api/'):
    """Construct a VPP instance from VPP JSON API files.

    :param vpp_json_dir: Directory containing all the JSON API files. If VPP is
        installed in the system it will be in /usr/share/vpp/api/.
    :type vpp_json_dir: str
    :returns: VPP instance.
    :rtype: VPP object
    :raises PapiJsonFileError: If no api.json file found.
    :raises PapiInitError: If PAPI initialization failed.
    """
    # construct a list of all the json api files
    jsonfiles = []
    for root, dirnames, filenames in os.walk(vpp_json_dir):
        for filename in fnmatch.filter(filenames, '*.api.json'):
            jsonfiles.append(os.path.join(vpp_json_dir, filename))
    if not jsonfiles:
        raise PapiJsonFileError(
            'No json api files found in location {dir}'.format(
                dir=vpp_json_dir))

    try:
        vpp = VPP(jsonfiles)
        return vpp
    except Exception as err:
        raise PapiInitError('PAPI init failed:\n{exc}'.format(exc=repr(err)))


def papi_connect(vpp_client, name='vpp_api'):
    """Attach to VPP client.

    :param vpp_client: VPP instance to connect to.
    :param name: VPP client name.
    :type vpp_client: VPP object
    :type name: str
    :returns: Return code of VPP.connect() method.
    :rtype: int
    """
    return vpp_client.connect(name)


def papi_disconnect(vpp_client):
    """Detach from VPP client.

    :param vpp_client: VPP instance to detach from.
    :type vpp_client: VPP object
    """
    vpp_client.disconnect()


def papi_run(vpp_client, api_name, api_args):
    """api_name

    :param vpp_client: VPP instance.
    :param api_name: VPP API name.
    :param api_args: Input arguments of the API.
    :type vpp_client: VPP object
    :type api_name: str
    :type api_args: dict
    :returns: VPP API reply.
    :rtype: Vpp_serializer reply object
    """
    papi_fn = getattr(vpp_client.api, api_name)
    return papi_fn(**api_args)


def convert_reply(api_r):
    """Process API reply / a part of API reply for smooth converting to
    JSON string.

    # Apply binascii.hexlify() method for string values.
    :param api_r: API reply.
    :type api_r: Vpp_serializer reply object (named tuple)
    :returns: Processed API reply / a part of API reply.
    :rtype: dict
    """
    unwanted_fields = ['count', 'index']

    reply_dict = dict()
    reply_key = repr(api_r).split('(')[0]
    reply_value = dict()
    for item in dir(api_r):
        if not item.startswith('_') and item not in unwanted_fields:
            # attr_value = getattr(api_r, item)
            # value = binascii.hexlify(attr_value) \
            #     if isinstance(attr_value, str) else attr_value
            value = getattr(api_r, item)
            reply_value[item] = value
    reply_dict[reply_key] = reply_value
    return reply_dict


def process_reply(api_reply):
    """Process API reply for smooth converting to JSON string.

    :param api_reply: API reply.
    :type api_reply: Vpp_serializer reply object (named tuple) or list of
        vpp_serializer reply objects
    :returns: Processed API reply.
    :rtype: list or dict
    """

    if isinstance(api_reply, list):
        converted_reply = list()
        for r in api_reply:
            converted_reply.append(convert_reply(r))
    else:
        converted_reply = convert_reply(api_reply)
    return converted_reply


def main():
    """Main function for the Python API provider.

    :raises PapiCommandInputError: If invalid attribute name or invalid value is
        used in API call.
    :raises PapiCommandError: If PAPI command(s) execution failed.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--json_data",
                        required=True,
                        type=str,
                        help="JSON string (list) containing API name(s) and "
                             "its/their input argument(s).")
    parser.add_argument("-d", "--json_dir",
                        type=str,
                        default='/usr/share/vpp/api/',
                        help="Directory containing all vpp json api files.")
    args = parser.parse_args()
    json_string = args.json_data
    vpp_json_dir = args.json_dir

    vpp = papi_init(vpp_json_dir=vpp_json_dir)

    reply = list()
    json_data = json.loads(json_string)
    papi_connect(vpp, CLIENT_NAME)
    for data in json_data:
        api_name = data['api_name']
        api_args_unicode = data['api_args']
        api_reply = dict(api_name=api_name)
        api_args = dict()
        for a_k, a_v in api_args_unicode.iteritems():
            value = binascii.unhexlify(a_v) if isinstance(a_v, unicode) else a_v
            api_args[str(a_k)] = value
        try:
            rep = papi_run(vpp, api_name, api_args)
            api_reply['api_reply'] = process_reply(rep)
            reply.append(api_reply)
        except (AttributeError, ValueError) as err:
            papi_disconnect(vpp)
            raise PapiCommandInputError(
                'PAPI command {api}({args}) input error:\n{exc}'.format(
                    api=api_name, args=api_args), exc=repr(err))
        except Exception as err:
            papi_disconnect(vpp)
            raise PapiCommandError(
                'PAPI command {api}({args}) error:\n{exc}'.format(
                    api=api_name, args=api_args), exc=repr(err))
    papi_disconnect(vpp)

    return json.dumps(reply)


if __name__ == '__main__':
    sys.stdout.write(main())
    sys.stdout.flush()
    sys.exit(0)
