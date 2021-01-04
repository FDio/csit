# 3n-hsw
### tests 150
### job hrs est. 14.83
### job hrs real 14.83
### test mins est. 5.93
### test mins real 5.93
#
# Tests with avf driver are not executed on 3n-hsw systems as it requires
# enabling of SoftIOMMU thats quite difficult there.
#
## ./container_memif
## ./crypto
### intel-xl710
#### dpdk-vfio-pci
##### ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND ndrpdr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1tnlhw-ip4base-int-aes256gcm
1c AND 1518b AND ndrpdr AND xl710 AND drv_vfio_pci AND ethip4ipsec1tnlhw-ip4base-int-aes256gcm
##### ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND ndrpdr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
1c AND 1518b AND ndrpdr AND xl710 AND drv_vfio_pci AND ethip4ipsec1000tnlhw-ip4base-int-aes256gcm
