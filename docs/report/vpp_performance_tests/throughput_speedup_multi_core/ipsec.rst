IPSec IPv4 Routing
==================

Following sections include Throughput Speedup Analysis for VPP multi-
core multi-thread configurations with no Hyper-Threading, specifically
for tested 2t2c (2threads, 2cores) and 4t4c scenarios. 1t1c throughput
results are used as a reference for reported speedup ratio.
VPP IPSec encryption is accelerated using DPDK cryptodev
library driving Intel Quick Assist (QAT) crypto PCIe hardware cards.
Performance is reported for VPP running in multiple configurations of
VPP worker thread(s), a.k.a. VPP data plane thread(s), and their
physical CPU core(s) placement.

3n-hsw-x520
~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------


64b-2t2c-base_and_scale
-----------------------


64b-1t1c-features
-----------------


64b-2t2c-features
-----------------


3n-hsw-x710
~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------


64b-2t2c-base_and_scale
-----------------------


64b-1t1c-features
-----------------


64b-2t2c-features
-----------------


3n-hsw-xl710
~~~~~~~~~~~~

64b-1t1c-base_and_scale
-----------------------


64b-2t2c-base_and_scale
-----------------------


3n-skx-x710
~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------


64b-4t2c-base_and_scale
-----------------------


64b-2t1c-features
-----------------


64b-4t2c-features
-----------------


3n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------


64b-4t2c-base_and_scale
-----------------------


64b-2t1c-features
-----------------


64b-4t2c-features
-----------------


2n-skx-x710
~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------


64b-4t2c-base_and_scale
-----------------------


64b-2t1c-features
-----------------


64b-4t2c-features
-----------------


2n-skx-xxv710
~~~~~~~~~~~~~

64b-2t1c-base_and_scale
-----------------------


64b-4t2c-base_and_scale
-----------------------


64b-2t1c-features
-----------------


64b-4t2c-features
-----------------

