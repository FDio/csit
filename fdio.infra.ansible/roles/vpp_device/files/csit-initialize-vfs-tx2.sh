#!/usr/bin/env bash

# Copyright (c) 2021 PANTHEON.tech and/or its affiliates.
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

# Add QLogic Corp. FastLinQ QL41000 Series 10/25/40/50GbE Controller to
# blacklist.
PCI_BLACKLIST=($(lspci -Dmmd ':8070:0200' | cut -f1 -d' '))
# Add I350 Gigabit Network Connection 1521 to blacklist.
PCI_BLACKLIST+=($(lspci -Dmmd ':1521:0200' | cut -f1 -d' '))
# Add MT27800 Family [ConnectX-5] 1017 to blacklist.
PCI_BLACKLIST+=($(lspci -Dmmd ':1017:0200' | cut -f1 -d' '))

# Add Intel Corporation Ethernet Controller XL710 for 40GbE QSFP+ to whitelist.
PCI_WHITELIST=($(lspci -Dmmd ':1583:0200' | cut -f1 -d' '))

# See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.

declare -A PF_INDICES
# Intel NICs
PF_INDICES["0000:05:00.0"]=0
PF_INDICES["0000:05:00.1"]=1
PF_INDICES["0000:91:00.0"]=0
PF_INDICES["0000:91:00.1"]=1
