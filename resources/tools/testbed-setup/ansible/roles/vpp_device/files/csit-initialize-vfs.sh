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

# CSIT SRIOV VF initialization and isolation.

set -euo pipefail

# Add Intel Corporation Ethernet Controller 10G X550T to blacklist.
# See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
pci_blacklist=($(lspci -Dmmd ':1563:0200' | cut -f1 -d' '))

# Add Intel Corporation Ethernet Controller X710 for 10GbE SFP+ to whitelist.
# See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
pci_whitelist=($(lspci -Dmmd ':1572:0200' | cut -f1 -d' '))

# Initilize whitelisted NICs with maximum number of VFs.
pci_idx=0
for pci_addr in ${pci_whitelist[@]}; do
    if ! [[ ${pci_blacklist[*]} =~ "${pci_addr}" ]]; then
        pci_path="/sys/bus/pci/devices/${pci_addr}"
        # SR-IOV initialization
        case "${1:-start}" in
            "start" )
                sriov_totalvfs=$(< "${pci_path}"/sriov_totalvfs)
                ;;
            "stop" )
                sriov_totalvfs=0
                ;;
        esac
        echo ${sriov_totalvfs} > "${pci_path}"/sriov_numvfs
        # SR-IOV 802.1Q isolation
        case "${1:-start}" in
            "start" )
                pf=$(basename "${pci_path}"/net/*)
                for vf in $(seq "${sriov_totalvfs}"); do
                    # PCI address index in array (pairing siblings).
                    vlan_pf_idx=$(( pci_idx % (${#pci_whitelist[@]} / 2) ))
                    # 802.1Q base offset.
                    vlan_bs_off=1100
                    # 802.1Q PF PCI address offset.
                    vlan_pf_off=$(( vlan_pf_idx * 100 + vlan_bs_off ))
                    # 802.1Q VF PCI address offset.
                    vlan_vf_off=$(( vlan_pf_off + vf - 1 ))
                    # VLAN string.
                    vlan_str="vlan ${vlan_vf_off}"
                    # MAC string.
                    mac5="$(printf '%x' ${pci_idx})"
                    mac6="$(printf '%x' $(( vf - 1 )))"
                    mac_str="mac ba:dc:0f:fe:${mac5}:${mac6}"
                    # Set 802.1Q VLAN id and MAC address
                    ip link set ${pf} vf $(( vf - 1 )) ${mac_str} ${vlan_str}
                    ip link set ${pf} vf $(( vf - 1 )) trust on
                    ip link set ${pf} vf $(( vf - 1 )) spoof off
                done
                pci_idx=$(( pci_idx + 1 ))
                ;;
        esac
    fi
done
