# Copyright (c) 2018 Cisco and/or its affiliates.
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

import datetime
from os import environ, remove
from os.path import basename
from shlex import split
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile
import threading

from robot.api import logger

from resources.libraries.python.Constants import Constants as con
from resources.libraries.python.ssh import (
    exec_cmd, exec_cmd_no_error, scp_node)
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.topology import NodeType

__all__ = ["SetupFramework"]


def pack_framework_dir():
    """Pack the testing WS into temp file, return its name.

    :returns: Tarball file name.
    :rtype: str
    :raises Exception: When failed to pack testing framework.
    """

    try:
        directory = environ["TMPDIR"]
    except KeyError:
        directory = None

    if directory is not None:
        tmpfile = NamedTemporaryFile(suffix=".tgz", prefix="csit-testing-",
                                     dir="{0}".format(directory))
    else:
        tmpfile = NamedTemporaryFile(suffix=".tgz", prefix="csit-testing-")
    file_name = tmpfile.name
    tmpfile.close()

    run(["tar", "--sparse", "--exclude-vcs", "--exclude=output*.xml",
         "--exclude=./tmp", "-zcf", file_name, "."],
        check=True, msg="Could not pack testing framework")

    return file_name


def copy_tarball_to_node(tarball, node):
    """Copy tarball file from local host to remote node.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :returns: nothing
    """
    host = node['host']
    logger.console('Copying tarball to {0} starts.'.format(host))
    scp_node(node, tarball, "/tmp/")
    logger.console('Copying tarball to {0} done.'.format(host))


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
    host = node['host']
    logger.console('Extracting tarball to {0} on {1} starts.'
                   .format(con.REMOTE_FW_DIR, host))
    # TODO: Make ssh.exec_cmd interface similar to LocalExecution.run one.
    # In this case we want both automatic (cmd, rc, output) and call-site
    # (failed to extract) information in exception.
    ret_code, _, _ = exec_cmd(
        node, "sudo rm -rf {1}; mkdir {1}; tar -zxf {0} -C {1};"
        " rm -f {0}".format(tarball, con.REMOTE_FW_DIR), timeout=30)
    if ret_code != 0:
        raise RuntimeError('Failed to extract {0} at node {1}'
                           .format(tarball, host))
    logger.console('Extracting tarball to {0} on {1} done.'
                   .format(con.REMOTE_FW_DIR, host))


def create_env_directory_at_node(node):
    """Create fresh virtualenv to a directory, install pip requirements.

    :param node: Node to create virtualenv on.
    :type node: dict
    :returns: nothing
    :raises RuntimeError: When failed to setup virtualenv.
    """
    host = node['host']
    logger.console('Virtualenv setup including requirements.txt on {0} starts.'
                   .format(host))
    exec_cmd_no_error(
        node, 'cd {0} && rm -rf env'
        ' && virtualenv --system-site-packages --never-download env'
        ' && source env/bin/activate && pip install -r requirements.txt'
        .format(con.REMOTE_FW_DIR), timeout=100)
    logger.console('Virtualenv setup on {0} done.'.format(host))


def setup_node(node, tarball, remote_tarball, results=None):
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
    host = node['host']
    try:
        copy_tarball_to_node(tarball, node)
        extract_tarball_at_node(remote_tarball, node)
        if node['type'] == NodeType.TG:
            create_env_directory_at_node(node)
    except RuntimeError as exc:
        logger.console("Node {node} setup failed, error: {err!r}".format(
            node=host, err=exc))
        result = False
    else:
        logger.console('Setup of node {0} done.'.format(host))
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
    host = node['host']
    logger.console('Deleting framework directory on {0} starts.'
                   .format(host))
    exec_cmd_no_error('sudo rm -rf {0}'.format(con.REMOTE_FW_DIR),
                          timeout=100)
    logger.console('Deleting framework directory on {0} done.'
                   .format(host))


def cleanup_node(node, results=None):
    """Delete a tarball from a node.

    :param node: A node where the tarball will be delete.
    :param results: A list where to store the result of node cleanup, optional.
    :type node: dict
    :type results: list
    :returns: True - success, False - error
    :rtype: bool
    """
    host = node['host']
    try:
        delete_framework_dir(node)
    except RuntimeError:
        logger.error("Cleanup of node {0} failed.".format(host))
        result = False
    else:
        logger.console('Cleanup of node {0} done.'.format(host))
        result = True

    if isinstance(results, list):
        results.append(result)
    return result


class SetupFramework(object):
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
        msg = 'Framework packed to {0}'.format(tarball)
        logger.console(msg)
        logger.trace(msg)
        remote_tarball = "/tmp/{0}".format(basename(tarball))

        results = []
        threads = []

        for node in nodes.values():
            args = node, tarball, remote_tarball, results
            thread = threading.Thread(target=setup_node, args=args)
            thread.start()
            threads.append(thread)

        logger.info(
            'Executing node setups in parallel, waiting for threads to end')

        for thread in threads:
            thread.join()

        logger.info('Results: {0}'.format(results))

        delete_local_tarball(tarball)
        if all(results):
            logger.console('All nodes are ready.')
        else:
            raise RuntimeError('Failed to setup framework.')


class CleanupFramework(object):
    """Clean up suite run on topology nodes."""

    @staticmethod
    def cleanup_framework(nodes):
        """Perform cleanup on each node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :raises RuntimeError: If cleanup framework failed.
        """

        results = []
        threads = []

        for node in nodes.values():
            thread = threading.Thread(target=cleanup_node,
                                      args=(node, results))
            thread.start()
            threads.append(thread)

        logger.info(
            'Executing node cleanups in parallel, waiting for threads to end.')

        for thread in threads:
            thread.join()

        logger.info('Results: {0}'.format(results))

        if all(results):
            logger.console('All nodes cleaned up.')
        else:
            raise RuntimeError('Failed to cleaned up framework.')
