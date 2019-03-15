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

"""Python API executor library.

This version supports only simple request / reply VPP API methods.

TODO:
 - Implement:
   - Dump functions
   - vpp-stats

"""

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

    def __init__(self, papi_reply=None, stdout="", stderr="", ret_code=None,
                 requests=None):
        """Construct the Papi response by setting the values needed.

        :param papi_reply: API reply from last executed PAPI command(s).
        :param stdout: stdout from last executed PAPI command(s).
        :param stderr: stderr from last executed PAPI command(s).
        :param ret_code: ret_code from last executed PAPI command(s).
        :param requests: List of used PAPI requests. It is used while verifying
            replies. If None, expected replies must be provided for verify_reply
            and verify_replies methods.
        :type papi_reply: list
        :type stdout: str
        :type stderr: str
        :type ret_code: int
        :type requests: list
        """

        # API reply from last executed PAPI command(s).
        self.reply = papi_reply

        # stdout from last executed PAPI command(s).
        self.stdout = stdout

        # stderr from last executed PAPI command(s).
        self.stderr = stderr

        # return code from last executed PAPI command(s).
        self.ret_code = ret_code

        # List of used PAPI requests.
        self.requests = requests

        # List of expected PAPI replies. It is used while verifying replies.
        if self.requests:
            self.expected_replies = \
                ["{rqst}_reply".format(rqst=rqst) for rqst in self.requests]

    def __str__(self):
        """Return string with human readable description of the PapiResponse.

        :returns: Readable description.
        :rtype: str
        """
        return ("papi_reply={papi_reply},"
                "stdout={stdout},"
                "stderr={stderr},"
                "ret_code={ret_code},"
                "requests={requests}".
                format(papi_reply=self.reply,
                       stdout=self.stdout,
                       stderr=self.stderr,
                       ret_code=self.ret_code,
                       requests=self.requests))

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return "PapiResponse({str})".format(str=str(self))

    def verify_reply(self, cmd_reply=None, idx=0,
                     err_msg="Failed to verify PAPI reply."):
        """Verify and return data from the PAPI response.

        Note: Use only with a simple request / reply command. In this case the
        PAPI reply includes 'retval' which is checked in this method.

        Use if PAPI response includes only one command reply.

        Use it this way (preferred):

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').execute_should_pass().\
                verify_reply()

        or if you must provide the expected reply (not recommended):

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').execute_should_pass().\
                verify_reply('show_version_reply')

        :param cmd_reply: PAPI reply. If None, list of 'requests' should have
            been provided to the __init__ method as pre-generated list of
            replies is used in this method in this case.
            The .execute* methods are providing the requests automatically.
        :param idx: Index to PapiResponse.reply list.
        :param err_msg: The message used if the verification fails.
        :type cmd_reply: str
        :type idx: int
        :type err_msg: str or None
        :returns: Verified data from PAPI response.
        :rtype: dict
        :raises AssertionError: If the PAPI return value is not 0, so the reply
            is not valid.
        :raises KeyError, IndexError: If the reply does not have expected
            structure.
        """
        cmd_rpl = self.expected_replies[idx] if cmd_reply is None else cmd_reply

        data = self.reply[idx]['api_reply'][cmd_rpl]
        if data['retval'] != 0:
            raise AssertionError("{msg}\nidx={idx}, cmd_reply={reply}".
                                 format(msg=err_msg, idx=idx, reply=cmd_rpl))

        return data

    def verify_replies(self, cmd_replies=None,
                       err_msg="Failed to verify PAPI reply."):
        """Verify and return data from the PAPI response.

        Note: Use only with request / reply commands. In this case each
        PAPI reply includes 'retval' which is checked.

        Use if PAPI response includes more than one command reply.

        Use it this way:

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd1, **args1).add(cmd2, **args2).add(cmd2, **args3).\
                execute_should_pass(err_msg).verify_replies()

        or if you need the data from the PAPI response:

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).execute_should_pass(err_msg).verify_replies()

        or if you must provide the list of expected replies (not recommended):

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).execute_should_pass(err_msg).\
                verify_replies(cmd_replies=cmd_replies)

        :param cmd_replies: List of PAPI command replies. If None, list of
            'requests' should have been provided to the __init__ method as
            pre-generated list of replies is used in this method in this case.
            The .execute* methods are providing the requests automatically.
        :param err_msg: The message used if the verification fails.
        :type cmd_replies: list of str or None
        :type err_msg: str
        :returns: List of verified data from PAPI response.
        :rtype list
        :raises AssertionError: If the PAPI response does not include at least
            one of specified command replies.
        """
        data = list()

        cmd_rpls = self.expected_replies if cmd_replies is None else cmd_replies

        if len(self.reply) != len(cmd_rpls):
            raise AssertionError(err_msg)
        for idx, cmd_reply in enumerate(cmd_rpls):
            data.append(self.verify_reply(cmd_reply, idx, err_msg))

        return data


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
            try:
                json_data = json.loads(stdout)
            except ValueError:
                logger.error("An error occured while processing the PAPI "
                             "request:\n{rqst}".format(rqst=local_list))
                logger.trace("ret_code = {ret_code}\n"
                             "stdout:\n{stdout}\n"
                             "stderr:\n{stderr}".format(ret_code=ret_code,
                                                        stdout=stdout,
                                                        stderr=stderr))
                raise
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
                            ret_code=ret_code,
                            requests=[rqst["api_name"] for rqst in local_list])

    def execute_should_pass(self, err_msg="Failed to execute PAPI command.",
                            process_reply=True, ignore_errors=False,
                            timeout=120):
        """Execute the PAPI commands and check the return code.
        Raise exception if the PAPI command(s) failed.

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
        :raises AssertionError: If PAPI command(s) execution failed.
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

        cmd = "{fw_dir}/{papi_provider} --json_data '{json}'".format(
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
