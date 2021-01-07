# Copyright (c) 2021 Cisco and/or its affiliates.
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

This one uses API socket to access DUT VPP from Robot machine.
Access to stats segment is not supported (yet), use PapiStatsExecutor for that.
"""

import copy
import glob
import logging
import select
import shutil
import struct  # vpp-papi can raise struct.error
import subprocess
import sys
import tempfile
import threading
import time

from pprint import pformat
from robot.api import logger

from resources.libraries.python.bytes_template import BytesTemplate
from resources.libraries.python.Constants import Constants
from resources.libraries.python.FilteredLogger import FilteredLogger
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.raise_from import raise_from
from resources.libraries.python.spying_socket import SpyingSocket
from resources.libraries.python.ssh import (exec_cmd_no_error, scp_node)
from resources.libraries.python.topology import Topology, SocketType
from resources.libraries.python.VppApiCrc import VppApiCrcChecker


__all__ = [
    u"PapiSocketExecutor",
    u"Disconnector",
]


# TODO: CSIT-1633: Switch libraries to attribute access and remove dictization.
def dictize(obj):
    """Make namedtuple-like object accessible as dict.

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
    ret = obj._asdict()
    ret.__getitem__ = lambda self, key: dictize(ret.__getitem__(self, key))
    return ret


def dictize_and_check_retval(obj, err_msg="Retval present and nonzero."):
    """Make namedtuple-like object accessible as dict, check retval if exists.

    If the object contains "retval" field, raise when the value is non-zero.
    Actually, two chained exceptions are raised,
    as it is not easy for err_msg to have placeholder for retval value.

    See dictize() for what it means to dictize.

    :param obj: Arbitrary object to dictize.
    :param err_msg: The text for the raised exception.
    :type obj: object
    :type err_msg: str
    :returns: Dictized object.
    :rtype: same as obj type or collections.OrderedDict
    :raises AssertionError: If retval field is present with nonzero value.
    """
    ret = dictize(obj)
    # *_details messages do not contain retval.
    retval = ret.get(u"retval", 0)
    if retval != 0:
        err = AssertionError(f"Retval nonzero in object {ret!r}")
        # Lowering log level, some retval!=0 calls are expected.
        # TODO: Expose level argument so callers can decide?
        raise_from(AssertionError(err_msg), err, level=u"DEBUG")
    return ret


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
    before each VPP restart.
    There is some amount of retries and disconnects on transport failure
    (so unresponsive VPPs do not breach test much more than needed),
    but it is hard to verify all that works correctly.
    Especially, if Robot crashes, files and ssh processes may leak.

    Delay for accepting socket connection is 14s.
    TODO: Decrease 14s to value that is long enough for creating connection
    and short enough to not affect performance.
    TODO: Find out which arch is the slowest.

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

    For advanced usage, see documentation of get_replies.
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
        cls.api_root_dir = tempfile.TemporaryDirectory(dir=u"/tmp")
        root_path = cls.api_root_dir.name
        # Pack, copy and unpack Python part of VPP installation from _node.
        # TODO: Use rsync or recursive version of ssh.scp_node instead?
        node = self._node
        exec_cmd_no_error(node, [u"rm", u"-rf", u"/tmp/papi.txz"])
        # Papi python version depends on OS (and time).
        # Python 2.7 or 3.4, site-packages or dist-packages.
        installed_papi_glob = u"/usr/lib/python3*/*-packages/vpp_papi"
        # We need to wrap this command in bash, in order to expand globs,
        # and as ssh does join, the inner command has to be quoted.
        inner_cmd = u" ".join([
            u"tar", u"cJf", u"/tmp/papi.txz", u"--exclude=*.pyc",
            installed_papi_glob, u"/usr/share/vpp/api"
        ])
        exec_cmd_no_error(node, [u"bash", u"-c", u"'" + inner_cmd + u"'"])
        scp_node(node, root_path + u"/papi.txz", u"/tmp/papi.txz", get=True)
        run([u"tar", u"xf", root_path + u"/papi.txz", u"-C", root_path])
        cls.api_json_path = root_path + u"/usr/share/vpp/api"
        # Perform initial checks before .api.json files are gone,
        # by creating the checker instance.
        cls.crc_checker = VppApiCrcChecker(cls.api_json_path)
        # When present locally, we finally can find the installation path.
        cls.api_package_path = glob.glob(root_path + installed_papi_glob)[0]
        # Package path has to be one level above the vpp_papi directory.
        cls.api_package_path = cls.api_package_path.rsplit(u"/", 1)[0]

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
            vpp_class.apidir = cls.api_json_path
            # We need to create instance before removing from sys.path.
            # Cannot use loglevel parameter, robot.api.logger lacks support.
            # TODO: Stop overriding read_timeout when VPP-1722 is fixed.
            vpp_instance = vpp_class(
                use_socket=True, server_address=None, async_thread=False,
                read_timeout=14, logger=FilteredLogger(logger, u"INFO")
            )
            # The following is needed to prevent union (e.g. Ip4) debug logging
            # of VPP part of PAPI from spamming robot logs.
            logging.getLogger("vpp_papi.vpp_serializer").setLevel(logging.INFO)
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
        vpp_instance.csit_temp_dir = tempfile.TemporaryDirectory(dir=u"/tmp")
        temp_path = vpp_instance.csit_temp_dir.name
        api_socket = temp_path + u"/vpp-api.sock"
        vpp_instance.csit_local_vpp_socket = api_socket
        ssh_socket = temp_path + u"/ssh.sock"
        vpp_instance.csit_control_socket = ssh_socket
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
        time_stop = time.monotonic() + 10.0
        # subprocess.Popen seems to be the best way to run commands
        # on background. Other ways (shell=True with "&" and ssh with -f)
        # seem to be too dependent on shell behavior.
        # In particular, -f does NOT return values for run().
        subprocess.Popen(ssh_cmd)
        # Check socket presence on local side.
        while time.monotonic() < time_stop:
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
        vpp_instance.transport.server_address = api_socket
        try:
            # The rx_qlen argument is ignored for socket transport.
            vpp_instance.connect(u"csit_socket", do_async=True)
        except (IOError, struct.error) as err:
            vpp_instance.disconnect()
            raising = RuntimeError(u"Failed to connect to VPP over a socket.")
            raise_from(raising, err, level="WARN")
        logger.trace(
            f"Establishing socket connection took"
            f" {time.monotonic() - time_enter} seconds."
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
        client_instance = cls.conn_cache.get(key, None)
        if client_instance is None:
            return
        logger.debug(f"Disconnecting by key: {key}")
        client_instance.disconnect()
        run([
            u"ssh", u"-S", client_instance.csit_control_socket, u"-O",
            u"exit", u"0.0.0.0"
        ], check=False)
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

    @classmethod
    def exec_fast(
            cls, node, command_name, gen_f, err_msg="Failed to get replies.",
            how_many=0, need_replies=True):
        """User friendly wrapper for fast execution, includes connect.

        When compared to connected_exec_fast,
        this saves horizontal space at call sites.
        Use connected_exec_fast if already inside a with block.

        Example of call site pattern (two blocks):

        err_msg = my_error_message
        cmd = constant_command
        args = initial_value
        def gen_foo():
            for index in range(scale_start, scale_stop):
                args[u"some_field"] = compute_some_value(index)
                args[u"other_field"] = compute_other_value(index)
                yield args
        replies = PapiSocketExecutor.exec_fast(
            node=node, command_name=cmd, gen_f=gen_foo, err_msg=err_msg,
            how_many=scale_stop - scale_start, need_replies=True
        )
        process_replies_outside_generator(replies)
        err_msg = alternative_error_message
        cmd = unrelated_command
        args = totally_different_structure
        def gen_bar():
            for index in range(scale_start, scale_stop):
                args[u"field0"] = compute0(index)
                yield args
        PapiSocketExecutor.exec_fast(
            node=node, command_name=cmd, gen_f=gen_bar(), err_msg=err_msg,
            how_many=scale_stop - scale_start, need_replies=False
        )

        Comments:
        In the example, args can have more fields but only some depend on index.
        The count needs to be passed as how_many, because fast sending
        avoids slow generation of full list of arguments.
        Note that the function with yield is not the generator object itself,
        but a callable which returns the generator object (iterable).
        The input argument is the function (can be closure),
        called generator function.

        :param node: Node to connect to and forward unix domain socket from.
        :param command_name: Name of the message to send. Fast execution
            only suports single message type (with differing arguments).
        :param gen_f: Generator function yielding message argument dicts.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param how_many: How many messages to send in total.
        :param need_replies: If false, further speed is gained
            by not processing replies (beyond first two).
        :type node: dict
        :type command_name: str
        :type gen_f: Argument-less function returning generator yielding dicts.
        :type err_msg: str
        :type how_many: int
        :type need_replies: bool
        :returns: Processed replies, only first two if not need_replies.
        :rtype: list of dict
        :raises RuntimeError: If retval is nonzero, parsing or ssh error.
        """
        with cls(node) as papi_exec:
            return papi_exec.connected_exec_fast(
                command_name=command_name, gen_f=gen_f, err_msg=err_msg,
                how_many=how_many, need_replies=need_replies
            )

    def connected_exec_fast(
            self, command_name, gen_f, err_msg="Failed to get replies.",
            how_many=0, need_replies=True):
        """User friendly wrapper for fast execution, assumes connected.

        Self has to be already connected (in with block).

        When compared to exec_fast, this takes more horizontal space.
        Mainly useful if already in with block opened for "slow" commands.

        Example of call site pattern (two blocks):

        with PapiSocketExecutor(node) as papi_exec:
            err_msg = my_error_message
            cmd = constant_command
            args = initial_value
            def gen_foo():
                for index in range(scale_start, scale_stop):
                    args[u"some_field"] = compute_some_value(index)
                    args[u"other_field"] = compute_other_value(index)
                    yield cmd, args
            replies = papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_foo, err_msg=err_msg,
                how_many=scale_stop - scale_start, need_replies=True
            )
            process_replies_outside_generator(replies)
            err_msg = alternative_error_message
            cmd = unrelated_command
            args = totally_different_structure
            def gen_bar():
                for index in range(scale_start, scale_stop):
                    args[u"field0"] = compute0(index)
                    yield cmd, args
            papi_exec.connected_exec_fast(
                command_name=cmd, gen_f=gen_bar, err_msg=err_msg,
                how_many=scale_stop - scale_start, need_replies=False
            )

        Comments:
        In the example, args can have more fields but only some depend on index.
        The count needs to be passed as how_many, because fast sending
        avoids slow generation of full list of arguments.
        Note that the function with yield is not the generator object itself,
        but a callable which returns the generator object (iterable).
        The input argument is the function (can be closure),
        called generator function.

        :param command_name: Name of the message to send. Fast execution
            only suports single message type (with differing arguments).
        :param gen_f: Generator function yielding message argument dicts.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param how_many: How many messages to send in total.
        :param need_replies: If false, further speed is gained
            by not processing replies (beyond first two).
        :type command_name: str
        :type gen_f: Argument-less function returning generator yielding dicts.
        :type err_msg: str
        :type how_many: int
        :type need_replies: bool
        :returns: Processed replies, only first two if not need_replies.
        :rtype: list of dict
        :raises RuntimeError: If retval is nonzero, parsing or ssh error.
        """
        # User could have passed a function for a more complicated iterable.
        iterator = gen_f().__iter__()
        # Either way, we only need at most 2 commands to add.
        fast = min(how_many, 2)
        for _ in range(fast):
            kwargs = iterator.__next__()
            self.add(command_name, history=True, **kwargs)
        if how_many <= 2:
            # Slow sending is equivalent or required.
            return self.get_replies(err_msg=err_msg, fast_send=0)
        # Use fast sending.
        return self.get_replies(
            err_msg=err_msg, fast_send=how_many, fast_receive=need_replies
        )

    def get_replies(
            self, err_msg="Failed to get replies.", fast_send=0,
            fast_receive=False):
        """Get replies from VPP Python API.

        If the "fast_send" argument is non-zero,
        this method requires exactly two commands added,
        assumed to be the same type with minimal differences in arguments.
        A fast but stupid method is then used to generate and send
        subsequent commands, saving much time for large scale tests.

        If fast_send is zero, or fast_receive is false,
        the replies are parsed into dict-like objects,
        "retval" field (if present) is guaranteed to be zero on success.

        If fast_send is non-zero and fast_receive is false,
        replies are still processed by full PAPI parsing includig retval check,
        assuming each request results in exactly one reply.
        Note that if fast_send is zero, fast_receive is effectively
        considered false. This simplifies logic in callers.

        If fast_send is non-zero and fast_receive is true,
        only first two replies are processed normally.
        Other replies are not checked at all, to save time,
        and also to avoid issues with non-deterministic response fields
        (e.g. stats_index of ip_route_add_del_reply).

        See exec_fast and connected_exec_fast for patterns
        recomended for scale tests.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param fast_send: This many (minus initia two) fast commands are added.
        :param fast_receive: Whether responses are to be parsed and returned.
        :type err_msg: str
        :type fast_send: int
        :type fast_receive: bool
        :returns: Papi responses parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: list of dict
        :raises RuntimeError: If retval is nonzero, parsing or ssh error.
        """
        return self._execute(
            err_msg=err_msg, fast_send=fast_send, fast_receive=fast_receive
        )

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
        # TODO: Currently boils down to _execute_sync. Call directly if that is the final way.
        return self._execute(err_msg, do_async=False)

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
                f"{cmd} {cli_cmd} ({node[u'host']} - {remote_vpp_socket}):\n"
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

    def _execute(
            self, err_msg=u"Undefined error message", fast_send=0,
            fast_receive=False, do_async=True):
        """Turn internal command list into data and execute; return replies.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_replies()
        - get_reply()
        - get_sw_if_index()
        - get_details()

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param fast_send: This many (minus initial two) fast commands are added.
        :param fast_receive: Whether responses are to be parsed and returned.
        :param do_async: If true, assume one reply per command. If false,
            emulate sync access via using conrol ping. Dump commands need false.
        :type err_msg: str
        :type fast_send: int
        :type fast_receive: bool
        :type do_async: bool
        :returns: Papi responses parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: NoneType or list of dict
        :raises RuntimeError: If the replies are not all correct.
        """
        local_list = self._api_command_list
        # Clear first as execution may fail.
        self._api_command_list = list()
        if do_async:
            return self._execute_async(
                local_list, err_msg=err_msg, fast_send=fast_send,
                fast_receive=fast_receive
            )
        if fast_send:
            raise RuntimeError(u"Fast sending is not supported in sync mode.")
        return self._execute_sync(local_list, err_msg=err_msg)

    def _execute_sync(self, local_list, err_msg="Undefined error message"):
        """Execute command waiting for replies one by one; return replies.

        This is the implementation using control ping to emulate sync PAPI calls.
        Reliable, but slow.

        :param local_list: The list of PAPI commands to be executed on the node.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :type local_list: list of dict
        :type err_msg: str
        :returns: Papi responses parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: list of dict
        :raises RuntimeError: If the replies are not all correct.
        """
        vpp_instance = self.get_connected_client()
        local_list = self._api_command_list
        # Clear first as execution may fail.
        self._api_command_list = list()
        ret_list = list()
        for command in local_list:
            api_name = command[u"api_name"]
            papi_fn = getattr(vpp_instance.api, api_name)
            replies = list()
            try:
                logger.trace(f"Sync-executing {api_name}")
                # Send the command.
                main_context = papi_fn(**command[u"api_args"])
                getattr(vpp_instance.api, u"control_ping")()
                # Receive the replies.
                while 1:
                    reply = vpp_instance.read_blocking()
                    logger.trace(f"Sync-read {reply}")
                    if reply.context != main_context:
                        # TODO: Assert it is control_ping_reply?
                        break
                    replies.append(reply)
            except (AttributeError, IOError, struct.error) as err:
                # TODO: Add retry if it is still needed.
                raise AssertionError(err_msg) from err
            for item in replies:
                # Request CRC has been checked in add, here check reply CRC.
                self.crc_checker.check_api_name(item.__class__.__name__)
                dict_item = dictize_and_check_retval(item)
                ret_list.append(dict_item)
        logger.trace(f"Sync-return {ret_list}")
        return ret_list

    # The internal state during asynchronous execution is too large
    # to be kept in separate "scalar" variables (pylint violations).
    # We need a "structure" to make the state accessible in a modular way.
    # Data classes are not available in Python 3.6,
    # plain class does not pass review (people do not like zero-method classes),
    # namedlist is an additional dependency not easy to add
    # (needs docker image update process we do not really have right now),
    # so the least evil is to use named tuple, even though updating the values
    # is clunky. Note that using plain dict is even less desirable,
    # as we would lose docstrings and visibility for pylint.
    #
    # Anyway, as we need to speed up the review proces,
    # implementing as a dict.

    # A dict is called AsyncState if it contains the following fields:
    # :param local_list: Copy of commands to execute.
    # :param fast_send: Zero or total number of similar commands.
    # :param fast_receive: Whether response processing is to be skipped.
    # :param err_msg: Text to use when raising an error.
    # :param vpp_instance: Connected client instance for sending and receiving.
    # :param ret_list: Responses gathered so far.
    # :param lll: Originally, Length of Local List.
    #     Currently, the overall number of messages to send.
    #     With nonzero fast_send, this is derived from that.
    # :param one_stop: Phase one ends when send index reaches this value.
    #     Depends on max_inflight and length of local list (or fast_send).
    # :param send_iterator: Iterator used to construct data to send.
    # :param send_index: Index of the next command to be send.
    # :param receive_index: Index of the next response to be read.
    # :type local_list: list
    # :type fast_send: int
    # :type fast_receive: bool
    # :type err_msg: str
    # :type vpp_instance: vpp_papi.VPPApiClient
    # :type ret_list: list
    # :type lll: int
    # :type one_stop: int
    # :type send_iterator: NoneType or iterator yielding bytes
    # :type send_index: int
    # :type receive_index: int

    def _execute_async(
            self, local_list, err_msg=u"Undefined error message",
            fast_send=0, fast_receive=False):
        """Send command messages, process replies lazily; return replies.

        Beware: It is not clear what to do when socket read fails
        in the middle of async processing.
        Yet another reason to use sync executor for *_dump commands.

        The implementation assumes each command results in one reply,
        there is no reordering in either commands nor replies,
        and context numbers increase one by one (and are matching for replies).

        To speed processing up, reply CRC values are not checked.

        :param local_list: The list of PAPI commands to be executed on the node.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param fast_send: This many (minus initia two) fast commands are added.
        :param fast_receive: Whether responses are to be parsed and returned.
        :type local_list: list of dict
        :type err_msg: str
        :type fast_send: int
        :type fast_receive: bool
        :returns: Papi responses parsed into a dict-like object, with fields
            according to API (possibly including retval). None for fast_receive.
        :rtype: None or list of dict
        :raises RuntimeError: If the replies are not all correct.
        """
        # TODO: Add fast receive checking only if it does not affect speed.

        # Sanity checks.
        if fast_send:
            if len(local_list) != 2:
                raise RuntimeError(
                    u"Fast sending requires exactly two commands."
                )
            if local_list[0][u"api_name"] != local_list[1][u"api_name"]:
                raise RuntimeError(
                    u"Fast sending requires two messages with the same command."
                )
        if not fast_send:
            # Simplification for callers.
            fast_receive = False

        # The rest is divided into sub-methods to keep complexity low (pylint).
        # Initialize the dynamic state object.
        state = dict(
            local_list=local_list, fast_send=fast_send,
            fast_receive=fast_receive, err_msg=err_msg, ret_list=list(),
            send_index=0, receive_index=0
        )
        # Phase zero: Initialize, handle two messages for fast send.
        state = self._phase_zero(state)
        # Phase one: Only sending commands.
        state = self._phase_one(state)
        # Phase two: Receive one, send one; repeat.
        state = self._phase_two(state)
        # Phase three: Only receiving.
        state = self._phase_three(state)
        # Re-start the background reading thread if needed (phase four?).
        if fast_receive:
            transport = state[u"vpp_instance"].transport
            transport.message_thread = threading.Thread(
                target=transport.msg_thread_func
            )
            transport.message_thread.daemon = True
            transport.message_thread.start()
        return state[u"ret_list"]

    def _phase_zero(self, state):
        """Compute dependent state fields and other setup actions.

        For fast sending, this includes handling first two commands
        (including responses) and updating max_inflight to a higher value,
        as we know all other commands will have the same length.
        The handling includes inserting a spying socket into transport,
        but only temporarily. Send_iterator is constructed.
        Send-index and receive_index are updated,
        so next phases work correctly.

        For fast receiving, this includes ending the background reading thread
        and setting restore_thread.

        :param state: Container holding current execution state.
        :type state: AsyncState
        :returns: Updated state container.
        :rtype: AsyncState
        """
        vpp_instance = self.get_connected_client()
        # The call above deals with node keys, so it is faster to cache into state.
        state[u"vpp_instance"] = vpp_instance
        # Not enough pylint-allowed variables to store vpp_instance.api.
        # Just to save some CPU work inside loop.
        transport = vpp_instance.transport
        # Unix Domain Sockets can hold 256 messages of length 256.
        # https://unix.stackexchange.com/a/424381
        # Linux TCP write buffer can hold 212992 bytes.
        # Deadlock can hapen if the following value (times average message size)
        # is too large, so all buffers get full before reply processing starts.
        # Performance is good so far even without adding TCP write buffer.
        # 603 is the biggest message length seen by Vratko during testing.
        max_inflight = 256 * 256 // 603
        state[u"lll"] = max(state[u"fast_send"], len(state[u"local_list"]))
        state[u"one_stop"] = min(max_inflight, state[u"lll"])
        if not state[u"fast_send"]:
            return state
        # Two more local variables, not visible to other phases.
        socket = SpyingSocket(transport.socket, capture=True)
        transport.socket = socket
        # The under_socket could have been SpyingSocket already.
        under_socket = socket.under_socket
        # Handle the two commands needed to construct data generator.
        command = state[u"local_list"][state[u"send_index"]]
        state[u"send_index"] += 1
        func = getattr(vpp_instance.api, command[u"api_name"])
        func(**command[u"api_args"])
        first_sent = socket.flush_sent()
        command = state[u"local_list"][state[u"send_index"]]
        state[u"send_index"] += 1
        func = getattr(vpp_instance.api, command[u"api_name"])
        func(**command[u"api_args"])
        second_sent = socket.flush_sent()
        # No need for spying anymore, swap back.
        transport.socket = under_socket
        # Be double sure no spying can happen from now on.
        # I wasted many hours investigating why sending becomes slow.
        socket.capture = False
        socket = None
        # Contruct the iterator.
        send_template = BytesTemplate.from_two_messages(
            first_sent, second_sent
        )
        state[u"send_iterator"] = send_template.generator(
            state[u"fast_send"] - 2, vpp_instance.get_context
        ).__iter__()
        # We need to wait for replies here, as we are not sure
        # whether first real reads are in phase two or three.
        # Check possible retval. No peek for multiprocessing.Queue.
        response = vpp_instance.read_blocking()
        state[u"receive_index"] += 1
        if response is None:
            raise RuntimeError(u"Timeout processing first reply.")
        state[u"ret_list"].append(dictize_and_check_retval(response))
        response = vpp_instance.read_blocking()
        state[u"receive_index"] += 1
        if response is None:
            raise RuntimeError(u"Timeout processing second reply.")
        state[u"ret_list"].append(dictize_and_check_retval(response))
        # Re-compute max_inflight.
        max_inflight = 256 * 256 // len(first_sent)
        logger.trace(
            f"Fast send {state[u'fast_send']} messages, second cmd {command}"
            f" message length {len(first_sent)} max_inflight {max_inflight}."
        )
        state[u"one_stop"] = min(max_inflight + 2, state[u"lll"])
        if not state[u"fast_receive"]:
            return state
        # Now, we disable the PAPI listening thread.
        transport.sque.put(True)
        transport.message_thread.join()
        state[u"restore_thread"] = True
        # Pop the one None added when the thread closes.
        read_timeout = vpp_instance.read_timeout
        non = transport.q.get(block=True, timeout=read_timeout)
        if non is not None:
            raise RuntimeError(f"Got non-None from q {non!r}")
        # Also pop the True we used to kill the thread with.
        non = transport.sque.get(block=False)
        if non is not True:
            raise RuntimeError(f"Got non-True from sque {non!r}")
        # Queues leave lingering threads, which may lower the speed.
        # Finally we are done with phase zero.
        return state

    def _phase_one(self, state):
        """Keep sending one_stop command without reading replies.

        :param state: Container holding current execution state.
        :type state: AsyncState
        :returns: Updated state container.
        :rtype: AsyncState
        """
        vpp_instance = state[u"vpp_instance"]
        # Just to save some CPU work inside loop.
        api_object = vpp_instance.api
        socket = vpp_instance.transport.socket
        while state[u"send_index"] < state[u"one_stop"]:
            if state[u"fast_send"]:
                generated = state[u"send_iterator"].__next__()
                socket.sendall(generated)
            else:
                command = state[u"local_list"][state[u"send_index"]]
                func = getattr(api_object, command[u"api_name"])
                func(**command[u"api_args"])
            state[u"send_index"] += 1
        return state

    def _phase_two(self, state):
        """One read, one send, repeat until all is sent.

        :param state: Container holding current execution state.
        :type state: AsyncState
        :returns: Updated state container.
        :rtype: AsyncState
        """
        # TODO: Send step and receive step can be moved to a function.
        #       It would make the code more maintainable.
        #       Investigate whether the call overhead is low enough.

        # Just to save some CPU work inside loop.
        vpp_instance = state[u"vpp_instance"]
        api_object = vpp_instance.api
        transport = vpp_instance.transport
        socket = transport.socket
        while state[u"send_index"] < state[u"lll"]:
            # Receive one.
            err = None
            if state[u"fast_receive"]:
                select.select([socket], [], [])
                # Pylint reports the following call to _read()
                # as W0212(protected-access).
                # But we need to do that for now, in order to be able to test
                # the current (and older) VPP builds, without wasting
                # tens of minutes without fast receive. Improvement for VPP
                # is planned, but we need to support few releases without it.
                transport._read()
            else:
                # Blocks up to timeout.
                response = vpp_instance.read_blocking()
                if response is None:
                    cmd = state[u"local_list"][state[u"receive_index"]]
                    err = AssertionError(
                        f"Timeout index {state.receive_index} cmd {cmd!r}"
                    )
                else:
                    state[u"ret_list"].append(
                        dictize_and_check_retval(response)
                    )
            if err:
                raise_from(RuntimeError(state.err_msg), err, u"INFO")
            state[u"receive_index"] += 1
            # Send one.
            if state[u"fast_send"]:
                generated = state[u"send_iterator"].__next__()
                socket.sendall(generated)
            else:
                command = state[u"local_list"][state[u"send_index"]]
                func = getattr(api_object, command[u"api_name"])
                func(**command[u"api_args"])
            state[u"send_index"] += 1
        return state

    def _phase_three(self, state):
        """Handle all remaining replies.

        :param state: Container holding current execution state.
        :type state: AsyncState
        :returns: Updated state container.
        :rtype: AsyncState
        """
        # Just to save some CPU work inside loop.
        vpp_instance = state[u"vpp_instance"]
        transport = vpp_instance.transport
        socket = transport.socket
        while state[u"receive_index"] < state[u"lll"]:
            err = None
            if state[u"fast_receive"]:
                select.select([socket], [], [])
                # Pylint reports the following call to _read()
                # as W0212(protected-access).
                # But we need to do that for now, in order to be able to test
                # the current (and older) VPP builds, without wasting
                # tens of minutes without fast receive. Improvement for VPP
                # is planned, but we need to support few releases without it.
                transport._read()
            else:
                # Blocks up to timeout.
                response = vpp_instance.read_blocking()
                if response is None:
                    cmd = state[u"local_list"][state[u"receive_index"]]
                    err = AssertionError(
                        f"Timeout index {state.receive_index} cmd {cmd!r}"
                    )
                else:
                    state[u"ret_list"].append(
                        dictize_and_check_retval(response)
                    )
            if err:
                raise_from(RuntimeError(state.err_msg), err, u"INFO")
            state[u"receive_index"] += 1
        return state


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
