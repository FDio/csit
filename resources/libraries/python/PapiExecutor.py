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

from pprint import pformat
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.PythonThree import raise_from
from resources.libraries.python.ssh import SSH, SSHTimeout


__all__ = ["PapiExecutor"]


class PapiExecutor(object):
    """Contains methods for executing VPP Python API commands on DUTs.

    Note: Use only with "with" statement, e.g.:

        with PapiExecutor(node) as papi_exec:
            replies = papi_exec.add('show_version').get_replies(err_msg)

    This class processes three classes of VPP PAPI methods:
    1. simple request / reply: method='request',
    2. dump functions: method='dump',
    3. vpp-stats: method='stats'.

    The recommended ways of use are (examples):

    1. Simple request / reply

    a. One request with no arguments:

        with PapiExecutor(node) as papi_exec:
            reply = papi_exec.add('show_version').get_reply()

    b. Three requests with arguments, the second and the third ones are the same
       but with different arguments.

        with PapiExecutor(node) as papi_exec:
            replies = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg)

    2. Dump functions

        cmd = 'sw_interface_rx_placement_dump'
        with PapiExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index']).\
                get_details(err_msg)

    3. vpp-stats

        path = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']

        with PapiExecutor(node) as papi_exec:
            stats = papi_exec.add(api_name='vpp-stats', path=path).get_stats()

        print('RX interface core 0, sw_if_index 0:\n{0}'.\
            format(stats[0]['/if/rx'][0][0]))

        or

        path_1 = ['^/if', ]
        path_2 = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']

        with PapiExecutor(node) as papi_exec:
            stats = papi_exec.add('vpp-stats', path=path_1).\
                add('vpp-stats', path=path_2).get_stats()

        print('RX interface core 0, sw_if_index 0:\n{0}'.\
            format(stats[1]['/if/rx'][0][0]))

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

    def add(self, csit_papi_command="vpp-stats", history=True, **kwargs):
        """Add next command to internal command list; return self.

        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.

        :param csit_papi_command: VPP API command.
        :param history: Enable/disable adding command to PAPI command history.
        :param kwargs: Optional key-value arguments.
        :type csit_papi_command: str
        :type history: bool
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """
        if history:
            PapiHistory.add_to_papi_history(
                self._node, csit_papi_command, **kwargs)
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
        :rtype: list of dict
        """

        paths = [cmd['api_args']['path'] for cmd in self._api_command_list]
        self._api_command_list = list()

        stdout = self._execute_papi(
            paths, method='stats', err_msg=err_msg, timeout=timeout)

        return json.loads(stdout)

    def get_replies(self, err_msg="Failed to get replies.", timeout=120):
        """Get replies from VPP Python API.

        The replies are parsed into dict-like objects,
        "retval" field is guaranteed to be zero on success.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type timeout: int
        :returns: Responses, dict objects with fields due to API and "retval".
        :rtype: list of dict
        :raises RuntimeError: If retval is nonzero, parsing or ssh error.
        """
        return self._execute(method='request', err_msg=err_msg, timeout=timeout)

    def get_reply(self, err_msg="Failed to get reply.", timeout=120):
        """Get reply from VPP Python API.

        The reply is parsed into dict-like object,
        "retval" field is guaranteed to be zero on success.

        TODO: Discuss exception types to raise, unify with inner methods.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type timeout: int
        :returns: Response, dict object with fields due to API and "retval".
        :rtype: dict
        :raises AssertionError: If retval is nonzero, parsing or ssh error.
        """
        replies = self.get_replies(err_msg=err_msg, timeout=timeout)
        if len(replies) != 1:
            raise RuntimeError("Expected single reply, got {replies!r}".format(
                replies=replies))
        return replies[0]

    def get_sw_if_index(self, err_msg="Failed to get reply.", timeout=120):
        """Get sw_if_index from reply from VPP Python API.

        Frequently, the caller is only interested in sw_if_index field
        of the reply, this wrapper makes such call sites shorter.

        TODO: Discuss exception types to raise, unify with inner methods.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type timeout: int
        :returns: Response, sw_if_index value of the reply.
        :rtype: int
        :raises AssertionError: If retval is nonzero, parsing or ssh error.
        """
        return self.get_reply(err_msg=err_msg, timeout=timeout)["sw_if_index"]

    def get_details(self, err_msg="Failed to get dump details.", timeout=120):
        """Get dump details from VPP Python API.

        The details are parsed into dict-like objects.
        The number of details per single dump command can vary,
        and all association between details and dumps is lost,
        so if you care about the association (as opposed to
        logging everything at once for debugging purposes),
        it is recommended to call get_details for each dump (type) separately.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type timeout: int
        :returns: Details, dict objects with fields due to API without "retval".
        :rtype: list of dict
        """
        return self._execute(method='dump', err_msg=err_msg, timeout=timeout)

    @staticmethod
    def dump_and_log(node, cmds):
        """Dump and log requested information, return None.

        :param node: DUT node.
        :param cmds: Dump commands to be executed.
        :type node: dict
        :type cmds: list of str
        """
        with PapiExecutor(node) as papi_exec:
            for cmd in cmds:
                details = papi_exec.add(cmd).get_details()
                logger.debug("{cmd}:\n{details}".format(
                    cmd=cmd, details=pformat(details)))

    @staticmethod
    def run_cli_cmd(node, cmd, log=True):
        """Run a CLI command as cli_inband, return the "reply" field of reply.

        Optionally, log the field value.

        :param node: Node to run command on.
        :param cmd: The CLI command to be run on the node.
        :param log: If True, the response is logged.
        :type node: dict
        :type cmd: str
        :type log: bool
        :returns: CLI output.
        :rtype: str
        """

        cli = 'cli_inband'
        args = dict(cmd=cmd)
        err_msg = "Failed to run 'cli_inband {cmd}' PAPI command on host " \
                  "{host}".format(host=node['host'], cmd=cmd)

        with PapiExecutor(node) as papi_exec:
            reply = papi_exec.add(cli, **args).get_reply(err_msg)["reply"]

        if log:
            logger.info("{cmd}:\n{reply}".format(cmd=cmd, reply=reply))

        return reply

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
            """Process value.

            :param val: Value to be processed.
            :type val: object
            :returns: Processed value.
            :rtype: dict or str or int
            """
            if isinstance(val, dict):
                for val_k, val_v in val.iteritems():
                    val[str(val_k)] = process_value(val_v)
                return val
            elif isinstance(val, list):
                for idx, val_l in enumerate(val):
                    val[idx] = process_value(val_l)
                return val
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
        def process_value(val):
            """Process value.

            :param val: Value to be processed.
            :type val: object
            :returns: Processed value.
            :rtype: dict or str or int
            """
            if isinstance(val, dict):
                for val_k, val_v in val.iteritems():
                    val[str(val_k)] = process_value(val_v)
                return val
            elif isinstance(val, list):
                for idx, val_l in enumerate(val):
                    val[idx] = process_value(val_l)
                return val
            elif isinstance(val, unicode):
                return binascii.unhexlify(val)
            else:
                return val

        reply_dict = dict()
        reply_value = dict()
        for reply_key, reply_v in api_r.iteritems():
            for a_k, a_v in reply_v.iteritems():
                reply_value[a_k] = process_value(a_v)
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
        :returns: Stdout from remote python utility, to be parsed by caller.
        :rtype: str
        :raises SSHTimeout: If PAPI command(s) execution has timed out.
        :raises RuntimeError: If PAPI executor failed due to another reason.
        :raises AssertionError: If PAPI command(s) execution has failed.
        """

        if not api_data:
            raise RuntimeError("No API data provided.")

        json_data = json.dumps(api_data) \
            if method in ("stats", "stats_request") \
            else json.dumps(self._process_api_data(api_data))

        cmd = "{fw_dir}/{papi_provider} --method {method} --data '{json}'".\
            format(
                fw_dir=Constants.REMOTE_FW_DIR, method=method, json=json_data,
                papi_provider=Constants.RESOURCES_PAPI_PROVIDER)
        try:
            ret_code, stdout, _ = self._ssh.exec_command_sudo(
                cmd=cmd, timeout=timeout, log_stdout_err=False)
        # TODO: Fail on non-empty stderr?
        except SSHTimeout:
            logger.error("PAPI command(s) execution timeout on host {host}:"
                         "\n{apis}".format(host=self._node["host"],
                                           apis=api_data))
            raise
        except Exception as exc:
            raise_from(RuntimeError(
                "PAPI command(s) execution on host {host} "
                "failed: {apis}".format(
                    host=self._node["host"], apis=api_data)), exc)
        if ret_code != 0:
            raise AssertionError(err_msg)

        return stdout

    def _execute(self, method='request', err_msg="", timeout=120):
        """Turn internal command list into data and execute; return replies.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_stats()
        - get_replies()
        - get_details()

        :param method: VPP Python API method. Supported methods are: 'request',
            'dump' and 'stats'.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type method: str
        :type err_msg: str
        :type timeout: int
        :returns: Papi responses parsed into a dict-like object,
            with field due to API or stats hierarchy.
        :rtype: list of dict
        :raises KeyError: If the reply is not correct.
        """

        local_list = self._api_command_list

        # Clear first as execution may fail.
        self._api_command_list = list()

        stdout = self._execute_papi(
            local_list, method=method, err_msg=err_msg, timeout=timeout)
        replies = list()
        try:
            json_data = json.loads(stdout)
        except ValueError as err:
            raise_from(RuntimeError(err_msg), err)
        for data in json_data:
            if method == "request":
                api_reply = self._process_reply(data["api_reply"])
                # api_reply contains single key, *_reply.
                obj = api_reply.values()[0]
                retval = obj["retval"]
                if retval != 0:
                    # TODO: What exactly to log and raise here?
                    err = AssertionError("Got retval {rv!r}".format(rv=retval))
                    raise_from(AssertionError(err_msg), err)
                replies.append(obj)
            elif method == "dump":
                api_reply = self._process_reply(data["api_reply"])
                # api_reply is a list where item contas single key, *_details.
                for item in api_reply:
                    obj = item.values()[0]
                    replies.append(obj)
            else:
                # TODO: Implement support for stats.
                raise RuntimeError("Unsuported method {method}".format(
                    method=method))

        # TODO: Make logging optional?
        logger.debug("PAPI replies: {replies}".format(replies=replies))

        return replies
