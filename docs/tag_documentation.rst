# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

Documentation for tags used to select and identify test cases.

List of TAGs and their descriptions
===================================

Topology TAGs
-------------

3_NODE_DOUBLE_LINK_TOPO
    3 nodes connected in a circular topology with two links interconnecting
    the devices.

3_NODE_SINGLE_LINK_TOPO
    3 nodes connected in a circular topology with at least one link
    interconnecting devices.

Objective TAGs
--------------

SKIP_PATCH
    Test case(s) marked to not run in case of vpp-csit-verify (i.e. VPP patch)
    and csit-vpp-verify jobs (i.e. CSIT patch).

Environment TAGs
----------------

HW_ENV
    DUTs and TGs are running on bare metal.

VM_ENV
    DUTs and TGs are running in virtual environment.

VPP_VM_ENV
    DUTs with VPP and capable of running Virtual Machine.

DUT Setup TAGs
--------------

1_THREAD_NOHTT_RSS_1
    1 worker thread pinned to dedicated core without use of Hyper-threading
    technology with 1 thread per interface. Main thread pinned to core 0.

2_THREAD_NOHTT_RSS_1
    2 worker threads each pinned to dedicated core without use of Hyper-threading
    technology with 1 thread per interface. Main thread pinned to core 0.

4_THREAD_NOHTT_RSS_2
    4 worker threads each pinned to dedicated core without use of Hyper-threading
    technology with 2 threads per interface. Main thread pinned to core 0.

6_THREAD_NOHTT_RSS_3
    6 worker threads each pinned to dedicated core without use of Hyper-threading
    technology with 3 threads per interface. Main thread pinned to core 0.

8_THREAD_HTT_RSS_4
    8 worker threads each pinned to dedicated core without use of Hyper-threading
    technology with 4 threads per interface. Main thread pinned to core 0.

SINGLE_THREAD
    All single threaded test cases.

MULTI_THREAD
    All test cases with more then one thread.

Performance testing TAGs
------------------------

PERFTEST
    All performance test cases.

PERFTEST_SHORT
    Performance of DUT should pass specific value. Each test case run is
    executed for 10 seconds.

PERFTEST_LONG
    Find performance of DUT based on RFC2544 with linear/binary/combined
    search. Each test case run is executed for 60 seconds.

PDR
    Partial Drop Rate evaluation of single run result. Loss acceptance of
    dropped packets from number of sent packet is set as variable in frames or
    percentage.

NDR
    Non Drop Rate evaluation of results. Loss acceptance of dropped packets is
    set to zero lost packets.

Scaling TAGs
------------

FIB_20K
    2x10,000 entries in single IP fib table

FIB_200K
    2x100,000 entries in single IP fib table

FIB_2M
    2x1,000,000 entries in single IP fib table
