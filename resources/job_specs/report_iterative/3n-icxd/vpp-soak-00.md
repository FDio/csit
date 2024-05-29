# 3n-icxd
## ./container_memif
### intel-e823c
#### avf
##### eth-l2bdbasemaclrn-eth-2memif-1dcr
1c AND 64b AND soak AND e823c AND drv_avf AND eth-l2bdbasemaclrn-eth-2memif-1dcr
1c AND 1518b AND soak AND e823c AND drv_avf AND eth-l2bdbasemaclrn-eth-2memif-1dcr
## ./crypto
### intel-e823c
#### vfio_pci
##### ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND soak AND e823c AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
1c AND 1518b AND soak AND e823c AND drv_vfio_pci AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
##### ethip4ipsec1000tnlhwasync-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND soak AND e823c AND drv_vfio_pci AND ethip4ipsec1000tnlhwasync-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1000tnlhwasync-ip4base-int-aes256gcm
1c AND 1518b AND soak AND e823c AND drv_vfio_pci AND ethip4ipsec1000tnlhwasync-ip4base-int-aes256gcm
## ./ip4
### intel-e823c
#### avf
##### ethip4-ip4base
1c AND 64b AND soak AND e823c AND drv_avf AND ethip4-ip4base
##### ethip4-ip4scale20k-rnd
1c AND 64b AND soak AND e823c AND drv_avf AND ethip4-ip4scale20k-rnd
##### ethip4-ip4scale200k-rnd
1c AND 64b AND soak AND e823c AND drv_avf AND ethip4-ip4scale200k-rnd
#### vfio-pci
##### ethip4-ip4scale200k-rnd
1c AND 64b AND soak AND e823c AND drv_vfio_pci AND ethip4-ip4scale200k-rnd
### mellanox-cx6dx
#### mlx5-core
##### ethip4-ip4scale200k-rnd
1c AND 64b AND soak AND cx6dx AND drv_mlx5_core AND ethip4-ip4scale200k-rnd
## ./ip6
### intel-e823c
#### avf
##### ethip6-ip6base
1c AND 78b AND soak AND e823c AND drv_avf AND ethip6-ip6base
##### ethip6-ip6scale20k-rnd
1c AND 78b AND soak AND e823c AND drv_avf AND ethip6-ip6scale20k-rnd
##### ethip6-ip6scale200k-rnd
1c AND 78b AND soak AND e823c AND drv_avf AND ethip6-ip6scale200k-rnd
#### vfio-pci
##### ethip6-ip6scale200k-rnd
1c AND 78b AND soak AND e823c AND drv_vfio_pci AND ethip6-ip6scale200k-rnd
### mellanox-cx6dx
#### mlx5-core
##### ethip6-ip6scale200k-rnd
1c AND 78b AND soak AND cx6dx AND drv_mlx5_core AND ethip6-ip6scale200k-rnd
## ./l2
### intel-e823c
#### avf
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND e823c AND drv_avf AND eth-l2bdbasemaclrn
##### eth-l2bdscale1mmaclrn
1c AND 64b AND soak AND e823c AND drv_avf AND eth-l2bdscale1mmaclrn
##### eth-l2xcbase
1c AND 64b AND soak AND e823c AND drv_avf AND eth-l2xcbase
#### vfio-pci
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND e823c AND drv_vfio_pci AND eth-l2bdbasemaclrn
### mellanox-cx6dx
#### mlx5-core
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND cx6dx AND drv_mlx5_core AND eth-l2bdbasemaclrn
## ./vm_vhost
### intel-e823c
#### avf
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND soak AND e823c AND drv_avf AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
