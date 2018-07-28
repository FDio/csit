.. include:: test_environment_intro.rst

.. include:: test_environment_sut_conf_1.rst

.. include:: test_environment_sut_conf_2.rst

.. include:: test_environment_sut_conf_3.rst


DUT Configuration - VPP
-----------------------

**VPP Version**

|vpp-release|

**VPP Compile Parameters**

`FD.io VPP compile job`_

**VPP Install Parameters**

::

    $ dpkg -i --force-all vpp*

**VPP Startup Configuration**

VPP startup configuration changes per test case with different settings for
`$$CORELIST_WORKERS`, `$$NUM_RX_QUEUES`, `$$UIO_DRIVER`, `$$NUM-MBUFS` and
`$$NO_MULTI_SEG` parameter. Default template:

::

    ip
    {
      heap-size 4G
    }
    statseg
    {
      size 4G
    }
    unix
    {
      cli-listen /run/vpp/cli.sock
      log /tmp/vpe.log
      nodaemon
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
      plugin dpdk_plugin.so
      {
        enable
      }
    }
    cpu
    {
      corelist-workers $$CORELIST_WORKERS
      main-core 1
    }
    dpdk
    {
      num-mbufs $$NUM-MBUFS
      uio-driver $$UIO_DRIVER
      $$NO_MULTI_SEG
      log-level debug
      dev default
      {
        num-rx-queues $$NUM_RX_QUEUES
      }
      socket-mem 1024,1024
      no-tx-checksum-offload
      dev $$DEV_1
      dev $$DEV_2
    }

.. include:: test_environment_tg.rst
