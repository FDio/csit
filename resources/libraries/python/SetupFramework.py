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
from tempfile import NamedTemporaryFile
import threading
import traceback

from robot.api import logger

from resources.libraries.python.Constants import Constants as con
from resources.libraries.python.ssh import exec_cmd_no_error, scp_node
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.topology import NodeType

__all__ = [u"SetupFramework"]


def pack_framework_dir():
    """Pack the testing WS into temp file, return its name.

    :returns: Tarball file name.
    :rtype: str
    :raises Exception: When failed to pack testing framework.
    """

    try:
        directory = environ[u"TMPDIR"]
    except KeyError:
        directory = None

    if directory is not None:
        tmpfile = NamedTemporaryFile(
            suffix=u".tgz", prefix=u"csit-testing-", dir=f"{directory}"
        )
    else:
        tmpfile = NamedTemporaryFile(suffix=u".tgz", prefix=u"csit-testing-")
    file_name = tmpfile.name
    tmpfile.close()

    run(
        [
            u"tar", u"--sparse", u"--exclude-vcs", u"--exclude=output*.xml",
            u"--exclude=./tmp", u"-zcf", file_name, u"."
        ], msg=u"Could not pack testing framework"
    )

    return file_name


def copy_tarball_to_node(tarball, node):
    """Copy tarball file from local host to remote node.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :returns: nothing
    """
    logger.console(
        f"Copying tarball to {node[u'type']} host {node[u'host']}, "
        f"port {node[u'port']} starts."
    )
    scp_node(node, tarball, u"/tmp/")
    logger.console(
        f"Copying tarball to {node[u'type']} host {node[u'host']}, "
        f"port {node[u'port']} done."
    )


def extract_tarball_at_node(tarball, node):
    """Extract tarball at given node.

    Extracts tarball using tar on given node to specific CSIT location.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :returns: nothing
    :raises RuntimeError: When failed to unpack tarball.
    """
    logger.console(
        f"Extracting tarball to {con.REMOTE_FW_DIR} on {node[u'type']} "
        f"host {node[u'host']}, port {node[u'port']} starts."
    )
    cmd = f"sudo rm -rf {con.REMOTE_FW_DIR}; mkdir {con.REMOTE_FW_DIR}; " \
        f"tar -zxf {tarball} -C {con.REMOTE_FW_DIR}; rm -f {tarball}"
    exec_cmd_no_error(
        node, cmd,
        message=f"Failed to extract {tarball} at node {node[u'type']} "
        f"host {node[u'host']}, port {node[u'port']}",
        timeout=30, include_reason=True
    )
    logger.console(
        f"Extracting tarball to {con.REMOTE_FW_DIR} on {node[u'type']} "
        f"host {node[u'host']}, port {node[u'port']} done."
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


def setup_node(node, tarball, remote_tarball, results=None, logs=None):
    """Copy a tarball to a node and extract it.

    :param node: A node where the tarball will be copied and extracted.
    :param tarball: Local path of tarball to be copied.
    :param remote_tarball: Remote path of the tarball.
    :param results: A list where to store the result of node setup, optional.
    :param logs: A list where to store anything that should be logged.
    :type node: dict
    :type tarball: str
    :type remote_tarball: str
    :type results: list
    :type logs: list
    :returns: True - success, False - error
    :rtype: bool
    """
    try:
        copy_tarball_to_node(tarball, node)
        extract_tarball_at_node(remote_tarball, node)
        if node[u"type"] == NodeType.TG:
            create_env_directory_at_node(node)
    except Exception:
        # any exception must result in result = False
        # since this runs in a thread and can't be caught anywhere else
        err_msg = f"Node {node[u'type']} host {node[u'host']}, " \
                  f"port {node[u'port']} setup failed."
        logger.console(err_msg)
        if isinstance(logs, list):
            logs.append(f"{err_msg} Exception: {traceback.format_exc()}")
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


def delete_local_tarball(tarball):
    """Delete local tarball to prevent disk pollution.

    :param tarball: Path of local tarball to delete.
    :type tarball: str
    :returns: nothing
    """
    remove(tarball)


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


def cleanup_node(node, results=None, logs=None):
    """Delete a tarball from a node.

    :param node: A node where the tarball will be delete.
    :param results: A list where to store the result of node cleanup, optional.
    :param logs: A list where to store anything that should be logged.
    :type node: dict
    :type results: list
    :type logs: list
    :returns: True - success, False - error
    :rtype: bool
    """
    try:
        delete_framework_dir(node)
    except Exception:
        err_msg = f"Cleanup of node {node[u'type']} host {node[u'host']}, " \
                  f"port {node[u'port']} failed."
        logger.console(err_msg)
        if isinstance(logs, list):
            logs.append(f"{err_msg} Exception: {traceback.format_exc()}")
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

        tarball = pack_framework_dir()
        msg = f"Framework packed to {tarball}"
        logger.console(msg)
        logger.trace(msg)
        remote_tarball = f"{tarball}"

        results = list()
        logs = list()
        threads = list()

        for node in nodes.values():
            args = node, tarball, remote_tarball, results, logs
            thread = threading.Thread(target=setup_node, args=args)
            thread.start()
            threads.append(thread)

        logger.info(
            u"Executing node setups in parallel, waiting for threads to end."
        )

        for thread in threads:
            thread.join()

        logger.info(f"Results: {results}")

        for log in logs:
            logger.trace(log)

        delete_local_tarball(tarball)
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
        logs = list()
        threads = list()

        for node in nodes.values():
            thread = threading.Thread(target=cleanup_node,
                                      args=(node, results, logs))
            thread.start()
            threads.append(thread)

        logger.info(
            u"Executing node cleanups in parallel, waiting for threads to end."
        )

        for thread in threads:
            thread.join()

        logger.info(f"Results: {results}")

        for log in logs:
            logger.trace(log)

        if all(results):
            logger.console(u"All nodes cleaned up.")
        else:
            raise RuntimeError(u"Failed to cleaned up framework.")
