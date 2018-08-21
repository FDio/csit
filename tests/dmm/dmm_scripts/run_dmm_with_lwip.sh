#!/bin/bash

set -x
CUR_DIR=`dirname $(readlink -f $0)`
ROOTDIR=$CUR_DIR/../../../
APP_DIR=${ROOTDIR}/dmm/stacks/lwip_stack/app_test/
LIB_PATH=${APP_DIR}/../release/lib64/
VAG_DIR=${ROOTDIR}/dmm/stacks/lwip_stack/vagrant
#proc_name => 0 = server, 1= client
proc_name=$1
ifname=$2
dut1_if1=172.28.128.3
dut2_if1=172.28.128.4

# Try to kill the vs_epoll
bash $CUR_DIR/kill_given_proc.sh vs_epoll
cat /proc/meminfo

sed -i 's!.*check_hugepage.sh!#skip hugepage check!1' $VAG_DIR/start_nstackMain.sh
sed -i 's!ifname=.*!ifname='$ifname'!1' $VAG_DIR/start_nstackMain.sh
sudo  LD_LIBRARY_PATH=${LIB_PATH} bash $VAG_DIR/start_nstackMain.sh  || exit 1

sleep 5

#after nstackmain
echo "after nstackmain"
ip addr
lspci -nn
lsmod | grep uio
cat /proc/meminfo | grep Huge
/tmp/dpdk/dpdk-18.02/usertools/dpdk-devbind.py --status

cd ${APP_DIR}

if [ ${proc_name} -eq 0 ]; then
sudo NSTACK_LOG_ON=DBG LD_LIBRARY_PATH=${LIB_PATH} ./vs_epoll -p 20000 -d ${dut2_if1} -a 10000 -s ${dut1_if1} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
else
sudo NSTACK_LOG_ON=DBG LD_LIBRARY_PATH=${LIB_PATH} ./vc_common -p 20000 -d ${dut1_if1} -a 10000 -s ${dut2_if1} -l 200 -t 50 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
fi

cd $APP_DIR/../release/
sudo ./stop_nstack.sh
exit 0
