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

"""This module exists to provide setup utilities for the framework on topology
nodes. All tasks required to be run before the actual tests are started is
supposed to end up here.
"""

from os import environ, remove
from os.path import basename, join
from tempfile import NamedTemporaryFile
import threading

from robot.api import logger

from resources.libraries.python.Constants import Constants as con
from resources.libraries.python.ssh import exec_cmd_no_error, scp_node
from resources.libraries.python.LocalExecution import run
from resources.libraries.python.topology import NodeType

__all__ = ["SetupFramework"]


def pack_framework_dir(prefix):
    """Pack the testing WS into temp file, return its name.

    :param prefix: a prefix to use for the tarball
    :type prefix: str
    :returns: Tarball file name.
    :rtype: str
    :raises Exception: When failed to pack testing framework.
    """
    try:
        directory = "{0}".format(environ["TMPDIR"])
    except KeyError:
        directory = None

    tmpfile = NamedTemporaryFile(suffix=".tgz", prefix=prefix, dir=directory)
    file_name = tmpfile.name
    tmpfile.close()

    run(["tar", "--sparse", "--exclude-vcs", "--exclude=output*.xml",
         "--exclude=./tmp", "-zcf", file_name, "."],
        msg="Could not pack testing framework")

    msg = 'Framework packed to {0}'.format(file_name)
    logger.console(msg)
    logger.trace(msg)
    return file_name


def copy_tarball_to_node(tarball, remote_tarball, node):
    """Copy tarball file from local host to remote node.

    :param tarball: Path to tarball to upload.
    :param remote_tarball: Path to tarball on remote node.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type remote_tarball: str
    :type node: dict
    :returns: nothing
    """
    host = node['host']
    logger.console('Copying tarball to {0} starts.'.format(host))
    scp_node(node, tarball, remote_tarball)
    logger.console('Copying tarball to {0} done.'.format(host))


def extract_tarball_at_node(tarball, directory, node):
    """Extract tarball at given node.

    Extracts tarball using tar on given node to specific CSIT location.

    :param tarball: Path to tarball to upload.
    :param directory: Path to framework directory
    :param node: Dictionary created from topology.
    :type tarball: str
    :type directory: str
    :type node: dict
    :returns: nothing
    :raises RuntimeError: When failed to unpack tarball.
    """
    host = node['host']
    logger.console('Extracting tarball to {0} on {1} starts.'
                   .format(directory, host))
    exec_cmd_no_error(
        node, "sudo rm -rf {1}; mkdir {1}; tar -zxf {0} -C {1};"
        " rm -f {0}".format(tarball, directory),
        message='Failed to extract {0} at node {1}'.format(tarball, host),
        timeout=30, include_reason=True)
    logger.console('Extracting tarball to {0} on {1} done.'
                   .format(directory, host))


def create_env_directory_at_node(directory, node):
    """Create fresh virtualenv to a directory, install pip requirements.

    :param node: Node to create virtualenv on.
    :param directory: directory on node under which to create virtualenv
    :type node: dict
    :type directory: str
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
        .format(directory), timeout=100, include_reason=True,
        message="Failed install at node {0}".format(host))
    logger.console('Virtualenv setup on {0} done.'.format(host))


def run_install_command_at_node(install_cmd, directory, node, timeout=600):
    """Run install command at given node.

    Executes install_cmd at specific CSIT framework location.

    :param install_cmd: Command to execute on node
    :param directory: Path to framework directory
    :param node: Dictionary created from topology
    :param timeout: time to execute command in seconds
    :type install_cmd: str
    :type directory: str
    :type node: dict
    :type timeout: int
    :raises RuntimeError: When failed to unpack tarball.
    """
    host = node['host']
    logger.console('Execute install command in {0} on {1} starts.'
                   .format(directory, host))
    exec_cmd_no_error(
        node, "cd {1} && {0}".format(install_cmd, directory),
        message='Failed to execute install command at node {0}'.format(host),
        timeout=timeout, include_reason=True)
    logger.console('Executing install command on {0} done.'.format(host))


def delete_framework_dir(directory, node):
    """Delete framework directory in /tmp/ on given node.

    :param node: Node to delete framework directory on.
    :param directory: Path to framework directory
    :type node: dict
    :type directory: str
    """
    host = node['host']
    logger.console(
        'Deleting framework directory on {0} starts.'.format(host))
    exec_cmd_no_error(
        node, 'sudo rm -rf {0}'.format(directory),
        message="Framework delete failed at node {0}".format(host),
        timeout=100, include_reason=True)
    logger.console(
        'Deleting framework directory on {0} done.'.format(host))


class _NodeExecutor(object):
    """Base for test maintenance operations remote hosts.

    The maintenance operations are executed on some testing topology nodes,
    with most operations executed in parallel on all applicable hosts.

    """

    def __init__(self):
        self.results = dict()

    def _perform_node(self, node):
        """Perform the given task for given node.

        The actual maintenance operation shall be implemented in a subclass.
        The result will be placed in the results dict.

        :param node: a node structure
        :type node: dict
        """
        raise NotImplementedError()

    def _thread_run(self, key, node):
        """Run the maintenance operations in a thread.

        The result of will be placed in the results dict.

        :param key: a key given to the node by the caller
        :param node: a node structure
        :type node: dict

        """
        try:
            result = self._perform_node(node)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error('Operation {name} failed for {key}: {exc}'.format(
                name=type(self).__name__, key=key, exc=exc))
            result = exc
        # this should be locked
        self.results[key] = result

    def perform(self, nodes):
        """Perform the given task on all nodes.

        :param nodes: The set of nodes on which to apply maintenance
        :type nodes: dict
        """
        threads = [threading.Thread(target=self._thread_run, args=(key, node))
                   for key, node in nodes.items()]

        logger.info(
            'Executing node setups in parallel, waiting for threads to end')
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def succeeded(self):
        """Return whether all operations returned a successful result

        A result is successful if it is a true value and not an Exception.
        :rtype: bool
        """
        for result in self.results.values():
            if not result or isinstance(result, Exception):
                return False
        return True


class SetupFramework(_NodeExecutor):
    """Setup suite run on topology nodes.

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    remote_fw_dir = con.REMOTE_FW_DIR
    remote_tmp_dir = "/tmp/"

    def __init__(self):
        super(SetupFramework, self).__init__()
        self.local_tarball_name = None
        self.remote_tarball_name = None

    def prepare(self):
        """Prepare for framework setup.

        Base method creates a tarball of current working directory, and stores
        its name in the local_tarball_name attribute.
        The remote_tarball_name attribute is used as the target name on nodes.
        """
        self.local_tarball_name = pack_framework_dir(type(self).__name__)
        remote = join(self.remote_tmp_dir, basename(self.local_tarball_name))
        self.remote_tarball_name = remote

    def cleanup(self):
        """Clean up any artifacts from prepare"""
        remove(self.local_tarball_name)

    def _needs_tarball(self, node):
        """Return whether node should have tarball prepared in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: The tarball should be recreated on the node
        :rtype: bool
        """
        # shutup pylint about not using self or node in base implementation
        _ = self
        _ = node
        return True

    def _needs_virtualenv(self, node):
        """Return whether node should have virtualenv prepared in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: A virtual env should be recreated on the node
        :rtype: bool
        """
        _ = self
        return node['type'] == NodeType.TG

    def _needs_install_command(self, node):
        """Return whether node should have a command executed in remote_fw_dir.

        :param node: Topology node being set up
        :type node: Topology node
        :returns: A command that should be executed on the node
        :rtype: str
        """
        _ = self
        _ = node
        return None

    def _perform_node(self, node):
        """Perform the setup for given node.

        The actual maintenance operation shall be implemented in a subclass.
        The result will be placed in the results dict.

        :param node: a node structure
        :type node: dict
        """
        if self._needs_tarball(node):
            copy_tarball_to_node(self.local_tarball_name,
                                 self.remote_tarball_name,
                                 node)
            extract_tarball_at_node(self.remote_tarball_name,
                                    self.remote_fw_dir,
                                    node)
            if self._needs_virtualenv(node):
                create_env_directory_at_node(self.remote_fw_dir, node)
            install_cmd = self._needs_install_command(node)
            if install_cmd:
                run_install_command_at_node(install_cmd,
                                            self.remote_fw_dir,
                                            node)
            logger.console('Setup of node {host} done.'.format(host=host))
            logger.info('Setup of {node_type} node {host} done.'
                        .format(node_type=node['type'], host=host))
        return True

    @classmethod
    def setup_framework(cls, nodes):
        """Pack the whole directory and extract in temp on each node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :raises RuntimeError: If setup framework failed.
        """
        instance = cls()
        instance.prepare()
        try:
            instance.perform(nodes)
        finally:
            instance.cleanup()

        if instance.succeeded():
            logger.console('All nodes are ready.')
        else:
            raise RuntimeError('Failed to setup framework.')


class CleanupFramework(_NodeExecutor):
    """Clean up suite run on topology nodes."""

    remote_fw_dir = con.REMOTE_FW_DIR

    def _perform_node(self, node):
        """Perform the setup for given node.

        The actual maintenance operation shall be implemented in a subclass.
        The result will be placed in the results dict.

        :param node: a node structure
        :type node: dict
        """
        delete_framework_dir(self.remote_fw_dir, node)

    @classmethod
    def cleanup_framework(cls, nodes):
        """Perform cleanup on each node.

        :param nodes: Topology nodes.
        :type nodes: dict
        :raises RuntimeError: If cleanup framework failed.
        """
        instance = cls()
        instance.perform(nodes)

        if instance.succeeded():
            logger.console('All nodes cleaned up.')
        else:
            raise RuntimeError('Failed to clean up framework.')
