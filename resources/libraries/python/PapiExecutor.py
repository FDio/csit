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

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import SSH, SSHTimeout
from resources.libraries.python.PapiHistory import PapiHistory

__all__ = ["PapiExecutor", "PapiResponse"]


class PapiResponse(object):
    """Class for metadata specifying the Papi reply, stdout, stderr and return
    code.
    """

    def __init__(self, papi_reply=None, stdout="", stderr="", ret_code=None):
        """Construct the Papi response by setting the values needed.

        :param papi_reply: API reply from last executed PAPI command(s).
        :param stdout: stdout from last executed PAPI command(s).
        :param stderr: stderr from last executed PAPI command(s).
        :param ret_code: ret_code from last executed PAPI command(s).
        :type papi_reply: list
        :type stdout: str
        :type stderr: str
        :type ret_code: int
        """

        # API reply from last executed PAPI command(s)
        self.reply = papi_reply

        # stdout from last executed PAPI command(s)
        self.stdout = stdout

        # stderr from last executed PAPI command(s).
        self.stderr = stderr

        # return code from last executed PAPI command(s)
        self.ret_code = ret_code

    def __str__(self):
        """Return string with human readable description of the group.

        :returns: Readable description.
        :rtype: str
        """
        return ("papi_reply={papi_reply} "
                "stdout={stdout} "
                "stderr={stderr} "
                "ret_code={ret_code}".
                format(papi_reply=self.reply,
                       stdout=self.stdout,
                       stderr=self.stderr,
                       ret_code=self.ret_code))

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return ("PapiResponse(papi_reply={papi_reply} "
                "stdout={stdout} "
                "stderr={stderr} "
                "ret_code={ret_code})".
                format(papi_reply=self.reply,
                       stdout=self.stdout,
                       stderr=self.stderr,
                       ret_code=self.ret_code))


class PapiExecutor(object):
    """Contains methods for executing Python API commands on DUTs.

    Use only with "with" statement, e.g.:

    with PapiExecutor(node) as papi_exec:
        papi_resp = papi_exec.add('show_version').execute_should_pass(err_msg)
    """

    def __init__(self, node):
        """Initialization.

        :param node: Node to run command(s) on.
        :type node: dict
        """

        # Node to run command(s) on.
        self._node = node

        # The list of PAPI commands to be executed on the node.
        self._api_command_list = list()

        # The response on the PAPI commands.
        self.response = PapiResponse()

        self._ssh = SSH()

    def __enter__(self):
        try:
            self._ssh.connect(self._node)
        except IOError:
            raise RuntimeError("Cannot open SSH connection to host {host} to "
                               "execute PAPI command(s)".
                               format(host=self._node["host"]))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh.disconnect(self._node)

    def clear(self):
        """Empty the internal command list; return self.

        Use when not sure whether previous usage has left something in the list.

        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """
        self._api_command_list = list()
        return self

    def add(self, csit_papi_command, **kwargs):
        """Add next command to internal command list; return self.

        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.

        :param csit_papi_command: VPP API command.
        :param kwargs: Optional key-value arguments.
        :type csit_papi_command: str
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """
        PapiHistory.add_to_papi_history(self._node, csit_papi_command, **kwargs)
        self._api_command_list.append(dict(api_name=csit_papi_command,
                                           api_args=kwargs))
        return self

    def execute(self, process_reply=True, ignore_errors=False, timeout=120):
        """Turn internal command list into proper data and execute; return
        PAPI response.

        This method also clears the internal command list.

        :param process_reply: Process PAPI reply if True.
        :param ignore_errors: If true, the errors in the reply are ignored.
        :param timeout: Timeout in seconds.
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: papi reply, stdout, stderr and
            return code.
        :rtype: PapiResponse
        :raises KeyError: If the reply is not correct.
        """

        local_list = self._api_command_list

        # Clear first as execution may fail.
        self.clear()

        ret_code, stdout, stderr = self._execute_papi(local_list, timeout)

        papi_reply = list()
        if process_reply:
            json_data = json.loads(stdout)
            for data in json_data:
                try:
                    api_reply_processed = dict(
                        api_name=data["api_name"],
                        api_reply=self._process_reply(data["api_reply"]))
                except KeyError:
                    if ignore_errors:
                        continue
                    else:
                        raise
                papi_reply.append(api_reply_processed)

        return PapiResponse(papi_reply=papi_reply,
                            stdout=stdout,
                            stderr=stderr,
                            ret_code=ret_code)

    def execute_should_pass(self, err_msg="Failed to execute PAPI command.",
                            process_reply=True, ignore_errors=False,
                            timeout=120):
        """Execute the PAPI commands and check the return code.
        Raise exception if the PAPI command(s) failed.

        Note: There are two exceptions raised to distinguish two situations. If
        not needed, re-implement using only RuntimeError.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Indicate whether or not to process PAPI reply.
        :param ignore_errors: If true, the errors in the reply are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: papi reply, stdout, stderr and
            return code.
        :rtype: PapiResponse
        :raises AssertionError: If PAPI command(s) execution passed.
        """

        response = self.execute(process_reply=process_reply,
                                ignore_errors=ignore_errors,
                                timeout=timeout)

        if response.ret_code != 0:
            raise AssertionError(err_msg)
        return response

    def execute_should_fail(self,
                            err_msg="Execution of PAPI command did not fail.",
                            process_reply=False, ignore_errors=False,
                            timeout=120):
        """Execute the PAPI commands and check the return code.
        Raise exception if the PAPI command(s) did not fail.

        It does not return anything as we expect it fails.

        Note: There are two exceptions raised to distinguish two situations. If
        not needed, re-implement using only RuntimeError.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Indicate whether or not to process PAPI reply.
        :param ignore_errors: If true, the errors in the reply are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :raises AssertionError: If PAPI command(s) execution passed.
        """

        response = self.execute(process_reply=process_reply,
                                ignore_errors=ignore_errors,
                                timeout=timeout)

        if response.ret_code == 0:
            raise AssertionError(err_msg)

    @staticmethod
    def verify_reply(papi_resp, cmd_reply,
                     err_msg="Failed to execute PAPI command."):
        """Verify and return data from the PAPI reply.

        Use it this way:

        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, **args).execute_should_pass(err_msg)

            # Single cmd_reply (cmd_reply is a string):
            data = papi_exec.verify_reply(papi_resp.reply,
                                          cmd_reply=[cmd_reply, ],
                                          err_msg)
            # Multiple cmd_replies (cmd_reply is a list of strings):
            data = papi_exec.verify_reply(papi_resp.reply,
                                          cmd_reply=cmd_reply,
                                          err_msg)

        TODO: rtype: list of dictionaries??? [{cmd_reply: data}, ]

        :param papi_resp: PAPI response including only reply/replies.
        :param cmd_reply: List of expected PAPI replies.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type papi_resp: list
        :type cmd_reply: list of str
        :type err_msg: str
        :returns: PAPI data: [(cmd_reply, data), ]
        :rtype list of tuples
        :raises RuntimeError: If the return value is not 0 or if the cmd_reply
            is not present in the response.
        """

        data = list()
        for reply in cmd_reply:
            for resp in papi_resp:
                resp_data = resp['api_replay'].get(reply, None)
                if resp_data:
                    if resp_data['retval'] != 0:
                        raise RuntimeError(err_msg)
                    data.append((reply, resp_data))
                    papi_resp.remove(resp_data)
                    break
            else:
                # The data for this cmd_reply is not present.
                raise RuntimeError(err_msg)

        return data

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
            api_args_processed = dict()
            for a_k, a_v in api["api_args"].iteritems():
                value = binascii.hexlify(a_v) if isinstance(a_v, str) else a_v
                api_args_processed[str(a_k)] = value
            api_data_processed.append(dict(api_name=api["api_name"],
                                           api_args=api_args_processed))
        return api_data_processed

    @staticmethod
    def _revert_api_reply(api_r):
        """Process API reply / a part of API reply.

        Apply binascii.unhexlify() method for unicode values.

        TODO: Remove the disabled code when definitely not needed.

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
            RuntimeError("No API data provided.")

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
            logger.error("PAPI command(s) execution timeout on host {host}:"
                         "\n{apis}".format(host=self._node["host"],
                                           apis=api_data))
            raise
        except Exception:
            raise RuntimeError("PAPI command(s) execution on host {host} "
                               "failed: {apis}".format(host=self._node["host"],
                                                       apis=api_data))
        return ret_code, stdout, stderr
