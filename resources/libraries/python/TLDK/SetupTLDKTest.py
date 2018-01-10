# Copyright (c) 2017 Cisco and/or its affiliates.
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
import os

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

from resources.libraries.python.ssh import SSH
from resources.libraries.python.TLDK.TLDKConstants import TLDKConstants as con
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.TLDK.gen_pcap import gen_all_pcap

__all__ = ["SetupTLDKTest"]


def pack_framework_dir():
    """Pack the testing WS into temp file, return its name.
    :returns: file_name
    :rtype: str
    :raises RuntimeError: If pack the testing framework failed.
    """
    # Remove the TLDK and DPDK dir existted.
    os.system("rm -rf tldk")
    os.system("rm -rf dpdk")
    os.system("rm -f dpdk-16.11.1.tar.xz")

    # Get the latest TLDK and dpdk code.
    os.system("git clone https://gerrit.fd.io/r/tldk")
    os.system("wget http://fast.dpdk.org/rel/dpdk-16.11.1.tar.xz")

    # Generate pcap file used to execute test case.
    gen_all_pcap()

    tmpfile = NamedTemporaryFile(suffix=".tgz", prefix="TLDK-testing-")
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
        raise RuntimeError("Could not pack testing framework.")

    return file_name


def copy_tarball_to_node(tarball, node):
    """Copy tarball file from local host to remote node.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :returns: nothing.
    """
    logger.console('Copying tarball to {0}'.format(node['host']))
    ssh = SSH()
    ssh.connect(node)

    ssh.scp(tarball, "/tmp/")


def extract_tarball_at_node(tarball, node):
    """Extract tarball at given node.

    Extracts tarball using tar on given node to specific CSIT location.
    Raise runtime errors when failed.

    :param tarball: Path to tarball to upload.
    :param node: Dictionary created from topology.
    :type tarball: str
    :type node: dict
    :return: nothing
    :raises RuntimeError: If extract tarball failed.
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
        raise RuntimeError('Failed to unpack {0} at node {1}'.format(
            tarball, node['host']))


def create_env_directory_at_node(node):
    """
    Create fresh virtualenv to a directory, install pip requirements.

    :param node: Dictionary created from topology, will only install in the TG.
    :type node: dict
    :returns: nothing
    :raises RuntimeError: If the setup of virtualenv failed.
    """
    logger.console('Extracting virtualenv, installing requirements.txt '
                   'on {0}'.format(node['host']))
    ssh = SSH()
    ssh.connect(node)
    (ret_code, stdout, stderr) = ssh.exec_command(
        'cd {0} && rm -rf env && '
        'virtualenv --system-site-packages --never-download env && '
        '. env/bin/activate && pip install -r requirements.txt'
        .format(con.REMOTE_FW_DIR), timeout=100)
    if ret_code != 0:
        logger.error('Virtualenv creation error: {0}'.format(stdout + stderr))
        raise RuntimeError('Virtualenv setup failed')
    else:
        logger.console('Virtualenv created on {0}'.format(node['host']))

def install_tldk_test(node):
    """Prepare the TLDK test envrionment.
    Raise errors when failed.

    :param node: Dictionary created from topology.
    :type node: dict
    :returns: nothing.
    :raises RuntimeError: If install tldk failed.
    """

    arch = Topology.get_node_arch(node)
    logger.console('Install the TLDK on {0} ({1})'.format(node['host'],
                                                          arch))

    ssh = SSH()
    ssh.connect(node)

    (ret_code, _, stderr) = ssh.exec_command(
        'cd {0}/{1} && ./install_tldk.sh {2}'
        .format(con.REMOTE_FW_DIR, con.TLDK_SCRIPTS, arch), timeout=600)

    if ret_code != 0:
        logger.error('Install the TLDK error: {0}'.format(stderr))
        raise RuntimeError('Install the TLDK failed')
    else:
        logger.console('Install the TLDK on {0} success!'.format(node['host']))

def setup_node(args):
    """Run all set-up methods for a node.

    This method is used as map_async parameter. It receives tuple with all
    parameters as passed to map_async function.

    :param args: All parameters needed to setup one node.
    :type args: tuple
    :returns: True - success, False - error
    :rtype: bool
    :raises RuntimeError: If node setup failed.
    """
    tarball, remote_tarball, node = args

    # if unset, arch defaults to x86_64
    Topology.get_node_arch(node)

    try:
        copy_tarball_to_node(tarball, node)
        extract_tarball_at_node(remote_tarball, node)
        if node['type'] == NodeType.DUT:
            install_tldk_test(node)
        if node['type'] == NodeType.TG:
            create_env_directory_at_node(node)
    except RuntimeError as exc:
        logger.error("Node setup failed, error:'{0}'".format(exc.message))
        return False
    else:
        logger.console('Setup of node {0} done'.format(node['host']))
        return True

def delete_local_tarball(tarball):
    """Delete local tarball to prevent disk pollution.

    :param tarball: Path to tarball to upload.
    :type tarball: str
    :returns: nothing.
    """
    call(split('sh -c "rm {0} > /dev/null 2>&1"'.format(tarball)))


class SetupTLDKTest(object):
    """Setup suite run on topology nodes.

    Many VAT/CLI based tests need the scripts at remote hosts before executing
    them. This class packs the whole testing directory and copies it over
    to all nodes in topology under /tmp/
    """

    @staticmethod
    def setup_tldk_test(nodes):
        """Pack the whole directory and extract in temp on each node."""

        tarball = pack_framework_dir()
        msg = 'Framework packed to {0}'.format(tarball)
        logger.console(msg)
        logger.trace(msg)
        remote_tarball = "/tmp/{0}".format(basename(tarball))

        # Turn off logging since we use multiprocessing.
        log_level = BuiltIn().set_log_level('NONE')
        params = ((tarball, remote_tarball, node) for node in nodes.values())
        pool = Pool(processes=len(nodes))
        result = pool.map_async(setup_node, params)
        pool.close()
        pool.join()

        # Turn on logging.
        BuiltIn().set_log_level(log_level)

        logger.info(
            'Executed node setups in parallel, waiting for processes to end')
        result.wait()

        results = result.get()
        node_setup_success = all(results)
        logger.info('Results: {0}'.format(results))

        logger.trace('Test framework copied to all topology nodes')
        delete_local_tarball(tarball)
        if node_setup_success:
            logger.console('All nodes are ready')
        else:
            logger.console('Failed to setup dpdk on all the nodes')
