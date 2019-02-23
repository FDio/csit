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

# Images settings
IMAGES="ubuntu-19.04-desktop-amd64"

# Cobbler settings
COBBLER_PASS=$(shell echo -e Csit1234 | openssl passwd -1 -stdin)
COBBLER_WEB_PASS="Csit1234"
COBBLER_IP_ADDR=$(shell hostname -I | cut -d' ' -f1)
COBBLER_HTTP_PORT="60080"

build:
	@docker build \
		--build-arg COBBLER_PASS=$(COBBLER_PASS) \
		--build-arg COBBLER_WEB_PASS=$(COBBLER_WEB_PASS) \
		--build-arg COBBLER_IP_ADDR=$(COBBLER_IP_ADDR) \
		--build-arg COBBLER_HTTP_PORT=$(COBBLER_HTTP_PORT) \
		--tag csit/cobbler .

run:
	@docker run \
		--detach \
		--volume /mnt:/mnt:ro \
		--publish 69:69/udp \
		--publish 60080:80 \
		--publish 60443:443 \
		--publish 25151:25151 \
		--name cobbler csit/cobbler:latest

setup:
	@docker exec -it cobbler cobbler get-loaders
	@docker exec -it cobbler cobbler sync
	@docker exec -it cobbler cobbler check

clear:
	@docker rmi --force csit/cobbler > /dev/null || true

clean:
	@docker rm --force cobbler > /dev/null || true

mount:
	@$(foreach image,$(IMAGES),\
		sudo mkdir -p /mnt/$(image);\
		echo mount -t iso9660 -o loop,ro -v /mnt/$(image).iso /mnt/$(image))

umount:
	@$(foreach image,$(IMAGES),\
		sudo umount /mnt/$(image))

tty:
	@docker exec -it cobbler /bin/bash

all: build run setup

