---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2306"
weight: 1
---

# CSIT-2306 Release Report

The format of FD.io CSIT reports has now changed. It is no longer available
in the static html format.

Instead current CSIT release information can be found in csit.fd.io.
Previous CSIT releases are also linked from there.

## CSIT-2306 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})
- [VPP Device]({{< relref "vpp_device" >}})

## CSIT-2306 Release Data

To access CSIT-2306 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2306`
  - `DUT` > `vpp`
  - `DUT Version` > `23.06-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of chioce`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v23.06 vs v23.02
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2306-23.02-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2306-23.06-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2306`

## CSIT-2306 Selected Performance Tests

CSIT-2306 VPP v23.06 Performance Tests:

- ip4
  - [2n-icx 100ge e810cq avf ip4scale20k](http://cuts2.com/zMwtS)
  - [2n-spr 100ge e810cq avf ip4scale20k](http://cuts2.com/ahfvO)
  - [2n-spr 100ge e810cq dpdk ip4scale20k](http://cuts2.com/yQCqU)
  - [2n-spr 200ge cx7 dpdk ip4scale20k](http://cuts2.com/ZRERf)
  - [2n-aws 50ge c5n.4xl ena dpdk ip4scale20k](http://cuts2.com/cwXOI)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k](http://cuts2.com/QjBlW)
  - [2n-spr 100ge e810cq avf ip6scale20k](http://cuts2.com/OmkQy)
  - [2n-spr 100ge e810cq dpdk ip6scale20k](http://cuts2.com/qbpWI)
  - [2n-spr 200ge cx7 dpdk ip6scale20k](http://cuts2.com/OtOzQ)
  - [2n-aws 50ge c5n.4xl ena dpdk ip6scale20k](http://cuts2.com/Uopiv)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](http://cuts2.com/XFLrM)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](http://cuts2.com/gzpDB)
  - [3n-spr 100ge e810cq avf 40tnlsw](http://cuts2.com/NJeBW)
  - [3n-spr 200ge cx7 dpdk 40tnlsw](http://cuts2.com/fUiMC)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](http://cuts2.com/WTRoA)
  - [3n-icx 100ge cx6 dpdk ip4udpquic](http://cuts2.com/ZGHEO)
  - [3n-spr 100ge e810cq dpdk ip4udpquic](http://cuts2.com/LoBjd)
  - [3n-spr 200ge cx7 dpdk ip4udpquic](http://cuts2.com/CODih)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](http://cuts2.com/jlSrJ)
  - [3n-icx 100ge cx6 dpdk ip4tcp ipudp](http://cuts2.com/Pkqng)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](http://cuts2.com/RMWmj)
  - [3n-spr 200ge cx7 dpdk ip4tcp ipudp](http://cuts2.com/cRVdc)
- nat44
  - [2n-icx 100ge e810cq avf ethip4tcp tput](http://cuts2.com/aLIBU)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed tput](http://cuts2.com/loEKr)
  - [2n-spr 100ge e810cq avf ethip4tcp-nat44ed cps](http://cuts2.com/boqsw)
  - [2n-spr 200ge cx7 dpdk ethip4tcp-nat44ed tput](http://cuts2.com/QwXZd)
- tunnels (gnv, vxlan, gtpu)
  - [2n-icx 100ge e810cq avf ethip4udpgeneve](http://cuts2.com/VOrQr)
  - [3n-icx 100ge cx6 dpdk gtpu sw](http://cuts2.com/uYTVT)
  - [3n-spr 200ge cx7 dpdk vxlan](http://cuts2.com/iOYme)
  - [3n-spr 200ge cx7 dpdk gtpu sw](http://cuts2.com/tZrfd)
  - [3n-spr 200ge cx7 dpdk wireguard](http://cuts2.com/xKCia)
- reassembly
  - [3n-icx 100ge e810cq dpdk reassembly](http://cuts2.com/vBqTg)

## CSIT-2306 Selected Performance Comparisons

Comparisons 23.06 vs 23.02
- [2n-icx 100ge e810cq avf 1c 64B PDR](http://cuts2.com/UBwMY)

## CSIT-2306 Selected Performance Coverage Data

CSIT-2306 VPP v23.06 coverage data
- [2n-icx 200ge cx7 dpdk ip4](http://cuts2.com/EfqNe)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
