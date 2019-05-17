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

from shlex import split
from subprocess import Popen, PIPE, call
from multiprocessing import Pool
from tempfile import NamedTemporaryFile
from os.path import basename
from os import environ

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.Constants import Constants as con
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

    proc = Popen(
        split("tar --sparse --exclude-vcs --exclude=output*.xml "
              "--exclude=./tmp -zcf {0} ."
              .format(file_name)), stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = proc.communicate()

    logger.debug(stdout)
    logger.debug(stderr)

    return_code = proc.wait()
    if return_code != 0:
        raise RuntimeError("Could not pack testing framework.")

    return file_name


def copy_tarball_to_node(tarball, node):
    """Copy tarball file from local host to remote node.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :returns: nothing
    """
    logger.console('Copying tarball to {0}'.format(node['host']))
    ssh = SSH()
    ssh.connect(node)

    ssh.scp(tarball, "/tmp/")
    logger.console('Copying tarball to {0} done'.format(node['host']))


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
    logger.console('Extracting tarball to {0} on {1}'
                   .format(con.REMOTE_FW_DIR, node['host']))
    ssh = SSH()
    ssh.connect(node)
    (ret_code, _, _) = ssh.exec_command(
        'sudo rm -rf {1}; mkdir {1} ; tar -zxf {0} -C {1}; rm -f {0}'
        .format(tarball, con.REMOTE_FW_DIR), timeout=30)
    if ret_code != 0:
        raise RuntimeError('Failed to extract {0} at node {1}'
                           .format(tarball, node['host']))
    logger.console('Extracting tarball to {0} on {1} done'
                   .format(con.REMOTE_FW_DIR, node['host']))


def create_env_directory_at_node(node):
    """Create fresh virtualenv to a directory, install pip requirements.

    :param node: Node to create virtualenv on.
    :type node: dict
    :returns: nothing
    :raises RuntimeError: When failed to setup virtualenv.
    """
    logger.console('Virtualenv setup including requirements.txt on {0}'
                   .format(node['host']))
    ssh = SSH()
    ssh.connect(node)
    (ret_code, _, _) = ssh.exec_command(
        'cd {0} && rm -rf env && '
        'virtualenv --system-site-packages --never-download env && '
        '. env/bin/activate && '
        'pip install -r requirements.txt'
        .format(con.REMOTE_FW_DIR), timeout=100)
    if ret_code != 0:
        raise RuntimeError('Virtualenv setup including requirements.txt on {0}'
                           .format(node['host']))

    logger.console('Virtualenv on {0} created'.format(node['host']))


def setup_node(args):
    """Run all set-up methods for a node.

    This method is used as map_async parameter. It receives tuple with all
    parameters as passed to map_async function.

    :param args: All parameters needed to setup one node.
    :type args: tuple
    :returns: True - success, False - error
    :rtype: bool
    """
    tarball, remote_tarball, node = args
    try:
        if node['type'] != NodeType.BUT:
            copy_tarball_to_node(tarball, node)
            extract_tarball_at_node(remote_tarball, node)
            if node['type'] == NodeType.TG:
                create_env_directory_at_node(node)
    except RuntimeError as exc:
        logger.error("Node {0} setup failed, error:'{1}'"
                     .format(node['host'], exc.message))
        return False
    else:
        logger.console('Setup of node {0} done'.format(node['host']))
        return True


def delete_local_tarball(tarball):
    """Delete local tarball to prevent disk pollution.

    :param tarball: Path to tarball to upload.
    :type tarball: str
    :returns: nothing
    """
    call(split('sh -c "rm {0} > /dev/null 2>&1"'.format(tarball)))


def delete_framework_dir(node):
    """Delete framework directory in /tmp/ on given node.

    :param node: Node to delete framework directory on.
    :type node: dict
    """
    logger.console('Deleting framework directory on {0}'
                   .format(node['host']))
    ssh = SSH()
    ssh.connect(node)
    (ret_code, _, _) = ssh.exec_command(
        'sudo rm -rf {0}'
        .format(con.REMOTE_FW_DIR), timeout=100)
    if ret_code != 0:
        raise RuntimeError('Deleting framework directory on {0} failed'
                           .format(node))


def cleanup_node(node):
    """Run all clean-up methods for a node.

    This method is used as map_async parameter. It receives tuple with all
    parameters as passed to map_async function.

    :param node: Node to do cleanup on.
    :type node: dict
    :returns: True - success, False - error
    :rtype: bool
    """
    try:
        if node['type'] != NodeType.BUT:
            delete_framework_dir(node)
    except RuntimeError:
        logger.error("Cleanup of node {0} failed".format(node['host']))
        return False
    else:
        logger.console('Cleanup of node {0} done'.format(node['host']))
        return True


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

        # Turn off logging since we use multiprocessing
        log_level = BuiltIn().set_log_level('NONE')
        params = ((tarball, remote_tarball, node) for node in nodes.values())
        pool = Pool(processes=len(nodes))
        result = pool.map_async(setup_node, params)
        pool.close()
        pool.join()

        # Turn on logging
        BuiltIn().set_log_level(log_level)

        logger.info(
            'Executing node setups in parallel, waiting for processes to end')
        result.wait()

        results = result.get()
        node_success = all(results)
        logger.info('Results: {0}'.format(results))

        delete_local_tarball(tarball)
        if node_success:
            logger.console('All nodes are ready')
        else:
            raise RuntimeError('Failed to setup framework')


class CleanupFramework(object):
    """Clean up suite run on topology nodes."""

    @staticmethod
    def cleanup_framework(nodes):
        """Perform cleaning on each node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :raises RuntimeError: If cleanup framework failed.
        """
        # Turn off logging since we use multiprocessing
        log_level = BuiltIn().set_log_level('NONE')
        params = (node for node in nodes.values())
        pool = Pool(processes=len(nodes))
        result = pool.map_async(cleanup_node, params)
        pool.close()
        pool.join()

        # Turn on logging
        BuiltIn().set_log_level(log_level)

        logger.info(
            'Executing node cleanups in parallel, waiting for processes to end')
        result.wait()

        results = result.get()
        node_success = all(results)
        logger.info('Results: {0}'.format(results))

        if node_success:
            logger.console('All nodes cleaned up')
        else:
            raise RuntimeError('Failed to cleaned up framework')
