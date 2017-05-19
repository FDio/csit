#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
# Copyright (c) 2017 Red Hat Incorporated
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

cat /etc/hostname
cat /etc/hosts

sudo yum install -y python-devel python-virtualenv

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

TEST_DUTS=("192.168.122.74" "192.168.122.220" "192.168.122.95")
TG="192.168.122.74"

TEST_HOSTS=("10.8.125.25")

TEST_USERNAME=cisco
TMP_DIR_LOC="/tmp"
TEST_DIR_LOC="${TMP_DIR_LOC}/openvpp-testing"

TEST_PKEY=${SCRIPT_DIR}/cisco.key

SSH_OPTIONS="-i ${TEST_PKEY} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=error"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

#TEST_GROUPS=("gre,ipv6,lisp,policer,rpf,softwire,dhcp,ipsec,l2bd,l2xc,telemetry,vrf,vxlan,cop,fds,iacl,ipv4,tap,vhost,vlan")
TEST_GROUPS="ip4"
SUITE_PATH="tests.vpp.func"
SKIP_PATCH="SKIP_PATCH"

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh ${SSH_OPTIONS} $@
}

# Create tmp dir
mkdir ${SCRIPT_DIR}/tmp

# Use tmp dir to store log files
LOG_PATH="${SCRIPT_DIR}/tmp"

# Use tmp dir for tarballs
export TMPDIR="${SCRIPT_DIR}/tmp"

rm -f ${TEST_PKEY}
cat > ${TEST_PKEY} <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA3fbNDEzhgfr/T3o+JD8gk5j3dx4GUjn24e5ZjUPNQSvBSDYk
y/5MN4nqMrLcbGL9kiwwUgctx32c1c/1UESuL4VUuWq42O0ST0IHAa0eILWlNlp3
6TWA2b9LBBpEPvyqyWpEEHi4VyN9Hd7XO0fJltO+mTjt0viLRUegeP35wFxW7fes
ZFsyqfHM6Beh+/xEmOD8UcychNkub0b1AvPMWuGN8A4funLOm54LrF15X5wO+Ri/
B24puKvudE+Q9EhvRWdRBy8i0naFqJYedR4b8l7Do0zeaReWEEzv8Qek9plz6Kdp
kPylIo2D0IhwQBghTqqYPqHeNulXL5uH34UX+wIDAQABAoIBAGpbdzdco3Xv+mRv
89TUdtyioHlwZqEB612pIzoAchq3R589anZg/M5kBFeUwvAgotZm3CSCEhqUAxGk
2yxCLKDSp51NGRPAzVQzFD5mYJhV0btwsCKMI5izA9QMbgUsdv2aMNEft1zxwWMN
w15BcMQX5C1xTOwZckqZHri7IfBcqkexj8zhF6ItpgSybY2waGzCOpA5jrKuqcZ4
Pj7SCI/ymeGObNEKRvNGEaNnlkurQHNudcGo6O7oGgTHCm4OWlfTv2EMXCZnL2Ds
EBGsPyNBQcic44FuzmuCySy3ScUoMnhxn/+nXZsXopRlYRWRfJ83sMHSf/ff2LM7
t3QehdkCgYEA8YmEaZQKxF/dit5izBBW7zVqveMt8+X/TSfnihQOzNygktWmDdSN
KUmFZvdU13jD1elymY8aX/5x/1LsSd0uGEGm2wGfC85qqRQSqcTmJWY2J1HpE2qD
4eCwrycRY7oXZp1vOQkEF7ETzGLf/ddkDjBt1nX60sz0X9NcEBKV8e0CgYEA60FA
NWZjB5p9MKWN6l+FGWmJu565aANlX/HhstNvnwNszLuYYmE6ricu+xdJ+2Ss/+KN
aVGhzonmg6/YVPKwdRP9cfKFjkhkBSTgDjG+msA7H6pZGsa7jW2pkWiyEzCS2Sfv
vQWdtjEax6zacqmCAttrl0ZOg75p/jDut0g8FIcCgYEAoB3uhmLaZGW8opNb4TUv
vDGoCiswyk981/QNHM7BJPNZCx3Qj7iIv4b6hVCOkKyA/ixciQmBjYNKpNyewTR7
mx7icqp3eccjk+Q3nw1lGAPTAGvfW7yvoqxl1CbM81RosODK239rlB0SJ9qf7FG+
BV37YkEhvl6Z3XBqxkjb190CgYAXD1ZT5a1fWW1cD15R0vsg+o9drLlP0MVnGjad
aMxQMe3AQ8M0IYO2/nBEfIvr8HpkurhR0oah0DKgReRWr1NMpqD5QmSFBeOH/Y1Y
1tdwI9enyvLhBQntWwp8Dl8mMmSylI+TX7GN4lJVsEPZaXQtA4UQVvvrPgb1u6Yq
oRICkQKBgQCE8FMXIYAQPT+m97XWYg/hLg6Al0rXCXDXUWyOoKGK/SFU1FvRvruT
+9UV77NmTNofAKrsMAlC8HgO/NsEa3zvUTzeIbnUJ/AmqdNy60nut+7mU+XLuFCY
uy/QYike+mLsPuYH+zclrj9NdseJPJkdRkV3Gh61wyvKI9ZjL5GCpw==
-----END RSA PRIVATE KEY-----
EOF
chmod 600 ${TEST_PKEY}


# Temporarily download VPP packages from nexus.fd.io
VPP_REPO_URL=$(cat ${SCRIPT_DIR}/VPP_REPO_URL_CENTOS)
VPP_CLASSIFIER=""
if [ "${#}" -ne "0" ]; then
    arr=(${@})
    echo ${arr[0]}
    SKIP_PATCH="skip_patchORskip_vpp_patch"
else
    rm -f *.rpm
    VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_CENTOS)
    wget -q "${VPP_REPO_URL}/vpp/${VPP_STABLE_VER}/vpp-${VPP_STABLE_VER}${VPP_CLASSIFIER}.rpm" || exit
    wget -q "${VPP_REPO_URL}/vpp-debuginfo/${VPP_STABLE_VER}/vpp-debuginfo-${VPP_STABLE_VER}${VPP_CLASSIFIER}.rpm" || exit
    wget -q "${VPP_REPO_URL}/vpp-devel/${VPP_STABLE_VER}/vpp-devel-${VPP_STABLE_VER}${VPP_CLASSIFIER}.rpm" || exit
    wget -q "${VPP_REPO_URL}/vpp-lib/${VPP_STABLE_VER}/vpp-lib-${VPP_STABLE_VER}${VPP_CLASSIFIER}.rpm" || exit
    wget -q "${VPP_REPO_URL}/vpp-plugins/${VPP_STABLE_VER}/vpp-plugins-${VPP_STABLE_VER}${VPP_CLASSIFIER}.rpm" || exit
fi

VPP_RPMS=(*.rpm)
echo ${VPP_RPMS[@]}
VPP_RPMS_FULL=(${VPP_RPMS[@]})

# Prepend directory location of remote host to rpm list
for index in "${!VPP_RPMS_FULL[@]}"; do
    VPP_RPMS_FULL[${index}]=${TMP_DIR_LOC}/${VPP_RPMS_FULL[${index}]}
done

echo "Updated rpm file paths: " ${VPP_RPMS_FULL[@]}

cat ${TEST_PKEY}

# Copy the files to duts
DONE=""
for index in "${!TEST_DUTS[@]}"; do
    # Do not copy files in case they have already been copied to the TEST host
    [[ "${DONE[@]}" =~ "${TEST_DUTS[${index}]}" ]] && copy=0 || copy=1

    if [ "${copy}" -eq "0" ]; then
        echo "VPP rpms have already been copied to the TEST host ${TEST_DUTS[${index}]}"
    else
        echo scp ${SSH_OPTIONS} *.rpm \
        ${TEST_USERNAME}@${TEST_DUTS[${index}]}:${TMP_DIR_LOC}/
        scp ${SSH_OPTIONS} *.rpm \
        ${TEST_USERNAME}@${TEST_DUTS[${index}]}:${TMP_DIR_LOC}/

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to copy VPP rpms to TEST host ${TEST_DUTS[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "VPP rpms successfully copied to the TEST host ${TEST_DUTS[${index}]}"
        fi
        DONE+=(${TEST_DUTS[${index}]})
    fi
done

# Copy huge table fix service to duts
cd centos-local
tar -cvf ${SCRIPT_DIR}/tmp/hugepage-fix.tar root etc
cd ${SCRIPT_DIR}

result=$?
if [ "${result}" -ne "0" ]; then
    echo "Failed to create hugepage-fix tarball"
    echo ${result}
    exit ${result}
fi

DONE2=""
for index in "${!TEST_DUTS[@]}"; do
    # Do not copy files in case they have already been copied to the TEST host
    [[ "${DONE2[@]}" =~ "${TEST_DUTS[${index}]}" ]] && copy=0 || copy=1

    if [ "${copy}" -eq "0" ]; then
        echo "huge table fix has already been copied to the TEST host ${TEST_DUTS[${index}]}"
    else
        echo scp ${SSH_OPTIONS} ${SCRIPT_DIR}/tmp/hugepage-fix.tar \
        ${TEST_USERNAME}@${TEST_DUTS[${index}]}:${TMP_DIR_LOC}/
        scp ${SSH_OPTIONS} ${SCRIPT_DIR}/tmp/hugepage-fix.tar \
        ${TEST_USERNAME}@${TEST_DUTS[${index}]}:${TMP_DIR_LOC}/

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to copy VPP huge table fix to TEST host ${TEST_DUTS[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "huge table fix successfully copied to the TEST host ${TEST_DUTS[${index}]}"
        fi
        echo ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo tar -xvf ${TMP_DIR_LOC}/hugepage-fix.tar -C /
        ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo tar -xvf ${TMP_DIR_LOC}/hugepage-fix.tar -C /

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to unpack VPP huge table fix on TEST host ${TEST_DUTS[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "Unpacked VPP huge table fix on TEST host ${TEST_DUTS[${index}]}"
        fi
        echo ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo systemctl daemon-reload
        ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo systemctl daemon-reload

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to load huge page service on TEST host ${TEST_DUTS[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "Loaded huge page service on TEST host ${TEST_DUTS[${index}]}"
        fi
        echo ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo systemctl enable hugepage-fix.service
        ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo systemctl enable hugepage-fix.service

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to enable hugepage fix service on TEST host ${TEST_DUTS[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "Enabled hugepage fix service on TEST host ${TEST_DUTS[${index}]}"
        fi
        echo ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo systemctl start hugepage-fix.service
        ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo systemctl start hugepage-fix.service

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to start hugepage fix service on TEST host ${TEST_DUTS[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "Started hugepage fix service on TEST host ${TEST_DUTS[${index}]}"
        fi

        DONE2+=(${TEST_DUTS[${index}]})
    fi
done

# Install RPMs on duts
for index in "${!TEST_DUTS[@]}"; do

    # Don't install vpp on TG for now.

    if [ ! ${TEST_DUTS[${index}]} == ${TG} ]; then
        echo ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo rpm -i ${TMP_DIR_LOC}/*.rpm
        ssh_do ${TEST_USERNAME}@${TEST_DUTS[${index}]} \
        sudo rpm -i ${TMP_DIR_LOC}/*.rpm
    fi
done

function run_test_set() {
    set +x
    OLDIFS=$IFS
    IFS=","
    rm -f ${LOG_PATH}/test_run.log
    exec &> >(while read line; do echo "$(date +'%H:%M:%S') $line" \
     >> ${LOG_PATH}/test_run.log; done;)
    IFS=$OLDIFS

    echo "PYTHONPATH=`pwd` pybot -L TRACE -W 136\
            -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology.yaml \
            -s ${TEST_GROUPS}\
            --noncritical EXPECTED_FAILING \
            --output ${LOG_PATH}/log_test_set_run \
            tests/vpp/func/"

    PYTHONPATH=`pwd` pybot -L TRACE -W 136 \
        -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology.yaml \
        -s ${TEST_GROUPS}\
        --noncritical EXPECTED_FAILING \
        --output ${LOG_PATH}/log_test_set_run \
        tests/vpp/func/

    local_run_rc=$?
    echo ${local_run_rc} > ${LOG_PATH}/rc_test_run
    set -x
}
echo "virtualenv --system-site-packages env"
virtualenv --system-site-packages env

echo ". env/bin/activate"
. env/bin/activate

echo "pip install -r requirements.txt"
pip install -r requirements.txt

echo "export PYTHONPATH=."
export PYTHONPATH=.

# Watch the background process to check if pid is still there.

run_test_set &
pid=$!
echo "Sent to background: Test_set (pid=$pid)"
for i in $(seq 0 9); do
    sleep 1
    echo -n "."
done
while ! ps "$pid" >/dev/null; do
    echo -n -e "\nStill waiting for test set: ${pid} ..."
    sleep 10
done
echo -e "\n"
echo "Test set with PID $pid finished."
