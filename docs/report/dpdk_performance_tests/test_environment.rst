.. include:: ../vpp_performance_tests/test_environment_intro.rst

.. include:: ../vpp_performance_tests/test_environment_sut_conf_1.rst

.. include:: ../vpp_performance_tests/test_environment_sut_conf_3.rst


DUT Configuration - DPDK
------------------------

**DPDK Version**

|dpdk-release|

**DPDK Compile Parameters**

.. code-block:: bash

    make install T=x86_64-native-linuxapp-gcc -j

**Testpmd Startup Configuration**

Testpmd startup configuration changes per test case with different settings for CPU
cores, rx-queues. Startup config is aligned with applied test case tag:

Tagged by **1T1C**

.. code-block:: bash

    testpmd -c 0x3 -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=1 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=1 --txq=1 --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

Tagged by **2T2C**

.. code-block:: bash

    testpmd -c 0x403 -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=2 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=1 --txq=1 --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

Tagged by **4T4C**

.. code-block:: bash

    testpmd -c 0xc07 -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=4 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=2 --txq=2 --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

**L3FWD Startup Configuration**

L3FWD startup configuration changes per test case with different settings for CPU
cores, rx-queues. Startup config is aligned with applied test case tag:

Tagged by **1T1C**

.. code-block:: bash

    l3fwd -l 1 -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype

Tagged by **2T2C**

.. code-block:: bash

    l3fwd -l 1,2 -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype

Tagged by **4T4C**

.. code-block:: bash

    l3fwd -l 1,2,3,4 -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype


.. include:: ../vpp_performance_tests/test_environment_tg.rst
