# Copyright (c) 2016 Cisco and/or its affiliates.
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

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants as con
from resources.libraries.python.topology import NodeType

__all__ = ["SetupFramework"]


def pack_framework_dir():
    """Pack the testing WS into temp file, return its name."""

    tmpfile = NamedTemporaryFile(suffix=".tgz", prefix="openvpp-testing-")
    file_name = tmpfile.name
    tmpfile.close()

    proc = Popen(
        split("tar --exclude-vcs -zcf {0} .".format(file_name)),
        stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = proc.communicate()

    logger.debug(stdout)
    logger.debug(stderr)

    return_code = proc.wait()
    if return_code != 0:
        raise Exception("Could not pack testing framework.")

    return file_name


def copy_tarball_to_node(tarball, node):
    """Copy tarball file from local host to remote node.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :return: nothing
    """
    logger.console('Copying tarball to {0}'.format(node['host']))
    ssh = SSH()
    ssh.connect(node)

    ssh.scp(tarball, "/tmp/")


def extract_tarball_at_node(tarball, node):
    """Extract tarball at given node.

    Extracts tarball using tar on given node to specific CSIT location.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :return: nothing
    """
    logger.console('Extracting tarball to {0} on {1}'.format(
        con.REMOTE_FW_DIR, node['host']))
    ssh = SSH()
    ssh.connect(node)

    cmd = 'sudo rm -rf {1}; mkdir {1} ; tar -zxf {0} -C {1}; ' \
        'rm -f {0}'.format(tarball, con.REMOTE_FW_DIR)
    (ret_code, _, stderr) = ssh.exec_command(cmd, timeout=30)
    if ret_code != 0:
        logger.error('Unpack error: {0}'.format(stderr))
        raise Exception('Failed to unpack {0} at node {1}'.format(
            tarball, node['host']))


def create_env_directory_at_node(node):
    """Create fresh virtualenv to a directory, install pip requirements."""
    logger.console('Extracting virtualenv, installing requirements.txt '
                   'on {0}'.format(node['host']))
    ssh = SSH()
    ssh.connect(node)
    (ret_code, stdout, stderr) = ssh.exec_command(
        'cd {0} && '
        'rm -rf env && '
        'virtualenv --system-site-packages env && '
        '. env/bin/activate && '
        'pip install -r requirements.txt'
        .format(con.REMOTE_FW_DIR), timeout=100)
    if ret_code != 0:
        logger.error('Virtualenv creation error: {0}'.format(stdout + stderr))
        raise Exception('Virtualenv setup failed')
    else:
        logger.console('Virtualenv created on {0}'.format(node['host']))


def setup_node(args):
    """Run all set-up methods for a node.

    This method is used as map_async parameter. It receives tuple with all
    parameters as passed to map_async function.

    :param args: All parameters needed to setup one node.
    :type args: tuple
    :return: nothing
    """
    tarball, remote_tarball, node = args
    copy_tarball_to_node(tarball, node)
    extract_tarball_at_node(remote_tarball, node)
    if node['type'] == NodeType.TG:
        create_env_directory_at_node(node)
    logger.console('Setup of node {0} done'.format(node['host']))


def delete_local_tarball(tarball):
    """Delete local tarball to prevent disk pollution.

    :param tarball: Path to tarball to upload.
    :type tarball: str
    :return: nothing
    """
    call(split('sh -c "rm {0} > /dev/null 2>&1"'.format(tarball)))


class SetupFramework(object):  # pylint: disable=too-few-public-methods
    """Setup suite run on topology nodes.

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    @staticmethod
    def setup_framework(nodes):
        """Pack the whole directory and extract in temp on each node."""

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

        logger.info(
            'Executed node setups in parallel, waiting for processes to end')
        result.wait()

        logger.info('Results: {0}'.format(result.get()))

        # Turn on logging
        BuiltIn().set_log_level(log_level)
        logger.trace('Test framework copied to all topology nodes')
        delete_local_tarball(tarball)
        logger.console('All nodes are ready')
