Test Environment
================

To execute performance tests, there are three identical testbeds, each testbed
consists of two SUTs and one TG.

Server HW Configuration
-----------------------

See `Performance HW Configuration <../vpp_performance_tests/test_environment.html>`_

Additionally, configuration for the Honeycomb client:


**Honeycomb Startup Command**

Use the server mode JIT compiler, increase the default memory size,
metaspace size, and enable NUMA optimizations for the JVM.

::

    $ java -server -Xms128m -Xmx512m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=512m -XX:+UseNUMA -XX:+UseParallelGC
