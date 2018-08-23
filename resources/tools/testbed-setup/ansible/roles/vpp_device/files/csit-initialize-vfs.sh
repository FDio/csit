#!/usr/bin/env bash

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

# CSIT SRIOV VF initialization.

set -euo pipefail

# Add Intel Corporation Ethernet Controller 10G X550T to blacklist.
# See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
pci_blacklist=($(lspci -Dmmd ':1563:0200' | cut -f1 -d' '))

# Add Intel Corporation Ethernet Controller X710 for 10GbE SFP+ to whitelist.
# See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
pci_whitelist=($(lspci -Dmmd ':1572:0200' | cut -f1 -d' '))

# Initilize whitelisted NICs with maximum number of VFs.
for pci_addr in ${pci_whitelist[@]}; do
    if ! [[ ${pci_blacklist[*]} =~ "${pci_addr}" ]]; then
        case "${1:-start}" in
            "start" )
                pci_path="/sys/bus/pci/devices"
                sriov_totalvfs=$(cat "${pci_path}"/"${pci_addr}"/sriov_totalvfs)
                ;;
            "stop" )
                sriov_totalvfs=0
                ;;
        esac
        echo ${sriov_totalvfs} > /sys/bus/pci/devices/"${pci_addr}"/sriov_numvfs
    fi
done
