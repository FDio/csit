# Copyright (c) 2019 Cisco and/or its affiliates.
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

from abc import ABCMeta, abstractmethod
from robot.api import logger

from resources.libraries.python.constants import Constants
from resources.libraries.python.ssh import SSH, SSHTimeout

__all__ = ['PapiExecutor', 'PapiResponse']

# TODO: Implement Papi History
# from resources.libraries.python.PapiHistory import PapiHistory


class AbstractPapiResponse(object):
    """Abstract class defining API for metadata.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __str__(self):
        """Return string with human readable description of the Papi response.

        :returns: Readable description.
        :rtype: str
        """
        pass

    @abstractmethod
    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        pass


class PapiResponse(AbstractPapiResponse):
    """Class for metadata specifying the Papi reply, stdout, stderr and return
    code.
    """

    def __init__(self, papi_replay=None, stdout="", stderr="", ret_code=None):
        """Construct the Papi response by setting the values needed.

        :param papi_replay: API reply from last executed PAPI command(s).
        :param stdout: stdout from last executed PAPI command(s).
        :param stderr: stderr from last executed PAPI command(s).
        :param ret_code: ret_code from last executed PAPI command(s).
        :type papi_replay: list
        :type stdout: str
        :type stderr: str
        :type ret_code: int
        """

        self._papi_replay = papi_replay
        self._stdout = stdout
        self._stderr = stderr
        self._ret_code = ret_code

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        return ("papi_replay={papi_replay} "
                "stdout={stdout} "
                "stderr={stderr} "
                "ret_code={ret_code}".
                format(papi_replay=self._papi_replay,
                       stdout=self._stdout,
                       stderr=self._stderr,
                       ret_code=self._ret_code))

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return ("PapiResponse(papi_replay={papi_replay} "
                "stdout={stdout} "
                "stderr={stderr} "
                "ret_code={ret_code})".
                format(papi_replay=self._papi_replay,
                       stdout=self._stdout,
                       stderr=self._stderr,
                       ret_code=self._ret_code))

    @property
    def ret_code(self):
        """Returns return code from last executed PAPI command(s).
        """
        return self._ret_code

    @property
    def stdout(self):
        """Returns value of stdout from last executed PAPI command(s).
        """
        return self._stdout

    @property
    def stderr(self):
        """Returns value of stderr from last executed PAPI command(s).
        """
        return self._stderr

    @property
    def replay(self):
        """Returns API reply from last executed PAPI command(s).
        """
        return self._papi_replay


class PapiExecutor(object):
    """Contains methods for executing Python API commands on DUTs.
    """

    def __init__(self, node):

        self._node = node

        self._stdout = None
        self._stderr = None
        self._ret_code = None

        self._json_data = None
        self._api_reply = list()
        self._api_data = None
        self._api_command_list = list()

        self._ssh = SSH()

    def __enter__(self):
        try:
            self._ssh.connect(self._node)
        except IOError:
            raise RuntimeError('Cannot open SSH connection to host {host} to '
                               'execute PAPI command(s)'.
                               format(host=self._node['host']))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh.disconnect(self._node)

    @property
    def stdout(self):
        """Returns value of stdout from last executed PAPI command(s).
        """
        return self._stdout

    @property
    def stderr(self):
        """Returns value of stderr from last executed PAPI command(s).
        """
        return self._stderr

    @property
    def ret_code(self):
        """Returns return code from last executed PAPI command(s).
        """
        return self._ret_code

    @property
    def reply(self):
        """Returns API reply from last executed PAPI command(s).
        """
        self._json_data = json.loads(self._stdout)
        self._process_json_data()

        return self._api_reply

    def clear(self):
        """Empty the internal command list; return self.

        Use when not sure whether previous usage has left something in the list.

        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """

        self._api_command_list = list()

        self._api_reply = list()
        self._stdout = None
        self._stderr = None
        self._ret_code = None

        return self

    def add(self, command, **kwargs):
        """Add next command to internal command list; return self.

        :param command: VPP API command.
        :param kwargs: Optional key-value arguments.
        :type command: str
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """

        self._api_command_list.append(dict(api_name=command, api_args=kwargs))

        return self

    def execute(self, timeout=120):
        """Turn internal command list into proper data and execute; return self.

        This method also clears the internal command list.

        :param timeout: Timeout in seconds.
        :type timeout: int
        :returns: Papi response including: papi replay, stdout, stderr and
            return code.
        :rtype: PapiResponse

        """

        local_list = self._api_command_list
        # Clear first as execution may fail.
        self.clear()
        self._execute_papi(local_list, timeout)

        return PapiResponse(papi_replay=self.reply,
                            stdout=self.stdout,
                            stderr=self.stderr,
                            ret_code=self.ret_code)

    def papi_should_have_failed(self):
        """Read return code from last executed script and raise exception if the
        PAPI command(s) didn't fail.

        Note: There are two exceptions raised to distinguish two situations. If
        not needed, reimplement using only RuntimeError.

        :raises RuntimeError: If no PAPI command(s) executed.
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

        Note: There are two exceptions raised to distinguish two situations. If
        not needed, reimplement using only RuntimeError.

        :raises RuntimeError: If no PAPI command(s) has been command executed.
        :raises AssertionError: If PAPI command(s) execution failed.
        """

        if self._ret_code is None:
            raise RuntimeError("First execute the PAPI command(s)!")
        if self._ret_code != 0:
            raise AssertionError(
                "PAPI command(s) execution failed, but success was expected: "
                "{apis}".format(apis=self._api_data))

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
            try:
                api_name = api['api_name']
                api_args = api['api_args']
            except KeyError:
                continue

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
            reverted_reply = [self._revert_api_reply(a_r) for a_r in api_reply]
        else:
            reverted_reply = self._revert_api_reply(api_reply)
        return reverted_reply

    def _process_json_data(self):
        """Process received JSON data."""

        for data in self._json_data:
            try:
                api_reply_processed = dict(
                    api_name=data['api_name'],
                    api_reply=self._process_reply(data['api_reply']))
            except KeyError:
                continue

            self._api_reply.append(api_reply_processed)

    def _execute_papi(self, api_data, timeout=120):
        """Execute PAPI command(s) on remote node and store the result.

        :param api_data: List of APIs with their arguments.
        :param timeout: Timeout in seconds.
        :type api_data: list
        :type timeout: int
        :raises SSHTimeout: If PAPI command(s) execution has timed out.
        :raises RuntimeError: If PAPI executor failed due to another reason.
        """

        if not api_data:
            logger.warn("No API data provided.")
            return

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
        except Exception:
            raise RuntimeError('PAPI command(s) execution on host {host} '
                               'failed: {apis}'.format(host=self._node['host'],
                                                       apis=self._api_data))

        self._ret_code = int(ret_code)
        self._stdout = stdout
        self._stderr = stderr
