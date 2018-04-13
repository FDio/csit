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

"""Implementation of keywords for managing Honeycomb persistence files."""

from robot.api import logger

from resources.libraries.python.constants import Constants as Const
from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError
from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType


class HcPersistence(object):
    """Implements keywords for managing Honeycomb persistence files.

    The keywords implemented in this class make possible to:
    - find and replace strings in config.json persistence file
    """

    def __init__(self):
        pass

    @staticmethod
    def clear_persisted_honeycomb_config(*nodes):
        """Remove configuration data persisted from last Honeycomb session.
        Default configuration will be used instead.

        :param nodes: List of DUTs to execute on.
        :type nodes: list
        :raises HoneycombError: If persisted configuration could not be removed.
        """
        cmd = "rm -rf {}/*".format(Const.REMOTE_HC_PERSIST)
        for node in nodes:
            if node['type'] == NodeType.DUT:
                ssh = SSH()
                ssh.connect(node)
                (ret_code, _, stderr) = ssh.exec_command_sudo(cmd)
                if ret_code != 0:
                    if "No such file or directory" not in stderr:
                        raise HoneycombError('Could not clear persisted '
                                             'configuration on node {0}, {1}'
                                             .format(node['host'], stderr))
                    else:
                        logger.info("Persistence data was not present on node"
                                    " {0}".format(node['host']))
                else:
                    logger.info("Persistence files removed on node {0}"
                                .format(node['host']))

    @staticmethod
    def modify_persistence_files(node, find, replace):
        """Searches contents of persistence file data.json for the provided
         string, and replaces all occurrences with another string.

        :param node: Honeycomb node.
        :param find: Text to find in file.
        :param replace: String to replace anything found with.
        :type node: dict
        :type find: string
        :type replace: string
        :raises HoneycombError: If persistent configuration couldn't be
            modified.
        """

        argument = "\"s/{0}/{1}/g\"".format(find, replace)
        path = "{0}/config/data.json".format(Const.REMOTE_HC_PERSIST)
        command = "sed -i {0} {1}".format(argument, path)

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, stderr) = ssh.exec_command_sudo(command)
        if ret_code != 0:
            raise HoneycombError("Failed to modify persistence file on node"
                                 " {0}, {1}".format(node, stderr))

    @staticmethod
    def log_persisted_configuration(node):
        """Read contents of Honeycomb persistence files and print them to log.

        :param node: Honeycomb node.
        :type node: dict
        """

        commands = [
            "cat {0}/config/data.json".format(Const.REMOTE_HC_PERSIST),
            "cat {0}/context/data.json".format(Const.REMOTE_HC_PERSIST),
        ]

        ssh = SSH()
        ssh.connect(node)
        for command in commands:
            (_, _, _) = ssh.exec_command_sudo(command)

    @staticmethod
    def configure_persistence(node, state):
        """Enable or disable Honeycomb configuration data persistence.

        :param node: Honeycomb node.
        :param state: Enable or Disable.
        :type node: dict
        :type state: str
        :raises ValueError: If the state argument is incorrect.
        :raises HoneycombError: If the operation fails.
        """

        state = state.lower()
        if state == "enable":
            state = "true"
        elif state == "disable":
            state = "false"
        else:
            raise ValueError("Unexpected value of state argument:"
                             " {0} provided. Must be enable or disable."
                             .format(state))

        for setting in ("persist-config", "persist-context"):
            # find the setting, replace entire line with 'setting: state'
            find = '\\"{setting}\\":'.format(setting=setting)
            replace = '\\"{setting}\\": \\"{state}\\",'.format(
                setting=setting, state=state)

            argument = '"/{0}/c\\ {1}"'.format(find, replace)
            path = "{0}/config/honeycomb.json".format(Const.REMOTE_HC_DIR)
            command = "sed -i {0} {1}".format(argument, path)

            ssh = SSH()
            ssh.connect(node)
            (ret_code, _, stderr) = ssh.exec_command_sudo(command)
            if ret_code != 0:
                raise HoneycombError("Failed to modify configuration on "
                                     "node {0}, {1}".format(node, stderr))
