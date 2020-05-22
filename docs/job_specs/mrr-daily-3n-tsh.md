# 3n-tsh
### tests 204
### job hrs est. 9.5
### job hrs real xx.x
### test mins est. 2.8
### test mins real x.x
## ./container_memif
### intel-x520-da2
#### dpdk-vfio-pci
##### eth-l2bdbasemaclrn-eth-2memif-1lxc
tc01-64B-1c-eth-l2bdbasemaclrn-eth-2memif-1lxc-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-eth-2memif-1lxc-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-eth-2memif-1lxc-mrr
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2memif-1lxc
#2c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2memif-1lxc
#4c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2memif-1lxc
##### dot1q-l2bdbasemaclrn-eth-2memif-1dcr
tc01-64B-1c-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
tc02-64B-2c-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
tc03-64B-4c-dot1q-l2bdbasemaclrn-eth-2memif-1dcr-mrr
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2memif-1dcr
#2c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2memif-1dcr
#4c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2memif-1dcr
##### eth-l2xcbase-eth-2memif-1dcr
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2memif-1dcr
#2c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2memif-1dcr
#4c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2memif-1dcr
tc01-64B-1c-eth-l2xcbase-eth-2memif-1dcr-mrr
tc02-64B-2c-eth-l2xcbase-eth-2memif-1dcr-mrr
tc03-64B-4c-eth-l2xcbase-eth-2memif-1dcr-mrr
##### eth-l2xcbase-eth-2memif-1lxc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2memif-1lxc
#2c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2memif-1lxc
#4c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2memif-1lxc
tc01-64B-1c-eth-l2xcbase-eth-2memif-1lxc-mrr
tc02-64B-2c-eth-l2xcbase-eth-2memif-1lxc-mrr
tc03-64B-4c-eth-l2xcbase-eth-2memif-1lxc-mrr
##### ethip4-ip4base-eth-2memif-1dcr
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2memif-1dcr
#2c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2memif-1dcr
#4c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2memif-1dcr
tc01-64B-1c-ethip4-ip4base-eth-2memif-1dcr-mrr
tc02-64B-2c-ethip4-ip4base-eth-2memif-1dcr-mrr
tc03-64B-4c-ethip4-ip4base-eth-2memif-1dcr-mrr
## ./crypto
### intel-x520-da2
#### dpdk-vfio-pci
##### ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
#1c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
#2c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
#4c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
#1c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
#2c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
#4c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
tc04-1518B-1c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc05-1518B-2c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc06-1518B-4c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc10-IMIX-1c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc11-IMIX-2c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc12-IMIX-4c-ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
##### ethip4ipsec4tnlsw-ip4base-int-aes256gcm
#1c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
#2c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
#4c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
#1c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
#2c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
#4c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
tc04-1518B-1c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
tc05-1518B-2c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
tc06-1518B-4c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
tc10-IMIX-1c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
tc11-IMIX-2c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
tc12-IMIX-4c-ethip4ipsec4tnlsw-ip4base-int-aes256gcm-mrr
##### ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
#1c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
#2c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
#4c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
#1c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
#2c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
#4c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
tc04-1518B-1c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc05-1518B-2c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc06-1518B-4c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc10-IMIX-1c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc11-IMIX-2c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc12-IMIX-4c-ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
##### ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
#1c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
#2c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
#4c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
#1c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
#2c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
#4c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
tc04-1518B-1c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
tc05-1518B-2c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
tc06-1518B-4c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
tc10-IMIX-1c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
tc11-IMIX-2c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
tc12-IMIX-4c-ethip4ipsec1000tnlsw-ip4base-int-aes256gcm-mrr
##### ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
#1c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
#2c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
#4c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
#1c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
#2c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
#4c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
tc04-1518B-1c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc05-1518B-2c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc06-1518B-4c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc10-IMIX-1c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc11-IMIX-2c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
tc12-IMIX-4c-ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha-mrr
##### ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
#1c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
#2c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
#4c AND 1518b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
#1c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
#2c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
#4c AND imix AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
tc04-1518B-1c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
tc05-1518B-2c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
tc06-1518B-4c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
tc10-IMIX-1c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
tc11-IMIX-2c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
tc12-IMIX-4c-ethip4ipsec10000tnlsw-ip4base-int-aes256gcm-mrr
## ./ip4
### intel-x520-da2
#### dpdk-vfio-pci
##### ethip4-ip4base
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base
tc01-64B-1c-ethip4-ip4base-mrr
tc02-64B-2c-ethip4-ip4base-mrr
tc03-64B-4c-ethip4-ip4base-mrr
##### ethip4-ip4scale20k
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale20k
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale20k
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale20k
tc01-64B-1c-ethip4-ip4scale20k-mrr
tc02-64B-2c-ethip4-ip4scale20k-mrr
tc03-64B-4c-ethip4-ip4scale20k-mrr
##### ethip4-ip4scale200k
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale200k
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale200k
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale200k
tc01-64B-1c-ethip4-ip4scale200k-mrr
tc02-64B-2c-ethip4-ip4scale200k-mrr
tc03-64B-4c-ethip4-ip4scale200k-mrr
##### ethip4-ip4scale2m
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale2m
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale2m
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4scale2m
tc01-64B-1c-ethip4-ip4scale2m-mrr
tc02-64B-2c-ethip4-ip4scale2m-mrr
tc03-64B-4c-ethip4-ip4scale2m-mrr
##### dot1q-ip4base
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-ip4base
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-ip4base
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-ip4base
tc01-64B-1c-dot1q-ip4base-mrr
tc02-64B-2c-dot1q-ip4base-mrr
tc03-64B-4c-dot1q-ip4base-mrr
##### ethip4udp-ip4base-iacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-iacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-iacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-iacl50sf-10kflows
tc01-64B-1c-ethip4udp-ip4base-iacl50sf-10kflows-mrr
tc02-64B-2c-ethip4udp-ip4base-iacl50sf-10kflows-mrr
tc03-64B-4c-ethip4udp-ip4base-iacl50sf-10kflows-mrr
##### ethip4udp-ip4base-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-iacl50sl-10kflows
tc01-64B-1c-ethip4udp-ip4base-iacl50sl-10kflows-mrr
tc02-64B-2c-ethip4udp-ip4base-iacl50sl-10kflows-mrr
tc03-64B-4c-ethip4udp-ip4base-iacl50sl-10kflows-mrr
##### ethip4udp-ip4base-oacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-oacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-oacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-oacl50sf-10kflows
tc01-64B-1c-ethip4udp-ip4base-oacl50sf-10kflows-mrr
tc02-64B-2c-ethip4udp-ip4base-oacl50sf-10kflows-mrr
tc03-64B-4c-ethip4udp-ip4base-oacl50sf-10kflows-mrr
##### ethip4udp-ip4base-oacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-oacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-oacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-oacl50sl-10kflows
tc01-64B-1c-ethip4udp-ip4base-oacl50sl-10kflows-mrr
tc02-64B-2c-ethip4udp-ip4base-oacl50sl-10kflows-mrr
tc03-64B-4c-ethip4udp-ip4base-oacl50sl-10kflows-mrr
##### ethip4udp-ip4base-nat44
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-nat44
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-nat44
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4base-nat44
tc01-64B-1c-ethip4udp-ip4base-nat44-mrr
tc02-64B-2c-ethip4udp-ip4base-nat44-mrr
tc03-64B-4c-ethip4udp-ip4base-nat44-mrr
##### ethip4udp-ip4scale1000-udpsrcscale15-nat44
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4scale1000-udpsrcscale15-nat44
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4scale1000-udpsrcscale15-nat44
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4udp-ip4scale1000-udpsrcscale15-nat44
tc01-64B-1c-ethip4udp-ip4scale1000-udpsrcscale15-nat44-mrr
tc02-64B-2c-ethip4udp-ip4scale1000-udpsrcscale15-nat44-mrr
tc03-64B-4c-ethip4udp-ip4scale1000-udpsrcscale15-nat44-mrr
## ./ip4_tunnels
### intel-x520-da2
#### dpdk-vfio-pci
##### dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
tc01-64B-1c-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-mrr
tc02-64B-2c-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-mrr
tc03-64B-4c-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan-mrr
##### dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
tc01-64B-1c-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-mrr
tc02-64B-2c-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-mrr
tc03-64B-4c-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan-mrr
##### ethip4vxlan-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
tc01-64B-1c-ethip4vxlan-l2bdbasemaclrn-mrr
tc02-64B-2c-ethip4vxlan-l2bdbasemaclrn-mrr
tc03-64B-4c-ethip4vxlan-l2bdbasemaclrn-mrr
##### ethip4vxlan-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
tc01-64B-1c-ethip4vxlan-l2xcbase-mrr
tc02-64B-2c-ethip4vxlan-l2xcbase-mrr
tc03-64B-4c-ethip4vxlan-l2xcbase-mrr
## ./ip6
### intel-x520-da2
#### dpdk-vfio-pci
##### ethip6-ip6base
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6base
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6base
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6base
tc01-78B-1c-ethip6-ip6base-mrr
tc02-78B-2c-ethip6-ip6base-mrr
tc03-78B-4c-ethip6-ip6base-mrr
##### ethip6-ip6scale20k
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale20k
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale20k
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale20k
tc01-78B-1c-ethip6-ip6scale20k-mrr
tc02-78B-2c-ethip6-ip6scale20k-mrr
tc03-78B-4c-ethip6-ip6scale20k-mrr
##### ethip6-ip6scale200k
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale200k
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale200k
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale200k
tc01-78B-1c-ethip6-ip6scale200k-mrr
tc02-78B-2c-ethip6-ip6scale200k-mrr
tc03-78B-4c-ethip6-ip6scale200k-mrr
##### ethip6-ip6scale2m
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale2m
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale2m
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6-ip6scale2m
tc01-78B-1c-ethip6-ip6scale2m-mrr
tc02-78B-2c-ethip6-ip6scale2m-mrr
tc03-78B-4c-ethip6-ip6scale2m-mrr
##### dot1q-ip6base
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-ip6base
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-ip6base
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-ip6base
tc01-78B-1c-dot1q-ip6base-mrr
tc02-78B-2c-dot1q-ip6base-mrr
tc03-78B-4c-dot1q-ip6base-mrr
## ./ip6_tunnels
## ./l2
### intel-x520-da2
#### dpdk-vfio-pci
##### eth-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn
tc01-64B-1c-eth-l2bdbasemaclrn-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-mrr
##### eth-l2bdscale10kmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale10kmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale10kmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale10kmaclrn
tc01-64B-1c-eth-l2bdscale10kmaclrn-mrr
tc02-64B-2c-eth-l2bdscale10kmaclrn-mrr
tc03-64B-4c-eth-l2bdscale10kmaclrn-mrr
##### eth-l2bdscale100kmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale100kmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale100kmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale100kmaclrn
tc01-64B-1c-eth-l2bdscale100kmaclrn-mrr
tc02-64B-2c-eth-l2bdscale100kmaclrn-mrr
tc03-64B-4c-eth-l2bdscale100kmaclrn-mrr
##### eth-l2bdscale1mmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale1mmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale1mmaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdscale1mmaclrn
tc01-64B-1c-eth-l2bdscale1mmaclrn-mrr
tc02-64B-2c-eth-l2bdscale1mmaclrn-mrr
tc03-64B-4c-eth-l2bdscale1mmaclrn-mrr
##### dot1q-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn
tc01-64B-1c-dot1q-l2bdbasemaclrn-mrr
tc02-64B-2c-dot1q-l2bdbasemaclrn-mrr
tc03-64B-4c-dot1q-l2bdbasemaclrn-mrr
##### eth-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase
tc01-64B-1c-eth-l2xcbase-mrr
tc02-64B-2c-eth-l2xcbase-mrr
tc03-64B-4c-eth-l2xcbase-mrr
##### dot1q-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase
tc01-64B-1c-dot1q-l2xcbase-mrr
tc02-64B-2c-dot1q-l2xcbase-mrr
tc03-64B-4c-dot1q-l2xcbase-mrr
##### eth-l2patch
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2patch
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2patch
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2patch
tc01-64B-1c-eth-l2patch-mrr
tc02-64B-2c-eth-l2patch-mrr
tc03-64B-4c-eth-l2patch-mrr
##### eth-l2bdbasemaclrn-iacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-iacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-iacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-iacl50sf-10kflows
tc01-64B-1c-eth-l2bdbasemaclrn-iacl50sf-10kflows-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-iacl50sf-10kflows-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-iacl50sf-10kflows-mrr
##### eth-l2bdbasemaclrn-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-iacl50sl-10kflows
tc01-64B-1c-eth-l2bdbasemaclrn-iacl50sl-10kflows-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-iacl50sl-10kflows-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-iacl50sl-10kflows-mrr
##### eth-l2bdbasemaclrn-macip-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-macip-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-macip-iacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-macip-iacl50sl-10kflows
tc01-64B-1c-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-macip-iacl50sl-10kflows-mrr
##### eth-l2bdbasemaclrn-oacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-oacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-oacl50sf-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-oacl50sf-10kflows
tc01-64B-1c-eth-l2bdbasemaclrn-oacl50sf-10kflows-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-oacl50sf-10kflows-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-oacl50sf-10kflows-mrr
##### eth-l2bdbasemaclrn-oacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-oacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-oacl50sl-10kflows
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-oacl50sl-10kflows
tc01-64B-1c-eth-l2bdbasemaclrn-oacl50sl-10kflows-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-oacl50sl-10kflows-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-oacl50sl-10kflows-mrr
## ./lb
## ./nfv_density/dcr_memif/chain
## ./nfv_density/dcr_memif/chain_ipsec
## ./nfv_density/dcr_memif/pipeline
## ./nfv_density/vm_vhost/chain
## ./nfv_density/vm_vhost/chain_dot1qip4vxlan
## ./srv6
### intel-x520-da2
#### dpdk-vfio-pci
##### ethip6ip6-ip6base-srv6enc1sid
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
tc01-78B-1c-ethip6ip6-ip6base-srv6enc1sid-mrr
tc02-78B-2c-ethip6ip6-ip6base-srv6enc1sid-mrr
tc03-78B-4c-ethip6ip6-ip6base-srv6enc1sid-mrr
##### ethip6srhip6-ip6base-srv6enc2sids
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
tc01-78B-1c-ethip6srhip6-ip6base-srv6enc2sids-mrr
tc02-78B-2c-ethip6srhip6-ip6base-srv6enc2sids-mrr
tc03-78B-4c-ethip6srhip6-ip6base-srv6enc2sids-mrr
##### ethip6srhip6-ip6base-srv6enc2sids-nodecaps
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
tc01-78B-1c-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
tc02-78B-2c-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
tc03-78B-4c-ethip6srhip6-ip6base-srv6enc2sids-nodecaps-mrr
##### ethip6srhip6-ip6base-srv6proxy-dyn
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
tc01-78B-1c-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
tc02-78B-2c-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
tc03-78B-4c-ethip6srhip6-ip6base-srv6proxy-dyn-mrr
##### ethip6srhip6-ip6base-srv6proxy-masq
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
tc01-78B-1c-ethip6srhip6-ip6base-srv6proxy-masq-mrr
tc02-78B-2c-ethip6srhip6-ip6base-srv6proxy-masq-mrr
tc03-78B-4c-ethip6srhip6-ip6base-srv6proxy-masq-mrr
##### ethip6srhip6-ip6base-srv6proxy-stat
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
#1c AND 78b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
tc01-78B-1c-ethip6srhip6-ip6base-srv6proxy-stat-mrr
tc02-78B-2c-ethip6srhip6-ip6base-srv6proxy-stat-mrr
tc03-78B-4c-ethip6srhip6-ip6base-srv6proxy-stat-mrr
## ./tcp
## ./vm_vhost
### intel-x520-da2
#### dpdk-vfio-pci
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
tc01-64B-1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
tc01-64B-1c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc02-64B-2c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc03-64B-4c-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
##### dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
tc01-64B-1c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
tc02-64B-2c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
tc03-64B-4c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
##### dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
tc01-64B-1c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc02-64B-2c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc03-64B-4c-dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
##### eth-l2xcbase-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm
tc01-64B-1c-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
tc02-64B-2c-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
tc03-64B-4c-eth-l2xcbase-eth-2vhostvr1024-1vm-mrr
##### eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
tc01-64B-1c-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc02-64B-2c-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc03-64B-4c-eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
##### dot1q-l2xcbase-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm
tc01-64B-1c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
tc02-64B-2c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
tc03-64B-4c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-mrr
##### dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
tc01-64B-1c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc02-64B-2c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc03-64B-4c-dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc-mrr
##### ethip4-ip4base-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm
tc01-64B-1c-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr
tc02-64B-2c-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr
tc03-64B-4c-ethip4-ip4base-eth-2vhostvr1024-1vm-mrr
##### ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
tc01-64B-1c-ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4-mrr
tc02-64B-2c-ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4-mrr
tc03-64B-4c-ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4-mrr
##### ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm
tc01-64B-1c-ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
tc02-64B-2c-ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
tc03-64B-4c-ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-mrr
##### ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
#1c AND 64b AND mrr AND x520-da2 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
tc01-64B-1c-ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc02-64B-2c-ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
tc03-64B-4c-ethip4vxlan-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc-mrr
## ./vts
