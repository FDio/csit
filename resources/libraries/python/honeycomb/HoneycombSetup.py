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

"""Implementation of keywords for Honeycomb setup."""

from json import loads
from time import time, sleep

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

        cmd = "sudo service honeycomb start"

        for node in nodes:
            if node['type'] == NodeType.DUT:
                logger.console(
                    "\n(re)Starting Honeycomb service on node {0}".format(
                        node["host"]))
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

        cmd = "sudo service honeycomb stop"
        errors = []

        for node in nodes:
            if node['type'] == NodeType.DUT:
                logger.console(
                    "\nShutting down Honeycomb service on node {0}".format(
                        node["host"]))
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
    def restart_honeycomb_on_dut(node):
        """Restart Honeycomb on specified DUT nodes.

        This keyword restarts the Honeycomb service on specified DUTs. Use the
        keyword "Check Honeycomb Startup State" to check if the Honeycomb is up
        and running.

        :param node: Node to restart Honeycomb on.
        :type node: dict
        :raises HoneycombError: If Honeycomb fails to start.
        """

        logger.console(
            "\n(re)Starting Honeycomb service on node {0}".format(node["host"]))

        cmd = "sudo service honeycomb restart"

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            raise HoneycombError('Node {0} failed to restart Honeycomb.'.
                                 format(node['host']))
        else:
            logger.info(
                "Honeycomb service restart is in progress on node {0}".format(
                    node['host']))

    @staticmethod
    def check_honeycomb_startup_state(node, timeout=360, retries=20,
                                      interval=15):
        """Repeatedly check the status of Honeycomb startup until it is fully
        started or until timeout or max retries is reached.

        :param node: Honeycomb node.
        :param timeout: Timeout value in seconds.
        :param retries: Max number of retries.
        :param interval: Interval between checks, in seconds.
        :type node: dict
        :type timeout: int
        :type retries: int
        :type interval: int
        :raises HoneycombError: If the Honeycomb process IP cannot be found,
            or if timeout or number of retries is exceeded.
        """

        ssh = SSH()
        ssh.connect(node)

        count = 0
        start = time()
        while time() - start < timeout and count < retries:
            count += 1

            try:
                status_code_version, _ = HcUtil.get_honeycomb_data(
                    node, "oper_vpp_version")
                status_code_if_cfg, _ = HcUtil.get_honeycomb_data(
                    node, "config_vpp_interfaces")
                status_code_if_oper, _ = HcUtil.get_honeycomb_data(
                    node, "oper_vpp_interfaces")
            except HTTPRequestError:
                sleep(interval)
                continue
            if status_code_if_cfg == HTTPCodes.OK\
                    and status_code_if_cfg == HTTPCodes.OK\
                    and status_code_if_oper == HTTPCodes.OK:
                logger.info("Check successful, Honeycomb is up and running.")
                break
            else:
                logger.debug(
                    "Attempt ${count} failed on Restconf check. Status codes:\n"
                    "Version: {version}\n"
                    "Interface config: {if_cfg}\n"
                    "Interface operational: {if_oper}".format(
                        count=count,
                        version=status_code_version,
                        if_cfg=status_code_if_cfg,
                        if_oper=status_code_if_oper))
                sleep(interval)
                continue
        else:
            _, vpp_status, _ = ssh.exec_command("sudo service vpp status")
            raise HoneycombError(
                "Timeout or max retries exceeded. Status of VPP:\n"
                "{vpp_status}".format(vpp_status=vpp_status))

    @staticmethod
    def check_honeycomb_shutdown_state(node):
        """Check state of Honeycomb service during shutdown on specified nodes.

        Honeycomb nodes reply with connection refused or the following status
        codes depending on shutdown progress: codes 200, 404.

        :param node: List of DUT nodes stopping Honeycomb.
        :type node: dict
        :returns: True if all GETs fail to connect.
        :rtype: bool
        """
        cmd = "pgrep honeycomb"

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

        find = "restconf-binding-address"
        try:
            IPv6Address(unicode(node["host"]))
            # if management IP of the node is in IPv6 format
            replace = '\\"restconf-binding-address\\": \\"0::0\\",'
        except (AttributeError, AddressValueError):
            replace = '\\"restconf-binding-address\\": \\"0.0.0.0\\",'

        argument = '"/{0}/c\\ {1}"'.format(find, replace)
        path = "{0}/config/restconf.json".format(Const.REMOTE_HC_DIR)
        command = "sed -i {0} {1}".format(argument, path)

        ssh = SSH()
        ssh.connect(node)
        (ret_code, _, stderr) = ssh.exec_command_sudo(command)
        if ret_code != 0:
            raise HoneycombError("Failed to modify configuration on "
                                 "node {0}, {1}".format(node, stderr))

    @staticmethod
    def configure_jvpp_timeout(node, timeout=10):
        """Configure timeout value for Java API commands Honeycomb sends to VPP.

        :param node: Information about a DUT node.
        :param timeout: Timeout value in seconds.
        :type node: dict
        :type timeout: int
        :raises HoneycombError: If the configuration could not be changed.
        """

        find = "jvpp-request-timeout"
        replace = '\\"jvpp-request-timeout\\": {0}'.format(timeout)

        argument = '"/{0}/c\\ {1}"'.format(find, replace)
        path = "{0}/config/jvpp.json".format(Const.REMOTE_HC_DIR)
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
                "ls -la /opt/honeycomb",
                "cat /opt/honeycomb/modules/*module-config")

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
    def manage_honeycomb_features(node, feature, disable=False):
        """Configure Honeycomb to use features that are disabled by default, or
        disable previously enabled features.

        ..Note:: If the module is not enabled in VPP, Honeycomb will
        be unable to establish VPP connection.

        :param node: Honeycomb node.
        :param feature: Feature to enable.
        :param disable: Disable the specified feature instead of enabling it.
        :type node: dict
        :type feature: string
        :type disable: bool
        :raises HoneycombError: If the configuration could not be changed.
        """

        disabled_features = {
            "NSH": ["io.fd.hc2vpp.vppnsh.impl.VppNshModule"],
            "BGP": ["io.fd.hc2vpp.bgp.inet.BgpInetModule",
                    "io.fd.honeycomb.infra.bgp.BgpModule",
                    "io.fd.honeycomb.infra.bgp.BgpReadersModule",
                    "io.fd.honeycomb.infra.bgp.BgpWritersModule",
                    "io.fd.honeycomb.northbound.bgp.extension.InetModule",
                    "io.fd.honeycomb.northbound.bgp.extension.EvpnModule",
                    "io.fd.honeycomb.northbound.bgp.extension.L3VpnV4Module",
                    "io.fd.honeycomb.northbound.bgp.extension.L3VpnV6Module",
                    "io.fd.honeycomb.northbound.bgp.extension."
                    "LabeledUnicastModule",
                    "io.fd.honeycomb.northbound.bgp.extension.LinkstateModule"]
        }

        ssh = SSH()
        ssh.connect(node)

        if feature in disabled_features.keys():
            # for every module, uncomment by replacing the entire line
            for item in disabled_features[feature]:
                find = replace = "{0}".format(item)
                if disable:
                    replace = "// {0}".format(find)

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
    def copy_odl_client(node, odl_name, src_path, dst_path):
        """Copy ODL Client from source path to destination path.

        :param node: Honeycomb node.
        :param odl_name: Name of ODL client version to use.
        :param src_path: Source Path where to find ODl client.
        :param dst_path: Destination path.
        :type node: dict
        :type odl_name: str
        :type src_path: str
        :type dst_path: str
        :raises HoneycombError: If the operation fails.
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = "sudo rm -rf {dst}/*karaf_{odl_name} && " \
              "cp -r {src}/*karaf_{odl_name}* {dst}".format(
                  src=src_path, odl_name=odl_name, dst=dst_path)

        ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=180)
        if int(ret_code) != 0:
            raise HoneycombError(
                "Failed to copy ODL client on node {0}".format(node["host"]))

    @staticmethod
    def setup_odl_client(node, path):
        """Start ODL client on the specified node.

        Karaf should be located in the provided path, and VPP and Honeycomb
        should already be running, otherwise the start will fail.

        :param node: Node to start ODL client on.
        :param path: Path to ODL client on node.
        :type node: dict
        :type path: str
        :raises HoneycombError: If Honeycomb fails to start.
        """

        logger.console("\nStarting ODL client ...")
        ssh = SSH()
        ssh.connect(node)

        cmd = "{path}/*karaf*/bin/start clean".format(path=path)
        ret_code, _, _ = ssh.exec_command_sudo(cmd)

        if int(ret_code) != 0:
            raise HoneycombError('Node {0} failed to start ODL.'.
                                 format(node['host']))
        else:
            logger.info("Starting the ODL client on node {0} is "
                        "in progress ...".format(node['host']))

    @staticmethod
    def install_odl_features(node, odl_name, path, *features):
        """Install required features on a running ODL client.

        :param node: Honeycomb node.
        :param odl_name: Name of ODL client version to use.
        :param path: Path to ODL client on node.
        :param features: Optional, list of additional features to install.
        :type node: dict
        :type odl_name: str
        :type path: str
        :type features: list
        """

        ssh = SSH()
        ssh.connect(node)

        auth = "-u karaf"
        if odl_name.lower() == "oxygen":
            auth = "-u karaf -p karaf"

        cmd = "{path}/*karaf*/bin/client {auth} feature:install " \
              "odl-restconf-all " \
              "odl-netconf-connector-all " \
              "odl-netconf-topology".format(path=path, auth=auth)
        for feature in features:
            cmd += " {0}".format(feature)

        ret_code, _, _ = ssh.exec_command_sudo(cmd, timeout=250)

        if int(ret_code) != 0:
            raise HoneycombError("Feature install did not succeed.")

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
    def check_odl_shutdown_state(node):
        """Check the status of ODL client shutdown.

        :param node: Honeycomb node.
        :type node: dict
        :returns: True when ODL is stopped.
        :rtype: bool
        :raises HoneycombError: When the response is not code 200: OK.
        """

        cmd = "pgrep -f karaf"
        path = HcUtil.read_path_from_url_file(
            "odl_client/odl_netconf_connector")

        try:
            HTTPRequest.get(node, path, timeout=10, enable_logging=False)
            raise HoneycombError("ODL client is still running.")
        except HTTPRequestError:
            logger.debug("Connection refused, checking process state....")
            ssh = SSH()
            ssh.connect(node)
            ret_code, _, _ = ssh.exec_command(cmd)
            if ret_code == 0:
                raise HoneycombError("ODL client is still running.")

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
                                    "odl_client/mount_honeycomb.json")

        with open(url_file) as template:
            data = template.read()

        data = loads(data)

        status_code, _ = HTTPRequest.post(
            node,
            path,
            headers={"Content-Type": "application/json",
                     "Accept": "text/plain"},
            json=data,
            timeout=10,
            enable_logging=False)

        if status_code == HTTPCodes.OK:
            logger.info("ODL mount point configured successfully.")
        elif status_code == HTTPCodes.CONFLICT:
            logger.info("ODL mount point was already configured.")
        else:
            raise HoneycombError('Mount point configuration not successful')

    @staticmethod
    def stop_odl_client(node, path):
        """Stop ODL client service on the specified node.

        :param node: Node to start ODL client on.
        :param path: Path to ODL client.
        :type node: dict
        :type path: str
        :raises HoneycombError: If ODL client fails to stop.
        """

        ssh = SSH()
        ssh.connect(node)

        cmd = "{0}/*karaf*/bin/stop".format(path)

        ssh = SSH()
        ssh.connect(node)
        ret_code, _, _ = ssh.exec_command_sudo(cmd)
        if int(ret_code) != 0:
            logger.debug("ODL Client refused to shut down.")
            cmd = "pkill -f 'karaf'"
            (ret_code, _, _) = ssh.exec_command_sudo(cmd)
            if int(ret_code) != 0:
                raise HoneycombError('Node {0} failed to stop ODL.'.
                                     format(node['host']))

        logger.info("ODL client service stopped.")

    @staticmethod
    def set_static_arp(node, ip_address, mac_address):
        """Configure a static ARP entry using arp.

        :param node: Node in topology.
        :param ip_address: IP address for the entry.
        :param mac_address: MAC adddress for the entry.
        :type node: dict
        :type ip_address: str
        :type mac_address: str
        :raises RuntimeError: If the operation fails.
        """

        ssh = SSH()
        ssh.connect(node)
        ret_code, _, _ = ssh.exec_command_sudo("arp -s {0} {1}".format(
            ip_address, mac_address))

        if ret_code != 0:
            raise RuntimeError("Failed to configure static ARP adddress.")


class HoneycombStartupConfig(object):
    """Generator for Honeycomb startup configuration.
    """
    def __init__(self):
        """Initializer."""

        self.template = """#!/bin/sh -
        STATUS=100

        while [ $STATUS -eq 100 ]
        do
          {java_call} -jar $(dirname $0)/{jar_filename}
          STATUS=$?
          echo "Honeycomb exited with status: $STATUS"
          if [ $STATUS -eq 100 ]
          then
            echo "Restarting..."
          fi
        done
        """

        self.java_call = "{scheduler} {affinity} java{jit_mode}{params}"

        self.scheduler = ""
        self.core_affinity = ""
        self.jit_mode = ""
        self.params = ""
        self.numa = ""

        self.config = ""
        self.ssh = SSH()

    def apply_config(self, node):
        """Generate configuration file /opt/honeycomb/honeycomb on the specified
        node.

        :param node: Honeycomb node.
        :type node: dict
        """

        self.ssh.connect(node)
        _, filename, _ = self.ssh.exec_command("ls /opt/honeycomb | grep .jar")

        java_call = self.java_call.format(scheduler=self.scheduler,
                                          affinity=self.core_affinity,
                                          jit_mode=self.jit_mode,
                                          params=self.params)
        self.config = self.template.format(java_call=java_call,
                                           jar_filename=filename)

        self.ssh.connect(node)
        cmd = "echo '{config}' > /tmp/honeycomb " \
              "&& chmod +x /tmp/honeycomb " \
              "&& sudo mv -f /tmp/honeycomb /opt/honeycomb".\
            format(config=self.config)
        self.ssh.exec_command(cmd)

    def set_cpu_scheduler(self, scheduler="FIFO"):
        """Use alternate CPU scheduler.

        Note: OTHER scheduler doesn't load-balance over isolcpus.

        :param scheduler: CPU scheduler to use.
        :type scheduler: str
        """

        schedulers = {"FIFO": "-f 99",  # First In, First Out
                      "RR": "-r 99",  # Round Robin
                      "OTHER": "-o",  # Ubuntu default
                     }
        self.scheduler = "chrt {0}".format(schedulers[scheduler])

    def set_cpu_core_affinity(self, low, high=None):
        """Set core affinity for the honeycomb process and subprocesses.

        :param low: Lowest core ID number.
        :param high: Highest core ID number. Leave empty to use a single core.
        :type low: int
        :type high: int
        """

        self.core_affinity = "taskset -c {low}-{high}".format(
            low=low, high=high if high else low)

    def set_jit_compiler_mode(self, jit_mode):
        """Set running mode for Java's JIT compiler.

        :param jit_mode: Desiret JIT mode.
        :type jit_mode: str
        """

        modes = {"client": " -client",  # Default
                 "server": " -server",  # Higher performance but longer warmup
                 "classic": " -classic"  # Disables JIT compiler
                }

        self.jit_mode = modes[jit_mode]

    def set_memory_size(self, mem_min, mem_max=None):
        """Set minimum and maximum memory use for the JVM.

        :param mem_min: Minimum amount of memory (MB).
        :param mem_max: Maximum amount of memory (MB). Default is 4 times
            minimum value.
        :type mem_min: int
        :type mem_max: int
        """

        self.params += " -Xms{min}m -Xmx{max}m".format(
            min=mem_min, max=mem_max if mem_max else mem_min*4)

    def set_metaspace_size(self, mem_min, mem_max=None):
        """Set minimum and maximum memory used for class metadata in the JVM.

        :param mem_min: Minimum metaspace size (MB).
        :param mem_max: Maximum metaspace size (MB). Defailt is 4 times
            minimum value.
        :type mem_min: int
        :type mem_max: int
        """

        self.params += " -XX:MetaspaceSize={min}m " \
                       "-XX:MaxMetaspaceSize={max}m".format(
                           min=mem_min, max=mem_max if mem_max else mem_min*4)

    def set_numa_optimization(self):
        """Use optimization of memory use and garbage collection for NUMA
        architectures."""

        self.params += " -XX:+UseNUMA -XX:+UseParallelGC"

    def set_ssh_security_provider(self):
        """Disables BouncyCastle for SSHD."""
        # Workaround for issue described in:
        # https://wiki.fd.io/view/Honeycomb/Releases/1609/Honeycomb_and_ODL

        self.params += " -Dorg.apache.sshd.registerBouncyCastle=false"
