---
bookCollapseSection: true
bookFlatSection: false
title: "CSIT rls2502"
weight: 1
---

# CSIT-2502 Release Report

This section includes release notes for FD.io CSIT-2502. The CSIT report
will be published on **Nov-13 2024**. The release plan is published on
[CSIT wiki](https://wiki.fd.io/view/CSIT/csit2502_plan) pages.

The release notes of the previous CSIT release can be found
[here]({{< relref "../previous/csit_rls2410" >}}).

## CSIT-2502 Release Notes

- [VPP Performance]({{< relref "vpp_performance" >}})
- [DPDK Performance]({{< relref "dpdk_performance" >}})
- [TRex Performance]({{< relref "trex_performance" >}})

For infra reasons, we ultimately stopped device testing.

## CSIT-2502 Release Data

To access CSIT-2502 Release data please use following web resources:

- [CSIT Per Release Performance](https://csit.fd.io/report/)
  - `CSIT Release` > `rls2502`
  - `DUT` > `vpp`
  - `DUT Version` > `25.02-release`
  - `Infra` > `testbed-nic-driver of choice`
  - `Area` > `IPv4 Routing` `IPv4 Tunnels` `IPv6 Routing` `Hoststack` ...
  - `Test` > `test of choice`
  - `Frame Size` > `64B` `78B`
  - `Number of Cores` > `1C` `2C` `4C`
  - `Test Type` > `MRR` `NDR` `PDR`
- [CSIT Per Release Comparisons](https://csit.fd.io/comparisons/) for VPP
  v25.10 vs v24.10
  - `REFERENCE VALUE`
    - `DUT` > `vpp`
    - `CSIT and DUT version` > `rls2410-24.10-release`
    - `Infra` > `testbed-nic-driver of choice`
    - `Frame Size` > `64B` `78B`
    - `Number of Cores` > `1C` `2C` `4C`
    - `Measurement` > `Latency` `MRR` `NDR` `PDR`
  - `COMPARED VALUE`
    - `Parameter` > `Release and Version`
    - `Value` > `rls2502-25.02-release`
- [CSIT Per Release Coverage Data](https://csit.fd.io/coverage/)
  - `CSIT Release` > `rls2502`
- [CSIT Search Tests](https://csit.fd.io/search/)
  - `Data Type` > `iterative`
  - `DUT` > `vpp`
  - `Release` > `rls2502`
  - `Type a Regular Expression` > `2n-zn2 -1c ethip4-ip4base-[mrr|ndrpdr]`
    ".*" can be replaced by " " (white space).
  - `Choose a cell in the table` > A corresponding graph(s) is displayed.
  - `Click a datapoint in the graph` > Detailed information is displayed.

## CSIT-2502 Selected Performance Tests

CSIT-2502 VPP v24.10 Performance Tests:

## CSIT-2502 Selected Performance Comparisons

Comparisons v25.10 vs v24.10

## CSIT-2502 Selected Performance Coverage Data

CSIT-2502 VPP v25.02 coverage data


## Further Information

For further information including instructions how to access the needed
information with user selectable options, please refer to
[csit.fd.io documentation]({{< relref "/" >}}).
