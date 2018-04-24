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

VPP startup configuration changes per test case with different settings for CPU
cores, rx-queues and no-multi-seg parameter. Startup config is aligned with
applied test case tag:

Tagged by **1T1C**

::

    ip
    {
      heap-size 4G
    }
    unix
    {
      cli-listen localhost:5002
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
      corelist-workers 2
      main-core 1
    }
    dpdk
    {
      dev 0000:0a:00.0
      dev 0000:0a:00.1
      no-multi-seg
      uio-driver uio_pci_generic
      log-level debug
      dev default
      {
        num-rx-queues 1
      }
      socket-mem 1024,1024
      no-tx-checksum-offload
    }

Tagged by **2T2C**

::

    ip
    {
      heap-size 4G
    }
    unix
    {
      cli-listen localhost:5002
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
      corelist-workers 2,3
      main-core 1
    }
    dpdk
    {
      dev 0000:0a:00.0
      dev 0000:0a:00.1
      no-multi-seg
      uio-driver uio_pci_generic
      log-level debug
      dev default
      {
        num-rx-queues 1
      }
      socket-mem 1024,1024
      no-tx-checksum-offload
    }

Tagged by **4T4C**

::

    ip
    {
      heap-size 4G
    }
    unix
    {
      cli-listen localhost:5002
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
      corelist-workers 2,3,4,5
      main-core 1
    }
    dpdk
    {
      dev 0000:0a:00.0
      dev 0000:0a:00.1
      no-multi-seg
      uio-driver uio_pci_generic
      log-level debug
      dev default
      {
        num-rx-queues 1
      }
      socket-mem 1024,1024
      no-tx-checksum-offload
    }

.. include:: test_environment_tg.rst
