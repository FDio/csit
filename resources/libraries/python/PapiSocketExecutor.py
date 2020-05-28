# Copyright (c) 2020 Cisco and/or its affiliates.
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

This one uses API socket to access DUT VPP from robot machine.
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
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.FilteredLogger import FilteredLogger
from resources.libraries.python.PapiHistory import PapiHistory
from resources.libraries.python.raise_from import raise_from
from resources.libraries.python.spying_socket import SpyingSocket
from resources.libraries.python.ssh import (exec_cmd_no_error, scp_node)
from resources.libraries.python.topology import Topology, SocketType
from resources.libraries.python.VppApiCrc import VppApiCrcChecker


__all__ = [u"PapiSocketExecutor"]


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
    :raises AssertionError: If retval field is present with nonzero.
    """
    ret = dictize(obj)
    if u"retval" in ret.keys():
        # *_details messages do not contain retval.
        retval = ret[u"retval"]
        if retval != 0:
            err = AssertionError(f"Retval nonzero in object {ret!r}")
            # Lowering log level, some retval!=0 calls are expected.
            # TODO: Expose level argument so callers can decide?
            raise_from(AssertionError(err_msg), err, level=u"DEBUG")
    return ret


class PapiSocketExecutor:
    """Methods for executing VPP Python API commands on forwarded socket.

    The current implementation connects for the duration of resource manager.
    Delay for accepting connection is 14s, and disconnect is explicit.
    TODO: Decrease 14s to value that is long enough for creating connection
    and short enough to not cause failures performance.

    The current implementation downloads and parses .api.json files only once
    and stores a VPPApiClient instance (disconnected) as a class variable.
    Accessing multiple nodes with different APIs is therefore not supported.

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
    vpp_instance = None
    """Takes long time to create, stores all PAPI functions and types."""
    crc_checker = None
    """Accesses .api.json files at creation, caching allows deleting them."""

    def __init__(self, node, remote_vpp_socket=Constants.SOCKSVR_PATH,
                 do_async=False):
        """Store the given arguments, declare managed variables.

        Async mode is faster when many commands are to be executed.
        But for *_dump commands it is safer to not use async mode,
        as that mode is not informed all *_details responses have arrived.

        :param node: Node to connect to and forward unix domain socket from.
        :param remote_vpp_socket: Path to remote socket to tunnel to.
        :param do_async: Whether the client should connect in async mode.
        :type node: dict
        :type remote_vpp_socket: str
        :type do_async: bool
        """
        self._node = node
        self._remote_vpp_socket = remote_vpp_socket
        # The list of PAPI commands to be executed on the node.
        self._api_command_list = list()
        # The following values are set on enter, reset on exit.
        self._temp_dir = None
        self._ssh_control_socket = None
        self._local_vpp_socket = None
        self._async = do_async
        self.initialize_vpp_instance()

    def initialize_vpp_instance(self):
        """Create VPP instance with bindings to API calls, store as class field.

        No-op if the instance had been stored already.

        The instance is initialized for unix domain socket access,
        it has initialized all the bindings, but it is not connected
        (to a local socket) yet.

        This method downloads .api.json files from self._node
        into a temporary directory, deletes them finally.
        """
        if self.vpp_instance:
            return
        cls = self.__class__  # Shorthand for setting class fields.
        package_path = None
        tmp_dir = tempfile.mkdtemp(dir=u"/tmp")
        try:
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
            scp_node(node, tmp_dir + u"/papi.txz", u"/tmp/papi.txz", get=True)
            run([u"tar", u"xf", tmp_dir + u"/papi.txz", u"-C", tmp_dir])
            api_json_directory = tmp_dir + u"/usr/share/vpp/api"
            # Perform initial checks before .api.json files are gone,
            # by creating the checker instance.
            cls.crc_checker = VppApiCrcChecker(api_json_directory)
            # When present locally, we finally can find the installation path.
            package_path = glob.glob(tmp_dir + installed_papi_glob)[0]
            # Package path has to be one level above the vpp_papi directory.
            package_path = package_path.rsplit(u"/", 1)[0]
            sys.path.append(package_path)
            # TODO: Pylint says import-outside-toplevel and import-error.
            # It is right, we should refactor the code and move initialization
            # of package outside.
            from vpp_papi.vpp_papi import VPPApiClient as vpp_class
            vpp_class.apidir = api_json_directory
            # We need to create instance before removing from sys.path.
            # Cannot use loglevel parameter, robot.api.logger lacks support.
            # TODO: Stop overriding read_timeout when VPP-1722 is fixed.
            cls.vpp_instance = vpp_class(
                use_socket=True, server_address=None, async_thread=False,
                read_timeout=14, logger=FilteredLogger(logger, "INFO"))
            # The following is needed to prevent union (e.g. Ip4) debug logging
            # of VPP part of PAPI from spamming robot logs.
            logging.getLogger("vpp_papi.vpp_serializer").setLevel(logging.INFO)
        finally:
            shutil.rmtree(tmp_dir)
            if sys.path[-1] == package_path:
                sys.path.pop()

    def __enter__(self):
        """Create a tunnel, connect VPP instance.

        Only at this point a local socket names are created
        in a temporary directory, because VIRL runs 3 pybots at once,
        so harcoding local filenames does not work.

        :returns: self
        :rtype: PapiSocketExecutor
        """
        time_enter = time.monotonic()
        # Parsing takes longer than connecting, prepare instance before tunnel.
        vpp_instance = self.vpp_instance
        node = self._node
        self._temp_dir = tempfile.mkdtemp(dir=u"/tmp")
        self._local_vpp_socket = self._temp_dir + u"/vpp-api.sock"
        self._ssh_control_socket = self._temp_dir + u"/ssh.sock"
        ssh_socket = self._ssh_control_socket
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
        run([u"rm", u"-rvf", self._local_vpp_socket])
        # We use sleep command. The ssh command will exit in 30 second,
        # unless a local socket connection is established,
        # in which case the ssh command will exit only when
        # the ssh connection is closed again (via control socket).
        # The log level is to suppress "Warning: Permanently added" messages.
        ssh_cmd = [
            u"ssh", u"-S", ssh_socket, u"-M",
            u"-o", u"LogLevel=ERROR", u"-o", u"UserKnownHostsFile=/dev/null",
            u"-o", u"StrictHostKeyChecking=no",
            u"-o", u"ExitOnForwardFailure=yes",
            u"-L", self._local_vpp_socket + u":" + self._remote_vpp_socket,
            u"-p", str(node[u"port"]), node[u"username"] + u"@" + node[u"host"],
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
                [u"ls", u"-l", self._local_vpp_socket], check=False
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
        vpp_instance.transport.server_address = self._local_vpp_socket
        try:
            if self._async:
                # The rx_qlen argument is ignored for socket transport.
                vpp_instance.connect(u"csit_socket", do_async=True)
            else:
                # We are still not interested in notifications.
                vpp_instance.connect_sync(u"csit_socket")
        except (IOError, struct.error) as err:
            vpp_instance.disconnect()
            raising = RuntimeError(u"Failed to connect to VPP over a socket.")
            raise_from(raising, err, level="WARN")
        logger.trace(
            u"Establishing socket connection took"
            f" {time.monotonic() - time_enter} seconds."
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnect the vpp instance, tear down the SHH tunnel.

        Also remove the local sockets by deleting the temporary directory.
        Arguments related to possible exception are entirely ignored.
        """
        self.vpp_instance.disconnect()
        run([
            u"ssh", u"-S", self._ssh_control_socket, u"-O", u"exit", u"0.0.0.0"
        ], check=False)
        shutil.rmtree(self._temp_dir)

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
        this saves horizontal space at call sites,
        but takes longer to execute due to reconnects.
        Mainly useful when there is only one block to execute (per DUT).

        Example of call site pattern (two blocks):

        cmd = constant_command
        args = initial_value
        err_msg = my_error_message
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
        cmd = unrelated_command
        args = totally_different_structure
        err_msg = alternative_error_message
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
        with cls(node, do_async=True) as papi_exec:
            return papi_exec.connected_exec_fast(
                command_name=command_name, gen_f=gen_f, err_msg=err_msg,
                how_many=how_many, need_replies=need_replies
            )

    def connected_exec_fast(
            self, command_name, gen_f, err_msg="Failed to get replies.",
            how_many=0, need_replies=True):
        """User friendly wrapper for fast execution, assumes connected.

        Self has to be already connected, in async mode.

        When compared to exec_fast,
        this takes more horizontal space,
        but is faster as reconnects are avoided.
        Mainly useful if multiple blocks are executed, per DUT, in sequence.

        Example of call site pattern (two blocks):

        with PapiSocketExecutor(node, do_async=True) as papi_exec:
            cmd = constant_command
            args = initial_value
            err_msg = my_error_message
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
            cmd = unrelated_command
            args = totally_different_structure
            err_msg = alternative_error_message
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
        The replies are parsed into dict-like objects,
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

        Here is a typical pattern for scale tests:

        cmd = some_command
        fast = 0 if scale < 3 else scale
        with PapiSocketExecutor(node, do_async=True) as papi_exec:
            for count in range(2 if fast else scale):
                args = get_args(count)
                papi_exec.add(cmd, **args)
            papi_exec.get_replies(
                err_msg=err_msg, fast_send=fast, fast_receive=True
            )

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
                f"{cmd} ({node[u'host']} - {remote_vpp_socket}):\n"
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
            fast_receive=False):
        """Turn internal command list into data and execute; return replies.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_replies()
        - get_reply()
        - get_sw_if_index()
        - get_details()

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param fast_send: This many (minus initia two) fast commands are added.
        :param fast_receive: Whether responses are to be parsed and returned.
        :type err_msg: str
        :type fast_send: int
        :type fast_receive: bool
        :returns: Papi responses parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: NoneType or list of dict
        :raises RuntimeError: If the replies are not all correct.
        """
        local_list = self._api_command_list
        # Clear first as execution may fail.
        self._api_command_list = list()
        if self._async:
            return self._execute_async(
                local_list, err_msg=err_msg, fast_send=fast_send,
                fast_receive=fast_receive
            )
        if fast_send:
            raise RuntimeError(u"Fast sending is not supported in sync mode.")
        return self._execute_sync(local_list, err_msg=err_msg)

    def _execute_sync(self, local_list, err_msg="Undefined error message"):
        """Execute command waiting for replies one by one; return replies.

        This is the implementation using sync PAPI calls.
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
        vpp_instance = self.vpp_instance
        ret_list = list()
        for command in local_list:
            api_name = command[u"api_name"]
            papi_fn = getattr(vpp_instance.api, api_name)
            try:
                try:
                    reply = papi_fn(**command[u"api_args"])
                except (IOError, struct.error) as err:
                    # Occasionally an error happens, try reconnect.
                    logger.warn(f"Reconnect after error: {err!r}")
                    self.vpp_instance.disconnect()
                    # Testing shows immediate reconnect fails.
                    time.sleep(1)
                    self.vpp_instance.connect_sync(u"csit_socket")
                    logger.trace(u"Reconnected.")
                    reply = papi_fn(**command[u"api_args"])
            except (AttributeError, IOError, struct.error) as err:
                raise AssertionError(err_msg) from err
            # *_dump commands return list of objects, convert, ordinary reply.
            replies = reply if isinstance(reply, list) else [reply]
            for item in replies:
                # Request CRC has been checked in add, here check reply CRC.
                self.crc_checker.check_api_name(item.__class__.__name__)
                dict_item = dictize_and_check_retval(item)
                ret_list.append(dict_item)
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
        :returns: Papi responses parsed into a dict-like object,
            with fields due to API (possibly including retval).
        :rtype: list of dict
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
            transport = self.vpp_instance.transport
            transport.message_thread = threading.Thread(
                target=transport.msg_thread_func
            )
            transport.message_thread.daemon = True
            transport.message_thread.start()
        return state[u"ret_list"]

    def _phase_zero(self, state):
        """Compute dependent state fields adn other setup actions.

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
        # Just to save some CPU work inside loop.
        vpp_instance = self.vpp_instance
        # Not enough pylint-allowed variables to store vpp_instance.api.
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
            raise RuntimeError(f"Timeout processing first reply.")
        state[u"ret_list"].append(dictize_and_check_retval(response))
        response = vpp_instance.read_blocking()
        state[u"receive_index"] += 1
        if response is None:
            raise RuntimeError(f"Timeout processing second reply.")
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
        # Just to save some CPU work inside loop.
        api_object = self.vpp_instance.api
        socket = self.vpp_instance.transport.socket
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
        vpp_instance = self.vpp_instance
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
                raise_from(RuntimeError(state.err_msg), err, f"INFO")
            state[u"receive_index"] += 1
            # Send one.
            if state[u"fast_send"]:
                generated = state[u"send_iterator"].__next__()
                socket.sendall(generated)
            else:
                command = state[u"local_list"][state[u"send_index"]]
                func = getattr(api_object, command[f"api_name"])
                func(**command[f"api_args"])
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
        vpp_instance = self.vpp_instance
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
                raise_from(RuntimeError(state.err_msg), err, f"INFO")
            state[u"receive_index"] += 1
        return state
