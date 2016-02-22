#!/bin/bash

set -x

#sudo apt-get -y install libpython2.7-dev

#VIRL_VMS="10.30.51.53,10.30.51.51,10.30.51.52"
#IFS=',' read -ra ADDR <<< "${VIRL_VMS}"
#

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh -i priv_key -o StrictHostKeyChecking=no $@
}

#for addr in "${ADDR[@]}"; do
#    echo
#    echo ${addr}
#    echo
#
#    ssh_do cisco@${addr} hostname || true
#    ssh_do cisco@${addr} "ifconfig -a" || true
#    ssh_do cisco@${addr} "lspci -Dnn | grep 0200" || true
#    ssh_do cisco@${addr} "free -m" || true
#    ssh_do cisco@${addr} "cat /proc/meminfo" || true
#    ssh_do cisco@${addr} "dpkg -l vpp\*" || true
#    ssh_do cisco@${addr} "lshw -c network" || true
#    ssh_do cisco@${addr} "sudo -S sh -c 'echo exec show  hardware | vpp_api_test '"
#done

VIRL_SERVER=10.30.51.28
VIRL_USERNAME=jenkins-in
VIRL_PKEY=priv_key

rm -f ${VIRL_PKEY}
echo > ${VIRL_PKEY} <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAubrPwsl0+7x68mFzVDWYlCASWuP9rP5hn6ypXqtfNDJwpPh4
DBQx2q+zvIN+OawkZgyUzvZGcSexHtiIrb7ek6Tfj8Gky7YIQQOdFosiOTBsGDTm
4i3jU9aCRnzLCOQoEl6IUbJ8N+F+D/DM53MXy8vthsHbcI1OX3v0LBRNqrIT429m
iAUJWutgE7pAW+xqtD95Y6MCJUYRGEo6UB1Pw85wMMWEb1oI9z134eW5FwH0OWZG
dUEIfsSbfgCasKY4unMKUEbX65rvE3un92CrYUgOrnyRFgMzP87hxvQ4pzTfPH01
DuchDunzK/qJLkRA/rJ3a+40UF95Skga+XMlOwIDAQABAoIBADfU/aGrl9wZA8ib
HOVCm1Rj88CY6ug3LDeo2t1XnO3+/7fH7aaL55S63sgbqzVBF0wKGi3BANoBOZBx
PV0llJlDpeT8LEMEvKR2pqFhP+97K/N267UwYDcSs+TmnM5Wb+ldu5L7mbXetluq
Yp5tDck4y3WIDyRdhiLUC0m47MQT8wYBQeUkvxhWyN/sNSi50EacgbZJOAlFw8Bj
626flDDQ6uURsHTBOnxKWEixd7/VxYoVSmWgGMFzI7fdNAykyNOYyIGRqtszQ3vC
p8IW7UKY3/gJJHjYppXcr/45Wv55oVUCSReAjF7QeJAO7JFB4tR5H0nKHMUA8MFj
/zxVc2kCgYEA4/tc3mbaWnqgSge92H6HS3ur3UuovtGrTbsnIwxRRB5gtYzs4RMp
ZLR98bKb4SW8LUK81Y4X6H6/iogGDkY7w8BLrdW6kkDBs0QWyg1RK0wnemP7jsZa
cAiPgFWYuTnHQiXKZNP7cFb85bfs+BXfh7ufW+OwU7GJIUlHIN8kgA0CgYEA0I4i
rAO2oNQHPYOi1c9mic6zwNts2u/w7YPj5u6emA6dpIYiPmo3BMnTYop8RL1QkhDV
pCqbgjDNNvgSYZAF/f8pX7+phEaErx70wjNq0cidgwKDpzwJSpVZNxHVARlzfVKH
b+6zc+ngxKBoufW7WvU9V43I+Ug1UmzSCJZKIGcCgYBuLFAh7kSBSxdhD0Kwd9z8
HmTcya5foMWPB+2O42n2aFPGCLeEwZTUZOEkR3NLJ8g7ey/0Z/mn0nDQCpIandhN
7gTkmg/Sk9bHwhTdSfg620+Mtvqfcb3MvGZU14i5onFnxwl7FnJBRNhsTykGbtOa
LZKCfpL8ryQc4OOtwAhMlQKBgBIDxRDwvSzFQ97XaRBo+uV6emJ1UcDTqw8JLn17
LS3bTVix0XFswVXjjSPc7IEPjU8gryOgHpCvYHqYERZmV24qRUulBaKMaNerp97C
jD6Uwq5XYEHo2LCdl/g+zRRsO2Ke514O02d201iItqMhi85+ko7mi26lAx4ckkP1
n2+PAoGANDdUE/DSKSdsaaXSHpKub+hqqgtKpeI0gnwvyCwlT2cJKdPOrJNAwW9T
PtdQUlj9j6AU3jRUvksw5LGGKIXtSLpm0GEN0G7mlkNbB99FoDtIC7NeX4pfSQem
EXuq4JmLzeGc8OsDGFWyRNGl9svfCWPwqm9zRFJvPXrmKFo7894=
-----END RSA PRIVATE KEY-----
EOF
chmod 600 priv_key

# Temporarily download VPP packages from nexus.fd.io

rm -f *.deb
wget "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp/1.0.0-185~gca0f3b3_amd64/vpp-1.0.0-185~gca0f3b3_amd64.deb" || exit
wget "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dbg/1.0.0-185~gca0f3b3_amd64/vpp-dbg-1.0.0-185~gca0f3b3_amd64.deb" || exit
wget "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dev/1.0.0-185~gca0f3b3_amd64/vpp-dev-1.0.0-185~gca0f3b3_amd64.deb" || exit
wget "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dpdk-dev/1.0.0-185~gca0f3b3_amd64/vpp-dpdk-dev-1.0.0-185~gca0f3b3_amd64.deb" || exit
wget "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dpdk-dkms/1.0.0-185~gca0f3b3_amd64/vpp-dpdk-dkms-1.0.0-185~gca0f3b3_amd64.deb" || exit
wget "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-lib/1.0.0-185~gca0f3b3_amd64/vpp-lib-1.0.0-185~gca0f3b3_amd64.deb" || exit

VPP_DEBS=*.deb
VIRL_DIR_LOC="/tmp"
IFS=' ' read -ra VPP_DEBS_FULL <<< "${VPP_DEBS}"

# Prepend directory location at remote host to deb file list
for index in "${!VPP_DEBS_FULL[@]}"; do
    VPP_DEBS_FULL[${index}]=${VIRL_DIR_LOC}/${VPP_DEBS_FULL[${index}]}
done

echo "Updated file names: " ${VPP_DEBS_FULL[@]}

# Copy the files to VIRL host
scp -i ${VIRL_PKEY} -o StrictHostKeyChecking=no *.deb \
    ${VIRL_USERNAME}@${VIRL_SERVER}:${VIRL_DIR_LOC}/

result=$?
if [ "$?" -ne "0" ]; then
    echo "Failed to copy vpp deb files to virl host"
    echo ${result}
fi

VIRL_SID=$(ssh -i priv_key -o StrictHostKeyChecking=no \
    ${VIRL_USERNAME}@${VIRL_SERVER} \
    "/home/virl/testcase-infra/bin/start-testcase simple-ring ${VPP_DEBS_FULL[@]}")

echo ${VIRL_SID}

ssh_do ${VIRL_USERNAME}@${VIRL_SERVER} cat /scratch/${VIRL_SID}/topology.yaml


# Start a simulation at VIRL

#virtualenv env
#. env/bin/activate
#
#echo pip install
#pip install -r requirements.txt
#
#PYTHONPATH=`pwd` pybot -L TRACE \
#    -v TOPOLOGY_PATH:topologies/available/virl.yaml \
#    --include vm_env \
#    --include 3_NODE_SINGLE_LINK_TOPO \
#    --exclude 3_node_double_link_topoNOT3_node_single_link_topo \
#    --exclude PERFTEST \
#    tests/
