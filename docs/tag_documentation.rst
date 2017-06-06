CSIT TAGs Descriptions
======================

Documentation for tags used to select and identify test cases.


Topology TAGs
-------------

.. topic:: 3_NODE_DOUBLE_LINK_TOPO

    3 nodes connected in a circular topology with two links interconnecting
    the devices.

.. topic:: 3_NODE_SINGLE_LINK_TOPO

    3 nodes connected in a circular topology with at least one link
    interconnecting devices.


Objective TAGs
--------------

.. topic:: SKIP_PATCH

    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP patch)
    and csit-vpp-verify jobs (i.e. CSIT patch).

.. topic:: SKIP_VPP_PATCH

    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP patch).


Environment TAGs
----------------

.. topic:: HW_ENV

    DUTs and TGs are running on bare metal.

.. topic:: VM_ENV

    DUTs and TGs are running in virtual environment.

.. topic:: VPP_VM_ENV

    DUTs with VPP and capable of running Virtual Machine.


NIC model tags
--------------

.. topic:: NIC_Intel-X520-DA2

    Intel X520-DA2 NIC.

.. topic:: NIC_Intel-XL710

    Intel XL710 NIC.

.. topic:: NIC_Intel-X710

    Intel X710 NIC.

.. topic:: NIC_Cisco-VIC-1227

    VIC-1227 by Cisco.

.. topic:: NIC_Cisco-VIC-1385

    VIC-1385 by Cisco.


Scaling TAGs
------------

.. topic:: FIB_20K

    2x10,000 entries in single fib table

.. topic:: FIB_200K

    2x100,000 entries in single fib table

.. topic:: FIB_2M

    2x1,000,000 entries in single fib table

.. topic:: TNL_1000

    IPSec in tunnel mode - 1000 tunnels.

.. topic:: SRC_USER_10

    Traffic flow with 10 unique IPs (users) in one direction.

.. topic:: SRC_USER_100

    Traffic flow with 100 unique IPs (users) in one direction.

.. topic:: SRC_USER_1000

    Traffic flow with 1000 unique IPs (users) in one direction.

.. topic:: SRC_USER_2000

    Traffic flow with 2000 unique IPs (users) in one direction.

.. topic:: SRC_USER_4000

    Traffic flow with 4000 unique IPs (users) in one direction.


Tags marking functional vs. performance of tests
------------------------------------------------

.. topic:: FUNCTEST

    All functional test cases.

.. topic:: PERFTEST

    All performance test cases.


Performance testing tags
------------------------

.. topic:: PDRDISC

    Partial Drop Rate evaluation of single run result, with non-zero packet
    loss tolerance (LT) expressed in percentage of packets transmitted.

.. topic:: NDRDISC

    Non Drop Rate evaluation of results. Loss acceptance of dropped packets is
    set to zero lost packets.

.. topic:: NDRCHK

    Performance tests where TG verifies DUTs' throughput at ref-NDR (reference
    Non Drop Rate) with zero packet loss tolerance.

.. topic:: NDRPDRDISC

    Find performance of DUT based on RFC2544 with linear / binary / combined
    search. (Previous LONG tests.)

Ethernet frame size tags for performance tests
----------------------------------------------

.. topic:: 64B

    64B frames used for test.

.. topic:: 78B

    78B frames used for test.

.. topic:: IMIX

    IMIX frame sequence (28x 64B, 16x 570B, 4x 1518B) used for test.

.. topic:: 1460B

    1460B frames used for test.

.. topic:: 1480B

    1480B frames used for test.

.. topic:: 1514B

    1514B frames used for test.

.. topic:: 1518B

    1518B frames used for test.

.. topic:: 9000B

    9000B frames used for test.

Test type tags
--------------

.. topic:: BASE

    Baseline test cases, no encapsulation, no feature(s) configured in tests.

.. topic:: IP4BASE

    IPv4 baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: IP6BASE

    IPv6 baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: L2XCBASE

    L2XC baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: L2BDBASE

    L2BD baseline test cases, no encapsulation, no feature(s) configured in
    tests.

.. topic:: SCALE

    Scale test cases.

.. topic:: ENCAP

    Test cases where encapsulation is used. Use also encapsulation tag(s).

.. topic:: FEATURE

    At least one feature is configured in test cases. Use also feature tag(s).


Forwarding mode tags
--------------------

.. topic:: L2BDMACSTAT

    VPP L2 bridge-domain, L2 MAC static.

.. topic:: L2BDMACLRN

    VPP L2 bridge-domain, L2 MAC learning.

.. topic:: L2XCFWD

    VPP L2 point-to-point cross-connect.

.. topic:: IP4FWD

    VPP IPv4 routed forwarding.

.. topic:: IP6FWD

    VPP IPv6 routed forwarding.


Underlay tags
-------------

.. topic:: IP4UNRLAY

    IPv4 underlay.

.. topic:: IP6UNRLAY

    IPv6 underlay.

.. topic:: MPLSUNRLAY

    MPLS underlay.


Overlay tags
------------

.. topic:: L2OVRLAY

    L2 overlay.

.. topic:: IP4OVRLAY

    IPv4 overlay (IPv4 payload).

.. topic:: IP6OVRLAY

    IPv6 overlay (IPv6 payload).


Encapsulation tags
------------------

.. topic:: ETH

    All test cases with base Ethernet (no encapsulation).

.. topic:: DOT1Q

    All test cases with dot1q.

.. topic:: DOT1AD

    All test cases with dot1ad.

.. topic:: LISP

    All test cases with LISP.

.. topic:: LISPGPE

    All test cases with LISP-GPE.

.. topic:: VXLAN

    All test cases with Vxlan.

.. topic:: VXLANGPE

    All test cases with VXLAN-GPE.

.. topic:: GRE

    All test cases with GRE.

.. topic:: IPSEC

    All test cases with IPSEC.


Interface tags
--------------

.. topic:: PHY

    All test cases which use physical interface(s).

.. topic:: VHOST

    All test cases which uses VHOST.

.. topic:: TUNTAP

    All test cases which uses TUN and TAP.

.. topic:: AFPKT

    All test cases which uses AFPKT.

.. topic:: NETMAP

    All test cases which uses Netmap.

.. topic:: MEMIF

    All test cases which uses Memif.

Feature tags
------------

.. topic:: IACLDST

    iACL destination.

.. topic:: COPWHLIST

    COP whitelist.

.. topic:: SNAT

    SNAT configured and tested.


Encryption tags
---------------

.. topic:: IPSECSW

    Crypto in software.

.. topic:: IPSECHW

    Crypto in hardware.

.. topic:: IPSECTRAN

    IPSec in transport mode.

.. topic:: IPSECTUN

    IPSec in tunnel mode.


Client-workload tags
--------------------

.. topic:: VM

    All test cases which use at least one virtual machine.

.. topic:: LXC

    All test cases which use Linux container.

.. topic:: APP

    All test cases with specific APP use.


Multi-threading tags
--------------------

.. topic:: STHREAD

    All test cases using single poll mode thread.

.. topic:: MTHREAD

    All test cases using more then one poll mode driver thread.

.. topic:: 1NUMA

    All test cases with packet processing on single socket.

.. topic:: 2NUMA

    All test cases with packet processing on two sockets.

.. topic:: SMT

    All test cases with symmetric Multi-Threading (HyperThreading) enabled.

.. topic:: NOSMT

    All test cases with symmetric Multi-Threading (HyperThreading) disabled.

.. topic:: 1T1C

    1 worker thread pinned to 1 dedicated physical core. 1 receive queue per
    interface. Main thread pinned to core 0.

.. topic:: 2T2C

    2 worker threads pinned to 2 dedicated physical cores. 1 receive queue per
    interface. Main thread pinned to core 0.

.. topic:: 4T4C

    4 worker threads pinned to 4 dedicated physical cores. 2 receive queues per
    interface. Main thread pinned to core 0.

.. topic:: 6T6C

    6 worker threads pinned to 6 dedicated physical cores. 3 receive queues per
    interface. Main thread pinned to core 0.

.. topic:: 8T8C

    8 worker threads pinned to 8 dedicated physical cores. 4 receive queues per
    interface. Main thread pinned to core 0.


Honeycomb tags
--------------

.. topic:: HC_FUNC

    Honeycomb functional test cases.

.. topic:: HC_PERSIST

    Honeycomb persistence test cases.

.. topic:: HC_REST_ONLY

    (Exclusion tag) Honeycomb test cases that cannot be run in Netconf mode
    using ODL client for Restfconf -> Netconf translation.
