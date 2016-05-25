# Copyright (c) 2016 Cisco and/or its affiliates.
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

        :param nodes: list of DUTs to execute on.
        :type nodes: list
        :raises HoneycombError: If persisted configuration could not be removed.
        """
        cmd = "rm {0}/../etc/opendaylight/honeycomb/*".format(
            Const.REMOTE_HC_DIR)
        for node in nodes:
            if node['type'] == NodeType.DUT:
                ssh = SSH()
                ssh.connect(node)
                (ret_code, _, stderr) = ssh.exec_command_sudo(cmd)
                if ret_code != 0:
                    if "No such file or directory" not in stderr:
                        raise HoneycombError('Couldn`t clear persisted '
                                             'configuration on node {0}, {1}'
                                             .format(node['host'], stderr))
                    else:
                        logger.info("persistence data was not present on node"
                                    " {0}".format(node['host']))
                else:
                    logger.info("Persistence files removed on node {0}"
                                .format(node['host']))

    @staticmethod
    def modify_persistence_files(node, find, replace):
        """Searches contents of persistence file config.json for the provided
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

        command = "sed -i \"s/{0}/{1}/g\" " \
                  "{2}/../etc/opendaylight/honeycomb/config.json".format(
                    find, replace, Const.REMOTE_HC_DIR)

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, stderr) = ssh.exec_command_sudo(command)
        if ret_code != 0:
            raise HoneycombError("Failed to modify persistence file.")
