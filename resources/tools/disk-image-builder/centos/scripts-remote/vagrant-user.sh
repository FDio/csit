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

echo "********** Adding Vagrant user ***********"
# Remove cloud-init as this will slow down the Vagrant boot
export DEBIAN_FRONTEND=noninteractive
apt-get purge -y cloud-init

# Add Vagrant user
useradd -c "Vagrant User" -m -s /bin/bash vagrant

mkdir /home/vagrant/.ssh
cat - > /home/vagrant/.ssh/authorized_keys <<_EOF
ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA6NF8iallvQVp22WDkTkyrtvp9eWW6A8YVr+kz4TjGYe7gHzIw+niNltGEFHzD8+v1I2YJ6oXevct1YeS0o9HZyN1Q9qgCgzUFtdOKLv6IedplqoPkcmF0aYet2PkEDo3MlTBckFXPITAMzF8dJSIFo9D8HfdOV0IAdx4O7PtixWKn5y2hMNG0zQPyUecp4pzC6kivAIhyfHilFR61RGL+GPXQ2MWZWFYbAGjyiYJnAmCP3NOTd0jMZEnDkbUvxhMmBYSdETk1rRgm+R4LOzFUGaHqHDLKLX+FIPKcF96hrucXzcWyLbIbEgE98OHlnVYCzRdK8jlqm8tehUc9c9WhQ== vagrant insecure public key
_EOF

chown -R vagrant.vagrant /home/vagrant/.ssh
chmod 700 /home/vagrant/.ssh

mkdir -p /etc/sudoers.d
cat - > /etc/sudoers.d/vagrant <<_EOF
vagrant ALL=(root) NOPASSWD:ALL
_EOF
chmod 440 /etc/sudoers.d/vagrant

echo "********** Rebooting with new kernel **********"
reboot
sleep 60
