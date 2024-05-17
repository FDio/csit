# 1n-spr
## ./container_memif
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4-l2xcbase-eth-2memif-1dcr
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2xcbase-eth-2memif-1dcr
##### ethip4-l2bdbasemaclrn-eth-2memif-1dcr
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-eth-2memif-1dcr
##### ethip4-ip4base-eth-2memif-1dcr
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base-eth-2memif-1dcr
## ./crypto/ethip4
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4ipsec1tnlsw-ip4base-int-aes128cbc-hmac512sha
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4ipsec1tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec11tnlsw-ip4base-int-aes128cbc-hmac512sha
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4ipsec11tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1tnlsw-ip4base-policy-aes128cbc-hmac512sha
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4ipsec1tnlsw-ip4base-policy-aes128cbc-hmac512sha
##### ethip4ipsec1tptsw-ip4base-policy-aes128cbc-hmac512sha
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4ipsec1tptsw-ip4base-policy-aes128cbc-hmac512sha
## ./crypto/ethip6
### intel-e810
#### dpdk-vfio-pci
##### ethip6ipsec1tnlsw-ip6base-policy-aes128cbc-hmac512sha
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6ipsec1tnlsw-ip6base-policy-aes128cbc-hmac512sha
##### ethip6ipsec1tptsw-ip6base-policy-aes128cbc-hmac512sha
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6ipsec1tptsw-ip6base-policy-aes128cbc-hmac512sha
## ./flow
### intel-e810cq
#### avf
##### ethip4-flow-ip4-ipsec-ah
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-ipsec-ah
##### ethip4-flow-ip4-ipsec-esp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-ipsec-esp
##### ethip4-flow-ip4-l2tpv3oip
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-l2tpv3oip
##### ethip4-flow-ip4-ntuple-tcp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-ntuple-tcp
##### ethip4-flow-ip4-ntuple-udp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-ntuple-udp
##### ethip4-flow-ip4-tcp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-tcp
##### ethip4-flow-ip4-udp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip4-flow-ip4-udp
##### ethip6-flow-ip6-ntuple-tcp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip6-flow-ip6-ntuple-tcp
##### ethip6-flow-ip6-ntuple-udp
# k0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip6-flow-ip6-ntuple-udp
##### ethip6-flow-ip6-tcp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip6-flow-ip6-tcp
##### ethip6-flow-ip6-udp
# 0c AND 64b AND scapy AND e810cq AND drv_avf AND ethip6-flow-ip6-udp
#### dpdk-vfio-pci
##### ethip4-flow-ip4-gtpu
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-gtpu
##### ethip4-flow-ip4-ipsec-ah
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-ipsec-ah
##### ethip4-flow-ip4-ipsec-esp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-ipsec-esp
##### ethip4-flow-ip4-l2tpv3oip
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-l2tpv3oip
##### ethip4-flow-ip4-ntuple-tcp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-ntuple-tcp
##### ethip4-flow-ip4-ntuple-udp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-ntuple-udp
##### ethip4-flow-ip4-tcp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-tcp
##### ethip4-flow-ip4-udp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-flow-ip4-udp
##### ethip6-flow-ip6-ntuple-tcp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-flow-ip6-ntuple-tcp
##### ethip6-flow-ip6-ntuple-udp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-flow-ip6-ntuple-udp
##### ethip6-flow-ip6-tcp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-flow-ip6-tcp
##### ethip6-flow-ip6-udp
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-flow-ip6-udp
## ./interfaces
### intel-e810cq
#### dpdk-vfio-pci
##### ethicmp4-ip4base-eth-1tap
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethicmp4-ip4base-eth-1tap
##### ethicmp4-ip4base-eth-1tap-namespace
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethicmp4-ip4base-eth-1tap-namespace
##### ethip4-l2bdbasemaclrn-eth-2tap
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-eth-2tap
## ./ip4
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4-ip4base-adlalwlistbase
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base-adlalwlistbase
##### ethip4-ip4base-adlblklistbase
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base-adlblklistbase
##### ethip4-ip4base
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base
##### ethip4-ip4base-iacldstbase
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base-iacldstbase
##### ethip4-ip4base-ipolicemarkbase
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base-ipolicemarkbase
##### ethip4tcp-nat44det
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4tcp-nat44det
##### ethip4tcp-nat44ed
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4tcp-nat44ed
##### ethip4udp-nat44det
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4udp-nat44det
##### ethip4udp-nat44ed
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4udp-nat44ed
## ./ip4_tunnel/lisp
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4lisp-ip4base
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4lisp-ip4base
##### ethip4lispgpe-ip4base
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4lispgpe-ip4base
##### ethip4lispgpe-ip6base
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4lispgpe-ip6base
## ./ip4_tunnel
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4--ethip4udpgeneve-1tun-ip4base
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4--ethip4udpgeneve-1tun-ip4base
##### ethip4vxlan-l2bdbasemaclrn
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
##### ethip4vxlan-l2xcbase
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
## ./ip6
### intel-e810cq
#### dpdk-vfio-pci
##### ethip6-ip6base-adlalwlistbase
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-ip6base-adlalwlistbase
##### ethip6-ip6base-adlblklistbase
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-ip6base-adlblklistbase
##### ethip6-ip6base-iacldstbase
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-ip6base-iacldstbase
##### ethip6-ip6base-ipolicemarkbase
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-ip6base-ipolicemarkbase
##### ethip6-ip6base
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-ip6base
## ./ip6_tunnels/lisp
### intel-e810cq
#### dpdk-vfio-pci
##### ethip6lispgpe-ip4base
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6lispgpe-ip4base
##### ethip6lispgpe-ip6base
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6lispgpe-ip6base
## ./l2bd
### intel-e810cq
#### avf
##### ethip4-l2bdbasemaclrn
0c AND 64b AND scapy AND x710 AND drv_avf AND ethip4-l2bdbasemaclrn
#### dpdk-vfio-pci
##### ethip4-l2bdbasemaclrn
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn
##### ethip4-l2bdbasemaclrn-iacl1sf
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-iacl1sf
##### ethip4-l2bdbasemaclrn-iacl1sl
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-iacl1sl
##### ethip4-l2bdbasemaclrn-macip-iacl1sl
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-macip-iacl1sl
##### ethip4-l2bdbasemaclrn-oacl1sf
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-oacl1sf
##### ethip4-l2bdbasemaclrn-oacl1sl
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-oacl1sl
## ./l2patch
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4-l2patch
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2patch
## ./l2xc
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4-l2xcbase
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2xcbase
## ./srv6
### intel-e810cq
#### dpdk-vfio-pci
##### ethip6ip6-ip6base-srv6enc1sid
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
##### ethip6srhip6-ip6base-srv6enc2sids
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
##### ethip6srhip6-ip6base-srv6enc2sids-nodecaps
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
##### ethip6srhip6-ip6base-srv6proxy-dyn
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
##### ethip6srhip6-ip6base-srv6proxy-masq
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
##### ethip6srhip6-ip6base-srv6proxy-stat
0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
## ./stats
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4-l2xcbase-stats
0c AND 64b AND scapy AND x710 AND drv_vfio_pci AND ethip4-l2xcbase-stats
## ./vm/ethip4
### intel-e810cq
#### dpdk-vfio-pci
##### ethip4-ip4base-eth-2vhost-1vm
0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-ip4base-eth-2vhost-1vm
##### ethip4-l2bdbasemaclrn-eth-2vhost-1vm
# 0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-l2bdbasemaclrn-eth-2vhost-1vm
##### ethip4-l2xcbase-eth-2vhost-1vm
# 0c AND 64b AND scapy AND e810cq AND drv_vfio_pci AND ethip4-l2xcbase-eth-2vhost-1vm
## ./vm/ethip6
### intel-e810cq
#### dpdk-vfio-pci
##### ethip6-ip6base-eth-2vhost-1vm
# 0c AND 78b AND scapy AND e810cq AND drv_vfio_pci AND ethip6-ip6base-eth-2vhost-1vm
