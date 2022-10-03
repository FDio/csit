
.. raw:: latex

    \clearpage

.. _vpp_test_environment:

.. include:: ../introduction/environment/intro.rst

.. include:: ../introduction/environment/changes_vpp.rst

.. include:: ../introduction/environment/sut_conf_1.rst


DUT Settings - VPP
------------------

VPP Version
~~~~~~~~~~~

|vpp-release|

VPP Compile Parameters
~~~~~~~~~~~~~~~~~~~~~~

`FD.io VPP compile job`_

VPP Install Parameters
~~~~~~~~~~~~~~~~~~~~~~

::

    $ dpkg -i --force-all *vpp*

VPP Startup Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

VPP startup configuration vary per test case, with different settings
for `$$CORELIST_WORKERS`, `$$NUM_RX_QUEUES`, `$$UIO_DRIVER`, and
`$$NO_MULTI_SEG` parameter. List of plugins to enable is driven by test
requirements. Default template is provided below:

::

    ip
    {
      heap-size 4G
    }
    statseg
    {
      size 4G
      per-node-counters on
    }
    unix
    {
      cli-listen /run/vpp/cli.sock
      log /tmp/vpe.log
      nodaemon
      full-coredump
    }
    socksvr {
      socket-name /run/vpp/api.sock
    }
    ip6
    {
      heap-size 4G
      hash-buckets 2000000
    }
    heapsize 4G
    plugins
    {
      plugin default
      {
        disable
      }
      plugin <$$test_requirement>_plugin.so
      {
        enable
      }
    }
    cpu
    {
      corelist-workers $$CORELIST_WORKERS
      main-core 1
    }
    buffers
    {
      buffers-per-numa 215040
    }

    # Below: in case of dpdk based drivers (vfio-pci) only
    dpdk
    {
      uio-driver $$UIO_DRIVER
      $$NO_MULTI_SEG
      log-level debug
      dev default
      {
        num-rx-queues $$NUM_RX_QUEUES
      }
      no-tx-checksum-offload
      dev $$DEV_1
      dev $$DEV_2
    }

Description of VPP startup settings used in CSIT is provided in
:ref:`test_methodology`.

.. include:: ../introduction/environment/tg.rst

.. include:: ../introduction/environment/pre_test_server_calib.rst

.. include:: ../introduction/environment/sut_calib_icx.rst
.. include:: ../introduction/environment/sut_meltspec_icx.rst

.. include:: ../introduction/environment/sut_calib_clx.rst
.. include:: ../introduction/environment/sut_meltspec_clx.rst

.. include:: ../introduction/environment/sut_calib_zn2.rst
.. include:: ../introduction/environment/sut_meltspec_zn2.rst

.. include:: ../introduction/environment/sut_calib_dnv.rst
.. include:: ../introduction/environment/sut_meltspec_dnv.rst

.. include:: ../introduction/environment/sut_calib_snr.rst
.. include:: ../introduction/environment/sut_meltspec_snr.rst

.. include:: ../introduction/environment/sut_calib_alt.rst
.. include:: ../introduction/environment/sut_meltspec_alt.rst

.. include:: ../introduction/environment/sut_calib_tsh.rst
.. include:: ../introduction/environment/sut_meltspec_tsh.rst

.. include:: ../introduction/environment/sut_calib_tx2.rst
.. include:: ../introduction/environment/sut_meltspec_tx2.rst
