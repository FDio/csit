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

    def __init__(self, papi_reply=None, stdout="", stderr="", requests=None):
        """Construct the Papi response by setting the values needed.

        TODO:
            Implement 'dump' analogue of verify_replies that would concatenate
            the values, so that call sites do not have to do that themselves.

        :param papi_reply: API reply from last executed PAPI command(s).
        :param stdout: stdout from last executed PAPI command(s).
        :param stderr: stderr from last executed PAPI command(s).
        :param requests: List of used PAPI requests. It is used while verifying
            replies. If None, expected replies must be provided for verify_reply
            and verify_replies methods.
        :type papi_reply: list or None
        :type stdout: str
        :type stderr: str
        :type requests: list
        """

        # API reply from last executed PAPI command(s).
        self.reply = papi_reply

        # stdout from last executed PAPI command(s).
        self.stdout = stdout

        # stderr from last executed PAPI command(s).
        self.stderr = stderr

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
        return (
            "papi_reply={papi_reply},stdout={stdout},stderr={stderr},"
            "requests={requests}").format(
                papi_reply=self.reply, stdout=self.stdout, stderr=self.stderr,
                requests=self.requests)

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

        Do not use with 'dump' and 'vpp-stats' methods.

        Use if PAPI response includes only one command reply.

        Use it this way (preferred):

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().verify_reply()

        or if you must provide the expected reply (not recommended):

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().\
                verify_reply('show_version_reply')

        :param cmd_reply: PAPI reply. If None, list of 'requests' should have
            been provided to the __init__ method as pre-generated list of
            replies is used in this method in this case.
            The PapiExecutor._execute() method provides the requests
            automatically.
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

        Do not use with 'dump' and 'vpp-stats' methods.

        Use if PAPI response includes more than one command reply.

        Use it this way:

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd1, **args1).add(cmd2, **args2).add(cmd2, **args3).\
                get_replies(err_msg).verify_replies()

        or if you need the data from the PAPI response:

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg).verify_replies()

        or if you must provide the list of expected replies (not recommended):

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg).\
                verify_replies(cmd_replies=cmd_replies)

        :param cmd_replies: List of PAPI command replies. If None, list of
            'requests' should have been provided to the __init__ method as
            pre-generated list of replies is used in this method in this case.
            The PapiExecutor._execute() method provides the requests
            automatically.
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
    """Contains methods for executing VPP Python API commands on DUTs.

    Note: Use only with "with" statement, e.g.:

        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add('show_version').get_replies(err_msg)

    This class processes three classes of VPP PAPI methods:
    1. simple request / reply: method='request',
    2. dump functions: method='dump',
    3. vpp-stats: method='stats'.

    The recommended ways of use are (examples):

    1. Simple request / reply

    a. One request with no arguments:

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().\
                verify_reply()

    b. Three requests with arguments, the second and the third ones are the same
       but with different arguments.

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg).verify_replies()

    2. Dump functions

        cmd = 'sw_interface_rx_placement_dump'
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index']).\
                get_dump(err_msg)

    3. vpp-stats

        path = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(api_name='vpp-stats', path=path).get_stats()

        print('RX interface core 0, sw_if_index 0:\n{0}'.\
            format(data[0]['/if/rx'][0][0]))

        or

        path_1 = ['^/if', ]
        path_2 = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('vpp-stats', path=path_1).\
                add('vpp-stats', path=path_2).get_stats()

        print('RX interface core 0, sw_if_index 0:\n{0}'.\
            format(data[1]['/if/rx'][0][0]))

        Note: In this case, when PapiExecutor method 'add' is used:
        - its parameter 'csit_papi_command' is used only to keep information
          that vpp-stats are requested. It is not further processed but it is
          included in the PAPI history this way:
          vpp-stats(path=['^/if', '/err/ip4-input', '/sys/node/ip4-input'])
          Always use csit_papi_command="vpp-stats" if the VPP PAPI method
          is "stats".
        - the second parameter must be 'path' as it is used by PapiExecutor
          method 'add'.
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

    def add(self, csit_papi_command="vpp-stats", **kwargs):
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

    def get_stats(self, err_msg="Failed to get statistics.", timeout=120):
        """Get VPP Stats from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type timeout: int
        :returns: Requested VPP statistics.
        :rtype: list
        """

        paths = [cmd['api_args']['path'] for cmd in self._api_command_list]
        self._api_command_list = list()

        stdout, _ = self._execute_papi(
            paths, method='stats', err_msg=err_msg, timeout=timeout)

        return json.loads(stdout)

    def get_replies(self, err_msg="Failed to get replies.",
                    process_reply=True, ignore_errors=False, timeout=120):
        """Get reply/replies from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Process PAPI reply if True.
        :param ignore_errors: If true, the errors in the reply are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: papi reply, stdout, stderr and
            return code.
        :rtype: PapiResponse
        """
        return self._execute(
            method='request', process_reply=process_reply,
            ignore_errors=ignore_errors, err_msg=err_msg, timeout=timeout)

    def get_dump(self, err_msg="Failed to get dump.",
                 process_reply=True, ignore_errors=False, timeout=120):
        """Get dump from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Process PAPI reply if True.
        :param ignore_errors: If true, the errors in the reply are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: papi reply, stdout, stderr and
            return code.
        :rtype: PapiResponse
        """
        return self._execute(
            method='dump', process_reply=process_reply,
            ignore_errors=ignore_errors, err_msg=err_msg, timeout=timeout)

    def execute_should_pass(self, err_msg="Failed to execute PAPI command.",
                            process_reply=True, ignore_errors=False,
                            timeout=120):
        """Execute the PAPI commands and check the return code.
        Raise exception if the PAPI command(s) failed.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_replies()
        - get_dump()
        This method will be removed soon.

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
        # TODO: Migrate callers to get_replies and delete this method.
        return self.get_replies(
            process_reply=process_reply, ignore_errors=ignore_errors,
            err_msg=err_msg, timeout=timeout)

    @staticmethod
    def _process_api_data(api_d):
        """Process API data for smooth converting to JSON string.

        Apply binascii.hexlify() method for string values.

        :param api_d: List of APIs with their arguments.
        :type api_d: list
        :returns: List of APIs with arguments pre-processed for JSON.
        :rtype: list
        """

        def process_value(val):
            """Process value"""
            if isinstance(val, dict):
                val_dict = dict()
                for val_k, val_v in val.iteritems():
                    val_dict[str(val_k)] = process_value(val_v)
                return val_dict
            else:
                return binascii.hexlify(val) if isinstance(val, str) else val

        api_data_processed = list()
        for api in api_d:
            api_args_processed = dict()
            for a_k, a_v in api["api_args"].iteritems():
                api_args_processed[str(a_k)] = process_value(a_v)
            api_data_processed.append(dict(api_name=api["api_name"],
                                           api_args=api_args_processed))
        return api_data_processed

    @staticmethod
    def _revert_api_reply(api_r):
        """Process API reply / a part of API reply.

        Apply binascii.unhexlify() method for unicode values.

        TODO: Implement complex solution to process of replies.

        :param api_r: API reply.
        :type api_r: dict
        :returns: Processed API reply / a part of API reply.
        :rtype: dict
        """
        reply_dict = dict()
        reply_value = dict()
        for reply_key, reply_v in api_r.iteritems():
            for a_k, a_v in reply_v.iteritems():
                reply_value[a_k] = binascii.unhexlify(a_v) \
                    if isinstance(a_v, unicode) else a_v
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

    def _execute_papi(self, api_data, method='request', err_msg="",
                      timeout=120):
        """Execute PAPI command(s) on remote node and store the result.

        :param api_data: List of APIs with their arguments.
        :param method: VPP Python API method. Supported methods are: 'request',
            'dump' and 'stats'.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type api_data: list
        :type method: str
        :type err_msg: str
        :type timeout: int
        :returns: Stdout and stderr.
        :rtype: 2-tuple of str
        :raises SSHTimeout: If PAPI command(s) execution has timed out.
        :raises RuntimeError: If PAPI executor failed due to another reason.
        :raises AssertionError: If PAPI command(s) execution has failed.
        """

        if not api_data:
            RuntimeError("No API data provided.")

        json_data = json.dumps(api_data) if method == "stats" \
            else json.dumps(self._process_api_data(api_data))

        cmd = "{fw_dir}/{papi_provider} --method {method} --data '{json}'".\
            format(fw_dir=Constants.REMOTE_FW_DIR,
                   papi_provider=Constants.RESOURCES_PAPI_PROVIDER,
                   method=method,
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
        if ret_code != 0:
            raise AssertionError(err_msg)

        return stdout, stderr

    def _execute(self, method='request', process_reply=True,
                 ignore_errors=False, err_msg="", timeout=120):
        """Turn internal command list into proper data and execute; return
        PAPI response.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_stats()
        - get_replies()
        - get_dump()

        :param method: VPP Python API method. Supported methods are: 'request',
            'dump' and 'stats'.
        :param process_reply: Process PAPI reply if True.
        :param ignore_errors: If true, the errors in the reply are ignored.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type method: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type err_msg: str
        :type timeout: int
        :returns: Papi response including: papi reply, stdout, stderr and
            return code.
        :rtype: PapiResponse
        :raises KeyError: If the reply is not correct.
        """

        local_list = self._api_command_list

        # Clear first as execution may fail.
        self._api_command_list = list()

        stdout, stderr = self._execute_papi(
            local_list, method=method, err_msg=err_msg, timeout=timeout)
        papi_reply = list()
        if process_reply:
            try:
                json_data = json.loads(stdout)
            except ValueError:
                logger.error("An error occured while processing the PAPI "
                             "request:\n{rqst}".format(rqst=local_list))
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

        # Log processed papi reply to be able to check API replies changes
        logger.debug("Processed PAPI reply: {reply}".format(reply=papi_reply))

        return PapiResponse(
            papi_reply=papi_reply, stdout=stdout, stderr=stderr,
            requests=[rqst["api_name"] for rqst in local_list])
