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

from ipaddress import IPv6Address, AddressValueError

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

        cmd = "sudo service honeycomb start"

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

        cmd = "sudo service honeycomb stop"
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
    def restart_honeycomb_and_vpp_on_duts(*nodes):
        """Restart the Honeycomb service on specified DUT nodes.

        Use the keyword "Check Honeycomb Startup State" to check when Honeycomb
        is fully restarted.
        :param nodes: List of nodes to restart Honeycomb on.
        :type nodes: list
        :raises HoneycombError: If Honeycomb failed to restart.
        """
        logger.console("\nRestarting Honeycomb service ...")

        cmd = "sudo service honeycomb restart && sudo service vpp restart"
        errors = []

        for node in nodes:
            if node['type'] == NodeType.DUT:
                ssh = SSH()
                ssh.connect(node)
                (ret_code, _, _) = ssh.exec_command_sudo(cmd)
                if int(ret_code) != 0:
                    errors.append(node['host'])
                else:
                    logger.info("Restart of Honeycomb and VPP on node {0} is "
                                "in progress ...".format(node['host']))
        if errors:
            raise HoneycombError('Node(s) {0} failed to restart Honeycomb'
                                 ' and/or VPP.'.
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
                HoneycombSetup.print_ports(node)
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

                status_code, _ = HcUtil.get_honeycomb_data(
                    node, "config_vpp_interfaces")
                if status_code != HTTPCodes.OK:
                    raise HoneycombError('Honeycomb on node {0} running but '
                                         'not yet ready.'.format(node['host']),
                                         enable_logging=False)
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
        cmd = "ps -ef | grep -v grep | grep honeycomb"
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
    def configure_restconf_binding_address(node):
        """Configure Honeycomb to accept restconf requests from all IP
        addresses. IP version is determined by node data.

         :param node: Information about a DUT node.
         :type node: dict
         :raises HoneycombError: If the configuration could not be changed.
         """

        find = "restconf-https-binding-address"
        try:
            IPv6Address(unicode(node["host"]))
            # if management IP of the node is in IPv6 format
            replace = '\\"restconf-https-binding-address\\": \\"0::0\\",'
        except (AttributeError, AddressValueError):
            replace = '\\"restconf-https-binding-address\\": \\"0.0.0.0\\",'

        argument = '"/{0}/c\\ {1}"'.format(find, replace)
        path = "{0}/config/honeycomb.json".format(Const.REMOTE_HC_DIR)
        command = "sed -i {0} {1}".format(argument, path)

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, stderr) = ssh.exec_command_sudo(command)
        if ret_code != 0:
            raise HoneycombError("Failed to modify configuration on "
                                 "node {0}, {1}".format(node, stderr))

    @staticmethod
    def print_environment(nodes):
        """Print information about the nodes to log. The information is defined
        by commands in cmds tuple at the beginning of this method.

        :param nodes: List of DUT nodes to get information about.
        :type nodes: list
        """

        # TODO: When everything is set and running in VIRL env, transform this
        # method to a keyword checking the environment.

        cmds = ("uname -a",
                "df -lh",
                "echo $JAVA_HOME",
                "echo $PATH",
                "which java",
                "java -version",
                "dpkg --list | grep openjdk",
                "ls -la /opt/honeycomb")

        for node in nodes:
            if node['type'] == NodeType.DUT:
                logger.info("Checking node {} ...".format(node['host']))
                for cmd in cmds:
                    logger.info("Command: {}".format(cmd))
                    ssh = SSH()
                    ssh.connect(node)
                    ssh.exec_command_sudo(cmd)

    @staticmethod
    def print_ports(node):
        """Uses "sudo netstat -anp | grep java" to print port where a java
        application listens.

        :param node: Honeycomb node where we want to print the ports.
        :type node: dict
        """

        cmds = ("netstat -anp | grep java",
                "ps -ef | grep [h]oneycomb")

        logger.info("Checking node {} ...".format(node['host']))
        for cmd in cmds:
            logger.info("Command: {}".format(cmd))
            ssh = SSH()
            ssh.connect(node)
            ssh.exec_command_sudo(cmd)

    @staticmethod
    def configure_log_level(node, level):
        """Set Honeycomb logging to the specified level.

        :param node: Honeycomb node.
        :param level: Log level (INFO, DEBUG, TRACE).
        :type node: dict
        :type level: str
        """

        find = 'logger name=\\"io.fd\\"'
        replace = '<logger name=\\"io.fd\\" level=\\"{0}\\"/>'.format(level)

        argument = '"/{0}/c\\ {1}"'.format(find, replace)
        path = "{0}/config/logback.xml".format(Const.REMOTE_HC_DIR)
        command = "sed -i {0} {1}".format(argument, path)

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, stderr) = ssh.exec_command_sudo(command)
        if ret_code != 0:
            raise HoneycombError("Failed to modify configuration on "
                                 "node {0}, {1}".format(node, stderr))

    @staticmethod
    def enable_module_features(node, *features):
        """Configure Honeycomb to use VPP modules that are disabled by default.

        ..Note:: If the module is not enabled in VPP, Honeycomb will
        be unable to establish VPP connection.

        :param node: Honeycomb node.
        :param features: Features to enable.
        :type node: dict
        :type features: string
        :raises HoneycombError: If the configuration could not be changed.
         """

        disabled_features = {
            "NSH": "io.fd.hc2vpp.vppnsh.impl.VppNshModule"
        }

        ssh = SSH()
        ssh.connect(node)

        for feature in features:
            if feature in disabled_features.keys():
                # uncomment by replacing the entire line
                find = replace = "{0}".format(disabled_features[feature])

                argument = '"/{0}/c\\ {1}"'.format(find, replace)
                path = "{0}/modules/*module-config"\
                    .format(Const.REMOTE_HC_DIR)
                command = "sed -i {0} {1}".format(argument, path)

                (ret_code, _, stderr) = ssh.exec_command_sudo(command)
                if ret_code != 0:
                    raise HoneycombError("Failed to modify configuration on "
                                         "node {0}, {1}".format(node, stderr))
            else:
                raise HoneycombError(
                    "Unrecognized feature {0}.".format(feature))

    @staticmethod
    def copy_java_libraries(node):
        """Copy Java libraries installed by vpp-api-java package to honeycomb
        lib folder.

        This is a (temporary?) workaround for jvpp version mismatches.

        :param node: Honeycomb node
        :type node: dict
        """

        ssh = SSH()
        ssh.connect(node)
        (_, stdout, _) = ssh.exec_command_sudo(
            "ls /usr/share/java | grep ^jvpp-*")

        files = stdout.split("\n")[:-1]
        for item in files:
            # example filenames:
            # jvpp-registry-17.04.jar
            # jvpp-core-17.04.jar

            parts = item.split("-")
            version = "{0}-SNAPSHOT".format(parts[2][:5])
            artifact_id = "{0}-{1}".format(parts[0], parts[1])

            directory = "{0}/lib/io/fd/vpp/{1}/{2}".format(
                Const.REMOTE_HC_DIR, artifact_id, version)
            cmd = "sudo mkdir -p {0}; " \
                  "sudo cp /usr/share/java/{1} {0}/{2}-{3}.jar".format(
                    directory, item, artifact_id, version)

            (ret_code, _, stderr) = ssh.exec_command(cmd)
            if ret_code != 0:
                raise HoneycombError("Failed to copy JVPP libraries on "
                                     "node {0}, {1}".format(node, stderr))

    @staticmethod
    def find_odl_client(node):
        """Check if there is a karaf directory in home.

        :param node: Honeycomb node.
        :type node: dict
        :returns: True if ODL client is present on node, else False.
        :rtype: bool
        """

        ssh = SSH()
        ssh.connect(node)
        (ret_code, stdout, _) = ssh.exec_command_sudo(
            "ls ~ | grep karaf")

        logger.debug(stdout)
        return not bool(ret_code)

    @staticmethod
    def start_odl_client(node):
        """Start ODL client on the specified node.

        karaf should be located in home directory, and VPP and Honeycomb should
        already be running, otherwise the start will fail.
        :param node: Nodes to start ODL client on.
        :type node: dict
        :raises HoneycombError: If Honeycomb fails to start.
        """

        logger.console("\nStarting ODL client ...")

        cmd = "~/*karaf*/bin/start"

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise HoneycombError('Node {0} failed to start ODL.'.
                                 format(node['host']))
        else:
            logger.info("Starting the ODL client on node {0} is "
                        "in progress ...".format(node['host']))

    @staticmethod
    def check_odl_startup_state(node):
        """Check the status of ODL client startup.

        :param node: Honeycomb node.
        :param node: dict
        :returns: True when ODL is started.
        :rtype: bool
        :raises HoneycombError: When the response is not code 200: OK.
        """

        path = HcUtil.read_path_from_url_file(
            "odl_client/odl_netconf_connector")
        expected_status_codes = (HTTPCodes.UNAUTHORIZED,
                                 HTTPCodes.FORBIDDEN,
                                 HTTPCodes.NOT_FOUND,
                                 HTTPCodes.SERVICE_UNAVAILABLE,
                                 HTTPCodes.INTERNAL_SERVER_ERROR)

        status_code, _ = HTTPRequest.get(node, path, timeout=10,
                                         enable_logging=False)
        if status_code == HTTPCodes.OK:
            logger.info("ODL client on node {0} is up and running".
                        format(node['host']))
        elif status_code in expected_status_codes:
            if status_code == HTTPCodes.UNAUTHORIZED:
                logger.info('Unauthorized. If this triggers keyword '
                            'timeout, verify username and password.')
            raise HoneycombError('ODL client on node {0} running but '
                                 'not yet ready.'.format(node['host']),
                                 enable_logging=False)
        else:
            raise HoneycombError('Unexpected return code: {0}.'.
                                 format(status_code))
        return True

    @staticmethod
    def mount_honeycomb_on_odl(node):
        """Tell ODL client to mount Honeycomb instance over netconf.

        :param node: Honeycomb node.
        :type node: dict
        :raises HoneycombError: When the response is not code 200: OK.
        """

        path = HcUtil.read_path_from_url_file(
            "odl_client/odl_netconf_connector")

        url_file = "{0}/{1}".format(Const.RESOURCES_TPL_HC,
                                    "odl_client/mount_honeycomb.xml")

        with open(url_file) as template:
            data = template.read()

        status_code, _ = HTTPRequest.post(
            node, path, headers={"Content-Type": "application/xml"},
            payload=data, timeout=10, enable_logging=False)

        if status_code == HTTPCodes.OK:
            logger.info("ODL mount point configured successfully.")
        elif status_code == HTTPCodes.CONFLICT:
            logger.warn("ODL mount point was already configured.")
        else:
            raise HoneycombError('Mount point configuration not successful')
