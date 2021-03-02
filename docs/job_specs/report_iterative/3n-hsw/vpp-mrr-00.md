# 3n-hsw
### tests 192
### job hrs est. 4.13
### job hrs real 4.13
### test mins est. 1.29
### test mins real 1.29
#
# Tests with avf driver are not executed on 3n-hsw systems as it requires
# enabling of SoftIOMMU that is quite difficult there.
#
## ./container_memif
## ./crypto
### intel-xl710
#### dpdk-vfio-pci
##### ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1tnlhw-ip4base-int-aes256gcm
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
##### ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
##### ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec4tnlsw-ip4base-int-aes256gcm
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlsw-ip4base-int-aes256gcm
##### ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
##### ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
1c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
1c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec10000tnlsw-ip4base-int-aes256gcm
##### ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
3c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
3c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlswasync-scheduler-ip4base-int-aes256gcm
##### ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec2tnlswasync-scheduler-ip4base-int-aes256gcm
##### ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec4tnlswasync-scheduler-ip4base-int-aes256gcm
##### ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
3c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
3c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND 1518b AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
2c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
3c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
4c AND imix AND mrr AND xl710 AND drv_vfio_pci AND ethip4ipsec8tnlswasync-scheduler-ip4base-int-aes256gcm
## ./ip4
### intel-xl710
#### dpdk-vfio-pci
##### ethip4-ip4base
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base
##### ethip4-ip4scale2m
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4scale2m
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4scale2m
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4scale2m
##### ethip4-ip4scale2m-rnd
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4scale2m-rnd
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4scale2m-rnd
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4scale2m-rnd
##### dot1q-ip4base
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-ip4base
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-ip4base
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-ip4base
## ./ip4_tunnels
### intel-xl710
#### dpdk-vfio-pci
##### ethip4vxlan-l2bdbasemaclrn
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4vxlan-l2bdbasemaclrn
##### ethip4vxlan-l2xcbase
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4vxlan-l2xcbase
## ./ip6
### intel-xl710
#### dpdk-vfio-pci
##### ethip6-ip6base
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6base
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6base
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6base
##### ethip6-ip6scale2m
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6scale2m
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6scale2m
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6scale2m
##### ethip6-ip6scale2m-rnd
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6scale2m-rnd
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6scale2m-rnd
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6-ip6scale2m-rnd
##### dot1q-ip6base
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-ip6base
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-ip6base
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-ip6base
## ./ip6_tunnels
## ./l2
### intel-xl710
#### dpdk-vfio-pci
##### eth-l2bdbasemaclrn
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn
##### eth-l2bdscale1mmaclrn
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdscale1mmaclrn
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdscale1mmaclrn
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdscale1mmaclrn
##### dot1q-l2bdbasemaclrn
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn
##### eth-l2xcbase
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase
##### dot1q-l2xcbase
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase
##### eth-l2patch
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2patch
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2patch
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2patch
## ./lb
## ./nfv_density/dcr_memif/chain
## ./nfv_density/dcr_memif/chain_ipsec
## ./nfv_density/dcr_memif/pipeline
## ./nfv_density/vm_vhost/chain
## ./nfv_density/vm_vhost/chain_dot1qip4vxlan
## ./srv6
### intel-xl710
#### dpdk-vfio-pci
##### ethip6ip6-ip6base-srv6enc1sid
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6ip6-ip6base-srv6enc1sid
##### ethip6srhip6-ip6base-srv6enc2sids
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids
##### ethip6srhip6-ip6base-srv6enc2sids-nodecaps
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6enc2sids-nodecaps
##### ethip6srhip6-ip6base-srv6proxy-dyn
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-dyn
##### ethip6srhip6-ip6base-srv6proxy-masq
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-masq
##### ethip6srhip6-ip6base-srv6proxy-stat
1c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
2c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
4c AND 78b AND mrr AND xl710 AND drv_vfio_pci AND ethip6srhip6-ip6base-srv6proxy-stat
## ./tcp
## ./vm_vhost
### intel-xl710
#### dpdk-vfio-pci
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
##### dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm
##### dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
##### eth-l2xcbase-eth-2vhostvr1024-1vm
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm
##### eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND eth-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
##### dot1q-l2xcbase-eth-2vhostvr1024-1vm
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm
##### dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND dot1q-l2xcbase-eth-2vhostvr1024-1vm-vppl2xc
##### ethip4-ip4base-eth-2vhostvr1024-1vm
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm
##### ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base-eth-2vhostvr1024-1vm-vppip4
## ./vts
