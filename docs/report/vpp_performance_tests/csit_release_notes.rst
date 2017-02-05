CSIT Release Notes
==================

Changes in CSIT |release|
-------------------------

#. Naming change for all VPP performance test suites and test cases.
#. VPP performance test environment changes

    - upgrade to Ubuntu 16.04
    - VM and vhost-user test environment optimizations
    - addition of HW cryptodev devices in LFD FD.io physical testbed

#. Added tests

    - NICs

      - Intel x710 (L2 Bridge Domain switched-forwarding, vhost-user)
      - Cisco VIC1385 (L2 Bridge Domain switched-forwarding)
      - Cisco VIC1227 (L2 Bridge Domain switched-forwarding)

    - vhost-user tests with VM

      - L2 Bridge Domain switched-forwarding with Intel x710 NIC
      - L2 Bridge Domain switched-forwarding with VxLAN and Intel x520 NIC
      - L2 Bridge Domain switched-forwarding with Intel xl710 NIC

    - Tests with VxLAN

      - L2 Bridge Domain switched-forwarding with Intel x520 NIC
      - L2 Bridge Domain switched-forwarding with vhost-user, VM and Intel x520
        NIC

Performance Improvements
------------------------

Substantial improvements in measured packet throughput, with relative increase
of double-digit percentage points, have been observed in a number of CSIT
|release| tests listed below. Relative improvements are calculated against the
test results in CSIT rls1609 report.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01       | Relative Improvement |
+===================+=================================================================+===========+=================+======================+
| L2XC              | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-ndrdisc                      | 9.4 Mpps  | 12.7 Mpps       | 35%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC              | 10ge2p1xl710: 64B-1t1c-eth-l2xcbase-ndrdisc                     | 9.5 Mpps  | 12.2..12.4 Mpps | 28..30%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC dot1ad       | 10ge2p1x520: 64B-1t1c-dot1ad-l2xcbase-ndrdisc                   | 7.4 Mpps  | 8.8..9.0 Mpps   | 19..23%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC dot1q        | 10ge2p1x520: 64B-1t1c-dot1q-l2xcbase-ndrdisc                    | 7.5 Mpps  | 8.8..9.0 Mpps   | 17..20%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC VxLAN        | 10ge2p1x520: 64B-1t1c-ethip4vxlan-l2xcbase-ndrdisc              | 5.4 Mpps  | 6.5 Mpps        | 20%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc       | 0.5 Mpps  | 2.8..3.2 Mpps   | 460..540%            |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2BD              | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-ndrdisc                | 7.8 Mpps  | 10.4..10.6 Mpps | 33..36%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2BD-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc | 0.4 Mpps  | 2.7..2.8 Mpps   | 575..600%            |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4              | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ndrdisc                    | 8.7 Mpps  | 9.7 Mpps        | 12%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 COP          | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-copwhtlistbase-ndrdisc     | 7.1 Mpps  | 8.3..8.5 Mpps   | 17..20%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 iAcl         | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-iacldstbase-ndrdisc        | 6.9 Mpps  | 7.6..7.8 Mpps   | 10..13%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 vhost        | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-ndrdisc     | 0.3 Mpps  | 2.6 Mpps        | 767%                 |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6              | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-ndrdisc                    | 3.0 Mpps  | 7.3..7.7 Mpps   | 143..157%            |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01       | Relative Improvement |
+===================+=================================================================+===========+=================+======================+
| L2XC              | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-pdrdisc                      | 9.4 Mpps  | 12.7..12.9 Mpps | 35..37%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC dot1ad       | 10ge2p1x520: 64B-1t1c-dot1ad-l2xcbase-pdrdisc                   | 7.4 Mpps  | 8.8..9.1 Mpps   | 19..23%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC dot1q        | 10ge2p1x520: 64B-1t1c-dot1q-l2xcbase-pdrdisc                    | 7.5 Mpps  | 8.8..9.0 Mpps   | 17..20%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC VxLAN        | 10ge2p1x520: 64B-1t1c-ethip4vxlan-l2xcbase-pdrdisc              | 5.4 Mpps  | 6.5 Mpps        | 20%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-pdrdisc       | 2.6 Mpps  | 3.2..3.3 Mpps   | 23..26%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2BD              | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-pdrdisc                | 7.8 Mpps  | 10.6 Mpps       | 36%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2BD-vhost-VM     | 10ge2p1x520: 64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-pdrdisc | 2.1 Mpps  | 2.9 Mpps        | 38%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4              | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-pdrdisc                    | 8.7 Mpps  | 9.7 Mpps        | 11%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 COP          | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-copwhtlistbase-pdrdisc     | 7.1 Mpps  | 8.3..8.5 Mpps   | 17..20%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 vhost        | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-pdrdisc     | 2.0 Mpps  | 2.7 Mpps        | 35%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+

Measured improvements are in line with VPP code optimizations listed in
`VPP-17.01 release notes
<https://docs.fd.io/vpp/17.01/release_notes_1701.html>`_.

Additionally, vhost-VM performance improvements are due to both VPP code
optimizations as well as due to the FD.io CSIT Linux KVM test environment
optimizations for vhost-VM tests - see section "2.1.7. Methodology: KVM VM
vhost".


Other Performance Changes
-------------------------

Other changes in measured packet throughput, with either minor relative
increase or decrease, have been observed in a number of CSIT |release| tests
listed below. Relative changes are calculated against the test results in CSIT
rls1609 report.

NDR Throughput
~~~~~~~~~~~~~~

Non-Drop Rate Throughput discovery tests:

+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01       | Relative Change      |
+===================+=================================================================+===========+=================+======================+
| IPv4 FIB 200k     | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale200k-ndrdisc               | 8.5 Mpps  | 9.0 Mpps        | 6%                   |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 20k      | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale20k-ndrdisc                | 8.5 Mpps  | 9.0..9.2 Mpps   | 6..8%                |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 2M       | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale2m-ndrdisc                 | 8.5 Mpps  | 7.8..8.1 Mpps   | -8..-5%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 Policer      | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ipolicemarkbase-ndrdisc    | 6.9 Mpps  | 7.4..7.6 Mpps   | 7..10%               |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 LISP         | 10ge2p1x520: 64B-1t1c-ethip4lispip4-ip4base-ndrdisc             | 4.4 Mpps  | 4.8 Mpps        | 9%                   |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 COP          | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-copwhtlistbase-ndrdisc     | 6.1 Mpps  | 6.1..6.5 Mpps   | 0..7%                |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 FIB 200k     | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale200k-ndrdisc               | 6.5 Mpps  | 5.3..5.7 Mpps   | -18..-12%            |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 FIB 20k      | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale20k-ndrdisc                | 6.9 Mpps  | 6.5 Mpps        | -6%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 FIB 2M       | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale2m-ndrdisc                 | 5.3 Mpps  | 4.2 Mpps        | -21%                 |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 iAcl         | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-iacldstbase-ndrdisc        | 6.5 Mpps  | 6.1..6.5 Mpps   | -6..0%               |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+

PDR Throughput
~~~~~~~~~~~~~~

Partial Drop Rate thoughput discovery tests with packet Loss Tolerance of 0.5%:

+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01       | Relative Change      |
+===================+=================================================================+===========+=================+======================+
| IPv4 FIB 200k     | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale200k-pdrdisc               | 8.5 Mpps  | 9.0 Mpps        | 6%                   |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 20k      | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale20k-pdrdisc                | 8.5 Mpps  | 9.0..9.2 Mpps   | 6..8%                |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 2M       | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale2m-pdrdisc                 | 8.3 Mpps  | 8.1 Mpps        | -2%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 iAcl         | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-iacldstbase-pdrdisc        | 7.1 Mpps  | 7.6..7.8 Mpps   | 7..10%               |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 Policer      | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ipolicemarkbase-pdrdisc    | 7.1 Mpps  | 7.4..7.6 Mpps   | 4..7%                |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 LISP         | 10ge2p1x520: 64B-1t1c-ethip4lispip4-ip4base-pdrdisc             | 4.6 Mpps  | 4.8 Mpps        | 9%                   |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6              | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-pdrdisc                    | 7.7 Mpps  | 7.3..7.7 Mpps   | -5..0%               |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 COP          | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-copwhtlistbase-pdrdisc     | 6.1 Mpps  | 6.1..6.5 Mpps   | 0..7%                |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 FIB 200k     | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale200k-pdrdisc               | 6.9 Mpps  | 5.3..5.7 Mpps   | -23..-17%            |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 FIB 20k      | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale20k-pdrdisc                | 6.9 Mpps  | 6.5 Mpps        | -6%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 FIB 2M       | 10ge2p1x520: 78B-1t1c-ethip6-ip6scale2m-pdrdisc                 | 5.3 Mpps  | 4.2 Mpps        | -21%                 |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6 iAcl         | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-iacldstbase-pdrdisc        | 6.5 Mpps  | 6.1..6.5 Mpps   | -6..0%               |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP performance tests in physical HW testbed:

+---+-------------------------------------------------+-----------------------------------------------------------------+
| # | Issue                                           | Description                                                     |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 1 | Sporadic IPv4 routed-forwarding NDR discovery   | Suspected issue with DPDK IPv4 checksum calculation, VPP jira # |
|   | test failures for 1518B frame size              | Observed frequency: sporadic, ca. 20% to 30% of test runs       |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 2 | Vic1385 and Vic1227 NICs jumbo frames test      | Suspected issue with Vic drivers that does not support jumbo    |
|   | failures (9000B)                                | frames (dropped rx-miss). Observed frequency: 100%              |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 3 | Vic1385 and Vic1227 performance                 | Low performance of NDR results. Big difference between NDR and  |
|   |                                                 | PDR                                                             |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 4 | Sporadic NDR discovery test failures on x520    | Suspected issue with HW settings (BIOS, FW) in LF               |
|   |                                                 | infrastructure. Issue can't be replicated outside LF.           |
+---+-------------------------------------------------+-----------------------------------------------------------------+

Tests to be Added - Cryptodev
-----------------------------

DPDK Cryptodev functionality support for both SW and HW crypto devices has
been introduced in VPP-17.01 release. CSIT functional and performance tests
have been also developed and merged. However due to the factors beyond CSIT
project control execution of those tests within the LF FD.io test environment
still need to complete. Once the results become available, they will be
published as an addendum to the current version of CSIT |release| report.

Tests to be Added - SNAT44
--------------------------

VPP SNAT44 functionality has been introduced in VPP-17.01 release. CSIT
performance tests are still in development and integration into LFD FD.io test
environment. Once the tests are fully integrated and results become available,
they will be published as an addendum to the current version of CSIT |release|
report.
