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

import copy
import glob
import shutil
import struct  # vpp-papi can raise struct.error
import subprocess
import sys
import tempfile
import time
from collections import UserDict


from pprint import pformat
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.FilteredLogger import FilteredLogger
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.papi.client import Clients
from resources.libraries.python.ssh import (exec_cmd_no_error, scp_node)
from resources.libraries.python.topology import Topology, SocketType
from resources.libraries.python.VppApiCrc import VppApiCrcChecker


__all__ = [u"PapiSocketExecutor", u"Disconnector"]


def dictize(obj):
    """A helper method, to make namedtuple-like object accessible as dict.

    If the object is namedtuple-like, its _asdict() form is returned,
    but in the returned object __getitem__ method is wrapped
    to dictize also any items returned.
    If the object does not have _asdict, it will be returned without any change.
    Integer keys still access the object as tuple.

    A more useful version would be to keep obj mostly as a namedtuple,
    just add getitem for string keys. Unfortunately, namedtuple inherits
    from tuple, including its read-only __getitem__ attribute,
    so we cannot monkey-patch it.

    TODO: Create a proxy for named tuple to allow that.

    :param obj: Arbitrary object to dictize.
    :type obj: object
    :returns: Dictized object.
    :rtype: same as obj type or collections.OrderedDict
    """
    if not hasattr(obj, u"_asdict"):
        return obj
    overriden = UserDict(obj._asdict())
    old_get = overriden.__getitem__
    new_get = lambda self, key: dictize(old_get(self, key))
    overriden.__getitem__ = new_get
    return overriden


class PapiSocketExecutor:
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
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

    This class processes two classes of VPP PAPI methods:
    1. Simple request / reply: method='request'.
    2. Dump functions: method='dump'.

    Note that access to VPP stats over socket is not supported yet.

    The recommended ways of use are (examples):

    1. Simple request / reply

    a. One request with no arguments:

        cmd = 'show_version'
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

    b. Three requests with arguments, the second and the third ones are the same
       but with different arguments.

        with PapiSocketExecutor(node) as papi_exec:
            replies = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg)

    2. Dump functions

        cmd = 'sw_interface_rx_placement_dump'
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index']).\
                get_details(err_msg)
    """

    # Class cache for reuse between instances.
    clients = None
    conn_cache = dict()
    """Mapping from node key to connected client instance."""

    def __init__(self, node, remote_vpp_socket=Constants.SOCKSVR_PATH):
        """Store the given arguments, declare managed variables.

        :param node: Node to connect to and forward unix domain socket from.
        :param remote_vpp_socket: Path to remote socket to tunnel to.
        :type node: dict
        :type remote_vpp_socket: str
        """
        self._node = node
        self._remote_vpp_socket = remote_vpp_socket
        # The list of PAPI commands to be executed on the node.
        self._api_command_list = list()
        cls = self.__class__
        if not cls.clients:
            cls.clients = Clients(node)

    @classmethod
    def key_for_node_and_socket(cls, node, remote_socket):
        """Return a hashable object to distinguish nodes.

        The usual node object (of "dict" type) is not hashable,
        and can contain mutable information (mostly virtual interfaces).
        Use this method to get an object suitable for being a key in dict.

        The fields to include are chosen by what ssh needs.

        This class method is needed, for disconnect.

        :param node: The node object to distinguish.
        :param remote_socket: Path to remote socket.
        :type node: dict
        :type remote_socket: str
        :return: Tuple of values distinguishing this node from similar ones.
        :rtype: tuple of str
        """
        return (
            node[u"host"],
            node[u"port"],
            remote_socket,
            # TODO: Do we support sockets paths such as "~/vpp/api.socket"?
            # If yes, add also:
            # node[u"username"],
        )

    def key_for_self(self):
        """Return a hashable object to distinguish nodes.

        Just a wrapper around key_for_node_and_socket
        which sets up proper arguments.

        :return: Tuple of values distinguishing this node from similar ones.
        :rtype: tuple of str
        """
        return self.__class__.key_for_node_and_socket(
            self._node, self._remote_vpp_socket,
        )

    def set_connected_client(self, client):
        """Add a connected client instance into cache.

        This hides details of what the node key is.

        If there already is a client for the computed key,
        fail, as it is a sign of resource leakage.

        :param client: VPP client instance in connected state.
        :type client: vpp_papi.VPPApiClient
        :raises RuntimeError: If related key already has a cached client.
        """
        key = self.key_for_self()
        cache = self.__class__.conn_cache
        if key in cache:
            raise RuntimeError(f"Caching client with existing key: {key}")
        cache[key] = client

    def get_connected_client(self, check_connected=True):
        """Return None or cached connected client.

        If check_connected, RuntimeError is raised when the client is
        not in cache. None is returned if client is not in cache
        (and the check is disabled).

        This hides details of what the node key is.

        :param check_connected: Whether cache miss raises.
        :type check_connected: bool
        :returns: Connected client instance, or None if uncached and no check.
        :rtype: Optional[vpp_papi.VPPApiClient]
        :raises RuntimeError: If cache miss and check enabled.
        """
        key = self.key_for_self()
        ret = self.__class__.conn_cache.get(key, None)

        if ret is None:
            if check_connected:
                raise RuntimeError(f"Client not cached for key: {key}")
        else:
            # When reading logs, it is good to see which VPP is accessed.
            logger.debug(f"Activated cached PAPI client for key: {key}")
        return ret

    def __enter__(self):
        """Create a tunnel, connect VPP instance.

        If the connected client is in cache, return it.
        Only if not, create a new (or reuse a disconnected) client instance.

        Only at this point a local socket names are created
        in a temporary directory, as CSIT can connect to multiple VPPs.

        The following attributes are added to the client instance
        to simplify caching and cleanup:
        csit_temp_dir
            - Temporary socket files are created here.
        csit_control_socket
            - This socket controls the local ssh process doing the forwarding.
        csit_local_vpp_socket
            - This is the forwarded socket to talk with remote VPP.

        The attribute names do not start with underscore,
        so pylint does not complain about accessing private attribute.
        The attribute names start with csit_ to avoid naming conflicts
        with "real" attributes from VPP Python code.

        :returns: self
        :rtype: PapiSocketExecutor
        """
        # Do we have the connected instance in the cache?
        vpp_client = self.get_connected_client(check_connected=False)
        if vpp_client is not None:
            return self
        # No luck, create and connect a new instance.
        time_enter = time.time()
        node = self._node
        # Parsing takes longer than connecting, prepare instance before tunnel.
        vpp_client = self.clients.get_vpp_client()
        # Store into cache as soon as possible.
        # If connection fails, it is better to attempt disconnect anyway.
        self.set_connected_client(vpp_client)
        # Set additional attributes.
        vpp_client.csit_temp_dir = tempfile.TemporaryDirectory(dir=u"/tmp")
        temp_path = vpp_client.csit_temp_dir.name
        api_socket = temp_path + u"/vpp-api.sock"
        vpp_client.csit_local_vpp_socket = api_socket
        ssh_socket = temp_path + u"/ssh.sock"
        vpp_client.csit_control_socket = ssh_socket
        # Cleanup possibilities.
        ret_code, _ = run([u"ls", ssh_socket], check=False)
        if ret_code != 2:
            # This branch never seems to be hit in CI,
            # but may be useful when testing manually.
            run(
                [u"ssh", u"-S", ssh_socket, u"-O", u"exit", u"0.0.0.0"],
                check=False, log=True
            )
            # TODO: Is any sleep necessary? How to prove if not?
            run([u"sleep", u"0.1"])
            run([u"rm", u"-vrf", ssh_socket])
        # Even if ssh can perhaps reuse this file,
        # we need to remove it for readiness detection to work correctly.
        run([u"rm", u"-rvf", api_socket])
        # We use sleep command. The ssh command will exit in 30 second,
        # unless a local socket connection is established,
        # in which case the ssh command will exit only when
        # the ssh connection is closed again (via control socket).
        # The log level is to suppress "Warning: Permanently added" messages.
        ssh_cmd = [
            u"ssh", u"-S", ssh_socket, u"-M", u"-L",
            api_socket + u":" + self._remote_vpp_socket,
            u"-p", str(node[u"port"]),
            u"-o", u"LogLevel=ERROR",
            u"-o", u"UserKnownHostsFile=/dev/null",
            u"-o", u"StrictHostKeyChecking=no",
            u"-o", u"ExitOnForwardFailure=yes",
            node[u"username"] + u"@" + node[u"host"],
            u"sleep", u"30"
        ]
        priv_key = node.get(u"priv_key")
        if priv_key:
            # This is tricky. We need a file to pass the value to ssh command.
            # And we need ssh command, because paramiko does not support sockets
            # (neither ssh_socket, nor _remote_vpp_socket).
            key_file = tempfile.NamedTemporaryFile()
            key_file.write(priv_key)
            # Make sure the content is written, but do not close yet.
            key_file.flush()
            ssh_cmd[1:1] = [u"-i", key_file.name]
        password = node.get(u"password")
        if password:
            # Prepend sshpass command to set password.
            ssh_cmd[:0] = [u"sshpass", u"-p", password]
        time_stop = time.time() + 10.0
        # subprocess.Popen seems to be the best way to run commands
        # on background. Other ways (shell=True with "&" and ssh with -f)
        # seem to be too dependent on shell behavior.
        # In particular, -f does NOT return values for run().
        subprocess.Popen(ssh_cmd)
        # Check socket presence on local side.
        while time.time() < time_stop:
            # It can take a moment for ssh to create the socket file.
            ret_code, _ = run(
                [u"ls", u"-l", api_socket], check=False
            )
            if not ret_code:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError(u"Local side socket has not appeared.")
        if priv_key:
            # Socket up means the key has been read. Delete file by closing it.
            key_file.close()
        # Everything is ready, set the local socket address and connect.
        vpp_client.transport.server_address = api_socket
        # It seems we can get read error even if every preceding check passed.
        # Single retry seems to help.
        for _ in range(2):
            try:
                vpp_client.connect_sync(u"csit_socket")
            except (IOError, struct.error) as err:
                logger.warn(f"Got initial connect error {err!r}")
                vpp_client.disconnect()
            else:
                break
        else:
            raise RuntimeError(u"Failed to connect to VPP over a socket.")
        logger.trace(
            f"Establishing socket connection took {time.time()-time_enter}s"
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """No-op, the client instance remains in cache in connected state."""

    @classmethod
    def disconnect_by_key(cls, key):
        """Disconnect a connected client instance, noop it not connected.

        Also remove the local sockets by deleting the temporary directory.
        Put disconnected client instances to the reuse list.
        The added attributes are not cleaned up,
        as their values will get overwritten on next connect.

        This method is useful for disconnect_all type of work.

        :param key: Tuple identifying the node (and socket).
        :type key: tuple of str
        """
        vpp_client = cls.conn_cache.get(key, None)
        if vpp_client is None:
            return
        logger.debug(f"Disconnecting by key: {key}")
        vpp_client.disconnect()
        run([
            u"ssh", u"-S", vpp_client.csit_control_socket, u"-O",
            u"exit", u"0.0.0.0"
        ], check=False)
        # Temp dir has autoclean, but deleting explicitly
        # as an error can happen.
        try:
            vpp_client.csit_temp_dir.cleanup()
        except FileNotFoundError:
            # There is a race condition with ssh removing its ssh.sock file.
            # Single retry should be enough to ensure the complete removal.
            shutil.rmtree(vpp_client.csit_temp_dir.name)
        # Finally, put disconnected clients to reuse list.
        self.clients.recycle_client(vpp_client)
        # Invalidate cache last. Repeated errors are better than silent leaks.
        del cls.conn_cache[key]

    @classmethod
    def disconnect_by_node_and_socket(
            cls, node, remote_socket=Constants.SOCKSVR_PATH
        ):
        """Disconnect a connected client instance, noop it not connected.

        Also remove the local sockets by deleting the temporary directory.
        Put disconnected client instances to the reuse list.
        The added attributes are not cleaned up,
        as their values will get overwritten on next connect.

        Call this method just before killing/restarting remote VPP instance.
        """
        key = cls.key_for_node_and_socket(node, remote_socket)
        return cls.disconnect_by_key(key)

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
                PapiSocketExecutor.disconnect_by_node_and_socket(node, socket)
        # Always attempt to disconnect the default socket.
        return cls.disconnect_by_node_and_socket(node)

    @staticmethod
    def disconnect_all_papi_connections():
        """Disconnect all connected client instances, tear down the SSH tunnels.

        Also remove the local sockets by deleting the temporary directory.
        Put disconnected client instances to the reuse list.
        The added attributes are not cleaned up,
        as their values will get overwritten on next connect.

        This should be a class method,
        but we prefer to call static methods from Robot.

        Call this method just before killing/restarting all VPP instances.
        """
        cls = PapiSocketExecutor
        # Iterate over copy of entries so deletions do not mess with iterator.
        keys_copy = list(cls.conn_cache.keys())
        for key in keys_copy:
            cls.disconnect_by_key(key)

    def add(self, csit_papi_command, history=True, **kwargs):
        """Add next command to internal command list; return self.

        Unless disabled, new entry to papi history is also added at this point.
        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.
        The kwargs dict is deep-copied, so it is safe to use the original
        with partial modifications for subsequent commands.

        Any pending conflicts from .api.json processing are raised.
        Then the command name is checked for known CRCs.
        Unsupported commands raise an exception, as CSIT change
        should not start using messages without making sure which CRCs
        are supported.
        Each CRC issue is raised only once, so subsequent tests
        can raise other issues.

        :param csit_papi_command: VPP API command.
        :param history: Enable/disable adding command to PAPI command history.
        :param kwargs: Optional key-value arguments.
        :type csit_papi_command: str
        :type history: bool
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiSocketExecutor
        :raises RuntimeError: If unverified or conflicting CRC is encountered.
        """
        self.crc_checker.report_initial_conflicts()
        if history:
            PapiHistory.add_to_papi_history(
                self._node, csit_papi_command, **kwargs
            )
        self.crc_checker.check_api_name(csit_papi_command)
        self._api_command_list.append(
            dict(
                api_name=csit_papi_command,
                api_args=copy.deepcopy(kwargs)
            )
        )
        return self

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

        with PapiSocketExecutor(node, remote_vpp_socket) as papi_exec:
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
                PapiSocketExecutor.run_cli_cmd(
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
        with PapiSocketExecutor(node) as papi_exec:
            for cmd in cmds:
                dump = papi_exec.add(cmd).get_details()
                logger.debug(f"{cmd}:\n{pformat(dump)}")

    def _execute(self, err_msg=u"Undefined error message", exp_rv=0):
        """Turn internal command list into data and execute; return replies.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_replies()
        - get_reply()
        - get_sw_if_index()
        - get_details()

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Papi responses parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: list of dict
        :raises RuntimeError: If the replies are not all correct.
        """
        vpp_client = self.get_connected_client()
        local_list = self._api_command_list
        # Clear first as execution may fail.
        self._api_command_list = list()
        replies = list()
        for command in local_list:
            api_name = command[u"api_name"]
            papi_fn = getattr(vpp_client.api, api_name)
            try:
                try:
                    reply = papi_fn(**command[u"api_args"])
                except (IOError, struct.error) as err:
                    # Occasionally an error happens, try reconnect.
                    logger.warn(f"Reconnect after error: {err!r}")
                    vpp_client.disconnect()
                    # Testing shows immediate reconnect fails.
                    time.sleep(1)
                    vpp_client.connect_sync(u"csit_socket")
                    logger.trace(u"Reconnected.")
                    reply = papi_fn(**command[u"api_args"])
            except (AttributeError, IOError, struct.error) as err:
                raise AssertionError(err_msg) from err
            # *_dump commands return list of objects, convert, ordinary reply.
            if not isinstance(reply, list):
                reply = [reply]
            for item in reply:
                message_name = item.__class__.__name__
                self.crc_checker.check_api_name(message_name)
                dict_item = dictize(item)
                if u"retval" in dict_item.keys():
                    # *_details messages do not contain retval.
                    retval = dict_item[u"retval"]
                    if retval != exp_rv:
                        raise AssertionError(
                            f"Retval {retval!r} does not match expected "
                            f"retval {exp_rv!r} in message {message_name} "
                            f"for command {command}."
                        )
                replies.append(dict_item)
        return replies


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

        This could be a class method of PapiSocketExecutor.
        But Robot calls methods on instances, and it would be weird
        to give node argument for constructor in import.
        Also, as we have a class of the same name as the module,
        the keywords defined on module level are not accessible.
        """
        cls = PapiSocketExecutor
        # Iterate over copy of entries so deletions do not mess with iterator.
        keys_copy = list(cls.conn_cache.keys())
        for key in keys_copy:
            cls.disconnect_by_key(key)
