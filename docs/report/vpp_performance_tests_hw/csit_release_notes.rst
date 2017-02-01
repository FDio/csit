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

    - new NICs - Intel x710, Cisco VIC1385, Cisco VIC1227
    - more VM vhost-user tests
    - more LISP tests


Performance Tests Naming
------------------------

CSIT |release| introduced a common structured naming convention for all
performance and functional tests. This change was driven by substantially
growing number and type of CSIT test cases. Firstly, the original practice did
not always follow any strict naming convention. Secondly test names did not
always clearly capture tested packet encapsulations, and the actual type or
content of the tests. Thirdly HW configurations in terms of NICs, ports and
their locality were not captured either. These were but few reasons that drove
the decision to change and define a new more complete and stricter test naming
convention, and to apply this to all existing and new test cases.

The new naming should be intuitive for majority of the tests. The complete
description of CSIT test naming convention is provided on `CSIT test naming wiki
<https://wiki.fd.io/view/CSIT/csit-test-naming>`_.

Here few illustrative examples of the new naming usage for performance test
suites:

#. **Physical port to physical port - a.k.a. NIC-to-NIC, Phy-to-Phy, P2P**

    - *PortNICConfig-WireEncapsulation-PacketForwardingFunction-
      PacketProcessingFunction1-...-PacketProcessingFunctionN-TestType*
    - *10ge2p1x520-dot1q-l2bdbasemaclrn-ndrdisc.robot* => 2 ports of 10GE on
      Intel x520 NIC, dot1q tagged Ethernet, L2 bridge-domain baseline switching
      with MAC learning, NDR throughput discovery.
    - *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-ndrchk.robot* => 2 ports of 10GE
      on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain baseline
      switching with MAC learning, NDR throughput discovery.
    - *10ge2p1x520-ethip4-ip4base-ndrdisc.robot* => 2 ports of 10GE on Intel
      x520 NIC, IPv4 baseline routed forwarding, NDR throughput discovery.
    - *10ge2p1x520-ethip6-ip6scale200k-ndrdisc.robot* => 2 ports of 10GE on
      Intel x520 NIC, IPv6 scaled up routed forwarding, NDR throughput
      discovery.

#. **Physical port to VM (or VM chain) to physical port - a.k.a. NIC2VM2NIC,
   P2V2P, NIC2VMchain2NIC, P2V2V2P**

    - *PortNICConfig-WireEncapsulation-PacketForwardingFunction-
      PacketProcessingFunction1-...-PacketProcessingFunctionN-VirtEncapsulation-
      VirtPortConfig-VMconfig-TestType*
    - *10ge2p1x520-dot1q-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot* => 2 ports
      of 10GE on Intel x520 NIC, dot1q tagged Ethernet, L2 bridge-domain
      switching to/from two vhost interfaces and one VM, NDR throughput
      discovery.
    - *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc.robot* => 2
      ports of 10GE on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain
      switching to/from two vhost interfaces and one VM, NDR throughput
      discovery.
    - *10ge2p1x520-ethip4vxlan-l2bdbasemaclrn-eth-4vhost-2vm-ndrdisc.robot* => 2
      ports of 10GE on Intel x520 NIC, IPv4 VXLAN Ethernet, L2 bridge-domain
      switching to/from four vhost interfaces and two VMs, NDR throughput
      discovery.

Measured Performance Improvements
---------------------------------

Substantial improvements in measured packet throughput have been observed
in VPP-17.01 for the following CSIT |release| tests:

+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+
| VPP Functionality | Test Name                                                      | VPP-16.09 | VPP-17.01       | Relative Improvement |
+===================+================================================================+===========+=================+======================+
| L2XC              | 10ge2p1x520:64B-1t1c-eth-l2xcbase-ndrdisc                      | 9.4 Mpps  | 12.6..12.9 Mpps | 34..37%              |
+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC              | 10ge2p1xl710:64B-1t1c-eth-l2xcbase-ndrdisc                     | 9.5 Mpps  | 12.1..12.4 Mpps | 27..30%              |
+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2BD              | 10ge2p1x520:64B-1t1c-eth-l2bdbasemaclrn-ndrdisc                | 7.8 Mpps  | 10.6 Mpps       | 36%                  |
+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2BD-vhost-VM     | 10ge2p1x520:64B-1t1c-eth-l2bdbasemaclrn-eth-2vhost-1vm-ndrdisc | 0.4 Mpps  | 2.8 Mpps        | 600%                 |
+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC-vhost-VM     | 10ge2p1x520:64B-1t1c-eth-l2xcbase-eth-2vhost-1vm-ndrdisc       | 0.4 Mpps  | 3.2 Mpps        | 700%                 |
+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4              | 10ge2p1x520:64B-1t1c-ethip4-ip4base-ndrdisc                    | 8.7 Mpps  | 9.7 Mpps        | 12%                  |
+-------------------+----------------------------------------------------------------+-----------+-----------------+----------------------+

Non-drop rate search:

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
| IPv4              | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ndrdisc                    | 8.7 Mpps  | 9.7 Mpps        | 11%                  |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 COP          | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-copwhtlistbase-ndrdisc     | 7.1 Mpps  | 8.3..8.5 Mpps   | 17..20%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 200k     | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale200k-ndrdisc               | 8.5 Mpps  | 9.0 Mpps        | 6%                   |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 20k      | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale20k-ndrdisc                | 8.5 Mpps  | 9.0..9.2 Mpps   | 6..8%                |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 FIB 2M       | 10ge2p1x520: 64B-1t1c-ethip4-ip4scale2m-ndrdisc                 | 8.5 Mpps  | 7.8..8.1 Mpps   | -8..-5%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 iAcl         | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-iacldstbase-ndrdisc        | 6.9 Mpps  | 7.6..7.8 Mpps   | 10..13%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 Policer      | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-ipolicemarkbase-ndrdisc    | 6.9 Mpps  | 7.4..7.6 Mpps   | 7..10%               |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 LISP         | 10ge2p1x520: 64B-1t1c-ethip4lispip4-ip4base-ndrdisc             | 4.4 Mpps  | 4.8 Mpps        | 9%                   |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv4 vhost        | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-ndrdisc     | 0.3 Mpps  | 2.6 Mpps        | 767%                 |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| IPv6              | 10ge2p1x520: 78B-1t1c-ethip6-ip6base-ndrdisc                    | 3.0 Mpps  | 7.3..7.7 Mpps   | 143..157%            |
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

Partial drop rate search, LT = 0.5%:

+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| VPP Functionality | Test Name                                                       | VPP-16.09 | VPP-17.01       | Relative Improvement |
+===================+=================================================================+===========+=================+======================+
| L2XC              | 10ge2p1x520: 64B-1t1c-eth-l2xcbase-pdrdisc                      | 9.4 Mpps  | 12.7..12.9 Mpps | 35..37%              |
+-------------------+-----------------------------------------------------------------+-----------+-----------------+----------------------+
| L2XC              | 10ge2p1xl710: 64B-1t1c-eth-l2xcbase-pdrdisc                     | no data   | no data         |                      |
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
| IPv4 vhost        | 10ge2p1x520: 64B-1t1c-ethip4-ip4base-eth-2vhost-1vm-pdrdisc     | 2.0 Mpps  | 2.7 Mpps        | 35%                  |
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

This is in line with VPP code optimizations listed in `VPP-17.01 release notes
<https://docs.fd.io/vpp/17.01/release_notes_1701.html>`_.

vhost-VM performance improvement is also due to Linux KVM test environment
optimization for vhost-VM tests - see section below "VM vhost-user
Throughput Measurements".

Multi-Thread and Multi-Core Measurements
----------------------------------------

**HyperThreading** - CSIT |release| performance tests are executed with SUT
servers' Intel XEON CPUs configured in HyperThreading Disabled mode (BIOS
settings). This is the simplest configuration used to establish baseline
single-thread single-core SW packet processing and forwarding performance.
Subsequent releases of CSIT will add performance tests with Intel
HyperThreading Enabled (requires BIOS settings change and hard reboot).

**Multi-core Test** - CSIT |release| multi-core tests are executed in the
following VPP thread and core configurations:

#. 1t1c - 1 VPP worker thread on 1 CPU physical core.
#. 2t2c - 2 VPP worker threads on 2 CPU physical cores.
#. 4t4c - 4 VPP threads on 4 CPU physical cores.

Note that in quite a few test cases running VPP on 2 or 4 physical cores hits
the tested NIC I/O bandwidth or packets-per-second limit.

Packet Throughput Measurements
------------------------------

Following values are measured and reported for packet throughput tests:

- NDR binary search per RFC2544:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps
    (2x <per direction packets-per-second>)"
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)"

- PDR binary search per RFC2544:

  - Packet rate: "RATE: <aggregate packet rate in packets-per-second> pps (2x
    <per direction packets-per-second>)"
  - Aggregate bandwidth: "BANDWIDTH: <aggregate bandwidth in Gigabits per
    second> Gbps (untagged)"
  - Packet loss tolerance: "LOSS_ACCEPTANCE <accepted percentage of packets
    lost at PDR rate>""

- NDR and PDR are measured for the following L2 frame sizes:

  - IPv4: 64B, IMIX_v4_1 (28x64B,16x570B,4x1518B), 1518B, 9000B.
  - IPv6: 78B, 1518B, 9000B.


Packet Latency Measurements
---------------------------

TRex Traffic Generator (TG) is used for measuring latency of VPP DUTs. Reported
latency values are measured using following methodology:

- Latency tests are performed at 10%, 50% of discovered NDR rate (non drop rate)
  for each NDR throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the rate of
  10kpps at the prescribed packet size; these are sent in addition to the main
  load streams.
- TG reports min/avg/max latency values per stream direction, hence two sets
  of latency values are reported per test case; future release of TRex is
  expected to report latency percentiles.
- Reported latency values are aggregate across two SUTs due to three node
  topology used for all performance tests; for per SUT latency, reported value
  should be divided by two.
- 1usec is the measurement accuracy advertised by TRex TG for the setup used in
  FD.io labs used by CSIT project.
- TRex setup introduces an always-on error of about 2*2usec per latency flow -
  additonal Tx/Rx interface latency induced by TRex SW writing and reading
  packet timestamps on CPU cores without HW acceleration on NICs closer to the
  interface line.


KVM VM vhost Measurements
-------------------------

CSIT |release| introduced environment configuration changes to KVM Qemu vhost-
user tests in order to more representatively measure VPP-17.01 performance in
configurations with vhost-user interfaces and VMs.

Current setup of CSIT FD.io performance lab is using tuned settings for more
optimal performance of KVM Qemu:

- Default Qemu virtio queue size of 256 descriptors.
- Adjusted Linux kernel CFS scheduler settings, as detailed on this CSIT wiki
  page: https://wiki.fd.io/view/CSIT/VM-vhost-env-tuning.

Adjusted Linux kernel CFS settings make the NDR and PDR throughput performance
of VPP+VM system less sensitive to other Linux OS system tasks by reducing
their interference on CPU cores that are designated for critical software
tasks under test, namely VPP worker threads in host and Testpmd threads in
guest dealing with data plan.

Report Addendum Tests - Cryptodev
---------------------------------

DPDK Cryptodev functionality support for both SW and HW crypto devices has
been introduced in VPP-17.01 release. CSIT functional and performance tests
have been also developed and merged. However due to the factors beyond CSIT
project control execution of those tests within the LF FD.io test environment
still need to complete. Once the results become available, they will be
published as an addendum to the current version of CSIT |release| report.

Report Addendum Tests - Centos
------------------------------

CSIT |release| added Centos functional test execution environment in FD.io
VIRL testbeds.However due to the factors beyond CSIT project control execution
of those tests within the LF FD.io test environment still need to complete.
Once the results become available, they will be published as an addendum to
the current version of CSIT |release| report.

Report Addendum Tests - SNAT44
------------------------------

VPP SNAT44 functionality has been introduced in VPP-17.01 release. CSIT
performance tests are still in development and integration into LFD FD.io test
environment. Once the tests are fully integrated and results become available,
they will be published as an addendum to the current version of CSIT |release|
report.

Known Issues
------------

Here is the list of known issues in CSIT |release| for VPP performance tests in physical HW testbed:

+---+-------------------------------------------------+-----------------------------------------------------------------+
| # | Issue                                           | Description                                                     |
+---+-------------------------------------------------+-----------------------------------------------------------------+
| 1 | Sporadic IPv4 routed-forwwarding NDR discovery  | Suspected issue with DPDK IPv4 checksum calculation, VPP jira # |
|   | test failures for 1518B frame size              | Observed frequency: sporadic, ca. 20% to 30% of test runs       |
+---+-------------------------------------------------+-----------------------------------------------------------------+
|   |                                                 |                                                                 |
+---+-------------------------------------------------+-----------------------------------------------------------------+
|   |                                                 |                                                                 |
+---+-------------------------------------------------+-----------------------------------------------------------------+
