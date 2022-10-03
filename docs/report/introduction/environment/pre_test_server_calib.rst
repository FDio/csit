Pre-Test Server Calibration
---------------------------

Number of SUT server sub-system runtime parameters have been identified
as impacting data plane performance tests. Calibrating those parameters
is part of FD.io CSIT pre-test activities, and includes measuring and
reporting following:

#. System level core jitter - measure duration of core interrupts by
   Linux in clock cycles and how often interrupts happen. Using
   `CPU core jitter tool <https://git.fd.io/pma_tools/tree/jitter>`_.

#. Memory bandwidth - measure bandwidth with `Intel MLC tool
   <https://software.intel.com/en-us/articles/intelr-memory-latency-checker>`_.

#. Memory latency - measure memory latency with Intel MLC tool.

#. Cache latency at all levels (L1, L2, and Last Level Cache) - measure
   cache latency with Intel MLC tool.

Measured values of listed parameters are especially important for
repeatable zero packet loss throughput measurements across multiple
system instances. Generally they come useful as a background data for
comparing data plane performance results across disparate servers.

Following sections include measured calibration data for testbeds.
