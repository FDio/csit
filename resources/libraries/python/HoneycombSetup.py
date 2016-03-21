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


from robot.api import logger
from topology import NodeType
from ssh import SSH
from HTTPRequest import HTTPRequest, HTTPRequestError, HTTPCodes
from constants import Constants as C
from xml.etree import ElementTree as xml


class HoneycombError(Exception):
    """Exception(s) raised by methods working with Honeycomb."""

    def __init__(self, msg, enable_logging=True):
        """Sets the exception message and enables / disables logging

        It is not wanted to log errors when using these keywords together
        with keywords like "Wait until keyword succeeds".

        :param msg: Message to be displayed and logged
        :param enable_logging: When True, logging is enabled, otherwise
        logging is disabled.
        :type msg: str
        :type enable_logging: bool
        """
        self._msg = msg
        self._repr_msg = self.__module__ + '.' + \
                         self.__class__.__name__ + ": " + self._msg
        if enable_logging:
            logger.error(self._msg)
            logger.debug(self._repr_msg)

    def __repr__(self):
        return repr(self._repr_msg)

    def __str__(self):
        return str(self._repr_msg)


class HoneycombSetup(object):

    def __init__(self):
        pass

    @staticmethod
    def start_honeycomb_on_all_duts(nodes):
        """Start honeycomb on all DUT nodes in topology.

        :param nodes: all nodes in topology
        :type nodes: dict
        :raises HoneycombError: if a DUT node is missing honeycomb information.
        """

        logger.console("Starting honeycomb service")

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                try:
                    if (node['honeycomb_user'] and node['honeycomb_passwd'] and
                            node['honeycomb_port'] and node['netconf_port']):
                        HoneycombSetup.start_honeycomb(node)
                except KeyError:
                    raise HoneycombError(
                        'Insufficient information about node {0} in topology'.
                        format(node['host']))

    @staticmethod
    def start_honeycomb(node):
        """Start up honeycomb on DUT node.

        :param node: DUT node with honeycomb
        :type node: dict
        :return: ret_code, stdout, stderr
        :rtype: tuple
        :raises HoneycombError: if Honeycomb fails to start.
        """

        ssh = SSH()
        ssh.connect(node)
        (ret_code, stdout, stderr) = \
            ssh.exec_command_sudo('{0}/start'.format(C.REMOTE_HC_DIR))
        if 0 != int(ret_code):
            logger.debug('stdout: {0}'.format(stdout))
            logger.debug('stderr: {0}'.format(stderr))
            raise HoneycombError('Node {0} failed to start honeycomb'.
                                 format(node['host']))
        return ret_code, stdout, stderr

    @staticmethod
    def stop_honeycomb_on_all_duts(nodes):
        """Stop the honeycomb service on all DUTs.

        :param nodes: nodes in topology
        :type nodes: dict
        :return: ret_code, stdout, stderr
        :rtype: tuple
        :raises HoneycombError: if Honeycomb failed to stop.
        """
        logger.console("Shutting down honeycomb service")
        errors = []
        for node in nodes.values():
            if node['type'] == NodeType.DUT:

                ssh = SSH()
                ssh.connect(node)
                (ret_code, stdout, stderr) = \
                    ssh.exec_command_sudo('{0}/stop'.format(C.REMOTE_HC_DIR))
                if 0 != int(ret_code):
                    logger.debug('stdout: {0}'.format(stdout))
                    logger.debug('stderr: {0}'.format(stderr))
                    errors.append(node['host'])
                    continue
                logger.info("Honeycomb on node {0} was successfully stopped.".
                            format(node['host']))
        if errors:
            raise HoneycombError('Nodes {0} failed to stop honeycomb'.
                                 format(errors))

    @staticmethod
    def check_honeycomb_startup_state(nodes):
        """Check state of honeycomb service during startup.

        Reads html path from template file vpp_version.hc

        Honeycomb node replies with connection refused or the following status
        codes depending on startup progress: codes 200, 401, 403, 404, 503

        :param nodes: nodes in topology
        :type nodes: dict
        :return: True if all GETs returned code 200(OK)
        :rtype bool
        """

        with open("{0}/vpp_version.hc".format(C.RESOURCES_TPL_HC)) as f:
            data = f.readline()

        expected_status_codes = (HTTPCodes.UNAUTHORIZED,
                                 HTTPCodes.FORBIDDEN,
                                 HTTPCodes.NOT_FOUND,
                                 HTTPCodes.SERVICE_UNAVAILABLE)

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                status_code, resp = HTTPRequest.get(
                        node,
                        data,
                        timeout=10,
                        enable_logging=False)
                if status_code == HTTPCodes.OK:
                    pass
                elif status_code in expected_status_codes:
                    raise HoneycombError('honeycomb running but not yet ready',
                                         enable_logging=False)
                else:
                    raise HoneycombError('unexpected return code: {0}'.
                                         format(status_code))
        return True

    @staticmethod
    def check_honeycomb_shutdown_state(nodes):
        """Check state of honeycomb service during shutdown.

        Honeycomb node replies with connection refused or the following status
        codes depending on shutdown progress: codes 200, 404

        :param nodes: nodes in topology
        :type nodes: dict
        :return: True if all GETs fail to connect
        :rtype bool
        """

        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                try:
                    status_code, resp = HTTPRequest.get(
                            node,
                            '/index.html',
                            timeout=5,
                            enable_logging=False)
                    if status_code == HTTPCodes.OK:
                        raise HoneycombError('honeycomb still running',
                                             enable_logging=False)
                    elif status_code == HTTPCodes.NOT_FOUND:
                        raise HoneycombError('honeycomb shutting down',
                                             enable_logging=False)
                    else:
                        raise HoneycombError('unexpected return code: {0}'.
                                             format(status_code))
                except HTTPRequestError:
                    logger.debug('Connection refused')
                    pass

        return True


    @staticmethod
    def add_vpp_to_honeycomb_network_topology(nodes, headers):
        """Add vpp node to Honeycomb network topology

        :param nodes: all nodes in test topology
        :param headers: headers to be used with PUT requests
        :type nodes: dict
        :type headers: dict
        :return: status code and response from PUT requests
        :rtype: tuple
        :raises HoneycombError: if a node was not added to honeycomb topology

        Reads HTML path from template file config_topology_node.hc
        Path to the node to be added, e.g.:
        ("/restconf/config/network-topology:network-topology"
         "/topology/topology-netconf/node/")
        There must be "/" at the end, as generated node name is added
        at the end.

        Reads payload data from template file add_vpp_to_topology.xml
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
                {honeycomb_user}
            </username>
            <password xmlns="urn:opendaylight:netconf-node-topology">
                {honeycomb_passwd}
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
            {honeycomb_user}
            {honeycomb_passwd}
        MUST be there as they are replaced by correct values.
        """

        with open("{0}/config_topology_node.hc".
                          format(C.RESOURCES_TPL_HC)) as f:
            path = f.readline()+'/'

        xml_data = xml.parse("{0}/add_vpp_to_topology.xml".
                             format(C.RESOURCES_TPL_HC))
        data = xml.tostring(xml_data.getroot())

        vpp_id = 0
        status_code = []
        response = []
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                vpp_id += 1
                try:
                    payload = data.format(
                        vpp_host=("vpp" + str(vpp_id)),
                        vpp_ip=node["host"],
                        vpp_port=node["netconf_port"],
                        honeycomb_user=node["honeycomb_user"],
                        honeycomb_passwd=node["honeycomb_passwd"])
                    sc, resp = HTTPRequest.put(
                        node=node,
                        path=path + "vpp" + str(vpp_id),
                        headers=headers,
                        payload=payload)
                    if sc != HTTPCodes.OK:
                        raise HoneycombError(
                            "VPP {0} was not added to topology. "
                            "Status code: {1}".format(node["host"], sc))

                    status_code.append(sc)
                    response.append(resp)

                except HTTPRequestError as err:
                    raise HoneycombError(
                        "VPP {0} was not added to topology.\n{1}"
                        .format(node["host"], repr(err)))

        return status_code, response
