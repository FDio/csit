#!/bin/bash
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
set -x

USERNAME=csit

function ssh_do_duts {
    ssh ${USERNAME}@192.168.255.101 ${@} || exit
    ssh ${USERNAME}@192.168.255.102 ${@} || exit
}

rsync -avz ${@} ${USERNAME}@192.168.255.101:/tmp/ || exit
rsync -avz ${@} ${USERNAME}@192.168.255.102:/tmp/ || exit

ssh_do_duts "sudo apt-get -y purge 'vpp.*' ; exit 0"
ssh_do_duts "sudo dpkg -i /tmp/vpp*.deb"
