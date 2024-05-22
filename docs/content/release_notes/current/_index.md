---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2406"
weight: 1
---

# CSIT-2406 Release Report

This section will include release notes for FD.io CSIT-2406. The CSIT report
will be published on **Jul-10 2024**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2406_plan) pages.

The release notes of the previous CSIT release can be found
[here]({{< relref "../previous/csit_rls2402" >}}).

## CSIT-2406 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})
- [VPP Device]({{< relref "vpp_device" >}})

## CSIT-2406 Release Data

To access CSIT-2406 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2406`
  - `DUT` > `vpp`
  - `DUT Version` > `24.06-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v24.06 vs v24.02
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2402-24.02-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2406-24.06-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2406`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2406`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2406 Selected Performance Tests

CSIT-2406 VPP v24.06 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k-rnd]()
  - [2n-spr 100ge e810cq avf ip4scale20k-rnd]()
  - [2n-spr 100ge e810cq dpdk ip4scale20k-rnd]()
  - [2n-spr 200ge cx7 mlx5 ip4scale20k-rnd]()
  - [2n-c6in 200ge c6in.4xl ena dpdk ip4scale20k-rnd]()
  - [2n-c7gn 100ge c7gn ena dpdk ip4scale20k-rnd]()
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k-rnd]()
  - [2n-spr 100ge e810cq avf ip6scale20k-rnd]()
  - [2n-spr 100ge e810cq dpdk ip6scale20k-rnd]()
  - [2n-spr 200ge cx7 mlx5 ip6scale20k-rnd]()
  - [2n-c6in 200ge c6in.4xl ena dpdk ip6scale20k-rnd]()
  - [2n-c7gn 200ge c7gn ena dpdk ip6scale20k-rnd]()
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw]()
  - [3n-icx 100ge cx6 dpdk 40tnlsw]()
  - [3n-spr 100ge e810cq avf 40tnlsw]()
  - [3n-spr 200ge cx7 mlx5 40tnlsw]()
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic]()
  - [3n-icx 100ge cx6 mlx5 ip4udpquic]()
  - [3n-spr 200ge cx7 mlx5 ip4udpquic]()
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp]()
  - [3n-icx 100ge cx6 mlx5 ip4tcp ipudp]()
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp]()
  - [3n-spr 200ge cx7 mlx5 ip4tcp ipudp]()
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput]()
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput]()
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps]()
  - [2n-spr 200ge cx7 mlx5 ethip4tcp-nat44ed tput]()
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve]()
  - [3n-icx 100ge cx6 mlx5 gtpu sw]()
  - [3n-spr 200ge cx7 mlx5 vxlan]()
  - [3n-spr 200ge cx7 mlx5 gtpu sw]()
  - [3n-spr 200ge cx7 mlx5 wireguard]()
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly]()

## CSIT-2406 Selected Performance Comparisons

Comparisons 24.06 vs 24.02
- [2n-icx 100ge e810cq avf 1c 64B PDR]()

## CSIT-2406 Selected Performance Coverage Data

CSIT-2406 VPP v24.06 coverage data
- [2n-icx 200ge cx7 mlx5 ip4]()

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
