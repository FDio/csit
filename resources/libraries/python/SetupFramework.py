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

"""This module exists to provide setup utilities for the framework on topology
nodes. All tasks required to be run before the actual tests are started is
supposed to end up here.
"""

from os import environ, remove
import socket  # For catching socket.timeout.
from tempfile import NamedTemporaryFile
import threading

from robot.api import logger

from resources.libraries.python.Constants import Constants as con
from resources.libraries.python.ssh import exec_cmd_no_error, scp_node
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.topology import NodeType

__all__ = [u"SetupFramework"]


def rsync_framework(node):
    """Use Rsync to copy framework from robot to DUT or TG.

    It is assumed current working directory is the root directory
    of the framework to copy.

    :param node: Node to copy to.
    :type node: dict
    :raises RuntimeError: On non-zero return code.
    """
    path = con.REMOTE_FW_DIR
    host = node[u"host"]
    user = node[u"username"]
    port = node[u"port"]
    passwd = node[u"password"]
    node_type = node[u"type"]
    logger.console(
        f"Rsyncing framework to {path} on {node_type} "
        f"host {host}, port {port} starts."
    )
    # TODO: Support priv keys.
    ret_code, output = run([
        u"sshpass", u"-p", f"{passwd}", u"rsync", u"-e", f"ssh -p {port}",
        u"-acy", u"--delete-during", u"--time-limit=2",
        u".", f"{user}@{host}:{path}"
    ])
    if ret_code != 0:
        raise RuntimeError(
            f"Failed to rsync framework to node {node_type} "
            f"host {host}, port {port}. Output:\n{output}"
        )
    logger.console(
        f"Rsyncing framework to {path} on {node_type} "
        f"host {host}, port {port} done."
    )


def create_env_directory_at_node(node):
    """Create fresh virtualenv to a directory, install pip requirements.

    :param node: Node to create virtualenv on.
    :type node: dict
    :returns: nothing
    :raises RuntimeError: When failed to setup virtualenv.
    """
    logger.console(
        f"Virtualenv setup including requirements.txt on {node[u'type']} "
        f"host {node[u'host']}, port {node[u'port']} starts."
    )
    cmd = f"cd {con.REMOTE_FW_DIR} && rm -rf env && virtualenv " \
        f"-p $(which python3) --system-site-packages --never-download env " \
        f"&& source env/bin/activate && ANSIBLE_SKIP_CONFLICT_CHECK=1 " \
        f"pip3 install -r requirements.txt"
    exec_cmd_no_error(
        node, cmd, timeout=100, include_reason=True,
        message=f"Failed install at node {node[u'type']} host {node[u'host']}, "
        f"port {node[u'port']}"
    )
    logger.console(
        f"Virtualenv setup on {node[u'type']} host {node[u'host']}, "
        f"port {node[u'port']} done."
    )


def setup_node(node, results=None):
    """Copy a tarball to a node and extract it.

    :param node: A node where the tarball will be copied and extracted.
    :param tarball: Local path of tarball to be copied.
    :param remote_tarball: Remote path of the tarball.
    :param results: A list where to store the result of node setup, optional.
    :type node: dict
    :type tarball: str
    :type remote_tarball: str
    :type results: list
    :returns: True - success, False - error
    :rtype: bool
    """
    try:
        rsync_framework(node)
        if node[u"type"] == NodeType.TG:
            create_env_directory_at_node(node)
    except (RuntimeError, socket.timeout) as exc:
        logger.console(
            f"Node {node[u'type']} host {node[u'host']}, port {node[u'port']} "
            f"setup failed, error: {exc!r}"
        )
        result = False
    else:
        logger.console(
            f"Setup of node {node[u'type']} host {node[u'host']}, "
            f"port {node[u'port']} done."
        )
        result = True

    if isinstance(results, list):
        results.append(result)
    return result


def delete_framework_dir(node):
    """Delete framework directory in /tmp/ on given node.

    :param node: Node to delete framework directory on.
    :type node: dict
    """
    logger.console(
        f"Deleting framework directory on {node[u'type']} host {node[u'host']},"
        f" port {node[u'port']} starts."
    )
    exec_cmd_no_error(
        node, f"sudo rm -rf {con.REMOTE_FW_DIR}",
        message=f"Framework delete failed at node {node[u'type']} "
        f"host {node[u'host']}, port {node[u'port']}",
        timeout=100, include_reason=True
    )
    logger.console(
        f"Deleting framework directory on {node[u'type']} host {node[u'host']},"
        f" port {node[u'port']} done."
    )


def cleanup_node(node, results=None):
    """Delete the copy of framework on a remote node.

    :param node: A node where the framework copy will be deleted.
    :param results: A list where to store the result of node cleanup, optional.
    :type node: dict
    :type results: list
    :returns: True - success, False - error
    :rtype: bool
    """
    try:
        delete_framework_dir(node)
    except RuntimeError:
        logger.error(
            f"Cleanup of node {node[u'type']} host {node[u'host']}, "
            f"port {node[u'port']} failed."
        )
        result = False
    else:
        logger.console(
            f"Cleanup of node {node[u'type']} host {node[u'host']}, "
            f"port {node[u'port']} done."
        )
        result = True

    if isinstance(results, list):
        results.append(result)
    return result


class SetupFramework:
    """Setup suite run on topology nodes.

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    @staticmethod
    def setup_framework(nodes):
        """Pack the whole directory and extract in temp on each node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :raises RuntimeError: If setup framework failed.
        """

        results = list()
        threads = list()

        for node in nodes.values():
            args = node, results
            thread = threading.Thread(target=setup_node, args=args)
            thread.start()
            threads.append(thread)

        logger.info(
            u"Executing node setups in parallel, waiting for threads to end."
        )

        for thread in threads:
            thread.join()

        logger.info(f"Results: {results}")

        if all(results):
            logger.console(u"All nodes are ready.")
            for node in nodes.values():
                logger.info(
                    f"Setup of node {node[u'type']} host {node[u'host']}, "
                    f"port {node[u'port']} done."
                )
        else:
            raise RuntimeError(u"Failed to setup framework.")


class CleanupFramework:
    """Clean up suite run on topology nodes."""

    @staticmethod
    def cleanup_framework(nodes):
        """Perform cleanup on each node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :raises RuntimeError: If cleanup framework failed.
        """

        results = list()
        threads = list()

        for node in nodes.values():
            thread = threading.Thread(target=cleanup_node, args=(node, results))
            thread.start()
            threads.append(thread)

        logger.info(
            u"Executing node cleanups in parallel, waiting for threads to end."
        )

        for thread in threads:
            thread.join()

        logger.info(f"Results: {results}")

        if all(results):
            logger.console(u"All nodes cleaned up.")
        else:
            raise RuntimeError(u"Failed to cleaned up framework.")
