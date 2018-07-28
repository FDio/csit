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

Testpmd startup configuration changes per test case with different settings for
`$$CORES`, `$$RXQ` and max-pkt-len parameter if test is sending jumbo frames.
Startup command template:

.. code-block:: bash

    testpmd -c $$CORE_MASK -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=$$CORES --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=$$RXQ --txq=$$TXQ --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

**L3FWD Startup Configuration**

L3FWD startup configuration changes per test case with different settings for
`$$CORES` and enable-jumbo parameter if test is sending jumbo frames.
Startup command template:

.. code-block:: bash

    l3fwd -l $$CORE_LIST -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype


.. include:: ../vpp_performance_tests/test_environment_tg.rst
