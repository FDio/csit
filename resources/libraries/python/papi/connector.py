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

"""FIXME."""

import shutil
import struct  # vpp-papi can raise struct.error
import subprocess
import tempfile
import time

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.papi.client import Clients
from resources.libraries.python.papi.conn_cache import ConnectionCache


def _key_for_node_and_socket(node, remote_socket):
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


class Connector:
    """FIXME."""

    def __init__(self, node):
        """Create client cache and initialize empty cache of connections.

        :param node: Topology node to download client code from.
        :type node: dict
        """
        self.clients = Clients(node)
        self.conn_cache = ConnectionCache()

    def connect(self, node, remote_vpp_socket):
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

        FIXME.
        :returns: self
        :rtype: SocketExecutor
        """
        # Do we have the connected instance in the cache?
        key = _key_for_node_and_socket(node, remote_vpp_socket)
        vpp_client = self.conn_cache.get_connected_client(key)
        if vpp_client is not None:
            return vpp_client
        # No luck, create and connect a new instance.
        time_enter = time.time()
        # Parsing takes longer than connecting, prepare instance before tunnel.
        vpp_client = self.clients.get_client()
        # Store into cache as soon as possible.
        # If connection fails, it is better to attempt disconnect anyway.
        key = _key_for_node_and_socket(node, remote_vpp_socket)
        self.conn_cache.set_client_connected(vpp_client, key)
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
            api_socket + u":" + remote_vpp_socket,
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
        return vpp_client

    def disconnect_by_key(self, key):
        """Disconnect a connected client instance, noop it not connected.

        Also remove the local sockets by deleting the temporary directory.
        Put disconnected client instances to the reuse list.
        The added attributes are not cleaned up,
        as their values will get overwritten on next connect.

        This method is useful for disconnect_all type of work.

        :param key: Tuple identifying the node (and socket).
        :type key: tuple of str
        """
        vpp_client = self.conn_cache.get_connected_client(key)
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
        self.conn_cache.set_client_disconnected(key)

    def disconnect(self, node, remote_vpp_socket=Constants.SOCKSVR_PATH):
        """FIXME."""
        self.disconnect_by_key(
            _key_for_node_and_socket(node, remote_vpp_socket)
        )

    def disconnect_all(self):
        """FIXME."""
        # Disconnect removes keys from cache, so we must iterate over copy.
        for key in list(self.conn_cache.cache):
            self.disconnect_by_key(key)
