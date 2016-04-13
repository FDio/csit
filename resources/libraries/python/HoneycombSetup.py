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

from xml.etree import ElementTree as ET

from robot.api import logger

from resources.libraries.python.topology import NodeType
from resources.libraries.python.ssh import SSH
from resources.libraries.python.HTTPRequest import HTTPRequest, HTTPCodes, \
    HTTPRequestError
from resources.libraries.python.HoneycombUtil import HoneycombUtil as HcUtil
from resources.libraries.python.HoneycombUtil import HoneycombError
from resources.libraries.python.constants import Constants as Const


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
    def start_honeycomb_on_all_duts(nodes):
        """Start Honeycomb on all DUT nodes in topology.

        This keyword starts the Honeycomb service on all DUTs. The keyword just
        starts the Honeycomb and does not check its startup state. Use the
        keyword "Check Honeycomb Startup State" to check if the Honeycomb is up
        and running.
        Honeycomb must be installed in "/opt" directory, otherwise the start
        will fail.
        :param nodes: All nodes in topology.
        :type nodes: dict
        :raises HoneycombError: If Honeycomb fails to start.
        """
        logger.console("Starting Honeycomb service ...")

        cmd = "{0}/start".format(Const.REMOTE_HC_DIR)

        for node in nodes.values():
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
    def stop_honeycomb_on_all_duts(nodes):
        """Stop the Honeycomb service on all DUTs.

        This keyword stops the Honeycomb service on all nodes. It just stops the
        Honeycomb and does not check its shutdown state. Use the keyword "Check
        Honeycomb Shutdown State" to check if Honeycomb has stopped.
        :param nodes: Nodes in topology.
        :type nodes: dict
        :raises HoneycombError: If Honeycomb failed to stop.
        """
        logger.console("Shutting down Honeycomb service ...")

        cmd = "{0}/stop".format(Const.REMOTE_HC_DIR)
        errors = []

        for node in nodes.values():
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
    def check_honeycomb_startup_state(nodes):
        """Check state of Honeycomb service during startup.

        Reads html path from template file oper_vpp_version.url.

        Honeycomb node replies with connection refused or the following status
        codes depending on startup progress: codes 200, 401, 403, 404, 503

        :param nodes: Nodes in topology.
        :type nodes: dict
        :return: True if all GETs returned code 200(OK).
        :rtype bool
        """

        path = HcUtil.read_path_from_url_file("oper_vpp_version")
        expected_status_codes = (HTTPCodes.UNAUTHORIZED,
                                 HTTPCodes.FORBIDDEN,
                                 HTTPCodes.NOT_FOUND,
                                 HTTPCodes.SERVICE_UNAVAILABLE)

        for node in nodes.values():
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
    def check_honeycomb_shutdown_state(nodes):
        """Check state of Honeycomb service during shutdown.

        Honeycomb node replies with connection refused or the following status
        codes depending on shutdown progress: codes 200, 404.

        :param nodes: Nodes in topology.
        :type nodes: dict
        :return: True if all GETs fail to connect.
        :rtype bool
        """

        cmd = "ps -ef | grep -v grep | grep karaf"
        for node in nodes.values():
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
    def add_vpp_to_honeycomb_network_topology(nodes):
        """Add vpp node to Honeycomb network topology.

        :param nodes: All nodes in test topology.
        :type nodes: dict
        :return: Status code and response content from PUT requests.
        :rtype: tuple
        :raises HoneycombError: If a node was not added to Honeycomb topology.

        Reads HTML path from template file config_topology_node.url.
        Path to the node to be added, e.g.:
        ("/restconf/config/network-topology:network-topology"
         "/topology/topology-netconf/node/")
        There must be "/" at the end, as generated node name is added at the
        end.

        Reads payload data from template file add_vpp_to_topology.xml.
        Information about node as XML structure, e.g.:
        <node xmlns="urn:TBD:params:xml:ns:yang:network-topology">
            <node-id>
                {vpp_host}
            </node-id>
            <host xmlns="urn:opendaylight:netconf-node-topology">
                {vpp_ip}
            </host>
            <port xmlns="urn:opendaylight:netconf-node-topology">
                {vpp_port}
            </port>
            <username xmlns="urn:opendaylight:netconf-node-topology">
                {user}
            </username>
            <password xmlns="urn:opendaylight:netconf-node-topology">
                {passwd}
            </password>
            <tcp-only xmlns="urn:opendaylight:netconf-node-topology">
                false
            </tcp-only>
            <keepalive-delay xmlns="urn:opendaylight:netconf-node-topology">
                0
            </keepalive-delay>
        </node>
        NOTE: The placeholders:
            {vpp_host}
            {vpp_ip}
            {vpp_port}
            {user}
            {passwd}
        MUST be there as they are replaced by correct values.
        """

        path = HcUtil.read_path_from_url_file("config_topology_node")
        try:
            xml_data = ET.parse("{0}/add_vpp_to_topology.xml".
                                format(Const.RESOURCES_TPL_HC))
        except ET.ParseError as err:
            raise HoneycombError(repr(err))
        data = ET.tostring(xml_data.getroot())

        headers = {"Content-Type": "application/xml"}

        status_codes = []
        responses = []
        for node_name, node in nodes.items():
            if node['type'] == NodeType.DUT:
                try:
                    payload = data.format(
                        vpp_host=node_name,
                        vpp_ip=node["host"],
                        vpp_port=node['honeycomb']["netconf_port"],
                        user=node['honeycomb']["user"],
                        passwd=node['honeycomb']["passwd"])
                    status_code, resp = HTTPRequest.put(
                        node=node,
                        path="{0}/{1}".format(path, node_name),
                        headers=headers,
                        payload=payload)
                    if status_code != HTTPCodes.OK:
                        raise HoneycombError(
                            "VPP {0} was not added to topology. "
                            "Status code: {1}.".format(node["host"],
                                                       status_code))

                    status_codes.append(status_code)
                    responses.append(resp)

                except HTTPRequestError as err:
                    raise HoneycombError("VPP {0} was not added to topology.".
                                         format(node["host"]), repr(err))
        return status_codes, responses
