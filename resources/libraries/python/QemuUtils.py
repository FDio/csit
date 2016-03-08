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

"""QEMU utilities library."""

from robot.api import logger
from ssh import SSH
from constants import Constants


class QemuUtils(object):
    """QEMU utilities."""

    @staticmethod
    def build_qemu(node):
        """Build QEMU from sources.

        :param node: Node to build QEMU on.
        :type node: dict
        """
        ssh = SSH()
        ssh.connect(node)

        (ret_code, stdout, stderr) = \
            ssh.exec_command('sudo -Sn bash {0}/{1}/qemu_build.sh'.format(
                Constants.REMOTE_FW_DIR, Constants.RESOURCES_LIB_SH), 1000)
        logger.trace(stdout)
        if 0 != int(ret_code):
            logger.debug('QEMU build failed {0}'.format(stderr))
            raise RuntimeError('QEMU build failed on {0}'.format(node['host']))
