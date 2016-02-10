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

echo
echo Restart VPP
echo
sudo -S service vpp restart

echo
echo List vpp packages
echo
dpkg -l vpp\*

echo
echo List /proc/meminfo
echo
cat /proc/meminfo

echo
echo See vpp process
echo
ps aux | grep vpp

echo
echo See free memory
echo
free -m


echo QQQQ
sudo dmidecode


sudo vpp_api_test <<< "exec trace add dpdk-input 100"
