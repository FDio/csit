# Copyright (c) 2018 Cisco and/or its affiliates.
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

set -exuo pipefail

# Build docker image (with vpp, ligato and vpp-agent), put it to ${DOWNLOAD_DIR}/.
#
# Access rights needed for:
# - "wget", "git clone", "dpdk -x", "cd" above ${CSIT_DIR}.
# - "sudo" without password.
# - With sudo:
#   - "dpdk -i" is allowed.
#   - "docker" commands have everything they needs.
# Variables read:
# - BASH_FRAGMENT_DIR - Path to directory holding VPP gather script.
# - DOWNLOAD_DIR - Path to directory where pybot takes the build to test from.
# - CSIT_DIR - Path to existing directory with root of local CSIT git repository.
# Files read:
# - ${CSIT_DIR}/VPP_AGENT_STABLE_VER - Vpp agent version to use.
# Directories updated:
# - ${DOWNLOAD_DIR} - Docker image stored, VPP *.deb stored and deleted.
# - /tmp/vpp - VPP is unpacked there, not cleaned afterwards.
# - ${CSIT_DIR}/vpp-agent - Created, vpp-agent git repo si cloned there.
#   - Also, various temporary files are stored there.
# System consequences:
# - Docker package is installed.
# - Presumably dockerd process is started.
# - The ligato/dev-vpp-agent docker image is downloaded.
# - Results of subsequent image manipulation are probably left lingering.
# Other hardcoded values:
# - Docker .deb file name to download and install.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh
# TODO: What is the best order of description items?

# TODO: Many of the following comments act as abstraction.
#   But the abstracted blocks are mostly one-liners (plus "|| die"),
#   so perhaps it is not worth introducing fragments/functions for the blocks.

source "${BASH_FRAGMENT_DIR}/verify/gather_vpp.sh"

# Extract VPP API to specific folder
# FIXME: Make sure /tmp/vpp/ exists. Should we clean it?
dpkg -x "${DOWNLOAD_DIR}"/vpp_*.deb /tmp/vpp || {
    die 1 "Failed to extract VPP packages for kubernetes!"
}

ligato_repo_url="https://github.com/ligato/"
vpp_agent_stable_ver=$(cat ${CSIT_DIR}/VPP_AGENT_STABLE_VER) || {
    die 1 "Cat failed."
}
docker_deb="docker-ce_18.03.0~ce-0~ubuntu_amd64.deb"

# Clone & checkout stable vpp-agent
cd "${CSIT_DIR}" || die 1 "Cd failed."
git clone -b "${vpp_agent_stable_ver}" --single-branch \
    "${ligato_repo_url}/vpp-agent" "vpp-agent" || {
    die 1 "Failed to run: git clone ${ligato_repo_url}/vpp-agent!"
}
cd "vpp-agent" || die 1 "Cd failed."

# Install Docker
wget -q "https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/${docker_deb}" || {
    die 1 "Failed to download Docker package!"
}

sudo dpkg -i "${docker_deb}" || {
    die 1 "Failed to install Docker!"
}

# Pull ligato/dev_vpp_agent docker image and re-tag as local
sudo docker pull "ligato/dev-vpp-agent:${vpp_agent_stable_ver}" || {
    die 1 "Failed to pull Docker image!"
}

sudo docker tag "ligato/dev-vpp-agent:${vpp_agent_stable_ver}"\
    "dev_vpp_agent:latest" || {
    die 1 "Failed to tag Docker image!"
}

# Start dev_vpp_agent container as daemon
sudo docker run --rm -itd --name "agentcnt" "dev_vpp_agent" bash || {
    die 1 "Failed to run Docker image!"
}

# Copy latest vpp api into running container
sudo docker exec agentcnt rm -rf "agentcnt:/usr/share/vpp/api" || {
    die 1 "Failed to remove previous API!"
}
sudo docker cp "/tmp/vpp/usr/share/vpp/api" "agentcnt:/usr/share/vpp" || {
    die 1 "Failed to copy files Docker image!"
}
## bash -c is needed so that the globs are expanded at the correct place.
#sudo docker exec agentcnt bash -c "rm -vf \
#    /opt/vpp-agent/dev/vpp/build-root/vpp*.deb /opt/vpp/*.deb" || {
#    die 1 "Failed to remove previous debian packages!"
#}
#for f in "${DOWNLOAD_DIR}"/*; do
#    sudo docker cp "$f" "agentcnt:/opt/vpp-agent/dev/vpp/build-root"/ || {
#        die 1 "Failed to copy files Docker image!"
#    }
#done

# Recompile vpp-agent
sudo docker exec -i agentcnt \
    script -qec '. ~/.bashrc; cd /go/src/github.com/ligato/vpp-agent && make generate && make install' || {
    die 1 "Failed to recompile vpp-agent in Docker image!"
}
# Make sure .deb files of other version are not present.
sudo docker exec agentcnt bash -c "rm -vf \
    /opt/vpp-agent/dev/vpp/build-root/vpp*.deb /opt/vpp/*.deb" || {
    die 1 "Failed to remove VPP debian packages!"
}
for f in "${DOWNLOAD_DIR}"/*; do
    sudo docker cp "$f" "agentcnt:/opt/vpp-agent/dev/vpp/build-root"/ || {
        die 1 "Failed to copy files Docker image!"
    }
done
# Save container state
sudo docker commit `sudo docker ps -q` "dev_vpp_agent:latest" || {
    die 1 "Failed to commit state of Docker image!"
}

# Build prod_vpp_agent docker image
cd "docker/prod" || die 1 "Cd failed."
sudo docker build --tag "prod_vpp_agent" --no-cache . || {
    die 1 "Failed to build Docker image!"
}
# Export Docker image
sudo docker save "prod_vpp_agent" | gzip > "prod_vpp_agent.tar.gz" || {
    die 1 "Failed to save Docker image!"
}
docker_image=$(readlink -e "prod_vpp_agent.tar.gz") || die 1 "Readlink failed."
rm -r "${DOWNLOAD_DIR}/vpp"* || die 1 "Rm failed."
mv "${docker_image}" "${DOWNLOAD_DIR}"/ || die 1 "Mv failed."
