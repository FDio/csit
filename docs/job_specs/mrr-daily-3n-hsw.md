# 3n-hsw
#
# Tests with avf driver are not executed on 3n-hsw systems as it requires
# enabling of SoftIOMMU thats quite difficult there.
#
## ./ip4
### intel-xl710
#### dpdk-vfio-pci
##### ethip4-ip4base
1c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base
2c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base
4c AND 64b AND mrr AND xl710 AND drv_vfio_pci AND ethip4-ip4base
