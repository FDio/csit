#!/bin/bash

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
echo See vpe process
echo
ps aux | grep vpe

echo
echo See free memory
echo
free -m

