# Copyright (c) 2021 Cisco and/or its affiliates.
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

This one does not use sockets.
PapiNonsocketExecutor is a better name, but too long for import lines.
PapiStatsExecutor name hints accessing stats segment needs this executor.
"""

import copy
import json

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.ssh import (SSH, SSHTimeout)


__all__ = [u"PapiStatsExecutor"]


class PapiStatsExecutor:
    """Contains methods for executing VPP Python API commands on DUTs.

    TODO: Remove .add step, make get_stats accept paths directly.

    This class processes only one type of VPP PAPI methods: vpp-stats.

    The recommended ways of use are (examples):

    path = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']
    with PapiStatsExecutor(node) as papi_exec:
        stats = papi_exec.add(api_name='vpp-stats', path=path).get_stats()

    print('RX interface core 0, sw_if_index 0:\n{0}'.\
        format(stats[0]['/if/rx'][0][0]))

    or

    path_1 = ['^/if', ]
    path_2 = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']
    with PapiStatsExecutor(node) as papi_exec:
        stats = papi_exec.add('vpp-stats', path=path_1).\
            add('vpp-stats', path=path_2).get_stats()

    print('RX interface core 0, sw_if_index 0:\n{0}'.\
        format(stats[1]['/if/rx'][0][0]))

    Note: In this case, when PapiStatsExecutor method 'add' is used:
    - its parameter 'csit_papi_command' is used only to keep information
      that vpp-stats are requested. It is not further processed but it is
      included in the PAPI history this way:
      vpp-stats(path=['^/if', '/err/ip4-input', '/sys/node/ip4-input'])
      Always use csit_papi_command="vpp-stats" if the VPP PAPI method
      is "stats".
    - the second parameter must be 'path' as it is used by PapiStatsExecutor
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
            raise RuntimeError(
                f"Cannot open SSH connection to host {self._node[u'host']} "
                f"to execute PAPI command(s)"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh.disconnect(self._node)

    def add(self, csit_papi_command=u"vpp-stats", history=True, **kwargs):
        """Add next command to internal command list; return self.

        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.
        The kwargs dict is deep-copied, so it is safe to use the original
        with partial modifications for subsequent commands.

        :param csit_papi_command: VPP API command.
        :param history: Enable/disable adding command to PAPI command history.
        :param kwargs: Optional key-value arguments.
        :type csit_papi_command: str
        :type history: bool
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiStatsExecutor
        """
        if history:
            PapiHistory.add_to_papi_history(
                self._node, csit_papi_command, **kwargs
            )
        # TODO: Add only just before executing,
        # so if executing fails in the middle, history does not contain
        # commands we know VPP has never received.
        # Note that with async processing, CSIT is likely to send
        # many more commands before realizing something has failed.
        self._api_command_list.append(
            dict(
                api_name=csit_papi_command, api_args=copy.deepcopy(kwargs)
            )
        )
        return self

    def get_stats(
            self, err_msg=u"Failed to get statistics.", timeout=120,
            socket=Constants.SOCKSTAT_PATH):
        """Get VPP Stats from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :param socket: Path to Stats socket to tunnel to.
        :type err_msg: str
        :type timeout: int
        :type socket: str
        :returns: Requested VPP statistics.
        :rtype: list of dict
        """
        paths = [cmd[u"api_args"][u"path"] for cmd in self._api_command_list]
        self._api_command_list = list()

        stdout = self._execute_papi(
            paths, method=u"stats", err_msg=err_msg, timeout=timeout,
            socket=socket
        )

        return json.loads(stdout)

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
                for val_k, val_v in val.items():
                    val[str(val_k)] = process_value(val_v)
                return val
            if isinstance(val, list):
                for idx, val_l in enumerate(val):
                    val[idx] = process_value(val_l)
                return val
            return val.encode().hex() if isinstance(val, str) else val

        api_data_processed = list()
        for api in api_d:
            api_args_processed = dict()
            for a_k, a_v in api[u"api_args"].items():
                api_args_processed[str(a_k)] = process_value(a_v)
            api_data_processed.append(
                dict(
                    api_name=api[u"api_name"],
                    api_args=api_args_processed
                )
            )
        return api_data_processed

    def _execute_papi(
            self, api_data, method=u"request", err_msg=u"", timeout=120,
            socket=None):
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
            raise RuntimeError(u"No API data provided.")

        json_data = json.dumps(api_data) \
            if method in (u"stats", u"stats_request") \
            else json.dumps(self._process_api_data(api_data))

        sock = f" --socket {socket}" if socket else u""
        cmd = f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_PAPI_PROVIDER}" \
            f" --method {method} --data '{json_data}'{sock}"
        try:
            ret_code, stdout, _ = self._ssh.exec_command_sudo(
                cmd=cmd, timeout=timeout, log_stdout_err=False
            )
        # TODO: Fail on non-empty stderr?
        except SSHTimeout:
            logger.error(
                f"PAPI command(s) execution timeout on host "
                f"{self._node[u'host']}:\n{api_data}"
            )
            raise
        except Exception as exc:
            raise RuntimeError(
                f"PAPI command(s) execution on host {self._node[u'host']} "
                f"failed: {api_data}"
            ) from exc
        if ret_code != 0:
            raise AssertionError(err_msg)

        return stdout
