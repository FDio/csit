Mellanox NIC
------------

## System settings

Following recommendation from [^0][^1][^2].

- Flow Control OFF:
    $ ethtool -A $netdev rx off tx off
- Memory optimizations:
    $ sysctl -w vm.zone_reclaim_mode=0
    $ sysctl -w vm.swappiness=0
- Move all IRQs to far NUMA node:
    "IRQBALANCE_BANNED_CPUS="ffffffff,fffffeff,fffeffff,fefffffe""
- Change PCI MaxReadReq to 1024B for each port of each NIC:
    $ setpci -s $PORT_PCI_ADDRESS 68.w=3BCD
- Set CQE COMPRESSION to "AGGRESSIVE":
    $ mlxconfig -d $PORT_PCI_ADDRESS set CQE_COMPRESSION=1
- Standard CSIT testbed settings [^3]


Links

[^0]: [DPDK 19.11 performance report](http://static.dpdk.org/doc/perf/DPDK_19_11_Mellanox_NIC_performance_report.pdf)

[^1]: [Mellanox DPDK guide](https://www.mellanox.com/related-docs/prod_software/MLNX_DPDK_Quick_Start_Guide_v16.11_3.0.pdf)

[^2]: [Mellanox DPDK bits](https://community.mellanox.com/s/article/mellanox-dpdk)

[^3]: [CSIT testbed setting and calibration](https://docs.fd.io/csit/master/report/vpp_performance_tests/test_environment.html)

[^4]: [CSIT 2n-clx testbed specification](https://docs.fd.io/csit/master/report/introduction/physical_testbeds.html#node-xeon-cascade-lake-2n-clx)
