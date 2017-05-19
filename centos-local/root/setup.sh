#!/bin/bash


VPP_LOGFILE=/var/log/vpp_startup_script.log
VPP_LOGFILE_1=/var/log/vpp_startup_script_1.log
VPP_LOGFILE_2=/var/log/vpp_startup_script_2.log


#
# Save off logfiles
#
cp -f ${VPP_LOGFILE_1} ${VPP_LOGFILE_2}
cp -f ${VPP_LOGFILE} ${VPP_LOGFILE_1}

DATE=`date`
echo "Starting the vpp on $DATE: "  > ${VPP_LOGFILE}

#
# Disable selinux
#
echo >> ${VPP_LOGFILE}
echo "Disable selinux" >> ${VPP_LOGFILE}
setenforce 0


#
# Fix hugepage mount points
#
echo >> ${VPP_LOGFILE}
echo "Fix Hugepage Mount" >> ${VPP_LOGFILE}
mount | grep -q "hugepages"
if [ $? -eq 0 ] ; then
   echo "  Fixing huge pages mount point - umount /dev/hugepages" >> ${VPP_LOGFILE}
   umount /dev/hugepages
else
   echo "  /dev/hugepages already not mounted" >> ${VPP_LOGFILE}
fi

mount | grep -q "/mnt/huge"
if [ $? -ne 0 ] ; then
   echo "  Adding huge pages mount point - mount -t hugetlbfs nodev /mnt/huge" >> ${VPP_LOGFILE}
   mkdir /mnt/huge -p
   mount -t hugetlbfs nodev /mnt/huge
fi

# Test
mount | grep -q "hugepages"
if [ $? -eq 0 ] ; then
   echo "/dev/hugepages still mounted" >> ${VPP_LOGFILE}
fi
mount | grep -q "/mnt/huge"
if [ $? -ne 0 ] ; then
   echo " /mnt/huge still NOT mounted" >> ${VPP_LOGFILE}
fi

#
# Mark 4 vhost IFs down so vpp can find them.
#
ip link set dev eth1 down
echo "ip link set dev eth1 down" >>  ${VPP_LOGFILE}

ip link set dev eth2 down
echo "ip link set dev eth2 down" >>  ${VPP_LOGFILE}

ip link set dev eth3 down
echo "ip link set dev eth3 down" >>  ${VPP_LOGFILE}

ip link set dev eth4 down
echo "ip link set dev eth4 down" >>  ${VPP_LOGFILE}
