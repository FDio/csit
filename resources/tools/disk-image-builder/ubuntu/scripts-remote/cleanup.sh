#!/bin/sh -e

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

echo "********** CLEANING UP **********"

# Clean up host keys only if we're using cloud-init
# (which will generate new keys upon next boot). This
# currently applies to Qemu build only.

if dpkg -s cloud-init > /dev/null 2>&1
then
  rm -f /etc/ssh/ssh_host_*
fi

# Remove root's password, old resolv.conf and DHCP lease
passwd -d root
passwd -l root
rm -f /etc/resolv.conf
pkill dhclient
rm -f /var/lib/dhcp/*leases

echo "********** SCHEDULING SHUTDOWN IN 1 MINUTE **********"
sync
shutdown -h +1
exit
