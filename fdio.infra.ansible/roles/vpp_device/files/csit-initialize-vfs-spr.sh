#!/usr/bin/env bash

# Copyright (c) 2023 Cisco and/or its affiliates.
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

# Add Intel Corporation Ethernet Controller 10G X550T to blacklist.
PCI_BLACKLIST=($(lspci -Dmmd ':1563:0200' | cut -f1 -d' '))
# Add Intel Corporation Ethernet Controller E810-C for 100GbE QSFP to whitelist.
PCI_WHITELIST+=($(lspci -Dmmd ':1592:0200' | cut -f1 -d' '))

# See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.

declare -A PF_INDICES
# Intel NICs
PF_INDICES["0000:2a:00.0"]=0
PF_INDICES["0000:2c:00.0"]=1
PF_INDICES["0000:3d:00.0"]=0
PF_INDICES["0000:3f:00.0"]=1
