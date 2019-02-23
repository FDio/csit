# Copyright (c) 2019 Cisco and/or its affiliates.
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

build:
	@docker build \
		--build-arg cobbler_pass=$1$sshgkD9H$1pL64ybWVhO/EsRnioUNt. \
		--build-arg cobbler_web_pass=Csit1234 \
		--build-arg cobbler_ip_addr=$(shell hostname -I | cut -d' ' -f1) \
		--build-arg cobbler_http_port=60080 \
		--tag csit/cobbler .

run:
	@docker run \
		--detach \
		--net host \
		--volume /mnt:/mnt:ro \
		--name cobbler csit/cobbler:latest

setup:
	@docker exec -it cobbler cobbler get-loaders
	@docker exec -it cobbler cobbler sync
	@docker exec -it cobbler cobbler check
	@docker exec -it cobbler cobbler import \
		--path=/mnt/ubuntu-18.04.2-server-x86_64 \
		--name=ubuntu-18.04.2-server-x86_64 \
		--breed=ubuntu --os-version=bionic --arch=x86_64 \
		--kickstart=/var/lib/cobbler/kickstarts/ubuntu-18.04.2-server-x86_64.ks

clean:
	@docker rm --force cobbler > /dev/null || true

clear:
	@docker rmi --force csit/cobbler > /dev/null || true

mount:
	mkdir -p /mnt/ubuntu-18.04.2-server-x86_64
	mount -o loop,ro /mnt/ubuntu-18.04.2-server-x86_64.iso /mnt/ubuntu-18.04.2-server-x86_64

umount:
	umount /mnt/ubuntu-18.04.2-server-x86_64

tty:
	@docker exec -it cobbler /bin/bash

all: build mount run setup

