# Copyright (c) 2019 Cisco and/or its affiliates.
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

import binascii
import glob
import json
import os
import shutil
import socket
#import StringIO
import subprocess
import sys
import tempfile
import time

#import paramiko
from robot.api import logger
#import sshtunnel

from resources.libraries.python.Constants import Constants
from resources.libraries.python.ssh import SSH, SSHTimeout, exec_cmd_no_error
from resources.libraries.python.PapiHistory import PapiHistory


__all__ = ["PapiExecutor", "PapiSocketExecutor", "PapiResponse"]


# VPP instance is inserted here if needed.
INSTANCES = dict()


def get_vpp_instance(path):
    """Return VPP instance with bindings to all API calls.

    The returned instance is initialized for unix domain socket access,
    it has initialized all the bindings, but it is not connected yet.

    After first invocation, the result is cached, so other calls are quick.
    First invocation needs to extract .deb files to find .api.json files,
    using a temporary directory.

    :param path: Absolute path to local socket to use.
    :type path: str
    :returns: Initialized but not connected VPP instance.
    :rtype: vpp_papi.VPP
    """
    cached = INSTANCES.get("vpp_instance", None)
    if cached is not None:
        return cached
    # TODO: Do we want to use Constants.DOWNLOAD_DIR as a fallback?
    # The dir from Constants has no reason to contain .deb packages.
    download_dir = os.getenv("DOWNLOAD_DIR", None)
    if download_dir is None:
        raise RuntimeError("DOWNLOAD_DIR is needed to extract *.api.json from")
    tmp_dir = tempfile.mkdtemp(dir=download_dir)
    vad_backup = os.getenv("VPP_API_DIR", None)
    try:
        # TODO: We need to support .rpm and test also on aarch64 boxes.
        # TODO: The correct way is to scp the .api.json from testbeds probably.
        for deb_filename in glob.glob(download_dir + "/*vpp*.deb"):
            # TODO: Redirect stdout and stderr? To dev/null?
            subprocess.check_call(["dpkg", "-x", deb_filename, tmp_dir])
        package_path = None
        for root, _, files in os.walk(tmp_dir):
            for name in files:
                if name == "vpp_papi.py" and not "python3" in root:
                    # Package path is one dir above where the file was found.
                    package_path = os.path.split(root)[0]
                    break
            else:
                continue
            break
        if package_path:
            # TODO: Contribute a programmatic way to locate .api.json files.
            os.environ["VPP_API_DIR"] = tmp_dir
            sys.path.append(package_path)
            from vpp_papi.vpp_papi import VPP as vpp_class
            # We need to create instance before removing from sys.path.
            vpp_instance = vpp_class(use_socket=True, server_address=path)
        else:
            raise RuntimeError("vpp_papi module not found")
    finally:
        shutil.rmtree(tmp_dir)
        if "VPP_API_DIR" in os.environ:
            if vad_backup is None:
                del os.environ["VPP_API_DIR"]
            else:
                os.environ["VPP_API_DIR"] = vad_backup
        if sys.path[-1] == package_path:
            sys.path.pop()
    INSTANCES["vpp_instance"] = vpp_instance
    return vpp_instance


def dictize(obj):
    """A helper method, to make namedtuple-like object accessible as dict.

    If the object is namedtuple-like, its _asdict() form is returned,
    but in the returned object __getitem__ method is wrapped
    to dictize also any items returned.
    If the object does not have _asdict, it will be returned without change.
    Integer keys still access the object as tuple.

    :param obj: Arbitrary object to dictize.
    :type obj: object
    :returns: Dictized object.
    :rtype: same as obj type or collections.OrderedDict
    """
    if not hasattr(obj, "_asdict"):
        return obj
    ret = obj._asdict()
    old_get = ret.__getitem__
    new_get = lambda self, key: dictize(old_get(self, key))
    ret.__getitem__ = new_get
    return ret


class PapiResponse(object):
    """Class for metadata specifying the Papi replies, stdout, stderr and return
    code.
    """

    def __init__(self, replies=None, stdout="", stderr="", requests=None):
        """Construct the Papi response by setting the values needed.

        TODO:
            Implement 'dump' analogue of verify_replies that would concatenate
            the values, so that call sites do not have to do that themselves.

        :param replies: API replies from last executed PAPI command(s).
        :param stdout: stdout from last executed PAPI command(s).
        :param stderr: stderr from last executed PAPI command(s).
        :param requests: List of used PAPI requests. It is used while verifying
            replies. If None, expected replies must be provided for verify_reply
            and verify_replies methods.
        :type replies: list or None
        :type stdout: str
        :type stderr: str
        :type requests: list
        """

        # API replies from last executed PAPI command(s).
        self.replies = replies

        # stdout from last executed PAPI command(s).
        self.stdout = stdout

        # stderr from last executed PAPI command(s).
        self.stderr = stderr

        # List of used PAPI requests.
        self.requests = requests

        # List of expected PAPI replies. It is used while verifying replies.
        if self.requests:
            self.expected_replies = \
                ["{rqst}_reply".format(rqst=rqst) for rqst in self.requests]

    def __str__(self):
        """Return string with human readable description of the PapiResponse.

        :returns: Readable description.
        :rtype: str
        """
        return (
            "replies={replies},stdout={stdout},stderr={stderr},"
            "requests={requests}").format(
                replies=self.replies, stdout=self.stdout, stderr=self.stderr,
                requests=self.requests)

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call.
        :rtype: str
        """
        return "PapiResponse({str})".format(str=str(self))

    def verify_reply(self, cmd_reply=None, idx=0,
                     err_msg="Failed to verify PAPI reply."):
        """Verify and return data from the PAPI response.

        Note: Use only with a simple request / reply command. In this case the
        PAPI reply includes 'retval' which is checked in this method.

        Do not use with 'dump' and 'vpp-stats' methods.

        Use if PAPI response includes only one command reply.

        Use it this way (preferred):

        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().verify_reply()

        or if you must provide the expected reply (not recommended):

        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().\
                verify_reply('show_version_reply')

        :param cmd_reply: PAPI reply. If None, list of 'requests' should have
            been provided to the __init__ method as pre-generated list of
            replies is used in this method in this case.
            The PapiExecutor._execute() method provides the requests
            automatically.
        :param idx: Index to PapiResponse.replies list.
        :param err_msg: The message used if the verification fails.
        :type cmd_reply: str
        :type idx: int
        :type err_msg: str or None
        :returns: Verified data from PAPI response.
        :rtype: dict
        :raises AssertionError: If the PAPI return value is not 0, so the reply
            is not valid.
        :raises KeyError, IndexError: If the reply does not have expected
            structure.
        """
        cmd_rpl = self.expected_replies[idx] if cmd_reply is None else cmd_reply

        data = self.replies[idx]['api_reply'][cmd_rpl]
        if data['retval'] != 0:
            raise AssertionError("{msg}\nidx={idx}, cmd_reply={reply}".
                                 format(msg=err_msg, idx=idx, reply=cmd_rpl))

        return data

    def verify_replies(self, err_msg="Failed to verify PAPI replies."):
        """Verify and return data from the PAPI response.

        Note: Use only with request / replies commands. In this case each
        PAPI replies includes 'retval' which is checked.

        Do not use with 'dump' and 'vpp-stats' methods.

        Use if PAPI response includes more than one command replies.

        Use it this way:

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd1, **args1).add(cmd2, **args2).add(cmd2, **args3).\
                get_replies().verify_replies(err_msg)

        or if you need the data from the PAPI response:

        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies().verify_replies(err_msg)

        :param err_msg: The message used if the verification fails.
        :type err_msg: str
        :returns: List of verified data from PAPI response.
        :rtype list
        :raises AssertionError: If the PAPI response does not include at least
            one of specified command replies.
        """
        data = list()

        cmd_rpls = self.expected_replies

        if len(self.replies) != len(cmd_rpls):
            raise AssertionError(err_msg)
        for idx, cmd_reply in enumerate(cmd_rpls):
            data.append(self.verify_reply(cmd_reply, idx, err_msg))

        return data


    def verify_details(self, err_msg="Failed to verify PAPI replies."):
        """Verify and return data from the PAPI response.

        Note: Use only with dump type commands. In this case PAPI replies
        do not include 'retval'. Instead *_details is checked.

        Note that each dump-type command may result in multiple detail items,
        so it is recommended to use only one type of commands.

        Use it this way:

        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).get_details(
                ).verify_details(err_msg)

        :param err_msg: The message used if the verification fails.
        :type err_msg: str
        :returns: List of verified data from PAPI response.
        :rtype list
        :raises AssertionError: If the PAPI response does not match *_details.
        """
        # TODO: Implement the actual *_details checking.
        data = [item.values()[0] for item in self.replies]

        return data


class PapiSocketExecutor(object):
    """Methods for executing VPP Python API commands on forwarded socket.

    The current implementation connects only just before execution starts.

    TODO: Implement connection caching or pooling, to improve speed.

    TODO: Support sockets in NFs somehow.

    Note: Use only with "with" statement, e.g.:

        with PapiSocketExecutor(node, remote_socket_path) as papi_exec:
            data = papi_exec.add('show_version').\
                get_replies().verify_reply(err_msg)

    This class processes two classes of VPP PAPI methods:
    1. Simple request / reply: method='request'.
    2. Dump functions: method='dump'.

    Note that access to VPP stats over socket is not supported yet.

    The recommended ways of use are (examples):

    1. Simple request / reply

    a. One request with no arguments:

        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().\
                verify_reply()

    b. Three requests with arguments, the second and the third ones are the same
       but with different arguments.

        with PapiSocketExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies().verify_replies(err_msg)

    2. Dump functions

        cmd = 'sw_interface_rx_placement_dump'
        with PapiSocketExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index']).\
                get_details().verify_details(err_msg)
    """

    def __init__(self, node, local_socket_path="/run/vpp-api.sock",
                 remote_socket_path="/run/vpp-api.sock"):
        """Initialization.

        :param node: Node to connect to and forward unix domain socket from.
        :param local_socket_path: Path to local end of socket tunnel to create.
        :param remote_socket_path: Path to remote socket to tunnel to.
        :type node: dict
        :type local_socket_path: str
        :type remote_socket_path: str
        """
        self._node = node
        self._local_socket_path = local_socket_path
        self._remote_socket_path = remote_socket_path
        # The list of PAPI commands to be executed on the node.
        self._api_command_list = list()

    def __enter__(self):
        """Currently a no-op, but reserved for future improvements."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Currently a no-op, but reserved for future improvements."""
        return

    def add(self, csit_papi_command, **kwargs):
        """Add next command to internal command list; return self.

        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.

        :param csit_papi_command: VPP API command.
        :param kwargs: Optional key-value arguments.
        :type csit_papi_command: str
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """
        PapiHistory.add_to_papi_history(self._node, csit_papi_command, **kwargs)
        self._api_command_list.append(
            dict(api_name=csit_papi_command, api_args=kwargs))
        return self

    def get_replies(self):
        """Get reply/replies from VPP Python API.

        :returns: Papi response with only reply being non-trivial.
        :rtype: PapiResponse
        """
        return self._execute()

    def get_details(self):
        """Get dump details from VPP Python API.

        :returns: Papi response with only reply being non-trivial.
        :rtype: PapiResponse
        """
        return self._execute()

    def _execute(self):
        """Execute commands from internal list, return PAPI response.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_replies()
        - get_details()

        :param method: VPP Python API method. Supported methods are: 'request',
            and 'dump'.
        :type method: str
        :returns: Papi response with only replies being non-trivial.
        :rtype: PapiResponse
        :raises KeyError: If the replies is not correct.
        """
        local_list = self._api_command_list
        # Clear first as execution may fail.
        self._api_command_list = list()
        node = self._node
        vpp_instance = get_vpp_instance(self._local_socket_path)
        # TODO: Support private keys.
        #pkey = paramiko.RSAKey.from_private_key(StringIO.StringIO(
        #    node['priv_key'])) if 'priv_key' in node else None

        try:
            vpp_instance.connect("csit_socket")
        except socket.error as err:
            # For debugging only.
            logger.debug(repr(err))
            logger.debug(repr(type(err)))
            # Connection refused. Either first call, or previous connection
            # timed out. In either way, retry once by creating a tunnel.
            # TODO: Move package installation into appropriately early place.
            subprocess.check_call(["sudo", "apt-get", "install", "-y", "sshpass"])
            # Check socket presence on remote side.
            exec_cmd_no_error(self._node, "ls -l " + self._remote_socket_path)
            # We use sleep command. The ssh command wil exit in 1 second,
            # unless a local socket connection is established,
            # in which case the ssh command will exit only when
            # the socket connection is closed again.
            # TODO: Should we clear nohup.out?
            ssh_cmd_arg = [
                "sshpass", "-p", node.get('password'), "ssh",
                "-L", self._local_socket_path + ':' + self._remote_socket_path,
                "-p", str(node['port']), node['username'] + "@" + node['host'],
                "sleep", "10"]
            logger.debug("call arg repr: " + repr(ssh_cmd_arg))
            logger.debug("call arg types: " + str(map(type, ssh_cmd_arg)))
            time_stop = time.time() + 10.0
            # subprocess.Popen seems to be the best way to run commands
            # on background. Other ways (shell=True wit "&" and ssh with -f)
            # seem to be too dependent on shell behavior.
            subprocess.Popen(ssh_cmd_arg)
            # TODO: Except and log something?
            # Check socket presence on local side.
            while time.time() < time_stop:
                # It takes a while for ssh to create the socket file.
                try:
                    output = subprocess.check_output(
                        ["ls", "-l", self._local_socket_path],
                        stderr=subprocess.STDOUT)
                    logger.debug(output)
                except subprocess.CalledProcessError as err:
                    logger.debug(err.output)
                    time.sleep(0.2)
                else:
                    break
            else:
                raise RuntimeError("Local side socket has not appeared.")
            subprocess.check_output(["chmod", "a+rwx", self._local_socket_path])
            output = subprocess.check_output(
                ["ls", "-l", self._local_socket_path], stderr=subprocess.STDOUT)
            logger.debug(output)
            vpp_instance.connect("csit_socket")
        try:
            replies = list()
            for item in local_list:
                api_name = item["api_name"]
                papi_fn = getattr(vpp_instance.api, api_name)
                reply = papi_fn(**item["api_args"])
                # We need to cut the vpp_papi.vpp_serializer part.
                logger.debug(repr(reply))
                name = str(type(reply)).rsplit(".", 1)[1][:-2]
                replies.append(dict(api_name=api_name, api_reply={
                    name: dictize(reply)}))
                logger.debug(repr(replies[-1]))
        # TODO: Except common errors and add support for err_msg.
        finally:
            vpp_instance.disconnect()
        return PapiResponse(
            replies=replies, stdout=None, stderr=None,
            requests=[rqst["api_name"] for rqst in local_list])


class PapiExecutor(object):
    """Contains methods for executing VPP Python API commands on DUTs.

    Note: Use only with "with" statement, e.g.:

        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add('show_version').get_replies(err_msg)

    This class processes three classes of VPP PAPI methods:
    1. simple request / reply: method='request',
    2. dump functions: method='dump',
    3. vpp-stats: method='stats'.

    The recommended ways of use are (examples):

    1. Simple request / reply

    a. One request with no arguments:

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('show_version').get_replies().\
                verify_reply()

    b. Three requests with arguments, the second and the third ones are the same
       but with different arguments.

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd1, **args1).add(cmd2, **args2).\
                add(cmd2, **args3).get_replies(err_msg).verify_replies()

    2. Dump functions

        cmd = 'sw_interface_rx_placement_dump'
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, sw_if_index=ifc['vpp_sw_index']).\
                get_dump(err_msg)

    3. vpp-stats

        path = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(api_name='vpp-stats', path=path).get_stats()

        print('RX interface core 0, sw_if_index 0:\n{0}'.\
            format(data[0]['/if/rx'][0][0]))

        or

        path_1 = ['^/if', ]
        path_2 = ['^/if', '/err/ip4-input', '/sys/node/ip4-input']

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add('vpp-stats', path=path_1).\
                add('vpp-stats', path=path_2).get_stats()

        print('RX interface core 0, sw_if_index 0:\n{0}'.\
            format(data[1]['/if/rx'][0][0]))

        Note: In this case, when PapiExecutor method 'add' is used:
        - its parameter 'csit_papi_command' is used only to keep information
          that vpp-stats are requested. It is not further processed but it is
          included in the PAPI history this way:
          vpp-stats(path=['^/if', '/err/ip4-input', '/sys/node/ip4-input'])
          Always use csit_papi_command="vpp-stats" if the VPP PAPI method
          is "stats".
        - the second parameter must be 'path' as it is used by PapiExecutor
          method 'add'.
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
        except IOError:
            raise RuntimeError("Cannot open SSH connection to host {host} to "
                               "execute PAPI command(s)".
                               format(host=self._node["host"]))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ssh.disconnect(self._node)

    def add(self, csit_papi_command="vpp-stats", **kwargs):
        """Add next command to internal command list; return self.

        The argument name 'csit_papi_command' must be unique enough as it cannot
        be repeated in kwargs.

        :param csit_papi_command: VPP API command.
        :param kwargs: Optional key-value arguments.
        :type csit_papi_command: str
        :type kwargs: dict
        :returns: self, so that method chaining is possible.
        :rtype: PapiExecutor
        """
        PapiHistory.add_to_papi_history(self._node, csit_papi_command, **kwargs)
        self._api_command_list.append(dict(api_name=csit_papi_command,
                                           api_args=kwargs))
        return self

    def get_stats(self, err_msg="Failed to get statistics.", timeout=120):
        """Get VPP Stats from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type timeout: int
        :returns: Requested VPP statistics.
        :rtype: list
        """

        paths = [cmd['api_args']['path'] for cmd in self._api_command_list]
        self._api_command_list = list()

        stdout, _ = self._execute_papi(
            paths, method='stats', err_msg=err_msg, timeout=timeout)

        return json.loads(stdout)

    def get_replies(self, err_msg="Failed to get replies.",
                    process_reply=True, ignore_errors=False, timeout=120):
        """Get reply/replies from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Process PAPI replies if True.
        :param ignore_errors: If true, the errors in the replies are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: replies, stdout, stderr and
            return code.
        :rtype: PapiResponse
        """
        return self._execute(
            method='request', process_reply=process_reply,
            ignore_errors=ignore_errors, err_msg=err_msg, timeout=timeout)

    def get_dump(self, err_msg="Failed to get dump.",
                 process_reply=True, ignore_errors=False, timeout=120):
        """Get dump from VPP Python API.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Process PAPI replies if True.
        :param ignore_errors: If true, the errors in the replies are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: replies, stdout, stderr and
            return code.
        :rtype: PapiResponse
        """
        return self._execute(
            method='dump', process_reply=process_reply,
            ignore_errors=ignore_errors, err_msg=err_msg, timeout=timeout)

    def execute_should_pass(self, err_msg="Failed to execute PAPI command.",
                            process_reply=True, ignore_errors=False,
                            timeout=120):
        """Execute the PAPI commands and check the return code.
        Raise exception if the PAPI command(s) failed.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_replies()
        - get_dump()
        This method will be removed soon.

        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param process_reply: Indicate whether or not to process PAPI replies.
        :param ignore_errors: If true, the errors in the replies are ignored.
        :param timeout: Timeout in seconds.
        :type err_msg: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type timeout: int
        :returns: Papi response including: replies, stdout, stderr and
            return code.
        :rtype: PapiResponse
        :raises AssertionError: If PAPI command(s) execution failed.
        """
        # TODO: Migrate callers to get_replies and delete this method.
        return self.get_replies(
            process_reply=process_reply, ignore_errors=ignore_errors,
            err_msg=err_msg, timeout=timeout)

    @staticmethod
    def _process_api_data(api_d):
        """Process API data for smooth converting to JSON string.

        Apply binascii.hexlify() method for string values.

        :param api_d: List of APIs with their arguments.
        :type api_d: list
        :returns: List of APIs with arguments pre-processed for JSON.
        :rtype: list
        """

        api_data_processed = list()
        for api in api_d:
            api_args_processed = dict()
            for a_k, a_v in api["api_args"].iteritems():
                value = binascii.hexlify(a_v) if isinstance(a_v, str) else a_v
                api_args_processed[str(a_k)] = value
            api_data_processed.append(dict(api_name=api["api_name"],
                                           api_args=api_args_processed))
        return api_data_processed

    @staticmethod
    def _revert_api_reply(api_r):
        """Process API reply / a part of API reply.

        Apply binascii.unhexlify() method for unicode values.

        TODO: Implement complex solution to process of replies.

        :param api_r: API reply.
        :type api_r: dict
        :returns: Processed API reply / a part of API reply.
        :rtype: dict
        """
        reply_dict = dict()
        reply_value = dict()
        for reply_key, reply_v in api_r.iteritems():
            for a_k, a_v in reply_v.iteritems():
                reply_value[a_k] = binascii.unhexlify(a_v) \
                    if isinstance(a_v, unicode) else a_v
            reply_dict[reply_key] = reply_value
        return reply_dict

    def _process_reply(self, api_reply):
        """Process API reply.

        :param api_reply: API reply.
        :type api_reply: dict or list of dict
        :returns: Processed API reply.
        :rtype: list or dict
        """
        if isinstance(api_reply, list):
            reverted_reply = [self._revert_api_reply(a_r) for a_r in api_reply]
        else:
            reverted_reply = self._revert_api_reply(api_reply)
        return reverted_reply

    def _execute_papi(self, api_data, method='request', err_msg="",
                      timeout=120):
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
        :returns: Stdout and stderr.
        :rtype: 2-tuple of str
        :raises SSHTimeout: If PAPI command(s) execution has timed out.
        :raises RuntimeError: If PAPI executor failed due to another reason.
        :raises AssertionError: If PAPI command(s) execution has failed.
        """

        if not api_data:
            RuntimeError("No API data provided.")

        json_data = json.dumps(api_data) if method == "stats" \
            else json.dumps(self._process_api_data(api_data))

        cmd = "{fw_dir}/{papi_provider} --method {method} --data '{json}'".\
            format(fw_dir=Constants.REMOTE_FW_DIR,
                   papi_provider=Constants.RESOURCES_PAPI_PROVIDER,
                   method=method,
                   json=json_data)
        try:
            ret_code, stdout, stderr = self._ssh.exec_command_sudo(
                cmd=cmd, timeout=timeout)
        except SSHTimeout:
            logger.error("PAPI command(s) execution timeout on host {host}:"
                         "\n{apis}".format(host=self._node["host"],
                                           apis=api_data))
            raise
        except Exception:
            raise RuntimeError("PAPI command(s) execution on host {host} "
                               "failed: {apis}".format(host=self._node["host"],
                                                       apis=api_data))
        if ret_code != 0:
            raise AssertionError(err_msg)

        return stdout, stderr

    def _execute(self, method='request', process_reply=True,
                 ignore_errors=False, err_msg="", timeout=120):
        """Turn internal command list into proper data and execute; return
        PAPI response.

        This method also clears the internal command list.

        IMPORTANT!
        Do not use this method in L1 keywords. Use:
        - get_stats()
        - get_replies()
        - get_dump()

        :param method: VPP Python API method. Supported methods are: 'request',
            'dump' and 'stats'.
        :param process_reply: Process PAPI replies if True.
        :param ignore_errors: If true, the errors in the replies are ignored.
        :param err_msg: The message used if the PAPI command(s) execution fails.
        :param timeout: Timeout in seconds.
        :type method: str
        :type process_reply: bool
        :type ignore_errors: bool
        :type err_msg: str
        :type timeout: int
        :returns: Papi response including: replies, stdout, stderr and
            return code.
        :rtype: PapiResponse
        :raises KeyError: If the replies is not correct.
        """

        local_list = self._api_command_list

        # Clear first as execution may fail.
        self._api_command_list = list()

        stdout, stderr = self._execute_papi(
            local_list, method=method, err_msg=err_msg, timeout=timeout)
        replies = list()
        if process_reply:
            try:
                json_data = json.loads(stdout)
            except ValueError:
                logger.error("An error occured while processing the PAPI "
                             "request:\n{rqst}".format(rqst=local_list))
                raise
            for data in json_data:
                try:
                    api_reply_processed = dict(
                        api_name=data["api_name"],
                        api_reply=self._process_reply(data["api_reply"]))
                except KeyError:
                    if ignore_errors:
                        continue
                    else:
                        raise
                replies.append(api_reply_processed)

        # Log processed replies to be able to check API replies changes
        logger.debug("Processed PAPI replies: {replies}".format(replies=replies))

        return PapiResponse(
            replies=replies, stdout=stdout, stderr=stderr,
            requests=[rqst["api_name"] for rqst in local_list])
