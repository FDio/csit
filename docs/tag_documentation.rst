.. |copy| unicode:: 0xA9 .. copyright sign

| Copyright |copy| 2016 Cisco and/or its affiliates.
| Licensed under the Apache License, Version 2.0 (the "License");
| you may not use this file except in compliance with the License.
| You may obtain a copy of the License at:
|
|     http://www.apache.org/licenses/LICENSE-2.0
|
| Unless required by applicable law or agreed to in writing, software
| distributed under the License is distributed on an "AS IS" BASIS,
| WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
| See the License for the specific language governing permissions and
| limitations under the License.


.. contents:: Table of Contents
   :depth: 2


TAGs and their descriptions
===========================

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

Environment TAGs
----------------

.. topic:: HW_ENV

    DUTs and TGs are running on bare metal.

.. topic:: VM_ENV

    DUTs and TGs are running in virtual environment.

.. topic:: VPP_VM_ENV

    DUTs with VPP and capable of running Virtual Machine.


DUT Setup TAGs - old tags
-------------------------

.. note:: Remove this section when all new tags are implemented to tests and
          scripts.

1_THREAD_NOHTT_RSS_1
    1 worker thread pinned to dedicated core without use of Hyper-threading
    technology with 1 thread per interface. Main thread pinned to core 0.

2_THREAD_NOHTT_RSS_1
    2 worker threads each pinned to dedicated core without use of
    threading technology with 1 thread per interface. Main thread pinned
    to core 0.

4_THREAD_NOHTT_RSS_2
    4 worker threads each pinned to dedicated core without use of Hyper-
    Hyper-threading technology with 2 threads per interface. Main thread pinned
    to core 0.

6_THREAD_NOHTT_RSS_3
    6 worker threads each pinned to dedicated core without use of Hyper-
    Hyper-threading technology with 3 threads per interface. Main thread pinned
    to core 0.

8_THREAD_HTT_RSS_4
    8 worker threads each pinned to dedicated core without use of
    Hyper-threading technology with 4 threads per interface. Main thread pinned
    to core 0.

SINGLE_THREAD
    All single threaded test cases.

MULTI_THREAD
    All test cases with more then one thread.


Performance testing TAGs - old tags
-----------------------------------

.. note:: Remove this section when all new tags are implemented to tests and
          scripts.

PERFTEST
    All performance test cases.

PERFTEST_VHOST
    All performance test cases that include testing of VHOST with VM.

PERFTEST_SHORT
    Performance of DUT should pass specific value. Each test case run is
    executed for 10 seconds.

PERFTEST_LONG
    Find performance of DUT based on RFC2544 with linear/binary/combined
    search.

PERFTEST_ENCAP
    All encapsulation test case.

PERFTEST_BASE
    All baseline test case.

PDR
    Partial Drop Rate evaluation of single run result. Loss acceptance of
    dropped packets from number of sent packet is set as variable in frames or
    percentage.

NDR
    Non Drop Rate evaluation of results. Loss acceptance of dropped packets is
    set to zero lost packets.


Scaling TAGs
------------

.. topic:: FIB_20K

    2x10,000 entries in single fib table

.. topic:: FIB_200K

    2x100,000 entries in single fib table

.. topic:: FIB_2M

    2x1,000,000 entries in single fib table


LISP TAGs
---------

.. topic:: LISP

    All Lisp test cases.

.. topic:: LISP_IPv4

    Test Lisp in IPv4 topology.

.. topic:: LISP_IPv6

    Test Lisp in IPv6 topology.

.. topic:: LISP_IPv4oIPv6

    Test IPv4 over IPv6 topology.

.. topic:: LISP_IPv6oIPv4

    Test IPv6 over IPv4 topology.


New tags
========

.. note:: Remove the headline "New tags" when sections marked "Old tags" are
          removed.


Tags marking the kinds of tags
------------------------------

.. topic:: FUNCTEST

    All functional test cases.

.. topic:: PERFTEST

    All performance test cases.


Performance testing tags
------------------------

.. topic:: PDR

    Partial Drop Rate evaluation of single run result, with non-zero packet
    loss tolerance (LT) expressed in percentage of packets transmitted.

.. topic:: NDR

    Non Drop Rate evaluation of results. Loss acceptance of dropped packets is
    set to zero lost packets.

.. topic:: REF_NDR

    Performance tests where TG verifies DUTs' throughput at ref-NDR (reference
    Non Drop Rate) with zero packet loss tolerance.

.. topic:: RFC2544

    Find performance of DUT based on RFC2544 with linear / binary / combined
    search. (Previous LONG tests.)


Test type tags
--------------

.. topic:: BASE

    Baseline tests, no encapsulation.

.. topic:: ENCAP

    Tests where encapsulation is used.

.. topic:: SCALE

    Scale tests.


Layer tags
----------

.. topic:: L2BD

    VPP L2 bridge-domain, L2 MAC learning and switching.

.. topic:: L2XC

    VPP L2 point-to-point cross-connect.

.. topic:: IP4

    VPP IPv4 routed forwarding.

.. topic:: IP6

    VPP IPv6 routed forwarding.


Feature tags
------------

.. topic:: LISP

    All Lisp test cases.

.. topic:: FIB

    All FIB test cases.

.. topic:: VHOST

    All Vhost test cases.

.. topic:: VXLAN

    All Vxlan test cases.


VM tags
-------

.. topic:: VM

    All test cases which use at least one virtual machine.


Multi-threading tags
--------------------

.. topic:: SINGLE_THREAD

    All single threaded test cases.

.. topic:: MULTI_THREAD

    All test cases with more then one thread.

.. topic:: 1TH_1PC_1RXQ

    1 worker thread pinned to 1 dedicated physical core. 1 receive queue per
    interface. Main thread pinned to core 0.

.. topic:: 2TH_2PC_1RXQ

    2 worker threads pinned to 2 dedicated physical cores. 1 receive queue per
    interface. Main thread pinned to core 0.

.. topic:: 4TH_4PC_2RXQ

    4 worker threads pinned to 4 dedicated physical cores. 2 receive queues per
    interface. Main thread pinned to core 0.

.. topic:: 6TH_6PC_3RXQ

    6 worker threads pinned to 6 dedicated physical cores. 3 receive queues per
    interface. Main thread pinned to core 0.

.. topic:: 8TH_8PC_4RXQ

    8 worker threads pinned to 8 dedicated physical cores. 4 receive queues per
    interface. Main thread pinned to core 0.
