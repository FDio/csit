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

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh -i priv_key -o StrictHostKeyChecking=no $@
}

VIRL_SERVER=10.30.51.28
VIRL_USERNAME=jenkins-in
VIRL_PKEY=priv_key

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
chmod 600 priv_key

# Temporarily download VPP packages from nexus.fd.io

if [ "${#}" -ne "0" ]; then
    arr=(${@})
    echo ${arr[0]}
else
    rm -f *.deb
    wget -q "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp/1.0.0-343~gc02f02d_amd64/vpp-1.0.0-343~gc02f02d_amd64.deb" || exit
    wget -q "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dbg/1.0.0-343~gc02f02d_amd64/vpp-dbg-1.0.0-343~gc02f02d_amd64.deb" || exit
    wget -q "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dev/1.0.0-343~gc02f02d_amd64/vpp-dev-1.0.0-343~gc02f02d_amd64.deb" || exit
    wget -q "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dpdk-dev/1.0.0-343~gc02f02d_amd64/vpp-dpdk-dev-1.0.0-343~gc02f02d_amd64.deb" || exit
    wget -q "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-dpdk-dkms/1.0.0-343~gc02f02d_amd64/vpp-dpdk-dkms-1.0.0-343~gc02f02d_amd64.deb" || exit
    wget -q "https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp/vpp-lib/1.0.0-343~gc02f02d_amd64/vpp-lib-1.0.0-343~gc02f02d_amd64.deb" || exit
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
# Copy the files to VIRL host
scp -i ${VIRL_PKEY} -o StrictHostKeyChecking=no *.deb \
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
    ssh -i priv_key -o StrictHostKeyChecking=no ${VIRL_USERNAME}@${VIRL_SERVER}\
        "/home/jenkins-in/testcase-infra/bin/stop-testcase ${VIRL_SID}"
}

VIRL_SID=$(ssh -i priv_key -o StrictHostKeyChecking=no \
    ${VIRL_USERNAME}@${VIRL_SERVER} \
    "/home/jenkins-in/testcase-infra/bin/start-testcase -c double-ring-nested ${VPP_DEBS_FULL[@]}")
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
scp -i ${VIRL_PKEY} -o StrictHostKeyChecking=no \
    ${VIRL_USERNAME}@${VIRL_SERVER}:/scratch/${VIRL_SID}/topology.yaml \
    topologies/enabled/topology.yaml

retval=$?
if [ "$?" -ne "0" ]; then
    echo "Failed to copy topology file from VIRL simulation"
    exit ${retval}
fi


virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

PYTHONPATH=`pwd` pybot -L TRACE \
    -v TOPOLOGY_PATH:topologies/enabled/topology.yaml \
    --include vm_envAND3_node_single_link_topo \
    --include vm_envAND3_node_double_link_topo \
    --exclude PERFTEST \
    --noncritical EXPECTED_FAILING \
    tests/
