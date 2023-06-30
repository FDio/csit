---
bookHidden: true
title: "CSIT-2306 Release Report"
---

# CSIT-2306 Release Report

The format of FD.io CSIT reports has now changed is no longer available
in the static html format.

Instead current CSIT release information can be found in csit.fd.io.
Previous CSIT releases are also linked from there.

## CSIT-2306 Release Data

To access CSIT-2306 Release data please use following web resources:

- [CSIT-2306 Release Notes](https://csit.fd.io/cdocs/release_notes/csit_rls2306/)
- [CSIT Documentation](https://csit.fd.io/cdocs/)
- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2306`
  - `DUT` > `vpp`
  - `DUT Version` > `23.06-release`
  - `Infra` > <testbed-nic-driver of choice>
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > ...
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP v23.06 vs v23.02
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2306-23.02-release`
    - `Infra` > <testbed-nic-driver of choice>
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
  - [2n-icx 100ge e810cq avf ip4scale20k](http://cuts2.com/sIfjo)
  - [2n-spr 100ge e810cq avf ip4scale20k](http://cuts2.com/ExMRU)
  - [2n-spr 100ge e810cq dpdk ip4scale20k](http://cuts2.com/snSJi)
  - [2n-spr 200ge cx7 dpdk ip4scale20k](http://cuts2.com/bVpvF)
  - [2n-aws c5n.4xl 50ge ena dpdk ip4scale20k](http://cuts2.com/HrpyC)
- ip6
  - [2n-icx 100ge e810cq avf ip6scale20k](http://cuts2.com/zgxlu)
  - [2n-spr 100ge e810cq avf ip6scale20k](http://cuts2.com/HqEsk)
  - [2n-spr 100ge e810cq dpdk ip6scale20k](http://cuts2.com/mLZWm)
  - [2n-spr 200ge cx7 dpdk ip6scale20k](http://cuts2.com/eCVsx)
  - [2n-aws c5n.4xl 50ge ena dpdk ip6scale20k](http://cuts2.com/gsExR)
- ipsec
  - [3n-icx 100ge e810cq avf 40tnlsw](http://cuts2.com/weFIh)
  - [3n-icx 100ge cx6 dpdk 40tnlsw](http://cuts2.com/zNVVn)
  - [3n-spr 100ge e810cq avf 40tnlsw](http://cuts2.com/JFUvT)
  - [3n-spr 200ge cx7 dpdk 40tnlsw](http://cuts2.com/ihwxD)
- hoststack quic
  - [3n-icx 100ge e810cq dpdk ip4udpquic](http://cuts2.com/PRcZr)
  - [3n-icx 100ge cx6 dpdk ip4udpquic](http://cuts2.com/JJKBv)
  - [3n-spr 100ge e810cq dpdk ip4udpquic](http://cuts2.com/IqRxg)
  - [3n-spr 200ge cx7 dpdk ip4udpquic](http://cuts2.com/Orzya)
- hoststack tcp udp
  - [3n-icx 100ge e810cq dpdk ip4tcp ipudp](http://cuts2.com/cECAK)
  - [3n-icx 100ge cx6 dpdk ip4tcp ipudp](http://cuts2.com/sCjKI)
  - [3n-spr 100ge e810cq dpdk ip4tcp ipudp](http://cuts2.com/HvNmE)
  - [3n-spr 200ge cx7 dpdk ip4tcp ipudp](http://cuts2.com/nAFDH)
- nat44
- tunnels (gnv, vxlan, gtpu)
- reassembly

## CSIT-2306 Selected Performance Comparisons

Comparisons 23.06 vs 23.02
- [2n-icx e810 2p100ge](http://cuts2.com/UBwMY)

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to csit.fd.io
documentation at this [link](https://csit.fd.io/cdocs/overview/c_dash/).
