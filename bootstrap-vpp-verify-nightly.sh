#!/bin/bash
# Copyright (c) 2017 Cisco and/or its affiliates.
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

cat /etc/hostname
cat /etc/hosts

ARCHIVE_ARTIFACTS=(log.html output.xml report.html)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${SCRIPT_DIR}

# Create tmp dir
mkdir ${SCRIPT_DIR}/tmp

# Use tmp dir for tarballs
export TMPDIR="${SCRIPT_DIR}/tmp"

# Use tmp dir to store log files
LOG_PATH="$TMPDIR"

if [ -f "/etc/redhat-release" ]; then
    DISTRO="CENTOS"
    sudo yum install -y python-devel python-virtualenv openssh-clients sshpass
    PACKAGE=rpm
else
    DISTRO="UBUNTU"
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get -y update
    sudo apt-get -y install libpython2.7-dev python-virtualenv
    PACKAGE=deb
fi

# 1st step: Download and prepare VPP packages

# Temporarily download VPP packages from nexus.fd.io
if [ "${#}" -ne "0" ]; then
    arr=(${@})
    echo ${arr[0]}
else
    # Download the latest VPP build install packages
    rm -f *.${PACKAGE}
    echo Downloading VPP packages...
    CSIT_DIR=${SCRIPT_DIR}
    source "${SCRIPT_DIR}/resources/libraries/bash/function/artifacts.sh"
    download_artifacts
    # Need to revert -euo as the rest of script is not optimized for this.
    set +euo pipefail
fi

# Take vpp package and get the vpp version
VPP_PKGS=(*.$PACKAGE)
case "$DISTRO" in
        CENTOS )
            VPP_VER="$( expr match $(ls *.rpm | head -n 1) 'vpp-\(.*\).rpm' )"
            ;;
        UBUNTU )
            VPP_VER="$( expr match $(ls *.deb | head -n 1) 'vpp-\(.*\)-deb.deb' )"
esac

echo ${VPP_PKGS[@]}

set +x
echo "****************************************************************************************************************************************"
echo "1st step: Download VPP packages                                                                                                 FINISHED"
echo "VPP version to be tested: ${VPP_VER}"
echo "****************************************************************************************************************************************"
set -x


# 2nd step: Start virtual env and install requirements

echo Starting virtual env...
virtualenv --system-site-packages env
. env/bin/activate

echo Installing requirements...
pip install -r ${SCRIPT_DIR}/requirements.txt

set +x
echo "****************************************************************************************************************************************"
echo "2nd step: Start virtual env and install requirements                                                                            FINISHED"
echo "****************************************************************************************************************************************"
set -x


# 3rd step: Prepare VIRL system
echo Preparing VIRL system...

VIRL_SERVERS=("10.30.51.28" "10.30.51.29" "10.30.51.30")
IPS_PER_VIRL=( "10.30.51.28:252"
               "10.30.51.29:74"
               "10.30.51.30:74" )
SIMS_PER_VIRL=( "10.30.51.28:13"
               "10.30.51.29:13"
               "10.30.51.30:13" )
IPS_PER_SIMULATION=5

function get_max_ip_nr() {
    virl_server=$1
    IP_VALUE="0"
    for item in "${IPS_PER_VIRL[@]}" ; do
        if [ "${item%%:*}" == "${virl_server}" ]
        then
            IP_VALUE=${item#*:}
            break
        fi
    done
    echo "$IP_VALUE"
}

function get_max_sim_nr() {
    virl_server=$1
    SIM_VALUE="0"
    for item in "${SIMS_PER_VIRL[@]}" ; do
        if [ "${item%%:*}" == "${virl_server}" ]
        then
            SIM_VALUE=${item#*:}
            break
        fi
    done
    echo "$SIM_VALUE"
}

VIRL_USERNAME=jenkins-in
VIRL_PKEY=priv_key
VIRL_SERVER_STATUS_FILE="status"
VIRL_SERVER_EXPECTED_STATUS="PRODUCTION"

SKIP_PATCH="skip_patchORskip_vpp_patch"

case "$DISTRO" in
        CENTOS )
            VIRL_TOPOLOGY=$(cat ${SCRIPT_DIR}/VIRL_TOPOLOGY_CENTOS)
            VIRL_RELEASE=$(cat ${SCRIPT_DIR}/VIRL_RELEASE_CENTOS)
            NON_CRITICAL_TESTS="expected_failingORvm"
            ;;
        UBUNTU )
            VIRL_TOPOLOGY=$(cat ${SCRIPT_DIR}/VIRL_TOPOLOGY_UBUNTU)
            VIRL_RELEASE=$(cat ${SCRIPT_DIR}/VIRL_RELEASE_UBUNTU)
            NON_CRITICAL_TESTS="EXPECTED_FAILING"
            ;;
esac

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
# The server must be reachable and have a "status" file with
# the content "PRODUCTION" to be selected.
#
# If the server is not reachable or does not have the correct
# status remove it from the array and start again.
#
# Abort if there are no more servers left in the array.
#
VIRL_PROD_SERVERS=()
for index in "${!VIRL_SERVERS[@]}"; do
    virl_server_status=$(ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${VIRL_SERVERS[$index]} cat $VIRL_SERVER_STATUS_FILE 2>&1)
    echo VIRL HOST ${VIRL_SERVERS[$index]} status is \"$virl_server_status\"
    if [ "$virl_server_status" == "$VIRL_SERVER_EXPECTED_STATUS" ]
    then
        # Candidate is in good status. Add to array.
        VIRL_PROD_SERVERS+=(${VIRL_SERVERS[$index]})
    fi
done

VIRL_SERVERS=("${VIRL_PROD_SERVERS[@]}")
echo "VIRL servers in production: ${VIRL_SERVERS[@]}"
num_hosts=${#VIRL_SERVERS[@]}
if [ $num_hosts == 0 ]
then
    echo "No more VIRL candidate hosts available, failing."
    exit 127
fi

# Get the LOAD of each server based on number of active simulations (test cases)
VIRL_SERVER_LOAD=()
for index in "${!VIRL_SERVERS[@]}"; do
    VIRL_SERVER_LOAD[${index}]=$(ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${VIRL_SERVERS[$index]} "list-testcases | grep session | wc -l")
done

# Pick the least loaded server
VIRL_SERVER=""
least_load_server_idx=$(echo "${VIRL_SERVER_LOAD[*]}" | tr -s ' ' '\n' | awk '{print($0" "NR)}' | sort -g -k1,1 | head -1 | cut -f2 -d' ')
least_load_server=${VIRL_SERVERS[$least_load_server_idx-1]}
VIRL_SERVER=($least_load_server)

echo "Selected VIRL servers: ${VIRL_SERVER[@]}"

VIRL_DIR_LOC="/tmp"
VPP_PKGS_VIRL=(${VPP_PKGS[@]})

# Prepend directory location at remote host to package file list
for index in "${!VPP_PKGS_VIRL[@]}"; do
    VPP_PKGS_VIRL[${index}]=${VIRL_DIR_LOC}/${VPP_PKGS_VIRL[${index}]}
done

echo "Updated file names: " ${VPP_PKGS_VIRL[@]}

cat ${VIRL_PKEY}
# Copy the files to VIRL host
scp ${SSH_OPTIONS} *.${PACKAGE} \
    ${VIRL_USERNAME}@${VIRL_SERVER}:${VIRL_DIR_LOC}/

result=$?
if [ "${result}" -ne "0" ]; then
    echo "Failed to copy vpp package files to virl host"
    echo ${result}
    exit ${result}
fi

function stop_virl_simulation {
    ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${VIRL_SERVER}\
        "stop-testcase ${VIRL_SID}"
}

# Upon script exit, cleanup the VIRL simulation execution
trap stop_virl_simulation EXIT

# Start a simulation on VIRL server
echo "Starting simulation on VIRL server"

# Get given VIRL server limits for max. number of VMs and IPs
max_ips=$(get_max_ip_nr ${VIRL_SERVER})
max_ips_from_sims=$(($(get_max_sim_nr ${VIRL_SERVER[${index}]})*IPS_PER_SIMULATION))
# Set quota to lower value
IP_QUOTA=$([ $max_ips -le $max_ips_from_sims ] && echo "$max_ips" || echo "$max_ips_from_sims")

# Start the simulation
VIRL_SID=$(ssh ${SSH_OPTIONS} \
    ${VIRL_USERNAME}@${VIRL_SERVER} \
    "start-testcase -vv --quota ${IP_QUOTA} --copy ${VIRL_TOPOLOGY} \
    --release ${VIRL_RELEASE} ${VPP_PKGS_VIRL[@]}")
retval=$?
if [ ${retval} -ne "0" ]; then
    echo "VIRL simulation start failed on ${VIRL_SERVER}"
    exit ${retval}
fi

if [[ ! "${VIRL_SID}" =~ session-[a-zA-Z0-9_]{6} ]]; then
    echo "No VIRL session ID reported."
    exit 127
fi

echo ${VIRL_SID}

ssh_do ${VIRL_USERNAME}@${VIRL_SERVER} cat /scratch/${VIRL_SID}/topology.yaml

# Download the topology file from VIRL session
scp ${SSH_OPTIONS} \
    ${VIRL_USERNAME}@${VIRL_SERVER}:/scratch/${VIRL_SID}/topology.yaml \
    topologies/enabled/topology_VIRL.yaml

retval=$?
if [ ${retval} -ne "0" ]; then
    echo "Failed to copy topology file from VIRL simulation"
    exit ${retval}
fi

set +x
echo "****************************************************************************************************************************************"
echo "3rd step: Start the simulation on the VIRL server                                                                               FINISHED"
echo "****************************************************************************************************************************************"
set -x


# 4th step: Run functional test suites

pykwalify -s ${SCRIPT_DIR}/resources/topology_schemas/3_node_topology.sch.yaml \
          -s ${SCRIPT_DIR}/resources/topology_schemas/topology.sch.yaml \
          -d ${SCRIPT_DIR}/topologies/enabled/topology_VIRL.yaml \
          -vvv
if [ "$?" -ne "0" ]; then
    echo "Topology schema validation failed."
    echo "However, the tests will start."
fi

echo Running functional tests on the VIRL system...

echo "PYTHONPATH=`pwd` pybot -L TRACE -W 136\
    -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology_VIRL.yaml \
    --suite "tests.func" \
    --include vm_envAND3_node_single_link_topo \
    --include vm_envAND3_node_double_link_topo \
    --exclude PERFTEST \
    --exclude ${SKIP_PATCH} \
    --noncritical ${NON_CRITICAL_TESTS} \
    --outputdir ${LOG_PATH} \
    tests/"

PYTHONPATH=`pwd` pybot -L TRACE -W 136\
    -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology_VIRL.yaml \
    --suite "tests.func" \
    --include vm_envAND3_node_single_link_topo \
    --include vm_envAND3_node_double_link_topo \
    --exclude PERFTEST \
    --exclude ${SKIP_PATCH} \
    --noncritical ${NON_CRITICAL_TESTS} \
    --outputdir ${LOG_PATH} \
    tests/
RC=$(echo $?)

set +x
echo "****************************************************************************************************************************************"
echo "4th step: Run functional tests                                                                                                  FINISHED"
echo "****************************************************************************************************************************************"
set -x

# Log the final result
if [ ${RC} -eq 0 ]; then
    RETURN_STATUS=0
    set +x
    echo
    echo "========================================================================================================================================"
    echo "Final result of all tests:                                                                                                      | PASS |"
    echo "All critical tests have passed."
    echo "========================================================================================================================================"
    echo
    set -x
elif [ ${MORE_FAILS} -eq 0 ]; then
    RETURN_STATUS=1
    if [ ${RC} -eq 1 ]; then
        HLP_STR="test has"
    else
        HLP_STR="tests have"
    fi
    set +x
    echo
    echo "========================================================================================================================================"
    echo "Final result of all tests:                                                                                                      | FAIL |"
    echo "${RC} critical ${HLP_STR} failed."
    echo "========================================================================================================================================"
    echo
    set -x
else
    RETURN_STATUS=1
    set +x
    echo
    echo "========================================================================================================================================"
    echo "Final result of all tests:                                                                                                      | FAIL |"
    echo "More then 250 critical tests have failed in one test loop."
    echo "========================================================================================================================================"
    echo
    set -x
fi


# 5th step: Archive artifacts
mkdir archive
for i in ${ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${LOG_PATH}/${i} | tr '\n' ' ' ) archive/
done

echo Log files copied to archive directory.

exit ${RETURN_STATUS}
