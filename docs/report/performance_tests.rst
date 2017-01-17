Performance Tests
=================

Overview
--------

At a physical level there are actually five units of 10GE and 40GE NICs per
SUT made by different vendors: Intel 2p10GE NICs (x520, x710), Intel 40GE NICs
(xl710), Cisco 2p10GE VICs, Cisco 2p40GE VICs. During test execution, all nodes
are reachable thru the MGMT network connected to every node via dedicated NICs
and links (not shown above for clarity). Currently the performance tests only
utilize one model of Intel NICs.  Detailed test bed specification and topology
is described in [[CSIT/CSIT_LF_testbed]].

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a VM is created on SUT1 and SUT2. DUT (VPP) test topology with VM
is shown in the diagram below including the packet flow (marked with \*\*\*)::

    +------------------------+           +------------------------+
    |      +----------+      |           |      +----------+      |
    |      |    VM    |      |           |      |    VM    |      |
    |      |  ******  |      |           |      |  ******  |      |
    |      +--^----^--+      |           |      +--^----^--+      |
    |        *|    |*        |           |        *|    |*        |
    |  +------v----v------+  |           |  +------v----v------+  |
    |  |      *    *      |**|***********|**|      *    *      |  |
    |  |  *****    *******<----------------->*******    *****  |  |
    |  |  *    DUT1       |  |           |  |       DUT2    *  |  |
    |  +--^---------------+  |           |  +---------------^--+  |
    |    *|                  |           |                  |*    |
    |    *|            SUT1  |           |  SUT2            |*    |
    +------------------------+           +------------------^-----+
         *|                                                 |*
         *|                                                 |*
         *|                  +-----------+                  |*
         *|                  |           |                  |*
         *+------------------>    TG     <------------------+*
         ******************* |           |********************
                             +-----------+

Note that for VM tests, packets are switched by DUT (VPP) twice, hence the
throughput rates measured by TG must be multiplied by two to represent the
actual DUT packet forwarding rate.

Because performance testing is run on physical test beds and some tests require
a long time to complete, the performance test jobs have been split into short
duration and long duration variants. The long performance jobs are run on a
periodic basis and run all of the long performance test suites discovering
throughput rates - NDR (Non-Drop Rate) and PDR (Partial Drop Rate) - and
measuring packet latency. The short performance jobs are run on demand and run
the short performance test suites verifying packet throughput against the
reference NDR rates. There are also separate test suites for each NIC type.

The following performance test suites are included in the CSIT-16.09 Release and
measurements listed in this report - test areas added since CSIT-16.06 got
marked with "[&]", extended areas marked with "[%]":

- Long performance test suites with Intel X520-DA2 NIC (2 port 10GbE) - total
  of 469 tests:

  - **L2XC** - NDR & PDR for L2 Cross-Connect switched-forwarding of untagged \
    and QinQ, 801.2Q Vlan, VXLAN tagged packets.
  - **L2BD** - NDR & PDR for L2 Bridge Domain switched-forwarding.
  - **IPv4** - NDR & PDR for IPv4 routed-forwarding.
  - **IPv6** - NDR & PDR for IPv6 routed-forwarding.
  - **COP** - NDR & PDR for IPv4 and IPv6 routed-forwarding with COP address \
    security.
  - **iACL** - NDR & PDR for IPv4 and IPv6 routed-forwarding with iACL address \
    security.
  - **LISP [&]** - NDR & PDR for LISP tunneling dataplane with IP \
    routed-forwarding (IPv4).
  - **VXLAN [&]** - NDR & PDR for VXLAN tunnelling integration with L2XC.
  - **QoS Policer [&]** - NDR & PDR for ingress packet rate measuring, marking \
    and limiting (IPv4).
  - **IPv4 Scale [&]** - NDR & PDR for IPv4 routed-forwarding with 20K, 200K, \
    2M FIB entries.
  - **IPv6 Scale [&]** - NDR & PDR for IPv6 routed-forwarding with 20K, 200K, \
    2M FIB entries.
  - **vhost-user [&]** - NDR & PDR for L2 Cross-Connect, L2 Bridge-Domain, IPv4 \
    routed-forwarding with VM over vhost-user interface.

- Long performance test suites with Intel XL-710 NIC (2 ports 40GbE) - total of
  9 tests:

  - **L2 Cross-Connect [&]** - NDR & PDR for L2 Cross-Connect \
    switched-forwarding of untagged and QinQ, 801.2Q Vlan, VXLAN tagged packets.
  - **L2 Bridge-Domain [&]** - NDR & PDR for L2 Bridge Domain \
    switched-forwarding.
  - **IPv4 [&]** - NDR & PDR for IPv4 routed-forwarding.
  - **IPv6 [&]** - NDR & PDR for IPv6 routed-forwarding.

Measurements - Notes and Caveats
--------------------------------

Packet Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~

TRex traffic generator (TG) new (experimental) functionality is used for
measuring latency of VPP SUTs. Reported latency values are measured using
following methodology:

- Latency tests are performed at 10%, 50% of discovered NDR rate (non drop rate)
  for each NDR throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the rate of
  10kpps at the prescribed packet size; these are sent in addition to the main
  load streams.
- TG reports min/avg/max latency values per stream, hence two sets of latency
  values are reported per test case; future release of TRex is expected to
  report latency percentiles.
- Reported latency values are aggregate across two SUTs due to three node
  topology used for all performance tests; for per SUT latency, reported value
  should be divided by two.
- 1usec is measurements accuracy advertised by TRex TG for the setup used in
  FD.io labs.
- TRex setup introduces an always-on error of about 2*2usec per latency flow -
  additonal Tx/Rx interface latency induced by TRex SW writing and reading
  packet timestamps on CPU cores without HW acceleration on NICs closer to the
  interface line.

VM vhost-user Throughput Measurements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Current setup of CSIT FD.io performance lab is using default Ubuntu 14.04.02
KVM Qemu settings:

- Default Qemu virtio queue size of 256 descriptors.
- Default Linux CFS scheduler settings.

These default settings make the NDR performance of VPP+VM system very sensitive
to any OS system tasks (i.e. Linux kernel) interference on CPU cores that are
designated for critical software tasks under test, namely VPP worker threads in
host and Testpmd threads in guest. CSIT committers decided against tweaking
listed default settings. Instead we decided to report the NDR and PDR
performance numbers with default settings. The impact of CPU jitter on SUTs
performance is clearly visible if one compares NDR and PDR results across
multiple test runs as presented in trending graphs in sections "VPP Trend
Graphs RFC2544:NDR" and "VPP Trend Graphs RFC2544:PDR". To bring NDR rate for
SUTs closer to PDR rates, both Qemu virtio queue size and Linux CFS scheduler
settings need to be adjusted.

Going forward, once integrated into CSIT system, we want to add a separate set
of tests with adjusted default parameters namely i) increased Qemu virtio queue
size to 1024 descriptors, ii) consider adjusting CFS scheduler settings for
tasks under test. Both are subject to ongoing improvements in Qemu code (see
added vhost functionality in Qemu 2.7) and VPP vhost-user driver (see vhost
indirect descriptors patch).

Test Execution Environment
--------------------------

To execute performance tests, there are three identical testbeds, each testbed
consists of two SUTs and one TG.

Hardware details (CPU, memory, NIC layout) are described in
[[CSIT/CSIT_LF_testbed]]; in summary:

- All hosts are Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz,
  18c, 512GB RAM),
- BIOS settings are default except for the following:

  - Hyperthreading disabled,
  - SpeedStep disabled
  - TurboBoost disabled
  - Power Technology: Performance

- Hosts run Ubuntu 14.04.3, kernel 4.2.0-36-generic
- Linux kernel boot command line option "intel_pstate=disable" is applied to
  both SUTs and TG. In addition, on SUTs, only cores 0 and 18 (the first core on
  each socket) are available to the Linux operating system and generic tasks,
  all other CPU cores are isolated and reserved for VPP.
- In addition to CIMC and Management, each TG has 4x Intel X710 10GB NIC
  (=8 ports) and 2x Intel XL710 40GB NIC (=4 ports), whereas each SUT has:

  - 1x Intel X520 NIC (10GB, 2 ports),
  - 1x Cisco VIC 1385 (40GB, 2 ports),
  - 1x Intel XL710 NIC (40GB, 2 ports),
  - 1x Intel X710 NIC (10GB, 2 ports),
  - 1x Cisco VIC 1227 (10GB, 2 ports). This allows for a total of five
    "double-ring" topologies, each using a different NIC.

Config: VPP (DUT)
~~~~~~~~~~~~~~~~~

**NIC types**

- 0a:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+
  Network Connection (rev 01) Subsystem: Intel Corporation Ethernet Server
  Adapter X520-2
- 0a:00.1 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+
  Network Connection (rev 01) Subsystem: Intel Corporation Ethernet Server
  Adapter X520-2
- 85:00.0 Ethernet controller: Intel Corporation Ethernet Controller XL710
  for 40GbE QSFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged
  Network Adapter XL710-Q2
- 85:00.1 Ethernet controller: Intel Corporation Ethernet Controller XL710
  for 40GbE QSFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged
  Network Adapter XL710-Q2

**VPP Version**

vpp-16.09_amd64

**VPP Compile Parameters**

VPP Compile Job: https://jenkins.fd.io/view/vpp/job/vpp-merge-1609-ubuntu1404/

**VPP Install Parameters**

::

    $ dpkg -i --force-all

**VPP Startup Configuration**

VPP startup configuration changes per test case with different settings for CPU
cores, rx-queues and no-multi-seg parameter. Startup config is aligned with
applied test case tag:

Tagged by **1T1C**::

    $ cat /etc/vpp/startup.conf
    unix {
        nodaemon
        log /tmp/vpe.log
        cli-listen localhost:5002
        full-coredump
    }
    api-trace {
        on
    }
    cpu {
        main-core 0 corelist-workers 1
    }
    dpdk {
        socket-mem 1024,1024
        dev default {
            num-rx-queues 1
        }
        dev 0000:0a:00.1
        dev 0000:0a:00.0
        no-multi-seg
    }
    ip6 {
        hash-buckets 2000000
        heap-size 3g
    }

Tagged by **2T1C**::

    $ cat /etc/vpp/startup.conf
    unix {
        nodaemon
        log /tmp/vpe.log
        cli-listen localhost:5002
        full-coredump
    }
    api-trace {
        on
    }
    cpu {
        main-core 0 corelist-workers 1-2
    }
    dpdk {
        socket-mem 1024,1024
        dev default {
            num-rx-queues 1
        }
        dev 0000:0a:00.1
        dev 0000:0a:00.0
        no-multi-seg
    }
    ip6 {
        hash-buckets 2000000
        heap-size 3g
    }

Tagged by **4T4C**::

    $ cat /etc/vpp/startup.conf
    unix {
        nodaemon
        log /tmp/vpe.log
        cli-listen localhost:5002
        full-coredump
    }
    api-trace {
        on
    }
    cpu {
        main-core 0 corelist-workers 1-4
    }
    dpdk {
        socket-mem 1024,1024
        dev default {
            num-rx-queues 1
        }
        dev 0000:0a:00.1
        dev 0000:0a:00.0
        no-multi-seg
    }
    ip6 {
        hash-buckets 2000000
        heap-size 3g
    }


Config: Traffic Generator - TRex
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**TG Version**

TRex v2.09

**DPDK version**

DPDK v16.07 (20e2b6eba13d9eb61b23ea75f09f2aa966fa6325 - in DPDK repo)

**TG Build Script used**

https://gerrit.fd.io/r/gitweb?p=csit.git;a=blob;f=resources/tools/t-rex/t-rex-installer.sh;h=d015015c9275c706d47788cf308aee2a0477231f;hb=refs/heads/rls1609

**TG Startup Configuration**

::

    $ cat /etc/trex_cfg.yaml
    - port_limit      : 2
      version         : 2
      interfaces      : ["0000:0d:00.0","0000:0d:00.1"]
      port_info       :
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]

**TG common API - pointer to driver**

https://gerrit.fd.io/r/gitweb?p=csit.git;a=blob;f=resources/tools/t-rex/t-rex-stateless.py;h=8a7f34b27aaf86d81540d72f05959b409e2134a5;hb=refs/heads/rls1609
