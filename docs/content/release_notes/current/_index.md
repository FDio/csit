---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2606"
weight: 1
---

# CSIT-2606 Release Report

This section includes release notes for FD.io CSIT-2606. The CSIT report
will be published on **Jul-08 2026**. The release plan is published on
[CSIT wiki](https://github.com/FDio/csit/wiki/CSIT-Release-Plan#csit-rls2606)
pages.

## CSIT-2606 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})

## CSIT-2606 Release Data

To access CSIT-2606 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2606`
  - `DUT` > `vpp`
  - `DUT Version` > `26.06-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v26.06 vs v26.02
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2602-26.02-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2606-26.06-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2606`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2606`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2606 Selected Performance Tests

CSIT-2606 VPP v26.06 Performance Tests:

## CSIT-2606 Selected Performance Comparisons

Comparisons v26.06 vs v26.02

## CSIT-2606 Selected Performance Coverage Data

CSIT-2606 VPP v26.06 coverage data

## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
