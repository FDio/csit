# Copyright (c) 2024 Cisco and/or its affiliates.
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

TODO: Document sync and async handling properly.
"""

import copy
import glob
import json
import logging
import shutil
import struct  # vpp-papi can raise struct.error
import subprocess
import sys
import tempfile
import time
from collections import deque, UserDict

from pprint import pformat
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.FilteredLogger import FilteredLogger
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.ssh import (
    SSH,
    SSHTimeout,
    exec_cmd_no_error,
    scp_node,
)
from resources.libraries.python.topology import Topology, SocketType
from resources.libraries.python.VppApiCrc import VppApiCrcChecker


__all__ = [
    "PapiExecutor",
    "PapiSocketExecutor",
    "Disconnector",
]


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
    :rtype: same as obj type or collections.UserDict
    """
    if not hasattr(obj, "_asdict"):
        return obj
    overriden = UserDict(obj._asdict())
    old_get = overriden.__getitem__
    overriden.__getitem__ = lambda self, key: dictize(old_get(self, key))
    return overriden


def dictize_and_check_retval(obj, err_msg):
    """Make namedtuple-like object accessible as dict, check retval if exists.

    If the object contains "retval" field, raise when the value is non-zero.

    See dictize() for what it means to dictize.

    :param obj: Arbitrary object to dictize.
    :param err_msg: The (additional) text for the raised exception.
    :type obj: object
    :type err_msg: str
    :returns: Dictized object.
    :rtype: same as obj type or collections.UserDict
    :raises AssertionError: If retval field is present with nonzero value.
    """
    ret = dictize(obj)
    if ctx := ret.get("context"):
        logger.debug(f"context {ctx}")
    # *_details messages do not contain retval.
    retval = ret.get("retval", 0)
    if retval != 0:
        raise AssertionError(f"{err_msg}\nRetval nonzero in object {ret!r}")
    return ret


class PapiSocketExecutor:
    """Methods for executing VPP Python API commands on forwarded socket.

    The current implementation downloads and parses .api.json files only once
    and caches client instances for reuse.
    Cleanup metadata is added as additional attributes
    directly to the client instances.

    The current implementation caches the connected client instances.
    As a downside, clients need to be explicitly told to disconnect
    before VPP restart.

    The current implementation seems to run into read error occasionally.
    Not sure if the error is in Python code on Robot side, ssh forwarding,
    or socket handling at VPP side. Anyway, reconnect after some sleep
    seems to help, hoping repeated command execution does not lead to surprises.
    The reconnection is logged at WARN level, so it is prominently shown
    in log.html, so we can see how frequently it happens.
    There are similar retries cleanups in other places
    (so unresponsive VPPs do not break test much more than needed),
    but it is hard to verify all that works correctly.
    Especially, if Robot crashes, files and ssh processes may leak.

    TODO: Decrease current timeout value when creating connections
    so broken VPP does not prolong job duration too much
    while good VPP (almost) never fails to connect.

    TODO: Support handling of retval!=0 without try/except in caller.

    This class processes two classes of VPP PAPI methods:
    1. Simple request / reply: method='request'.
    2. Dump functions: method='dump'.

    Note that access to VPP stats over socket is not supported yet.

    The recommended ways of use are (examples):

    1. Simple request / reply. Example with no arguments:

        cmd = "show_version"
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

    2. Dump functions:

        cmd = "sw_interface_rx_placement_dump"
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, sw_if_index=ifc["vpp_sw_index"])
            details = papi_exec.get_details(err_msg)

    3. Multiple requests with one reply each.
       In this example, there are three requests with arguments,
       the second and the third ones are the same but with different arguments.
       This example also showcases method chaining.

        with PapiSocketExecutor(node, is_async=True) as papi_exec:
            replies = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg)

    The "is_async=True" part in the last example enables "async handling mode",
    which imposes limitations but gains speed and saves memory.
    This is different than async mode of VPP PAPI, as the default handling mode
    also uses async PAPI connections.

    The implementation contains more hidden details, such as
    support for old VPP PAPI async mode behavior, API CRC checking
    conditional usage of control ping, and possible susceptibility to VPP-2033.
    See docstring of methods for more detailed info.
    """

    # Class cache for reuse between instances.
    api_root_dir = None
    """We copy .api json files and PAPI code from DUT to robot machine.
    This class variable holds temporary directory once created.
    When python exits, the directory is deleted, so no downloaded file leaks.
    The value will be set to TemporaryDirectory class instance (not string path)
    to ensure deletion at exit."""
    api_json_path = None
    """String path to .api.json files, a directory somewhere in api_root_dir."""
    api_package_path = None
    """String path to PAPI code, a different directory under api_root_dir."""
    crc_checker = None
    """Accesses .api.json files at creation, caching speeds up accessing it."""
    reusable_vpp_client_list = list()
    """Each connection needs a separate client instance,
    and each client instance creation needs to parse all .api files,
    which takes time. If a client instance disconnects, it is put here,
    so on next connect we can reuse intead of creating new."""
    conn_cache = dict()
    """Mapping from node key to connected client instance."""

    def __init__(
        self, node, remote_vpp_socket=Constants.SOCKSVR_PATH, is_async=False
    ):
        """Store the given arguments, declare managed variables.

        :param node: Node to connect to and forward unix domain socket from.
        :param remote_vpp_socket: Path to remote socket to tunnel to.
        :param is_async: Whether to use async handling.
        :type node: dict
        :type remote_vpp_socket: str
        :type is_async: bool
        """
        self._node = node
        self._remote_vpp_socket = remote_vpp_socket
        self._is_async = is_async
        # The list of PAPI commands to be executed on the node.
        self._api_command_list = list()

    def ensure_api_dirs(self):
        """Copy files from DUT to local temporary directory.

        If the directory is still there, do not copy again.
        If copying, also initialize CRC checker (this also performs
        static checks), and remember PAPI package path.
        Do not add that to PATH yet.
        """
        cls = self.__class__
        if cls.api_package_path:
            return
        # Pylint suggests to use "with" statement, which we cannot,
        # do as the dir should stay for multiple ensure_vpp_instance calls.
        cls.api_root_dir = tempfile.TemporaryDirectory(dir="/tmp")
        root_path = cls.api_root_dir.name
        # Pack, copy and unpack Python part of VPP installation from _node.
        # TODO: Use rsync or recursive version of ssh.scp_node instead?
        node = self._node
        exec_cmd_no_error(node, ["rm", "-rf", "/tmp/papi.txz"])
        # Papi python version depends on OS (and time).
        # Python 3.4 or higher, site-packages or dist-packages.
        installed_papi_glob = "/usr/lib/python3*/*-packages/vpp_papi"
        # We need to wrap this command in bash, in order to expand globs,
        # and as ssh does join, the inner command has to be quoted.
        inner_cmd = " ".join(
            [
                "tar",
                "cJf",
                "/tmp/papi.txz",
                "--exclude=*.pyc",
                installed_papi_glob,
                "/usr/share/vpp/api",
            ]
        )
        exec_cmd_no_error(node, ["bash", "-c", f"'{inner_cmd}'"])
        scp_node(node, root_path + "/papi.txz", "/tmp/papi.txz", get=True)
        run(["tar", "xf", root_path + "/papi.txz", "-C", root_path])
        cls.api_json_path = root_path + "/usr/share/vpp/api"
        # Perform initial checks before .api.json files are gone,
        # by creating the checker instance.
        cls.crc_checker = VppApiCrcChecker(cls.api_json_path)
        # When present locally, we finally can find the installation path.
        cls.api_package_path = glob.glob(root_path + installed_papi_glob)[0]
        # Package path has to be one level above the vpp_papi directory.
        cls.api_package_path = cls.api_package_path.rsplit("/", 1)[0]

    def ensure_vpp_instance(self):
        """Create or reuse a closed client instance, return it.

        The instance is initialized for unix domain socket access,
        it has initialized all the bindings, it is removed from the internal
        list of disconnected instances, but it is not connected
        (to a local socket) yet.

        :returns: VPP client instance ready for connect.
        :rtype: vpp_papi.VPPApiClient
        """
        self.ensure_api_dirs()
        cls = self.__class__
        if cls.reusable_vpp_client_list:
            # Reuse in LIFO fashion.
            *cls.reusable_vpp_client_list, ret = cls.reusable_vpp_client_list
            return ret
        # Creating an instance leads to dynamic imports from VPP PAPI code,
        # so the package directory has to be present until the instance.
        # But it is simpler to keep the package dir around.
        try:
            sys.path.append(cls.api_package_path)
            # TODO: Pylint says import-outside-toplevel and import-error.
            # It is right, we should refactor the code and move initialization
            # of package outside.
            from vpp_papi.vpp_papi import VPPApiClient as vpp_class
            try:
                # The old way. Deduplicate when pre-2402 support is not needed.

                vpp_class.apidir = cls.api_json_path
                # We need to create instance before removing from sys.path.
                # Cannot use loglevel parameter, robot.api.logger lacks the support.
                vpp_instance = vpp_class(
                    use_socket=True,
                    server_address="TBD",
                    async_thread=False,
                    # Large read timeout was originally there for VPP-1722,
                    # it may still be helping against AVF device creation failures.
                    read_timeout=14,
                    logger=FilteredLogger(logger, "INFO"),
                )
            except vpp_class.VPPRuntimeError:
                # The 39871 way.

                # We need to create instance before removing from sys.path.
                # Cannot use loglevel parameter, robot.api.logger lacks the support.
                vpp_instance = vpp_class(
                    apidir=cls.api_json_path,
                    use_socket=True,
                    server_address="TBD",
                    async_thread=False,
                    # Large read timeout was originally there for VPP-1722,
                    # it may still be helping against AVF device creation failures.
                    read_timeout=14,
                    logger=FilteredLogger(logger, "INFO"),
                )
            # The following is needed to prevent union (e.g. Ip4) debug logging
            # of VPP part of PAPI from spamming robot logs.
            logging.getLogger("vpp_papi.serializer").setLevel(logging.INFO)
        finally:
            if sys.path[-1] == cls.api_package_path:
                sys.path.pop()
        return vpp_instance

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
            node["host"],
            node["port"],
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
            self._node,
            self._remote_vpp_socket,
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
        Successful retrieval from cache is logged only when check_connected.

        This hides details of what the node key is.

        :param check_connected: Whether cache miss raises (and success logs).
        :type check_connected: bool
        :returns: Connected client instance, or None if uncached and no check.
        :rtype: Optional[vpp_papi.VPPApiClient]
        :raises RuntimeError: If cache miss and check enabled.
        """
        key = self.key_for_self()
        ret = self.__class__.conn_cache.get(key, None)
        if check_connected:
            if ret is None:
                raise RuntimeError(f"Client not cached for key: {key}")
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
        csit_deque
            - Queue for responses.

        The attribute names do not start with underscore,
        so pylint does not complain about accessing private attribute.
        The attribute names start with csit_ to avoid naming conflicts
        with "real" attributes from VPP Python code.

        :returns: self
        :rtype: PapiSocketExecutor
        """
        # Do we have the connected instance in the cache?
        vpp_instance = self.get_connected_client(check_connected=False)
        if vpp_instance is not None:
            return self
        # No luck, create and connect a new instance.
        time_enter = time.monotonic()
        node = self._node
        # Parsing takes longer than connecting, prepare instance before tunnel.
        vpp_instance = self.ensure_vpp_instance()
        # Store into cache as soon as possible.
        # If connection fails, it is better to attempt disconnect anyway.
        self.set_connected_client(vpp_instance)
        # Set additional attributes.
        vpp_instance.csit_temp_dir = tempfile.TemporaryDirectory(dir="/tmp")
        temp_path = vpp_instance.csit_temp_dir.name
        api_socket = temp_path + "/vpp-api.sock"
        vpp_instance.csit_local_vpp_socket = api_socket
        ssh_socket = temp_path + "/ssh.sock"
        vpp_instance.csit_control_socket = ssh_socket
        # Cleanup possibilities.
        ret_code, _ = run(["ls", ssh_socket], check=False)
        if ret_code != 2:
            # This branch never seems to be hit in CI,
            # but may be useful when testing manually.
            run(
                ["ssh", "-S", ssh_socket, "-O", "exit", "0.0.0.0"],
                check=False,
                log=True,
            )
            # TODO: Is any sleep necessary? How to prove if not?
            run(["sleep", "0.1"])
            run(["rm", "-vrf", ssh_socket])
        # Even if ssh can perhaps reuse this file,
        # we need to remove it for readiness detection to work correctly.
        run(["rm", "-rvf", api_socket])
        # We use sleep command. The ssh command will exit in 30 second,
        # unless a local socket connection is established,
        # in which case the ssh command will exit only when
        # the ssh connection is closed again (via control socket).
        # The log level is to suppress "Warning: Permanently added" messages.
        ssh_cmd = [
            "ssh",
            "-S",
            ssh_socket,
            "-M",
            "-L",
            f"{api_socket}:{self._remote_vpp_socket}",
            "-p",
            str(node["port"]),
            "-o",
            "LogLevel=ERROR",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ExitOnForwardFailure=yes",
            f"{node['username']}@{node['host']}",
            "sleep",
            "30",
        ]
        priv_key = node.get("priv_key")
        if priv_key:
            # This is tricky. We need a file to pass the value to ssh command.
            # And we need ssh command, because paramiko does not support sockets
            # (neither ssh_socket, nor _remote_vpp_socket).
            key_file = tempfile.NamedTemporaryFile()
            key_file.write(priv_key)
            # Make sure the content is written, but do not close yet.
            key_file.flush()
            ssh_cmd[1:1] = ["-i", key_file.name]
        password = node.get("password")
        if password:
            # Prepend sshpass command to set password.
            ssh_cmd[:0] = ["sshpass", "-p", password]
        time_stop = time.monotonic() + 10.0
        # subprocess.Popen seems to be the best way to run commands
        # on background. Other ways (shell=True with "&" and ssh with -f)
        # seem to be too dependent on shell behavior.
        # In particular, -f does NOT return values for run().
        subprocess.Popen(ssh_cmd)
        # Check socket presence on local side.
        while time.monotonic() < time_stop:
            # It can take a moment for ssh to create the socket file.
            ret_code, _ = run(["ls", "-l", api_socket], check=False)
            if not ret_code:
                break
            time.sleep(0.01)
        else:
            raise RuntimeError("Local side socket has not appeared.")
        if priv_key:
            # Socket up means the key has been read. Delete file by closing it.
            key_file.close()
        # Everything is ready, set the local socket address and connect.
        vpp_instance.transport.server_address = api_socket
        # It seems we can get read error even if every preceding check passed.
        # Single retry seems to help. TODO: Confirm this is still needed.
        for _ in range(2):
            try:
                vpp_instance.connect("csit_socket", do_async=True)
            except (IOError, struct.error) as err:
                logger.warn(f"Got initial connect error {err!r}")
                vpp_instance.disconnect()
            else:
                break
        else:
            raise RuntimeError("Failed to connect to VPP over a socket.")
        # Only after rls2302 all relevant VPP builds should have do_async.
        if hasattr(vpp_instance.transport, "do_async"):
            deq = deque()
            vpp_instance.csit_deque = deq
            vpp_instance.register_event_callback(lambda x, y: deq.append(y))
        else:
            vpp_instance.csit_deque = None
        duration_conn = time.monotonic() - time_enter
        logger.trace(f"Establishing socket connection took {duration_conn}s.")
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
        client_instance = cls.conn_cache.get(key, None)
        if client_instance is None:
            return
        logger.debug(f"Disconnecting by key: {key}")
        client_instance.disconnect()
        run(
            [
                "ssh",
                "-S",
                client_instance.csit_control_socket,
                "-O",
                "exit",
                "0.0.0.0",
            ],
            check=False,
        )
        # Temp dir has autoclean, but deleting explicitly
        # as an error can happen.
        try:
            client_instance.csit_temp_dir.cleanup()
        except FileNotFoundError:
            # There is a race condition with ssh removing its ssh.sock file.
            # Single retry should be enough to ensure the complete removal.
            shutil.rmtree(client_instance.csit_temp_dir.name)
        # Finally, put disconnected clients to reuse list.
        cls.reusable_vpp_client_list.append(client_instance)
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
        The kwargs dict is serialized or deep-copied, so it is safe to use
        the original with partial modifications for subsequent calls.

        Any pending conflicts from .api.json processing are raised.
        Then the command name is checked for known CRCs.
        Unsupported commands raise an exception, as CSIT change
        should not start using messages without making sure which CRCs
        are supported.
        Each CRC issue is raised only once, so subsequent tests
        can raise other issues.

        With async handling mode, this method also serializes and sends
        the command, skips CRC check to gain speed, and saves memory
        by putting a sentinel (instead of deepcopy) to api command list.

        For scale tests, the call sites are responsible to set history values
        in a way that hints what is done without overwhelming the papi history.

        Note to contributors: Do not rename "csit_papi_command"
        to anything VPP could possibly use as an API field name.

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
            # No need for deepcopy yet, serialization isolates from edits.
            PapiHistory.add_to_papi_history(
                self._node, csit_papi_command, **kwargs
            )
        self.crc_checker.check_api_name(csit_papi_command)
        if self._is_async:
            # Save memory but still count the number of expected replies.
            self._api_command_list.append(0)
            api_object = self.get_connected_client(check_connected=False).api
            func = getattr(api_object, csit_papi_command)
            # No need for deepcopy yet, serialization isolates from edits.
            func(**kwargs)
        else:
            # No serialization, so deepcopy is needed here.
            self._api_command_list.append(
                dict(api_name=csit_papi_command, api_args=copy.deepcopy(kwargs))
            )
        return self

    def get_replies(self, err_msg="Failed to get replies."):
        """Get reply for each command from VPP Python API.

        This method expects one reply per command,
        and gains performance by reading replies only after
        sending all commands.

        The replies are parsed into dict-like objects,
        "retval" field (if present) is guaranteed to be zero on success.

        Do not use this for messages with variable number of replies,
        use get_details instead.
        Do not use for commands trigering VPP-2033,
        use series of get_reply instead.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Responses, dict objects with fields due to API and "retval".
        :rtype: list of dict
        :raises RuntimeError: If retval is nonzero, parsing or ssh error.
        """
        if not self._is_async:
            raise RuntimeError("Sync handling does not suport get_replies.")
        return self._execute(err_msg=err_msg, do_async=True)

    def get_reply(self, err_msg="Failed to get reply."):
        """Get reply to single command from VPP Python API.

        This method waits for a single reply (no control ping),
        thus avoiding bugs like VPP-2033.

        The reply is parsed into a dict-like object,
        "retval" field (if present) is guaranteed to be zero on success.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Response, dict object with fields due to API and "retval".
        :rtype: dict
        :raises AssertionError: If retval is nonzero, parsing or ssh error.
        """
        if self._is_async:
            raise RuntimeError("Async handling does not suport get_reply.")
        replies = self._execute(err_msg=err_msg, do_async=False)
        if len(replies) != 1:
            raise RuntimeError(f"Expected single reply, got {replies!r}")
        return replies[0]

    def get_sw_if_index(self, err_msg="Failed to get reply."):
        """Get sw_if_index from reply from VPP Python API.

        Frequently, the caller is only interested in sw_if_index field
        of the reply, this wrapper around get_reply (thus safe against VPP-2033)
        makes such call sites shorter.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Response, sw_if_index value of the reply.
        :rtype: int
        :raises AssertionError: If retval is nonzero, parsing or ssh error.
        """
        if self._is_async:
            raise RuntimeError("Async handling does not suport get_sw_if_index")
        reply = self.get_reply(err_msg=err_msg)
        return reply["sw_if_index"]

    def get_details(self, err_msg="Failed to get dump details."):
        """Get details (for possibly multiple dumps) from VPP Python API.

        The details are parsed into dict-like objects.
        The number of details per single dump command can vary,
        and all association between details and dumps is lost,
        so if you care about the association (as opposed to
        logging everything at once for debugging purposes),
        it is recommended to call get_details for each dump (type) separately.

        This method uses control ping to detect end of replies,
        so it is not suitable for commands which trigger VPP-2033
        (but arguably no dump currently triggers it).

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type err_msg: str
        :returns: Details, dict objects with fields due to API without "retval".
        :rtype: list of dict
        """
        if self._is_async:
            raise RuntimeError("Async handling does not suport get_details.")
        return self._execute(err_msg, do_async=False, single_reply=False)

    @staticmethod
    def run_cli_cmd(
        node, cli_cmd, log=True, remote_vpp_socket=Constants.SOCKSVR_PATH
    ):
        """Run a CLI command as cli_inband, return the "reply" field of reply.

        Optionally, log the field value.
        This is a convenience wrapper around get_reply.

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
        cmd = "cli_inband"
        args = dict(cmd=cli_cmd)
        err_msg = (
            f"Failed to run 'cli_inband {cli_cmd}' PAPI command"
            f" on host {node['host']}"
        )

        with PapiSocketExecutor(node, remote_vpp_socket) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)["reply"]
        if log:
            logger.info(
                f"{cli_cmd} ({node['host']} - {remote_vpp_socket}):\n"
                f"{reply.strip()}"
            )
        return reply

    @staticmethod
    def run_cli_cmd_on_all_sockets(node, cli_cmd, log=True):
        """Run a CLI command as cli_inband, on all sockets in topology file.

        Just a run_cli_cmd, looping over sockets.

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

        Just a get_details (with logging), looping over commands.

        :param node: DUT node.
        :param cmds: Dump commands to be executed.
        :type node: dict
        :type cmds: list of str
        """
        with PapiSocketExecutor(node) as papi_exec:
            for cmd in cmds:
                dump = papi_exec.add(cmd).get_details()
                logger.debug(f"{cmd}:\n{pformat(dump)}")

    @staticmethod
    def _read_internal(vpp_instance, timeout=None):
        """Blockingly read within timeout.

        This covers behaviors both before and after 37758.
        One read attempt is guaranteed even with zero timeout.

        TODO: Simplify after 2302 RCA is done.

        :param vpp_instance: Client instance to read from.
        :param timeout: How long to wait for reply (or transport default).
        :type vpp_instance: vpp_papi.VPPApiClient
        :type timeout: Optional[float]
        :returns: Message read or None if nothing got read.
        :rtype: Optional[namedtuple]
        """
        timeout = vpp_instance.read_timeout if timeout is None else timeout
        if vpp_instance.csit_deque is None:
            return vpp_instance.read_blocking(timeout=timeout)
        time_stop = time.monotonic() + timeout
        while 1:
            try:
                return vpp_instance.csit_deque.popleft()
            except IndexError:
                # We could busy-wait but that seems to starve the reader thread.
                time.sleep(0.01)
            if time.monotonic() > time_stop:
                return None

    @staticmethod
    def _read(vpp_instance, tries=3):
        """Blockingly read within timeout, retry on early None.

        For (sometimes) unknown reasons, VPP client in async mode likes
        to return None occasionally before time runs out.
        This function retries in that case.

        Most of the time, early None means VPP crashed (see VPP-2033),
        but is is better to give VPP more chances to respond without failure.

        TODO: Perhaps CSIT now never triggers VPP-2033,
        so investigate and remove this layer if even more speed is needed.

        :param vpp_instance: Client instance to read from.
        :param tries: Maximum number of tries to attempt.
        :type vpp_instance: vpp_papi.VPPApiClient
        :type tries: int
        :returns: Message read or None if nothing got read even with retries.
        :rtype: Optional[namedtuple]
        """
        timeout = vpp_instance.read_timeout
        for _ in range(tries):
            time_stop = time.monotonic() + 0.9 * timeout
            reply = PapiSocketExecutor._read_internal(vpp_instance)
            if reply is None and time.monotonic() < time_stop:
                logger.trace("Early None. Retry?")
                continue
            return reply
        logger.trace(f"Got {tries} early Nones, probably a real None.")
        return None

    @staticmethod
    def _drain(vpp_instance, err_msg, timeout=30.0):
        """Keep reading with until None or timeout.

        This is needed to mitigate the risk of a state with unread responses
        (e.g. after non-zero retval in the middle of get_replies)
        causing failures in everything subsequent (until disconnect).

        The reads are done without any waiting.

        It is possible some responses have not arrived yet,
        but that is unlikely as Python is usually slower than VPP.

        :param vpp_instance: Client instance to read from.
        :param err_msg: Error message to use when overstepping timeout.
        :param timeout: How long to try before giving up.
        :type vpp_instance: vpp_papi.VPPApiClient
        :type err_msg: str
        :type timeout: float
        :raises RuntimeError: If read keeps returning nonzero after timeout.
        """
        time_stop = time.monotonic() + timeout
        while time.monotonic() < time_stop:
            if PapiSocketExecutor._read_internal(vpp_instance, 0.0) is None:
                return
        raise RuntimeError(f"{err_msg}\nTimed out while draining.")

    def _execute(self, err_msg, do_async, single_reply=True):
        """Turn internal command list into data and execute; return replies.

        This method also clears the internal command list.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param do_async: If true, assume one reply per command and do not wait
            for each reply before sending next request.
            Dump commands (and calls causing VPP-2033) need False.
        :param single_reply: For sync emulation mode (cannot be False
            if do_async is True). When false use control ping.
            When true, wait for a single reply.
        :type err_msg: str
        :type do_async: bool
        :type single_reply: bool
        :returns: Papi replies parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: NoneType or list of dict
        :raises RuntimeError: If the replies are not all correct.
        """
        local_list = self._api_command_list
        # Clear first as execution may fail.
        self._api_command_list = list()
        if do_async:
            if not single_reply:
                raise RuntimeError("Async papi needs one reply per request.")
            return self._execute_async(local_list, err_msg=err_msg)
        return self._execute_sync(
            local_list, err_msg=err_msg, single_reply=single_reply
        )

    def _execute_sync(self, local_list, err_msg, single_reply):
        """Execute commands waiting for replies one by one; return replies.

        This implementation either expects a single response per request,
        or uses control ping to emulate sync PAPI calls.
        Reliable, but slow. Required for dumps. Needed for calls
        which trigger VPP-2033.

        CRC checking is done for the replies (requests are checked in .add).

        :param local_list: The list of PAPI commands to be executed on the node.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param single_reply: When false use control ping.
            When true, wait for a single reply.
        :type local_list: list of dict
        :type err_msg: str
        :type single_reply: bool
        :returns: Papi replies parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: List[UserDict]
        :raises AttributeError: If VPP does not know the command.
        :raises RuntimeError: If the replies are not all correct.
        """
        vpp_instance = self.get_connected_client()
        control_ping_fn = getattr(vpp_instance.api, "control_ping")
        ret_list = list()
        for command in local_list:
            api_name = command["api_name"]
            papi_fn = getattr(vpp_instance.api, api_name)
            replies = list()
            try:
                # Send the command maybe followed by control ping.
                main_context = papi_fn(**command["api_args"])
                if single_reply:
                    replies.append(PapiSocketExecutor._read(vpp_instance))
                else:
                    ping_context = control_ping_fn()
                    # Receive the replies.
                    while 1:
                        reply = PapiSocketExecutor._read(vpp_instance)
                        if reply is None:
                            raise RuntimeError(
                                f"{err_msg}\nSync PAPI timed out."
                            )
                        if reply.context == ping_context:
                            break
                        if reply.context != main_context:
                            raise RuntimeError(
                                f"{err_msg}\nUnexpected context: {reply!r}"
                            )
                        replies.append(reply)
            except (AttributeError, IOError, struct.error) as err:
                # TODO: Add retry if it is still needed.
                raise AssertionError(f"{err_msg}") from err
            finally:
                # Discard any unprocessed replies to avoid secondary failures.
                PapiSocketExecutor._drain(vpp_instance, err_msg)
            # Process replies for this command.
            for reply in replies:
                self.crc_checker.check_api_name(reply.__class__.__name__)
                dictized_reply = dictize_and_check_retval(reply, err_msg)
                ret_list.append(dictized_reply)
        return ret_list

    def _execute_async(self, local_list, err_msg):
        """Read, process and return replies.

        The messages were already sent by .add() in this mode,
        local_list is used just so we know how many replies to read.

        Beware: It is not clear what to do when socket read fails
        in the middle of async processing.

        The implementation assumes each command results in exactly one reply,
        there is no reordering in either commands nor replies,
        and context numbers increase one by one (and are matching for replies).

        To speed processing up, reply CRC values are not checked.

        The current implementation does not limit the number of messages
        in-flight, we rely on VPP PAPI background thread to move replies
        from socket to queue fast enough.

        :param local_list: The list of PAPI commands to get replies for.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type local_list: list
        :type err_msg: str
        :returns: Papi replies parsed into a dict-like object, with fields
            according to API (possibly including retval).
        :rtype: List[UserDict]
        :raises RuntimeError: If the replies are not all correct.
        """
        vpp_instance = self.get_connected_client()
        ret_list = list()
        try:
            for index, _ in enumerate(local_list):
                # Blocks up to timeout.
                reply = PapiSocketExecutor._read(vpp_instance)
                if reply is None:
                    time_msg = f"PAPI async timeout: idx {index}"
                    raise RuntimeError(f"{err_msg}\n{time_msg}")
                ret_list.append(dictize_and_check_retval(reply, err_msg))
        finally:
            # Discard any unprocessed replies to avoid secondary failures.
            PapiSocketExecutor._drain(vpp_instance, err_msg)
        return ret_list


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
        for key in list(cls.conn_cache.keys()):
            cls.disconnect_by_key(key)


class PapiExecutor:
    """Contains methods for executing VPP Python API commands on DUTs.

    TODO: Remove .add step, make get_stats accept paths directly.

    This class processes only one type of VPP PAPI methods: vpp-stats.

    The recommended ways of use are (examples):

    path = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']
    with PapiExecutor(node) as papi_exec:
        stats = papi_exec.add(api_name='vpp-stats', path=path).get_stats()

    print('RX interface core 0, sw_if_index 0:\n{0}'.\
        format(stats[0]['/if/rx'][0][0]))

    or

    path_1 = ['^/if', ]
    path_2 = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']
    with PapiExecutor(node) as papi_exec:
        stats = papi_exec.add('vpp-stats', path=path_1).\
            add('vpp-stats', path=path_2).get_stats()

    print('RX interface core 0, sw_if_index 0:\n{0}'.\
        format(stats[1]['/if/rx'][0][0]))

    Note: In this case, when PapiExecutor method 'add' is used:
    - its parameter 'csit_papi_command' is used only to keep information
      that vpp-stats are requested. It is not further processed but it is
      included in the PAPI history this way:
      vpp-stats(path=['^/if', '/err/ip4-input', '/sys/node/ip4-input'])
      Always use csit_papi_command="vpp-stats" if the VPP PAPI method
      is "stats".
    - the second parameter must be 'path' as it is used by PapiExecutor
      method 'add'.
    - even if the parameter contains multiple paths, there is only one
      reply item (for each .add).
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
        except IOError as err:
            msg = f"PAPI: Cannot open SSH connection to {self._node['host']}"
            raise RuntimeError(msg) from err
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh.disconnect(self._node)

    def add(self, csit_papi_command="vpp-stats", history=True, **kwargs):
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
        :rtype: PapiExecutor
        """
        if history:
            PapiHistory.add_to_papi_history(
                self._node, csit_papi_command, **kwargs
            )
        self._api_command_list.append(
            dict(api_name=csit_papi_command, api_args=copy.deepcopy(kwargs))
        )
        return self

    def get_stats(
        self,
        err_msg="Failed to get statistics.",
        timeout=120,
        socket=Constants.SOCKSTAT_PATH,
    ):
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
        paths = [cmd["api_args"]["path"] for cmd in self._api_command_list]
        self._api_command_list = list()

        stdout = self._execute_papi(
            paths,
            method="stats",
            err_msg=err_msg,
            timeout=timeout,
            socket=socket,
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
                retval = val
            elif isinstance(val, list):
                for idx, val_l in enumerate(val):
                    val[idx] = process_value(val_l)
                retval = val
            else:
                retval = val.encode().hex() if isinstance(val, str) else val
            return retval

        api_data_processed = list()
        for api in api_d:
            api_args_processed = dict()
            for a_k, a_v in api["api_args"].items():
                api_args_processed[str(a_k)] = process_value(a_v)
            api_data_processed.append(
                dict(api_name=api["api_name"], api_args=api_args_processed)
            )
        return api_data_processed

    def _execute_papi(
        self, api_data, method="request", err_msg="", timeout=120, socket=None
    ):
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
            raise RuntimeError("No API data provided.")

        json_data = (
            json.dumps(api_data)
            if method in ("stats", "stats_request")
            else json.dumps(self._process_api_data(api_data))
        )

        sock = f" --socket {socket}" if socket else ""
        cmd = (
            f"{Constants.REMOTE_FW_DIR}/{Constants.RESOURCES_PAPI_PROVIDER}"
            f" --method {method} --data '{json_data}'{sock}"
        )
        try:
            ret_code, stdout, _ = self._ssh.exec_command_sudo(
                cmd=cmd, timeout=timeout, log_stdout_err=False
            )
        # TODO: Fail on non-empty stderr?
        except SSHTimeout:
            logger.error(
                f"PAPI command(s) execution timeout on host"
                f" {self._node['host']}:\n{api_data}"
            )
            raise
        except Exception as exc:
            raise RuntimeError(
                f"PAPI command(s) execution on host {self._node['host']}"
                f" failed: {api_data}"
            ) from exc
        if ret_code != 0:
            raise AssertionError(err_msg)

        return stdout
