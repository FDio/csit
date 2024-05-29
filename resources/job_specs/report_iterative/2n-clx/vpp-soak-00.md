# 2n-clx
## ./container_memif
### intel-e810cq
#### avf
##### eth-l2bdbasemaclrn-eth-2memif-1dcr
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn-eth-2memif-1dcr
1c AND 1518b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn-eth-2memif-1dcr
## ./ip4
### intel-e810cq
#### avf
##### ethip4-ip4base
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4-ip4base
##### ethip4-ip4scale20k-rnd
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4-ip4scale20k-rnd
##### ethip4-ip4scale200k-rnd
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4-ip4scale200k-rnd
##### ethip4tcp-nat44ed-h65536-p63-s4128768-cps
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4tcp-nat44ed-h65536-p63-s4128768-cps
##### ethip4tcp-nat44ed-h65536-p63-s4128768-tput
1c AND 100b AND soak AND e810cq AND drv_avf AND ethip4tcp-nat44ed-h65536-p63-s4128768-tput
##### ethip4udp-nat44ed-h65536-p63-s4128768-cps
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4udp-nat44ed-h65536-p63-s4128768-cps
##### ethip4udp-nat44ed-h65536-p63-s4128768-tput
1c AND 100b AND soak AND e810cq AND drv_avf AND ethip4udp-nat44ed-h65536-p63-s4128768-tput
#### vfio-pci
##### ethip4-ip4scale200k-rnd
1c AND 64b AND soak AND e810cq AND drv_vfio_pci AND ethip4-ip4scale200k-rnd
### mellanox-cx556a
#### rdma-core
##### ethip4-ip4scale200k-rnd
1c AND 64b AND soak AND cx556a AND drv_rdma_core AND ethip4-ip4scale200k-rnd
## ./ip6
### intel-e810cq
#### avf
##### ethip6-ip6base
1c AND 78b AND soak AND e810cq AND drv_avf AND ethip6-ip6base
##### ethip6-ip6scale20k-rnd
1c AND 78b AND soak AND e810cq AND drv_avf AND ethip6-ip6scale20k-rnd
##### ethip6-ip6scale200k-rnd
1c AND 78b AND soak AND e810cq AND drv_avf AND ethip6-ip6scale200k-rnd
#### vfio-pci
##### ethip6-ip6scale200k-rnd
1c AND 78b AND soak AND e810cq AND drv_vfio_pci AND ethip6-ip6scale200k-rnd
### mellanox-cx556a
#### rdma-core
##### ethip6-ip6scale200k-rnd
1c AND 78b AND soak AND cx556a AND drv_rdma_core AND ethip6-ip6scale200k-rnd
## ./l2
### intel-e810cq
#### avf
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn
##### eth-l2bdscale1mmaclrn
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdscale1mmaclrn
##### eth-l2xcbase
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2xcbase
#### vfio-pci
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND e810cq AND drv_vfio_pci AND eth-l2bdbasemaclrn
### mellanox-cx556a
#### rdma-core
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND cx556a AND drv_rdma_core AND eth-l2bdbasemaclrn
## ./vm_vhost
### intel-e810cq
#### avf
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
