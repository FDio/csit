IPSec IPv4 Routing
==================

This section includes summary graphs of VPP Phy-to-Phy packet latency
with IPSec encryption used in combination with IPv4 routed-forwarding,
with latency measured at 50% of discovered NDR throughput rate. VPP
IPSec encryption is accelerated using DPDK cryptodev library driving
Intel Quick Assist (QAT) crypto PCIe hardware cards. Latency is reported
for VPP running in multiple configurations of VPP worker thread(s),
a.k.a. VPP data plane thread(s), and their physical CPU core(s)
placement.

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

