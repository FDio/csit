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

"""Implementation of keywords for Honeycomb setup."""

from robot.api import logger

from resources.libraries.python.HTTPRequest import HTTPRequest, HTTPCodes, \
    HTTPRequestError
from resources.libraries.python.constants import Constants as Const
from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError
from resources.libraries.python.honeycomb.HoneycombUtil \
    import HoneycombUtil as HcUtil
from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType


class HoneycombSetup(object):
    """Implements keywords for Honeycomb setup.

    The keywords implemented in this class make possible to:
    - start Honeycomb,
    - stop Honeycomb,
    - check the Honeycomb start-up state,
    - check the Honeycomb shutdown state,
    - add VPP to the topology.
    """

    def __init__(self):
        pass

    @staticmethod
    def start_honeycomb_on_duts(*nodes):
        """Start Honeycomb on specified DUT nodes.

        This keyword starts the Honeycomb service on specified DUTs.
        The keyword just starts the Honeycomb and does not check its startup
        state. Use the keyword "Check Honeycomb Startup State" to check if the
        Honeycomb is up and running.
        Honeycomb must be installed in "/opt" directory, otherwise the start
        will fail.
        :param nodes: List of nodes to start Honeycomb on.
        :type nodes: list
        :raises HoneycombError: If Honeycomb fails to start.
        """

        HoneycombSetup.print_environment(nodes)

        logger.console("\nStarting Honeycomb service ...")

        cmd = "{0}/bin/start".format(Const.REMOTE_HC_DIR)

        for node in nodes:
            if node['type'] == NodeType.DUT:
                ssh = SSH()
                ssh.connect(node)
                (ret_code, _, _) = ssh.exec_command_sudo(cmd)
                if int(ret_code) != 0:
                    raise HoneycombError('Node {0} failed to start Honeycomb.'.
                                         format(node['host']))
                else:
                    logger.info("Starting the Honeycomb service on node {0} is "
                                "in progress ...".format(node['host']))

    @staticmethod
    def stop_honeycomb_on_duts(*nodes):
        """Stop the Honeycomb service on specified DUT nodes.

        This keyword stops the Honeycomb service on specified nodes. It just
        stops the Honeycomb and does not check its shutdown state. Use the
        keyword "Check Honeycomb Shutdown State" to check if Honeycomb has
        stopped.
        :param nodes: List of nodes to stop Honeycomb on.
        :type nodes: list
        :raises HoneycombError: If Honeycomb failed to stop.
        """
        logger.console("\nShutting down Honeycomb service ...")

        cmd = "{0}/bin/stop".format(Const.REMOTE_HC_DIR)
        errors = []

        for node in nodes:
            if node['type'] == NodeType.DUT:
                ssh = SSH()
                ssh.connect(node)
                (ret_code, _, _) = ssh.exec_command_sudo(cmd)
                if int(ret_code) != 0:
                    errors.append(node['host'])
                else:
                    logger.info("Stopping the Honeycomb service on node {0} is "
                                "in progress ...".format(node['host']))
        if errors:
            raise HoneycombError('Node(s) {0} failed to stop Honeycomb.'.
                                 format(errors))

    @staticmethod
    def check_honeycomb_startup_state(*nodes):
        """Check state of Honeycomb service during startup on specified nodes.

        Reads html path from template file oper_vpp_version.url.

        Honeycomb nodes reply with connection refused or the following status
        codes depending on startup progress: codes 200, 401, 403, 404, 500, 503

        :param nodes: List of DUT nodes starting Honeycomb.
        :type nodes: list
        :return: True if all GETs returned code 200(OK).
        :rtype bool
        """
        path = HcUtil.read_path_from_url_file("oper_vpp_version")
        expected_status_codes = (HTTPCodes.UNAUTHORIZED,
                                 HTTPCodes.FORBIDDEN,
                                 HTTPCodes.NOT_FOUND,
                                 HTTPCodes.SERVICE_UNAVAILABLE,
                                 HTTPCodes.INTERNAL_SERVER_ERROR)

        for node in nodes:
            if node['type'] == NodeType.DUT:
                status_code, _ = HTTPRequest.get(node, path, timeout=10,
                                                 enable_logging=False)
                if status_code == HTTPCodes.OK:
                    logger.info("Honeycomb on node {0} is up and running".
                                format(node['host']))
                elif status_code in expected_status_codes:
                    if status_code == HTTPCodes.UNAUTHORIZED:
                        logger.info('Unauthorized. If this triggers keyword '
                                    'timeout, verify Honeycomb username and '
                                    'password.')
                    raise HoneycombError('Honeycomb on node {0} running but '
                                         'not yet ready.'.format(node['host']),
                                         enable_logging=False)
                else:
                    raise HoneycombError('Unexpected return code: {0}.'.
                                         format(status_code))
        return True

    @staticmethod
    def check_honeycomb_shutdown_state(*nodes):
        """Check state of Honeycomb service during shutdown on specified nodes.

        Honeycomb nodes reply with connection refused or the following status
        codes depending on shutdown progress: codes 200, 404.

        :param nodes: List of DUT nodes stopping Honeycomb.
        :type nodes: list
        :return: True if all GETs fail to connect.
        :rtype bool
        """
        cmd = "ps -ef | grep -v grep | grep karaf"
        for node in nodes:
            if node['type'] == NodeType.DUT:
                try:
                    status_code, _ = HTTPRequest.get(node, '/index.html',
                                                     timeout=5,
                                                     enable_logging=False)
                    if status_code == HTTPCodes.OK:
                        raise HoneycombError('Honeycomb on node {0} is still '
                                             'running.'.format(node['host']),
                                             enable_logging=False)
                    elif status_code == HTTPCodes.NOT_FOUND:
                        raise HoneycombError('Honeycomb on node {0} is shutting'
                                             ' down.'.format(node['host']),
                                             enable_logging=False)
                    else:
                        raise HoneycombError('Unexpected return code: {0}.'.
                                             format(status_code))
                except HTTPRequestError:
                    logger.debug('Connection refused, checking the process '
                                 'state ...')
                    ssh = SSH()
                    ssh.connect(node)
                    (ret_code, _, _) = ssh.exec_command_sudo(cmd)
                    if ret_code == 0:
                        raise HoneycombError('Honeycomb on node {0} is still '
                                             'running.'.format(node['host']),
                                             enable_logging=False)
                    else:
                        logger.info("Honeycomb on node {0} has stopped".
                                    format(node['host']))
        return True

    @staticmethod
    def print_environment(nodes):
        """Print information about the nodes to log. The information is defined
        by commands in cmds tuple at the beginning of this method.

        :param nodes: List of DUT nodes to get information about.
        :type nodes: list
        """

        #TODO: When everything is set and running in VIRL env, transform this
        # method to a keyword checking the environment.

        cmds = ("uname -a",
                "df -lh",
                "echo $JAVA_HOME",
                "echo $PATH",
                "which java",
                "java -version",
                "dpkg --list | grep openjdk",
                "ls -la /opt/honeycomb",
                "ls -la /opt/honeycomb/v3po-karaf-1.0.0-SNAPSHOT")

        for node in nodes:
            if node['type'] == NodeType.DUT:
                logger.info("Checking node {} ...".format(node))
                for cmd in cmds:
                    logger.info("Command: {}".format(cmd))
                    ssh = SSH()
                    ssh.connect(node)
                    ssh.exec_command_sudo(cmd)
