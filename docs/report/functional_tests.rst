Functional Tests
================

Overview
--------

Functional tests run on virtual testbeds which are created in VIRL running on a
Cisco UCS C240 servers hosted in Linux Foundation labs. There is currently only
one testbed topology being used for functional testing - a three node topology
with two links between each pair of nodes as shown in this diagram::

    +--------+                      +--------+
    |        |                      |        |
    |  SUT1  <---------------------->  SUT2  |
    |        <---------------------->        |
    |        |                      |        |
    +---^^---+                      +---^^---+
        ||                              ||
        ||          +--------+          ||
        ||          |        |          ||
        |+---------->   TG   <----------+|
        +----------->        <-----------+
                    |        |
                    +--------+

Virtual testbeds are created dynamically whenever a patch is submitted to gerrit
and destroyed upon completion of all functional tests. During test execution,
all nodes are reachable thru the MGMT network connected to every node via
dedicated NICs and links (not shown above for clarity). Each node is a Virtual
Machine and each connection that is drawn on the diagram is available for use in
any test case.

For test cases that require DUT (VPP) to communicate with VM over vhost-user
interfaces, a nested VM is created on SUT1 and/or SUT2 for the duration of that
particular test case only. DUT (VPP) test topology with VM is shown in the
diagram below including the packet flow (marked with ``*``)::

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

The following functional test suites are included in the CSIT-16.09 Release and
this report - test areas added since CSIT-16.06 got marked with [&], extended
areas marked with [%]:

* **L2XC [%]** - L2 Cross-Connect switching of Ethernet frames (untagged, VLAN
  single-tag 802.1q, double-tag 802.1ad).
* **L2BD [%]** - L2 Bridge-Domain switching of Ethernet frames (untagged,
  802.1q, 802.1ad).
* **IPv4 [%]** - IPv4 routed-forwarding, RPF, ARP, Proxy ARP, ICMPv4.
* **IPv6 [%]** - IPv6 routed-forwarding, NS/ND, RA, ICMPv6.
* **DHCP [%]** - DHCP Client and Proxy (IPv4, IPv6).
* **VXLAN** - VXLAN tunnelling dataplane with L2BD, L2XC (untagged, 802.1q).
* **COP** - COP address security, white-listing and black-listing (IPv4, IPv6).
* **GRE [%]** - GRE tunnelling dataplane with IP routed-forwarding (IPv4).
* **LISP [%]** - LISP tunneling dataplane with IP routed-forwarding (IPv4) and
  API functionality.
* **iACL [%]** - Ingress Access Control List security (IPv4, IPv6, L2).
* **VRF [&]** - IP VPN routed-forwarding (IPv4, IPv6).
* **QoS Policer [&]** - ingress packet rate measuring, marking and limiting
  (IPv4, IPv6).
* **IPFIX [&]** - IPFIX Netflow (IPv4, IPv6).
* **IPSec [&]** - IPSec transport and tunnel mode (IPv4, IPv6).
* **Softwire [&]** - IPv4-over-IPv6 Softwire Concentration including
  LightWeight4over6, MAP-E, MAP-T.
* **VLAN rewrites [&]** - L2 VLAN rewrite tests 2-2, 2-1, 1-2 with L2XC and L2BD.
* **Tap Interface [&]** - baseline Linux tap interface tests.
* **HoneyComb [&]** - HoneyComb control plane interface into VPP.

Total 199 functional tests in the CSIT-16.09 Release (up from 76 functional
tests in the CSIT-16.06 Release).


Test Execution Environment
--------------------------

CSIT functional tests are currently executed in VIRL, as mentioned above. The
physical VIRL testbed infrastructure consists of three identical VIRL hosts,
each host being a Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @
2.30GHz, 18c, 512GB RAM) running Ubuntu 14.04.3 and the following VIRL software
versions:

  STD server version 0.10.24.7
  UWM server version 0.10.24.7

Whenever a patch is submitted to gerrit for review, one of the three VIRL hosts
is selected randomly, and a three-node (TG+SUT1+SUT2), "double-ring" topology is
created as a VIRL simulation on the selected host. The appropriate pre-built VPP
packages built by Jenkins for the patch under review are then installed on the
two SUTs, along with their /etc/vpp/startup.conf file.

Current VPP tests have been executed on a single VM operating system and
version only, as described in the following paragraphs.

In CSIT terminology, the VM operating system for both SUTs and TG that VPP 17.01
has been tested with, is the following:

  ubuntu-16.04.1_2016-12-19_1.6

which implies Ubuntu 16.04.1 LTS, current as of 2016/12/19 (that is, package
versions are those that would have been installed by a "apt-get update",
"apt-get upgrade" on December 19), produced by CSIT disk image build scripts version
1.6.

The exact list of installed packages and their versions (including the Linux
kernel package version) are included in CSIT source repository:

  resources/tools/disk-image-builder/ubuntu/lists/ubuntu-16.04.1_2016-12-19_1.6

A replica of this VM image can be built by running the "build.sh" script in CSIT
repository resources/tools/disk-image-builder/.

In addition to this "main" VM image, tests which require VPP to communicate to a
VM over a vhost-user interface, utilize a "nested" VM image.

This "nested" VM is dynamically created and destroyed as part of a test case,
and therefore the "nested" VM image is optimized to be small, lightweight and
have a short boot time. The "nested" VM image is not built around any
established Linux distribution, but is based on BuildRoot
(https://buildroot.org/), a tool for building embedded Linux systems. Just as
for the "main" image, scripts to produce an identical replica of the "nested"
image are included in CSIT GIT repository, and the image can be rebuilt using
the "build.sh" script at:

   resources/tools/disk-image-builder/ubuntu/lists/nested

Functional tests utilize Scapy as a traffic generator.  All of the python
libraries used by CSIT are specified in csit/requirements.txt.
