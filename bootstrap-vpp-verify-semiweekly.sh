#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a ght (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not usecopy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

RETURN_STATUS=0

cat /etc/hostname
cat /etc/hosts

export DEBIAN_FRONTEND=noninteractive
sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

PYBOT_ARGS="--noncritical MULTI_THREAD"

ARCHIVE_ARTIFACTS=(log.html output.xml report.html output_perf_data.xml)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${SCRIPT_DIR}


# 1st step: Download and prepare VPP packages

# Temporarily download VPP packages from nexus.fd.io
rm -f *.deb
if [ "${#}" -ne "0" ]; then
    arr=(${@})
    echo ${arr[0]}
else
    # Download the latest VPP build .deb install packages
    echo Downloading VPP packages...
    bash ${SCRIPT_DIR}/resources/tools/download_install_vpp_pkgs.sh --skip-install
fi

VPP_DEBS=(*.deb)
echo ${VPP_DEBS[@]}

VPP_VER=$(echo ${VPP_DEBS#vpp-})
VPP_VER=$(echo ${VPP_VER%.deb})
echo VPP version to be tested: ${VPP_VER}

set +x
echo "******************************************************************************"
echo "1st step: Download VPP packages                                       FINISHED"
echo "******************************************************************************"
set -x


# 2nd step: Start virtual env and install requirements

echo Starting virtual env...
virtualenv --system-site-packages env
. env/bin/activate

echo Installing requirements...
pip install -r ${SCRIPT_DIR}/requirements.txt

set +x
echo "******************************************************************************"
echo "2nd step: Start virtual env and install requirements                  FINISHED"
echo "******************************************************************************"
set -x


# 3rd step: Prepare VIRL system
echo Preparing VIRL system...

VIRL_SERVERS=("10.30.51.28" "10.30.51.29" "10.30.51.30")
VIRL_SERVER=""

VIRL_USERNAME=jenkins-in
VIRL_PKEY=priv_key
VIRL_SERVER_STATUS_FILE="status"
VIRL_SERVER_EXPECTED_STATUS="PRODUCTION"

SSH_OPTIONS="-i ${VIRL_PKEY} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=error"

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
# Pick a random host from the array of VIRL servers, and attempt
# to reach it and verify it's status.
#
# The server must be reachable, and have a "status" file with
# the content "PRODUCTION", to be selected.
#
# If the server is not reachable, or does not have the correct
# status, remove it from the array and start again.
#
# Abort if there are no more servers left in the array.
#
while [[ ! "$VIRL_SERVER" ]]
do
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
        VIRL_SERVER="$virl_server_candidate"
    else
        # Candidate is in bad status. Remove from array.
        VIRL_SERVERS=("${VIRL_SERVERS[@]:0:$element}" "${VIRL_SERVERS[@]:$[$element+1]}")
    fi
done


VIRL_DIR_LOC="/tmp"
VPP_DEBS_VIRL=(${VPP_DEBS[@]})

# Prepend directory location at remote host to deb file list
for index in "${!VPP_DEBS_VIRL[@]}"; do
    VPP_DEBS_VIRL[${index}]=${VIRL_DIR_LOC}/${VPP_DEBS_VIRL[${index}]}
done

echo "Updated file names: " ${VPP_DEBS_VIRL[@]}

cat ${VIRL_PKEY}
# Copy the files to VIRL host
scp ${SSH_OPTIONS} *.deb \
    ${VIRL_USERNAME}@${VIRL_SERVER}:${VIRL_DIR_LOC}/

result=$?
if [ "${result}" -ne "0" ]; then
    echo "Failed to copy vpp deb files to virl host"
    echo ${result}
    exit ${result}
fi

# Start a simulation on VIRL server
echo "Starting simulation on VIRL server"

function stop_virl_simulation {
    ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${VIRL_SERVER}\
        "stop-testcase ${VIRL_SID}"
}

VIRL_SID=$(ssh ${SSH_OPTIONS} \
    ${VIRL_USERNAME}@${VIRL_SERVER} \
    "start-testcase -c double-ring-nested ${VPP_DEBS_VIRL[@]}")
retval=$?
if [ "$?" -ne "0" ]; then
    echo "VIRL simulation start failed"
    exit ${retval}
fi

if [[ ! "${VIRL_SID}" =~ session-[a-zA-Z0-9_]{6} ]]; then
    echo "No VIRL session ID reported."
    exit 127
fi

# Upon script exit, cleanup the VIRL simulation execution
trap stop_virl_simulation EXIT
echo ${VIRL_SID}

ssh_do ${VIRL_USERNAME}@${VIRL_SERVER} cat /scratch/${VIRL_SID}/topology.yaml

# Download the topology file from VIRL session
scp ${SSH_OPTIONS} \
    ${VIRL_USERNAME}@${VIRL_SERVER}:/scratch/${VIRL_SID}/topology.yaml \
    topologies/enabled/topology_VIRL.yaml

retval=$?
if [ "$?" -ne "0" ]; then
    echo "Failed to copy topology file from VIRL simulation"
    exit ${retval}
fi

set +x
echo "******************************************************************************"
echo "3rd step: Start the simulation on the VIRL server                     FINISHED"
echo "******************************************************************************"
set -x


# 4th step: Run functional test suites

RC=0
MORE_FAILS=0

echo Running functional tests on the VIRL system...

# There are used three iterations of functional tests there
# to check the stability and reliability of the results.
for test_set in 1 2 3
do
    echo
    echo Functional test loop: ${test_set}
    echo

    pybot -L TRACE \
        -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology_VIRL.yaml \
        --suite "tests.func" \
        --include vm_envAND3_node_single_link_topo \
        --include vm_envAND3_node_double_link_topo \
        --exclude PERFTEST \
        --noncritical EXPECTED_FAILING \
        --output log_func_test_set${test_set} \
        tests/
    PARTIAL_RC=$(echo $?)
    if [ ${PARTIAL_RC} -eq 250 ]; then
        MORE_FAILS=1
    fi
    RC=$((RC+PARTIAL_RC))
done

set +x
echo "******************************************************************************"
echo "4th step: Run functional tests                                        FINISHED"
echo "******************************************************************************"
set -x


# 5th step: Reserve and prepare HW system

echo Making a reservation for the HW system...

# Space separated list of available testbeds, described by topology files
TOPOLOGIES="topologies/available/lf_testbed1-X710-X520.yaml \
            topologies/available/lf_testbed2-X710-X520.yaml \
            topologies/available/lf_testbed3-X710-X520.yaml"

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

WORKING_TOPOLOGY=""

# We iterate over available topologies and wait until we reserve topology
while :; do
    for TOPOLOGY in ${TOPOLOGIES};
    do
        python ${SCRIPT_DIR}/resources/tools/topo_reservation.py -t ${TOPOLOGY}
        if [ $? -eq 0 ]; then
            WORKING_TOPOLOGY=${TOPOLOGY}
            echo "Reserved: ${WORKING_TOPOLOGY}"
            break
        fi
    done

    if [ ! -z "${WORKING_TOPOLOGY}" ]; then
        # Exit the infinite while loop if we made a reservation
        break
    fi

    # Wait ~3minutes before next try
    SLEEP_TIME=$[ ( $RANDOM % 20 ) + 180 ]s
    echo "Sleeping ${SLEEP_TIME}"
    sleep ${SLEEP_TIME}
done

function cancel_all {
    python ${SCRIPT_DIR}/resources/tools/topo_installation.py -c -d ${INSTALLATION_DIR} -t $1
    python ${SCRIPT_DIR}/resources/tools/topo_reservation.py -c -t $1
}

# Upon script exit, cleanup the VIRL simulation execution
# and cancel the reservation and installation of HW system
# and delete all vpp packages.
trap "stop_virl_simulation; cancel_all ${WORKING_TOPOLOGY}" EXIT

python ${SCRIPT_DIR}/resources/tools/topo_installation.py -t ${WORKING_TOPOLOGY} \
                                                       -d ${INSTALLATION_DIR} \
                                                       -p ${VPP_DEBS[@]}

if [ $? -eq 0 ]; then
    echo "VPP Installed on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy vpp deb files to DUTs"
    exit 1
fi

set +x
echo "******************************************************************************"
echo "5th step: Making a reservation for HW system                          FINISHED"
echo "******************************************************************************"
set -x

# 6th step: Run performance tests

# Performance tests on HW system
echo Performance tests on HW system

pybot ${PYBOT_ARGS} \
    -L TRACE \
    -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
    --suite "tests.perf" \
    --include perftest_long \
    --output log_perf_test_set \
    tests/

PARTIAL_RC=$(echo $?)
if [ ${PARTIAL_RC} -eq 250 ]; then
    MORE_FAILS=1
fi
RC=$((RC+PARTIAL_RC))

set +x
echo "******************************************************************************"
echo "6th step: Run performance tests                                       FINISHED"
echo "******************************************************************************"
set -x


# Set RETURN_STATUS=1 if some critical test failed
if [ ! ${RC} -eq 0 ]; then
        RETURN_STATUS=1
fi

# Log the final result
if [ ${RC} -eq 0 ]; then
    set +x
    echo
    echo "=============================================================================="
    echo "Final result of all test loops:                                       | PASS |"
    echo "All critical tests have passed."
    echo "=============================================================================="
    echo
    set -x
elif [ ${MORE_FAILS} -eq 0 ]; then
    if [ ${RC} -eq 1 ]; then
        HLP_STR="test has"
    else
        HLP_STR="tests have"
    fi
    set +x
    echo
    echo "=============================================================================="
    echo "Final result of all test loops:                                       | FAIL |"
    echo "${RC} critical ${HLP_STR} failed."
    echo "=============================================================================="
    echo
    set -x
else
    set +x
    echo
    echo "=============================================================================="
    echo "Final result of all test loops:                                       | FAIL |"
    echo "More then 250 critical tests have failed in one test loop."
    echo "=============================================================================="
    echo
    set -x
fi


# 7th step: Post-processing test data
echo Post-processing test data...

# Getting JSON perf data output
python ${SCRIPT_DIR}/resources/tools/robot_output_parser.py \
       -i ${SCRIPT_DIR}/log_perf_test_set.xml \
       -o ${SCRIPT_DIR}/output_perf_data.xml \
       -v ${VPP_VER}
if [ ! $? -eq 0 ]; then
    echo "Parsing ${SCRIPT_DIR}/log_perf_test_set.xml failed"
fi

# Rebot output post-processing
rebot --noncritical EXPECTED_FAILING \
      --output output.xml \
      ./log_func_test_set1.xml ./log_func_test_set2.xml \
      ./log_func_test_set3.xml ./log_perf_test_set.xml

# Remove unnecessary files
rm -f ./log_test_set1.xml ./log_test_set2.xml ./log_test_set3.xml \
    ./log_perf_test_set.xml

# Archive artifacts
mkdir archive
for i in ${ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) archive/
done

echo Post-processing finished.

exit ${RETURN_STATUS}
