CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. VPP performance test environment changes

    - Further optimizations of VM and vhost-user test environment - Qemu virtio
      queue size increased from default value of 256 to 1024.
    - Addition of HW cryptodev devices - Intel QAT 8950 50G - in all three
      LF FD.io physical testbeds.

#. VPP performance test framework changes

    - Added VAT command history collection for every test case as part of teardown.

#. Added VPP performance tests

    - **CGNAT**

      - Carrier Grade Network Address Translation tests with varying number
        of users and ports per user: 1u-15p, 10u-15p, 100u-15p, 1000u-15p,
        2000u-15p, 4000u-15p - with Intel x520 NIC.

    - **vhost-user tests with one VM**

      - L2 Bridge Domain switched-forwarding with Intel x710 NIC, Intel x520 NIC,
        Intel xl710 NIC.
      - VXLAN and L2 Bridge Domain switched-forwarding with Intel x520 NIC.

    - **vhost-user tests with two VMs service chain**

      - L2 cross-connect switched-forwarding with Intel x520 NIC, Intel xl710 NIC.
      - L2 Bridge Domain switched-forwarding with Intel x520 NIC, Intel xl710 NIC.
      - IPv4 routed-forwarding with Intel x520 NIC, Intel xl710 NIC.

    - **IPSec encryption with**

      - AES-GCM, CBC-SHA1 ciphers, in combination with IPv4 routed-forwarding
        with Intel xl710 NIC.
      - CBC-SHA1 ciphers, in combination with LISP-GPE overlay tunneling for
        IPv4-over-IPv4 with Intel xl710 NIC.

Performance Improvements
------------------------

Some performance improvements in measured packet throughput have been observed
in a number of CSIT |release| tests listed below. Relative improvements are
calculated against the test results in CSIT rls1701 report. VPP-16.09 and
VPP-17.01 numbers are provided for reference.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| VPP Functionality | Test Name                                                       | VPP-16.09  | VPP-17.01 | VPP-17.04 | 17.01 to 17.04  |
|                   |                                                                 |   [Mpps]   |  [Mpps]   |   [Mpps]  | Relative Change |
+===================+=================================================================+============+===========+===========+=================+
| L2XC              | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-ndrdisc                      | 9.4        | 12.7      | 13.4      | 6%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2XC              | 10ge2p1xl710: 64B-1t1c-eth-l2xcbase-ndrdisc                     | 9.5        | 12.2      | 12.4      | 2%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2XC dot1ad       | 10ge2p1x520: 64B-1t1c-dot1ad-l2xcbase-ndrdisc                   | 7.4        | 8.8       | 9.3       | 6%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2XC dot1q        | 10ge2p1x520: 64B-1t1c-dot1q-l2xcbase-ndrdisc                    | 7.5        | 8.8       | 9.2       | 5%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2XC VxLAN        | 10ge2p1x520: 64B-1t1c-ethip4vxlan-l2xcbase-ndrdisc              | 5.4        | 6.5       | 6.8       | 5%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2XC-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc       | 0.5        | 2.8       | 3.2       | 14%             |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2BD              | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-ndrdisc                | 7.8        | 10.4      | 10.8      | 4%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| L2BD-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc | 0.4        | 2.7       | 3.4       | 26%             |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| IPv4              | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ndrdisc                    | 8.7        | 9.7       | 10.6      | 9%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| IPv4 COP          | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-copwhtlistbase-ndrdisc     | 7.1        | 8.3       | 9.0       | 8%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| IPv4 iAcl         | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-iacldstbase-ndrdisc        | 6.9        | 7.6       | 8.3       | 9%              |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| IPv4 vhost        | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-ndrdisc     | 0.3        | 2.6       | 3.1       | 19%             |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+
| IPv6              | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-ndrdisc                    | 3.0        | 7.3       | 8.1       | 11%             |
+-------------------+-----------------------------------------------------------------+------------+-----------+-----------+-----------------+

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01 | VPP-17.04 | 17.01 to 17.04  |
|                   |                                                                 |   [Mpps]  |  [Mpps]   |   [Mpps]  | Relative Change |
+===================+=================================================================+===========+===========+===========+=================+
| L2XC              | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-pdrdisc                      | 9.4       | 12.7      | 13.4      | 6%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| L2XC dot1ad       | 10ge2p1x520: 64B-1t1c-dot1ad-l2xcbase-pdrdisc                   | 7.4       | 8.8       | 9.3       | 6%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| L2XC dot1q        | 10ge2p1x520: 64B-1t1c-dot1q-l2xcbase-pdrdisc                    | 7.5       | 8.8       | 9.5       | 8%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| L2XC VxLAN        | 10ge2p1x520: 64B-1t1c-ethip4vxlan-l2xcbase-pdrdisc              | 5.4       | 6.5       | 6.8       | 5%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| L2XC-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc       | 2.6       | 3.2       | 3.2       | 0%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| L2BD              | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-pdrdisc                | 7.8       | 10.6      | 11.1      | 5%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| L2BD-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc | 2.1       | 2.9       | 3.2       | 10%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4              | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-pdrdisc                    | 8.7       | 9.7       | 10.6      | 9%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 COP          | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-copwhtlistbase-pdrdisc     | 7.1       | 8.3       | 9.2       | 11%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 iAcl         | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-iacldstbase-pdrdisc        | 7.1       | 7.6       | 8.3       | 9%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 vhost        | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-pdrdisc     | 2.0       | 2.7       | 3.2       | 19%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6              | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-pdrdisc                    | 7.7       | 7.3       | 8.1       | 11%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+

Measured improvements are in line with VPP code optimizations listed in
`VPP-17.04 release notes
<https://docs.fd.io/vpp/17.04/release_notes_1704.html>`_.

Additionally, vhost-VM performance improvements are due to both VPP code
optimizations as well as due to the FD.io CSIT Linux KVM test environment
optimizations for vhost-VM tests - see section "2.1.7. Methodology: KVM VM
vhost".


Other Performance Changes
-------------------------

Other changes in measured packet throughput, with either minor relative
increase or decrease, have been observed in a number of CSIT |release| tests
listed below. Relative changes are calculated against the test results in CSIT
rls1701 report.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01 | VPP-17.04 | 17.01 to 17.04  |
|                   |                                                                 |   [Mpps]  |  [Mpps]   |   [Mpps]  | Relative Change |
+===================+=================================================================+===========+===========+===========+=================+
| IPv4 FIB 200k     | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale200k-ndrdisc               | 8.5       | 9.0       | 9.7       | 8%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 FIB 20k      | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale20k-ndrdisc                | 8.5       | 9.0       | 9.4       | 4%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 FIB 2M       | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale2m-ndrdisc                 | 8.5       | 7.8       | 8.1       | 4%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 Policer      | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ipolicemarkbase-ndrdisc    | 6.9       | 7.4       | 8.1       | 9%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 LISP         | 10ge2p1x520: 64B-1t1c-ethip4lispip4-ip4base-ndrdisc             | 4.4       | 4.8       | 5.5       | 15%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 COP          | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-copwhtlistbase-ndrdisc     | 6.1       | 6.1       | 6.9       | 13%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 FIB 200k     | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale200k-ndrdisc               | 6.5       | 5.3       | 5.3       | 0%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 FIB 20k      | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale20k-ndrdisc                | 6.9       | 6.5       | 6.9       | 6%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 FIB 2M       | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale2m-ndrdisc                 | 5.3       | 4.2       | 4.6       | 10%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 iAcl         | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-iacldstbase-ndrdisc        | 6.5       | 6.1       | 6.9       | 13%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01 | VPP-17.04 | 17.01 to 17.04  |
|                   |                                                                 |   [Mpps]  |  [Mpps]   |   [Mpps]  | Relative Change |
+===================+=================================================================+===========+===========+===========+=================+
| IPv4 FIB 200k     | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale200k-pdrdisc               | 8.5       | 9.0       | 9.7       | 8%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 FIB 20k      | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale20k-pdrdisc                | 8.5       | 9.0       | 9.7       | 8%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 FIB 2M       | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale2m-pdrdisc                 | 8.3       | 8.1       | 8.3       | 2%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 Policer      | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ipolicemarkbase-pdrdisc    | 7.1       | 7.4       | 8.1       | 9%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv4 LISP         | 10ge2p1x520: 64B-1t1c-ethip4lispip4-ip4base-pdrdisc             | 4.6       | 4.8       | 5.5       | 15%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 COP          | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-copwhtlistbase-pdrdisc     | 6.1       | 6.1       | 6.9       | 13%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 FIB 200k     | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale200k-pdrdisc               | 6.9       | 5.3       | 5.3       | 0%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 FIB 20k      | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale20k-pdrdisc                | 6.9       | 6.5       | 6.9       | 6%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 FIB 2M       | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale2m-pdrdisc                 | 5.3       | 4.2       | 4.6       | 10%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+
| IPv6 iAcl         | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-iacldstbase-pdrdisc        | 6.5       | 6.1       | 6.9       | 13%             |
+-------------------+-----------------------------------------------------------------+-----------+-----------+-----------+-----------------+

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP performance tests:

+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| # | Issue                                           | Jira ID    | Description                                                     |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 1 | NDR discovery test failures 1518B frame size    | VPP-663    | VPP reporting errors: dpdk-input Rx ip checksum errors.         |
|   | for ip4scale200k, ip4scale2m scale IPv4 routed- |            | Observed frequency: all test runs.                              |
|   | forwarding tests. ip4scale20k tests are fine.   |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 2 | VAT API timeouts during ip6scale2m scale IPv6   | VPP-712    | Needs fixing VPP VAT API timeouts for large volume of IPv6      |
|   | routed-forwarding tests when volume adding IPv6 |            | routes.                                                         |
|   | routes - 2M in this case. ip6scale2kk works.    |            |                                                                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 3 | Vic1385 and Vic1227 low performance             | VPP-664    | Low NDR performance.                                            |
|   |                                                 |            |                                       .                         |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 4 | Sporadic NDR discovery test failures on x520    | CSIT-750   | Suspected issue with HW settings (BIOS, FW) in LF               |
|   |                                                 |            | infrastructure. Issue can't be replicated outside LF.           |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 5 | VPP in 2t2c setups - large variation            | CSIT-568   | Suspected NIC firmware or DPDK driver issue affecting NDR       |
|   | of discovered NDR throughput values across      |            | throughput. Applies to XL710 and X710 NICs, x520 NICs are fine. |
|   | multiple test runs with xl710 and x710 NICs.    |            |                                       .                         |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+
| 6 | Lower than expected NDR and PDR throughput with | CSIT-569   | Suspected NIC firmware or DPDK driver issue affecting NDR and   |
|   | xl710 and x710 NICs, compared to x520 NICs.     |            | PDR throughput. Applies to XL710 and X710 NICs.                 |
+---+-------------------------------------------------+------------+-----------------------------------------------------------------+

