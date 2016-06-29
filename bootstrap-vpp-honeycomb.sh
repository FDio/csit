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

# Source the VIRL server parameters:
source virl_params.sh

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

# Get the latest VPP deb packages:
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

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

VIRL_DIR_LOC="/tmp"
VPP_DEBS_FULL=(${VPP_DEBS[@]})

# Prepend directory location at remote host to deb file list
for index in "${!VPP_DEBS_FULL[@]}"; do
    VPP_DEBS_FULL[${index}]=${VIRL_DIR_LOC}/${VPP_DEBS_FULL[${index}]}
done

echo "Updated file names: " ${VPP_DEBS_FULL[@]}

cat ${VIRL_PKEY}
# Copy the files to VIRL host
scp ${SSH_OPTIONS} *.deb \
    ${VIRL_USERNAME}@${VIRL_SERVER}:${VIRL_DIR_LOC}/

result=$?
if [ "${result}" -ne "0" ]; then
    echo "Failed to copy vpp deb files to VIRL host"
    echo ${result}
    exit ${result}
fi

set +x
echo "******************************************************************************"
echo "1st step: Download VPP packages and copy them to VIRL host            FINISHED"
echo "******************************************************************************"
set -x

# Get the latest Honeycomb:
URL="https://nexus.fd.io/service/local/artifact/maven/content"
REPO="fd.io.snapshot"
GROUP="io.fd.honeycomb.v3po"
ARTIFACT="v3po-karaf"
VERSION="1.0.0-SNAPSHOT"
EXT="tar.gz"

rm -f *.${EXT}
curl "${URL}?r=${REPO}&g=${GROUP}&a=${ARTIFACT}&v=${VERSION}&e=${EXT}" -O -J
result=$?
if [ "${result}" -ne "0" ]; then
    echo "Failed to download the latest Honeycomb package"
    echo ${result}
    exit ${result}
fi

HC_PKG=(*.tar.gz)
echo "Honeycomb package: " ${HC_PKG}

# Prepend directory location at remote host to Honeycomb package
HC_PKG_FULL=${VIRL_DIR_LOC}/${HC_PKG}
echo "Updated file name: " ${HC_PKG_FULL}

# Copy the Honeycomb package to VIRL host:
scp ${SSH_OPTIONS} ${HC_PKG} ${VIRL_USERNAME}@${VIRL_SERVER}:${VIRL_DIR_LOC}/

result=$?
if [ "${result}" -ne "0" ]; then
    echo "Failed to copy the Honeycomb package to VIRL host"
    echo ${result}
    exit ${result}
fi

set +x
echo "******************************************************************************"
echo "2nd step: Download Honeycomb package and copy it to VIRL host         FINISHED"
echo "******************************************************************************"
set -x

# Start a simulation on VIRL server
echo "Starting simulation on VIRL server"

function stop_virl_simulation {
    ssh ${SSH_OPTIONS} ${VIRL_USERNAME}@${VIRL_SERVER}\
        "stop-testcase ${VIRL_SID}"
}

VIRL_SID=$(ssh ${SSH_OPTIONS} \
    ${VIRL_USERNAME}@${VIRL_SERVER} \
    "start-testcase -c double-ring-nested -d ${HC_PKG_FULL} ${VPP_DEBS_FULL[@]}")
retval=$?
if [ "$?" -ne "0" ]; then
    echo "VIRL simulation start failed"
    exit ${retval}
fi

if [[ ! "${VIRL_SID}" =~ session-[a-zA-Z0-9_]{6} ]]; then
    echo "No VIRL session ID reported."
    exit 127
fi

# Upon script exit, cleanup the simulation execution
trap stop_virl_simulation EXIT
echo ${VIRL_SID}

ssh_do ${VIRL_USERNAME}@${VIRL_SERVER} cat /scratch/${VIRL_SID}/topology.yaml

# Download the topology file from virl session
scp ${SSH_OPTIONS} \
    ${VIRL_USERNAME}@${VIRL_SERVER}:/scratch/${VIRL_SID}/topology.yaml \
    topologies/enabled/topology.yaml

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

virtualenv --system-site-packages env
. env/bin/activate

echo pip install
pip install -r ${SCRIPT_DIR}/requirements.txt

pykwalify -s ${SCRIPT_DIR}/resources/topology_schemas/3_node_topology.sch.yaml \
          -s ${SCRIPT_DIR}/resources/topology_schemas/topology.sch.yaml \
          -d ${SCRIPT_DIR}/topologies/enabled/topology.yaml \
          -vvv

if [ "$?" -ne "0" ]; then
    echo "Topology schema validation failed."
    echo "However, the tests will start."
fi

set +x
echo "******************************************************************************"
echo "4th step: Start virtual env and install requirements                  FINISHED"
echo "******************************************************************************"
set -x

PYTHONPATH=`pwd` pybot -L TRACE \
    -v TOPOLOGY_PATH:${SCRIPT_DIR}/topologies/enabled/topology.yaml \
    --include honeycomb_sanity \
    --noncritical EXPECTED_FAILING \
    tests/

set +x
echo "******************************************************************************"
echo "5th step: Run Honeycomb tests                                        FINISHED"
echo "******************************************************************************"
set -x
