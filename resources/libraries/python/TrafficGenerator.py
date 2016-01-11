# Copyright (c) 2015 Cisco and/or its affiliates.
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
from ssh import SSH
from robot.api import logger

__all__ = ['TrafficGenerator']

class TrafficGenerator(object):

    def __init__(self):
        self._result = None
        self._loss = None
        self._sent = None
        self._received = None


    def send_traffic_on(self, node, tx_port, rx_port, duration, rate,
            framesize):
        ssh = SSH()
        ssh.connect(node)

        (ret, stdout, stderr) = ssh.exec_command(
                "sh -c 'cd MoonGen && sudo -S build/MoonGen "
                "rfc2544/benchmarks/vpp-frameloss.lua --txport 0 --rxport 1 "
                "--duration {0} --rate {1} --framesize {2}'".format(
                    duration, rate, framesize),
                timeout=int(duration)+60)

        logger.trace(ret)
        logger.trace(stdout)
        logger.trace(stderr)

        for line in stdout.splitlines():
            pass

        self._result = line
        logger.info('TrafficGen result: {0}'.format(self._result))

        self._loss = self._result.split(', ')[3].split('=')[1]

        return self._result

    def no_traffic_loss_occured(self):
        if self._loss is None:
            raise Exception('The traffic generation has not been issued')
        if self._loss != '0':
            raise Exception('Traffic loss occured: {0}'.format(self._loss))
