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

"""Python API executor library."""

import binascii
import json

from paramiko.ssh_exception import SSHException
from robot.api import logger

from resources.libraries.python.constants import Constants
from resources.libraries.python.PapiErrors import PapiInitError, \
    PapiJsonFileError, PapiCommandError, PapiCommandInputError
# TODO: from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.ssh import SSH, SSHTimeout

__all__ = ['PapiExecutor']


class PapiExecutor(object):
    """Contains methods for executing Python API commands on DUTs."""

    def __init__(self, node):
        self._stdout = None
        self._stderr = None
        self._ret_code = None
        self._node = node
        self._json_data = None
        self._api_reply = list()
        self._api_data = None

        self._ssh = SSH()
        try:
            self._ssh.connect(node)
        except:
            raise SSHException('Cannot open SSH connection to host {host} to '
                               'execute PAPI command(s)'.
                               format(host=self._node['host']))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def _process_api_data(api_d):
        """Process API data for smooth converting to JSON string.

        Apply binascii.hexlify() method for string values.

        :param api_d: List of APIs with their arguments.
        :type api_d: list
        :returns: List of APIs with arguments pre-processed for JSON.
        :rtype: list
        """

        api_data_processed = list()
        for api in api_d:
            api_name = api['api_name']
            api_args = api['api_args']
            api_processed = dict(api_name=api_name)
            api_args_processed = dict()
            for a_k, a_v in api_args.iteritems():
                value = binascii.hexlify(a_v) if isinstance(a_v, str) else a_v
                api_args_processed[str(a_k)] = value
            api_processed['api_args'] = api_args_processed
            api_data_processed.append(api_processed)
        return api_data_processed

    @staticmethod
    def _revert_api_reply(api_r):
        """Process API reply / a part of API reply.

        Apply binascii.unhexlify() method for unicode values.

        :param api_r: API reply.
        :type api_r: dict
        :returns: Processed API reply / a part of API reply.
        :rtype: dict
        """

        reply_dict = dict()
        reply_value = dict()
        for reply_key, reply_v in api_r.iteritems():
            for a_k, a_v in reply_v.iteritems():
                # value = binascii.unhexlify(a_v) if isinstance(a_v, unicode) \
                #     else a_v
                # reply_value[a_k] = value
                reply_value[a_k] = a_v
            reply_dict[reply_key] = reply_value
        return reply_dict

    def _process_reply(self, api_reply):
        """Process API reply.

        :param api_reply: API reply.
        :type api_reply: dict or list of dict
        :returns: Processed API reply.
        :rtype: list or dict
        """

        if isinstance(api_reply, list):
            reverted_reply = list()
            for a_r in api_reply:
                reverted_reply.append(self._revert_api_reply(a_r))
        else:
            reverted_reply = self._revert_api_reply(api_reply)
        return reverted_reply

    def _process_json_data(self):
        """Process received JSON data."""

        for data in self._json_data:
            api_name = data['api_name']
            api_reply = data['api_reply']
            api_reply_processed = dict(
                api_name=api_name, api_reply=self._process_reply(api_reply))
            self._api_reply.append(api_reply_processed)

    def execute_papi(self, api_data, timeout=120):
        """Execute PAPI command(s) on remote node and store the result.

        :param api_data: List of APIs with their arguments.
        :param timeout: Timeout in seconds.
        :type api_data: list
        :type timeout: int
        :raises SSHTimeout: If PAPI command(s) execution is timed out.
        :raises PapiInitError: If PAPI initialization failed.
        :raises PapiJsonFileError: If no api.json file found.
        :raises PapiCommandError: If PAPI command(s) execution failed.
        :raises PapiCommandInputError: If invalid attribute name or invalid
            value is used in API call.
        :raises RuntimeError: If PAPI executor failed due to another reason.
        """
        self._api_data = api_data
        api_data_processed = self._process_api_data(api_data)
        json_data = json.dumps(api_data_processed)

        cmd = "python {fw_dir}/{papi_provider} --json_data '{json}'".format(
            fw_dir=Constants.REMOTE_FW_DIR,
            papi_provider=Constants.RESOURCES_PAPI_PROVIDER,
            json=json_data)

        try:
            ret_code, stdout, stderr = self._ssh.exec_command_sudo(
                cmd=cmd, timeout=timeout)
        except SSHTimeout:
            logger.error('PAPI command(s) execution timeout on host {host}:'
                         '\n{apis}'.format(host=self._node['host'],
                                           apis=self._api_data))
            raise
        except (PapiInitError, PapiJsonFileError, PapiCommandError,
                PapiCommandInputError):
            logger.error('PAPI command(s) execution failed on host {host}'.
                         format(host=self._node['host']))
            raise
        except:
            raise RuntimeError('PAPI command(s) execution on host {host} '
                               'failed: {apis}'.format(host=self._node['host'],
                                                       apis=self._api_data))

        self._ret_code = ret_code
        self._stdout = stdout
        self._stderr = stderr

    def papi_should_have_failed(self):
        """Read return code from last executed script and raise exception if the
        PAPI command(s) didn't fail.

        :raises RuntimeError: When no PAPI command executed.
        :raises AssertionError: If PAPI command(s) execution passed.
        """

        if self._ret_code is None:
            raise RuntimeError("First execute the PAPI command(s)!")
        if self._ret_code == 0:
            raise AssertionError(
                "PAPI command(s) execution passed, but failure was expected: "
                "{apis}".format(apis=self._api_data))

    def papi_should_have_passed(self):
        """Read return code from last executed script and raise exception if the
        PAPI command(s) failed.

        :raises RuntimeError: When no PAPI command executed.
        :raises AssertionError: If PAPI command(s) execution failed.
        """

        if self._ret_code is None:
            raise RuntimeError("First execute the PAPI command(s)!")
        if self._ret_code != 0:
            raise AssertionError(
                "PAPI command(s) execution failed, but success was expected: "
                "{apis}".format(apis=self._api_data))

    def get_papi_stdout(self):
        """Returns value of stdout from last executed PAPI command(s)."""

        return self._stdout

    def get_papi_stderr(self):
        """Returns value of stderr from last executed PAPI command(s)."""

        return self._stderr

    def get_papi_reply(self):
        """Returns api reply from last executed PAPI command(s)."""

        self._json_data = json.loads(self._stdout)
        self._process_json_data()

        return self._api_reply
