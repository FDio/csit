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

cat /etc/hostname
cat /etc/hosts

export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

VIRL_SERVERS=("10.30.51.28" "10.30.51.29" "10.30.51.30")

VIRL_USERNAME=jenkins-in
VIRL_PKEY=priv_key
VIRL_SERVER_STATUS_FILE="status"
VIRL_SERVER_EXPECTED_STATUS="PRODUCTION"

VIRL_TOPOLOGY=$(cat ${SCRIPT_DIR}/VIRL_TOPOLOGY_UBUNTU)
VIRL_RELEASE=$(cat ${SCRIPT_DIR}/VIRL_RELEASE_UBUNTU)

SSH_OPTIONS="-i ${VIRL_PKEY} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=error"

TEST_GROUPS=("l2bd,dhcp,gre,honeycomb,l2xc,lisp,softwire" "cop,telemetry,ipsec,ipv6,rpf,tap,vrf" "fds,iacl,ipv4,policer,vlan,vxlan")
SUITE_PATH="tests.func"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create tmp dir
mkdir ${SCRIPT_DIR}/tmp

# Use tmp dir to store log files
LOG_PATH="${SCRIPT_DIR}/tmp"

# Use tmp dir for tarballs
export TMPDIR="${SCRIPT_DIR}/tmp"

SHARED_MEMORY_PATH="/run/shm"

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh ${SSH_OPTIONS} $@
}

rm -f ${VIRL_PKEY}
cat > ${VIRL_PKEY} <<EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEpQIBAAKCAQEA+IHXq87GcqMR1C47rzx6Cbip5Ghq8pKrbqKrP5Nf41HcYrT6
GOXl9nFWKsMOzIlIn+8y7Il27eZh7csQGApbg8QLiHMtcYEmWNzKZpkqg4nuAPxX
VXwlKgnKX902SrET9Gp9TDayiHtCRWVfrlPPPSA0UEXW6BjLN/uHJ+W/Xzrrab+9
asBVa05vT2W6n0KJ66zfCaeDM912mQ6SttscAwFoWDmdHlegiVqrlIG2ABxOvxxz
L3dM3iSmlmQlzv9bThjo+nI4KFYh6m5wrZmAo5r/4q9CIJc21HVnTqkGOWJIZz6J
73lePJVSq5gYqaoGw3swFEA/MDkOx7baWKSoLQIDAQABAoIBAQCNBeolNp+JWJ76
gQ4fwLsknyXSV6sxYyhkDW4PEwwcTU06uqce0AAzXVffxne0fMe48x47+zqBgPbb
4huM+Pu8B9nfojUMr5TaYtl9Zbgpk3F8H7dT7LKOa6XrxvZTZrADSRc30+Z26zPN
e9zTaf42Gvt0/l0Zs1BHwbaOXqO+XuwJ3/F9Sf3PQYWXD3EOWjpHDP/X/1vAs6lV
SLkm6J/9KKE1m6I6LTYjIXuYt4SXybW6N2TSy54hhQtYcDUnIU2hR/PHVWKrGA0J
kELgrtTNTdbML27O5gFWU4PLUEYTZ9fN11D6qUZKxLcPOiPPHXkiILMRCCnG5DYI
ksBAU/YlAoGBAPxZO9VO18TYc8THV1nLKcvT2+1oSs1UcA2wNQMU55t910ZYinRa
MRwUhMOf8Mv5wOeiZaRICQB1PnVWtDVmGECgPpK6jUxqAwn8rgJcnoafLGL5YKMY
RVafTe6N5LXgCaOcJrk21wxs6v7ninEbUxxc575urOvZMBkymDw91dwbAoGBAPwa
YRhKhrzFKZzdK0RadVjnxKvolUllpoqqg3XuvmeAJHAOAnaOgVWq68NAcp5FZJv0
2D2Up7TX8pjf9MofP1SJbcraKBpK4NzfNkA0dSdEi+FhVofAJ9umB2o5LW1n7sab
UIrjsdzSJK/9Zb9yTTHPyibYzNEgaJV1HsbxfEFXAoGAYO2RmvRm0phll18OQVJV
IpKk9kLKAKZ/R/K32hAsikBC8SVPQTPniyaifFWx81diblalff2hX4ipTf7Yx24I
wMIMZuW7Im/R7QMef4+94G3Bad7p7JuE/qnAEHJ2OBnu+eYfxaK35XDsrq6XMazS
NqHE7hOq3giVfgg+C12hCKMCgYEAtu9dbYcG5owbehxzfRI2/OCRsjz/t1bv1seM
xVMND4XI6xb/apBWAZgZpIFrqrWoIBM3ptfsKipZe91ngBPUnL9s0Dolx452RVAj
yctHB8uRxWYgqDkjsxtzXf1HnZBBkBS8CUzYj+hdfuddoeKLaY3invXLCiV+PpXS
U4KAK9kCgYEAtSv0m5+Fg74BbAiFB6kCh11FYkW94YI6B/E2D/uVTD5dJhyEUFgZ
cWsudXjMki8734WSpMBqBp/J8wG3C9ZS6IpQD+U7UXA+roB7Qr+j4TqtWfM+87Rh
maOpG56uAyR0w5Z9BhwzA3VakibVk9KwDgZ29WtKFzuATLFnOtCS46E=
-----END RSA PRIVATE KEY-----
EOF
chmod 600 ${VIRL_PKEY}

#
# Pick a random host from the array of VIRL servers for every test set run
# and attempt to reach it and verify it's status.
#
# The server must be reachable and have a "status" file with
# the content "PRODUCTION" to be selected.
#
# If the server is not reachable or does not have the correct
# status remove it from the array and start again.
#
# Abort if there are no more servers left in the array.
#
for index in "${!TEST_GROUPS[@]}"; do
    VIRL_SERVER[${index}]=""
    while [[ ! "${VIRL_SERVER[${index}]}" ]]; do
        num_hosts=${#VIRL_SERVERS[@]}
        if [ $num_hosts == 0 ]
        then
            echo "No more VIRL candidate hosts available, failing."
            exit 127
        fi
        element=$[ $RANDOM % $num_hosts ]
        virl_server_candidate=${VIRL_SERVERS[$element]}
        virl_server_status=$(ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${virl_server_candidate} cat $VIRL_SERVER_STATUS_FILE 2>&1)
        echo VIRL HOST $virl_server_candidate status is \"$virl_server_status\"
        if [ "$virl_server_status" == "$VIRL_SERVER_EXPECTED_STATUS" ]
        then
            # Candidate is in good status. Select this server.
            VIRL_SERVER[${index}]="$virl_server_candidate"
        else
            # Candidate is in bad status. Remove from array.
            VIRL_SERVERS=("${VIRL_SERVERS[@]:0:$element}" "${VIRL_SERVERS[@]:$[$element+1]}")
        fi
    done
done

echo "Selected VIRL servers: ${VIRL_SERVER[@]}"

# Temporarily download VPP and DPDK packages from nexus.fd.io
DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)_amd64
VPP_REPO_URL=$(cat ${SCRIPT_DIR}/VPP_REPO_URL_UBUNTU)
VPP_CLASSIFIER="-deb"
if [ "${#}" -ne "0" ]; then
    arr=(${@})
    echo ${arr[0]}
    # DPDK is not part of the vpp build
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dev/${DPDK_STABLE_VER}/vpp-dpdk-dev-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dkms/${DPDK_STABLE_VER}/vpp-dpdk-dkms-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
else
    rm -f *.deb
    VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_UBUNTU)
    wget -q "${VPP_REPO_URL}/vpp/${VPP_STABLE_VER}/vpp-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dbg/${VPP_STABLE_VER}/vpp-dbg-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dev/${VPP_STABLE_VER}/vpp-dev-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dev/${DPDK_STABLE_VER}/vpp-dpdk-dev-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dkms/${DPDK_STABLE_VER}/vpp-dpdk-dkms-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-lib/${VPP_STABLE_VER}/vpp-lib-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-plugins/${VPP_STABLE_VER}/vpp-plugins-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
fi

VPP_DEBS=(*.deb)
echo ${VPP_DEBS[@]}
VIRL_DIR_LOC="/tmp"
VPP_DEBS_FULL=(${VPP_DEBS[@]})

# Prepend directory location at remote host to deb file list
for index in "${!VPP_DEBS_FULL[@]}"; do
    VPP_DEBS_FULL[${index}]=${VIRL_DIR_LOC}/${VPP_DEBS_FULL[${index}]}
done

echo "Updated file names: " ${VPP_DEBS_FULL[@]}

cat ${VIRL_PKEY}

# Copy the files to VIRL hosts
DONE=""
for index in "${!VIRL_SERVER[@]}"; do
    # Do not copy files in case they have already been copied to the VIRL host
    [[ "${DONE[@]}" =~ "${VIRL_SERVER[${index}]}" ]] && copy=0 || copy=1

    if [ "${copy}" -eq "0" ]; then
        echo "VPP deb files have already been copied to the VIRL host ${VIRL_SERVER[${index}]}"
    else
        scp ${SSH_OPTIONS} *.deb \
        ${VIRL_USERNAME}@${VIRL_SERVER[${index}]}:${VIRL_DIR_LOC}/

        result=$?
        if [ "${result}" -ne "0" ]; then
            echo "Failed to copy VPP deb files to VIRL host ${VIRL_SERVER[${index}]}"
            echo ${result}
            exit ${result}
        else
            echo "VPP deb files successfully copied to the VIRL host ${VIRL_SERVER[${index}]}"
        fi
        DONE+=(${VIRL_SERVER[${index}]})
    fi
done

# Start a simulation on VIRL server

function stop_virl_simulation {
    for index in "${!VIRL_SERVER[@]}"; do
        ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${VIRL_SERVER[${index}]}\
            "stop-testcase ${VIRL_SID[${index}]}"
    done
}

# Upon script exit, cleanup the simulation execution
trap stop_virl_simulation EXIT

for index in "${!VIRL_SERVER[@]}"; do
    echo "Starting simulation nr. ${index} on VIRL server ${VIRL_SERVER[${index}]}"
    VIRL_SID[${index}]=$(ssh ${SSH_OPTIONS} \
        ${VIRL_USERNAME}@${VIRL_SERVER[${index}]} \
        "start-testcase -c ${VIRL_TOPOLOGY} -r ${VIRL_RELEASE} ${VPP_DEBS_FULL[@]}")
    retval=$?
    if [ ${retval} -ne "0" ]; then
        echo "VIRL simulation start failed on ${VIRL_SERVER[${index}]}"
        exit ${retval}
    fi
    if [[ ! "${VIRL_SID[${index}]}" =~ session-[a-zA-Z0-9_]{6} ]]; then
        echo "No VIRL session ID reported."
        exit 127
    fi
    echo "VIRL simulation started on ${VIRL_SERVER[${index}]}"

    ssh_do ${VIRL_USERNAME}@${VIRL_SERVER[${index}]}\
     cat /scratch/${VIRL_SID[${index}]}/topology.yaml

    # Download the topology file from VIRL session and rename it
    scp ${SSH_OPTIONS} \
        ${VIRL_USERNAME}@${VIRL_SERVER[${index}]}:/scratch/${VIRL_SID[${index}]}/topology.yaml \
        topologies/enabled/topology${index}.yaml

    retval=$?
    if [ ${retval} -ne "0" ]; then
        echo "Failed to copy topology file from VIRL simulation nr. ${index} on VIRL server ${VIRL_SERVER[${index}]}"
        exit ${retval}
    fi
done

echo ${VIRL_SID[@]}

virtualenv --system-site-packages env
. env/bin/activate

echo pip install
pip install -r ${SCRIPT_DIR}/requirements.txt

for index in "${!VIRL_SERVER[@]}"; do
    pykwalify -s ${SCRIPT_DIR}/resources/topology_schemas/3_node_topology.sch.yaml \
              -s ${SCRIPT_DIR}/resources/topology_schemas/topology.sch.yaml \
              -d ${SCRIPT_DIR}/topologies/enabled/topology${index}.yaml \
              -vvv
    if [ "$?" -ne "0" ]; then
        echo "Topology${index} schema validation failed."
        echo "However, the tests will start."
    fi
done

function run_test_set() {
    set +x
    OLDIFS=$IFS
    IFS=","
    nr=$(echo $1)
    rm -f ${LOG_PATH}/test_run${nr}.log
    exec &> >(while read line; do echo "$(date +'%H:%M:%S') $line" \
     >> ${LOG_PATH}/test_run${nr}.log; done;)
    suite_str=""
    for suite in ${TEST_GROUPS[${nr}]}; do
        suite_str="${suite_str} --suite ${SUITE_PATH}.${suite}"
    done
    IFS=$OLDIFS

    echo "PYTHONPATH=`pwd` pybot -L TRACE -W 136\
        -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology${nr}.yaml \
        ${suite_str} \
        --include vm_envAND3_node_single_link_topo \
        --include vm_envAND3_node_double_link_topo \
        --exclude PERFTEST \
        --exclude SKIP_PATCH \
        --noncritical EXPECTED_FAILING \
        --output ${LOG_PATH}/log_test_set_run${nr} \
        tests/"

    PYTHONPATH=`pwd` pybot -L TRACE -W 136\
        -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology${nr}.yaml \
        ${suite_str} \
        --include vm_envAND3_node_single_link_topo \
        --include vm_envAND3_node_double_link_topo \
        --exclude PERFTEST \
        --exclude SKIP_PATCH \
        --noncritical EXPECTED_FAILING \
        --output ${LOG_PATH}/log_test_set_run${nr} \
        tests/

    local_run_rc=$?
    echo ${local_run_rc} > ${SHARED_MEMORY_PATH}/rc_test_run${nr}
    set -x
}

set +x
# Send to background an instance of the run_test_set() function for each number,
# record the pid.
for index in "${!VIRL_SERVER[@]}"; do
    run_test_set ${index} &
    pid=$!
    echo "Sent to background: Test_set${index} (pid=$pid)"
    pids[$pid]=$index
done

echo
echo -n "Waiting..."

# Watch the stable of background processes.
# If a pid goes away, remove it from the array.
while [ -n "${pids[*]}" ]; do
    for i in $(seq 0 9); do
        sleep 1
        echo -n "."
    done
    for pid in "${!pids[@]}"; do
        if ! ps "$pid" >/dev/null; then
            echo -e "\n"
            echo "Test_set${pids[$pid]} with PID $pid finished."
            unset pids[$pid]
        fi
    done
    if [ -z "${!pids[*]}" ]; then
        break
    fi
    echo -n -e "\nStill waiting for test set(s): ${pids[*]} ..."
done

echo
echo "All test set runs finished."
echo

set -x

RC=0
for index in "${!VIRL_SERVER[@]}"; do
    echo "Test_set${index} log:"
    cat ${LOG_PATH}/test_run${index}.log
    RC_PARTIAL_RUN=$(cat ${SHARED_MEMORY_PATH}/rc_test_run${index})
    RC=$((RC+RC_PARTIAL_RUN))
    rm -f ${SHARED_MEMORY_PATH}/rc_test_run${index}
    rm -f ${LOG_PATH}/test_run${index}.log
    echo
done

# Log the final result
if [ "${RC}" -eq "0" ]; then
    set +x
    echo
    echo "========================================================================================================================================"
    echo "Final result of all test loops:                                                                                                 | PASS |"
    echo "All critical tests have passed."
    echo "========================================================================================================================================"
    echo
    set -x
else
    if [ "${RC}" -eq "1" ]; then
        HLP_STR="test has"
    else
        HLP_STR="tests have"
    fi
    set +x
    echo
    echo "========================================================================================================================================"
    echo "Final result of all test loops:                                                                                                 | FAIL |"
    echo "${RC} critical ${HLP_STR} failed."
    echo "========================================================================================================================================"
    echo
    set -x
fi

echo Post-processing test data...

partial_logs=""
for index in "${!VIRL_SERVER[@]}"; do
    partial_logs="${partial_logs} ${LOG_PATH}/log_test_set_run${index}.xml"
done

# Rebot output post-processing
rebot --noncritical EXPECTED_FAILING \
      --output output.xml ${partial_logs}

# Remove unnecessary log files
rm -f ${partial_logs}

echo Post-processing finished.

if [ ${RC} -eq 0 ]; then
    RETURN_STATUS=0
else
    RETURN_STATUS=1
fi

exit ${RETURN_STATUS}
