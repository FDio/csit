# 3n-icx
## ./container_memif
### intel-e810cq
#### avf
##### eth-l2bdbasemaclrn-eth-2memif-1dcr
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn-eth-2memif-1dcr
## ./crypto
### intel-e810cq
#### avf
##### ethip4ipsec10000tnlsw-ip4base-int-aes128cbc-hmac512sha
1c AND 1518b AND soak AND e810cq AND drv_avf AND ethip4ipsec1000tnlsw-ip4base-int-aes128cbc-hmac512sha
##### ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
1c AND 1518b AND soak AND e810cq AND drv_avf AND ethip4ipsec1000tnlsw-ip4base-int-aes256gcm
## ./ip4
### intel-e810cq
#### avf
##### ethip4-ip4base
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4-ip4base
##### ethip4-ip4scale20k-rnd
1c AND 64b AND soak AND e810cq AND drv_avf AND ethip4-ip4scale20k-rnd
## ./ip6
#### avf
##### ethip6-ip6base
1c AND 78b AND soak AND e810cq AND drv_avf AND ethip6-ip6base
##### ethip6-ip6scale20k-rnd
1c AND 78b AND soak AND e810cq AND drv_avf AND ethip6-ip6scale20k-rnd
## ./l2
### mellanox-cx6dx
#### mlx5-core
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND cx6dx AND drv_mlx5_core AND eth-l2bdbasemaclrn
### intel-e810cq
#### avf
##### eth-l2bdbasemaclrn
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn
##### eth-l2bdscale1mmaclrn
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdscale1mmaclrn
## ./vm_vhost
### intel-e810cq
#### avf
##### eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc
1c AND 64b AND soak AND e810cq AND drv_avf AND eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-vppl2xc

# TODO: No IPsecHW available, maybe add WireguardSW and GtpuHW?
