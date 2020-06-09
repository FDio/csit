#!/bin/bash

# Copyright (c) 2020 Cisco and/or its affiliates.
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

# Clean.
docker rm --force pxe-dnsmasq
docker rmi pxe-dnsmasq

# Build.
docker build \
    --network host \
    --build-arg HTTP_PROXY="$http_proxy" \
    --build-arg HTTPS_PROXY="$http_proxy" \
    --build-arg NO_PROXY="$no_proxy" \
    --build-arg http_proxy="$http_proxy" \
    --build-arg https_proxy="$http_proxy" \
    --build-arg no_proxy="$no_proxy" \
    --tag pxe-dnsmasq .

# Run.
docker run \
    --rm \
    --name pxe-dnsmasq \
    --env "E_INT=$(ip -o -4 route show to default | awk '{print $5}')" \
    --env "E_ADD=$(hostname -I | awk '{print $1}')" \
    --cap-add NET_ADMIN \
    --net host pxe-dnsmasq
