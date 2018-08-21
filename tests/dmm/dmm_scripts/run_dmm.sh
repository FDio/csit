#!/bin/bash

set -x

CUR_DIR=`dirname $(readlink -f $0)`
ROOTDIR=$CUR_DIR/../../../
APP_DIR=${ROOTDIR}/dmm/config/app_test
LIB_PATH=${ROOTDIR}/dmm/release/lib64
DMM_SCRIPT_DIR=$ROOTDIR/dmm/scripts

#proc_name => 0 = server, 1= client
proc_name=$1
ifname=$2

dut1_if1=172.28.128.3
dut2_if1=172.28.128.4

ifconfig -a
lspci -nn
lsmod | grep uio
bash kill_given_proc.sh vs_epoll
bash $CUR_DIR/setup_hugepage.sh

sed -i 's!.*check_hugepage.sh!#skip hugepage check!1' $DMM_SCRIPT_DIR/prep_app_test.sh
sed -i 's!enp0s8!'$ifname'!1' $DMM_SCRIPT_DIR/prep_app_test.sh
bash -x $DMM_SCRIPT_DIR/prep_app_test.sh

cd $APP_DIR
ls -l
#only for kernal stack
if [ ${proc_name} -eq 0 ]; then
sudo LD_LIBRARY_PATH=${LIB_PATH} ./vs_epoll -p 20000 -d ${dut2_if1} -a 10000 -s ${dut1_if1} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
else
sudo LD_LIBRARY_PATH=${LIB_PATH} ./vc_common -p 20000 -d ${dut1_if1} -a 10000 -s ${dut2_if1} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
fi

exit 0