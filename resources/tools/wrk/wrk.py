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

"""wrk implementation into CSIT framework.
"""


from robot.api import logger

from resources.libraries.python.ssh import SSH
from resources.libraries.python.topology import NodeType
from resources.libraries.python.constants import Constants
from wrk_traffic_profile_parser import WrkTrafficProfile
from wrk_errors import WrkError


def install_wrk(tg_node):
    """Install wrk on the TG node.

    :param tg_node: Traffic generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node or if the
    installation fails.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    ssh = SSH()
    ssh.connect(tg_node)

    ret, stdout, stderr = ssh.exec_command(
        "sudo -E "
        "sh -c '{0}/resources/tools/wrk/wrk_utils.sh install {1} force'".
        format(Constants.REMOTE_FW_DIR, Constants.WRK_PATH), timeout=1800)
    if int(ret) != 0:
        logger.error('wrk installation failed: {0}'.format(stdout + stderr))
        raise RuntimeError('Installation of wrk on TG node failed.')
    else:
        logger.debug(stdout)


def destroy_wrk(tg_node):
    """Destroy wrk on the TG node.

    :param tg_node: Traffic generator node.
    :type tg_node: dict
    :raises: RuntimeError if the given node is not a TG node.
    """

    if tg_node['type'] != NodeType.TG:
        raise RuntimeError('Node type is not a TG.')

    ssh = SSH()
    ssh.connect(tg_node)

    ret, stdout, stderr = ssh.exec_command(
        "sudo -E "
        "sh -c '{0}/resources/tools/wrk/wrk_utils.sh destroy {1}'".
        format(Constants.REMOTE_FW_DIR, Constants.WRK_PATH), timeout=1800)
    if int(ret) != 0:
        logger.error('wrk removal failed: {0}'.format(stdout + stderr))
        raise RuntimeError('Removal of wrk from the TG node failed.')
    else:
        logger.debug(stdout)


def run_wrk():
    """

    :return:
    """
    pass


def get_stats():
    """

    :return:
    """
    pass


# For testing purpose, will be removed
def main():
    try:
        profile = WrkTrafficProfile("/home/tibor/ws/vpp/git/csit/resources/"
                                    "traffic_profiles/wrk/example.yaml")
    except WrkError as err:
        print(err)


if __name__ == '__main__':
    main()
