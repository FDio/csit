# Copyright (c) 2022 Cisco and/or its affiliates.
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

from pprint import pformat
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.papi.bare_executor import BareExecutor
from resources.libraries.python.topology import Topology, SocketType


__all__ = [u"SocketExecutor", u"Disconnector"]


class SocketExecutor(BareExecutor):
    """Methods for executing VPP Python API commands on forwarded socket.

    Previously, we used an implementation with single client instance
    and connection being handled by a resource manager.
    On "with" statement, the instance connected, and disconnected
    on exit from the "with" block.
    This was limiting (no nested with blocks) and mainly it was slow:
    0.7 seconds per disconnect cycle on Skylake, more than 3 second on Taishan.

    The currently used implementation caches the connected client instances,
    providing speedup and making "with" blocks unnecessary.
    But with many call sites, "with" blocks are still the main usage pattern.
    Documentation still lists that as the intended pattern.

    As a downside, clients need to be explicitly told to disconnect
    before VPP restart.
    There is some amount of retries and disconnects on disconnect
    (so unresponsive VPPs do not breach test much more than needed),
    but it is hard to verify all that works correctly.
    Especially, if Robot crashes, files and ssh processes may leak.

    Delay for accepting socket connection is 10s.
    TODO: Decrease 10s to value that is long enough for creating connection
    and short enough to not affect performance.

    The current implementation downloads and parses .api.json files only once
    and caches client instances for reuse.
    Cleanup metadata is added as additional attributes
    directly to client instances.

    The current implementation seems to run into read error occasionally.
    Not sure if the error is in Python code on Robot side, ssh forwarding,
    or socket handling at VPP side. Anyway, reconnect after some sleep
    seems to help, hoping repeated command execution does not lead to surprises.
    The reconnection is logged at WARN level, so it is prominently shown
    in log.html, so we can see how frequently it happens.

    TODO: Support handling of retval!=0 without try/except in caller.

    Note: Use only with "with" statement, e.g.:

        cmd = 'show_version'
        with SocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

    This class processes two classes of VPP PAPI methods:
    1. Simple request / reply: method='request'.
    2. Dump functions: method='dump'.

    Note that access to VPP stats over socket is not supported yet.

    The recommended ways of use are (examples):

    1. Simple request / reply

    a. One request with no arguments:

        cmd = 'show_version'
        with SocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

    b. Three requests with arguments, the second and the third ones are the same
       but with different arguments.

        with SocketExecutor(node) as papi_exec:
            replies = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg)

    2. Dump functions

        cmd = 'sw_interface_rx_placement_dump'
        with SocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index']).\
                get_details(err_msg)
    """

    # Init is inherited.

    @classmethod
    def disconnect_all_sockets_by_node(cls, node):
        """Disconnect all socket connected client instance.

        Noop if not connected.

        Also remove the local sockets by deleting the temporary directory.
        Put disconnected client instances to the reuse list.
        The added attributes are not cleaned up,
        as their values will get overwritten on next connect.

        Call this method just before killing/restarting remote VPP instance.
        """
        sockets = Topology.get_node_sockets(node, socket_type=SocketType.PAPI)
        if sockets:
            for socket in sockets.values():
                # TODO: Remove sockets from topology.
                cls.connector.disconnect(node, socket)
        # Always attempt to disconnect the default socket.
        return cls.connector.disconnect(node)

    def get_replies(self, err_msg="Failed to get replies."):
        """Get replies from VPP Python API.

        The replies are parsed into dict-like objects,
        "retval" field is guaranteed to be zero on success.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Responses, dict objects with fields due to API and "retval".
        :rtype: list of dict
        :raises RuntimeError: If retval is nonzero, parsing or ssh error.
        """
        return self._execute(err_msg=err_msg)

    def get_reply(self, err_msg=u"Failed to get reply."):
        """Get reply from VPP Python API.

        The reply is parsed into dict-like object,
        "retval" field is guaranteed to be zero on success.

        TODO: Discuss exception types to raise, unify with inner methods.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Response, dict object with fields due to API and "retval".
        :rtype: dict
        :raises AssertionError: If retval is nonzero, parsing or ssh error.
        """
        replies = self.get_replies(err_msg=err_msg)
        if len(replies) != 1:
            raise RuntimeError(f"Expected single reply, got {replies!r}")
        return replies[0]

    def get_sw_if_index(self, err_msg=u"Failed to get reply."):
        """Get sw_if_index from reply from VPP Python API.

        Frequently, the caller is only interested in sw_if_index field
        of the reply, this wrapper makes such call sites shorter.

        TODO: Discuss exception types to raise, unify with inner methods.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Response, sw_if_index value of the reply.
        :rtype: int
        :raises AssertionError: If retval is nonzero, parsing or ssh error.
        """
        reply = self.get_reply(err_msg=err_msg)
        logger.trace(f"Getting index from {reply!r}")
        return reply[u"sw_if_index"]

    def get_details(self, err_msg="Failed to get dump details."):
        """Get dump details from VPP Python API.

        The details are parsed into dict-like objects.
        The number of details per single dump command can vary,
        and all association between details and dumps is lost,
        so if you care about the association (as opposed to
        logging everything at once for debugging purposes),
        it is recommended to call get_details for each dump (type) separately.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Details, dict objects with fields due to API without "retval".
        :rtype: list of dict
        """
        return self._execute(err_msg)

    @staticmethod
    def run_cli_cmd(
            node, cli_cmd, log=True, remote_vpp_socket=Constants.SOCKSVR_PATH):
        """Run a CLI command as cli_inband, return the "reply" field of reply.

        Optionally, log the field value.

        :param node: Node to run command on.
        :param cli_cmd: The CLI command to be run on the node.
        :param remote_vpp_socket: Path to remote socket to tunnel to.
        :param log: If True, the response is logged.
        :type node: dict
        :type remote_vpp_socket: str
        :type cli_cmd: str
        :type log: bool
        :returns: CLI output.
        :rtype: str
        """
        cmd = u"cli_inband"
        args = dict(
            cmd=cli_cmd
        )
        err_msg = f"Failed to run 'cli_inband {cli_cmd}' PAPI command " \
            f"on host {node[u'host']}"

        with SocketExecutor(node, remote_vpp_socket) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)["reply"]
        if log:
            logger.info(
                f"{cli_cmd} ({node[u'host']} - {remote_vpp_socket}):\n"
                f"{reply.strip()}"
            )
        return reply

    @staticmethod
    def run_cli_cmd_on_all_sockets(node, cli_cmd, log=True):
        """Run a CLI command as cli_inband, on all sockets in topology file.

        :param node: Node to run command on.
        :param cli_cmd: The CLI command to be run on the node.
        :param log: If True, the response is logged.
        :type node: dict
        :type cli_cmd: str
        :type log: bool
        """
        sockets = Topology.get_node_sockets(node, socket_type=SocketType.PAPI)
        if sockets:
            for socket in sockets.values():
                SocketExecutor.run_cli_cmd(
                    node, cli_cmd, log=log, remote_vpp_socket=socket
                )

    @staticmethod
    def dump_and_log(node, cmds):
        """Dump and log requested information, return None.

        :param node: DUT node.
        :param cmds: Dump commands to be executed.
        :type node: dict
        :type cmds: list of str
        """
        with SocketExecutor(node) as papi_exec:
            for cmd in cmds:
                dump = papi_exec.add(cmd).get_details()
                logger.debug(f"{cmd}:\n{pformat(dump)}")


class Disconnector:
    """Class for holding a single keyword."""

    @staticmethod
    def disconnect_all_papi_connections():
        """Disconnect all connected client instances, tear down the SSH tunnels.

        Also remove the local sockets by deleting the temporary directory.
        Put disconnected client instances to the reuse list.
        The added attributes are not cleaned up,
        as their values will get overwritten on next connect.

        Call this method just before killing/restarting all VPP instances.

        This could be a class method of SocketExecutor.
        But Robot calls methods on instances, and it would be weird
        to give node argument for constructor in import.
        Also, as we have a class of the same name as the module,
        the keywords defined on module level are not accessible.
        """
        connector = SocketExecutor.connector
        if connector:
            connector.disconnect_all()
            return
        logger.info(u"Papi never used, no connections to close.")
