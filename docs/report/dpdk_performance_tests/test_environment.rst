
.. raw:: latex

    \clearpage

.. _dpdk_test_environment:

.. include:: ../introduction/test_environment_intro.rst

.. include:: ../introduction/test_environment_sut_calib_skx.rst

.. include:: ../introduction/test_environment_sut_calib_clx.rst

.. include:: ../introduction/test_environment_sut_calib_hsw.rst

.. include:: ../introduction/test_environment_sut_calib_dnv.rst

.. include:: ../introduction/test_environment_sut_calib_tsh.rst

.. include:: ../introduction/test_environment_sut_conf_1.rst


DUT Settings - DPDK
-------------------

DPDK Version
~~~~~~~~~~~~

|dpdk-release|

DPDK Compile Parameters
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    make install T=<arch>-<machine>-linuxapp-gcc -j

Testpmd Startup Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Testpmd startup configuration changes per test case with different
settings for `$$INT`, `$$CORES`, `$$RXQ`, `$$RXD` and max-pkt-len parameter if
test is sending jumbo frames. Startup command template:

.. code-block:: bash

    testpmd -v -l $$CORE_LIST -w $$INT1 -w $$INT2 --master-lcore 0 --in-memory -- --forward-mode=io --burst=64 --txd=$$TXD --rxd=$$RXD --txq=$$TXQ --rxq=$$RXQ --tx-offloads=0x0 --numa --auto-start --total-num-mbufs=16384 --nb-ports=2 --portmask=0x3 --disable-link-check --max-pkt-len=$$PKT_LEN [--mbuf-size=16384] --nb-cores=$$CORES

L3FWD Startup Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

L3FWD startup configuration changes per test case with different
settings for `$$INT`, `$$CORES` and enable-jumbo parameter if test is sending
jumbo frames. Startup command template:

.. code-block:: bash

    l3fwd -v -l $$CORE_LIST -w $$INT1 -w $$INT2 --master-lcore 0 --in-memory -- --parse-ptype --eth-dest="0,${adj_mac0}" --eth-dest="1,${adj_mac1}" --config="${port_config}" [--enable-jumbo] -P -L -p 0x3

.. include:: ../introduction/test_environment_tg.rst
