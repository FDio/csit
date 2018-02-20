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

    unix
    {
      cli-listen localhost:5002
      log /tmp/vpe.log
      nodaemon
    }
    cpu
    {
      corelist-workers 2
      main-core 1
    }
    ip4
    {
      heap-size "4G"
    }
    ip6
    {
      heap-size "4G"
      hash-buckets "2000000"
    }
    plugins
    {
      plugin pppoe_plugin.so { disable }
      plugin kubeproxy_plugin.so { disable }
      plugin ioam_plugin.so { disable }
      plugin ila_plugin.so { disable }
      plugin stn_plugin.so { disable }
      plugin acl_plugin.so { disable }
      plugin l2e_plugin.so { disable }
      plugin sixrd_plugin.so { disable }
      plugin nat_plugin.so { disable }
      plugin ixge_plugin.so { disable }
      plugin lb_plugin.so { disable }
      plugin memif_plugin.so { disable }
      plugin gtpu_plugin.so { disable }
      plugin flowprobe_plugin.so { disable }
    }
    heapsize "4G"
    dpdk
    {
      dev 0000:88:00.1
      dev 0000:88:00.0
      no-multi-seg
      dev default
      {
        num-rx-desc 2048
        num-rx-queues 1
        num-tx-desc 2048
      }
      socket-mem "1024,1024"
      no-tx-checksum-offload
    }

Tagged by **2T2C**

::

    unix
    {
      cli-listen localhost:5002
      log /tmp/vpe.log
      nodaemon
    }
    cpu
    {
      corelist-workers 2,3
      main-core 1
    }
    ip4
    {
      heap-size "4G"
    }
    ip6
    {
      heap-size "4G"
      hash-buckets "2000000"
    }
    plugins
    {
      plugin pppoe_plugin.so { disable }
      plugin kubeproxy_plugin.so { disable }
      plugin ioam_plugin.so { disable }
      plugin ila_plugin.so { disable }
      plugin stn_plugin.so { disable }
      plugin acl_plugin.so { disable }
      plugin l2e_plugin.so { disable }
      plugin sixrd_plugin.so { disable }
      plugin nat_plugin.so { disable }
      plugin ixge_plugin.so { disable }
      plugin lb_plugin.so { disable }
      plugin memif_plugin.so { disable }
      plugin gtpu_plugin.so { disable }
      plugin flowprobe_plugin.so { disable }
    }
    heapsize "4G"
    dpdk
    {
      dev 0000:88:00.1
      dev 0000:88:00.0
      no-multi-seg
      dev default
      {
        num-rx-desc 2048
        num-rx-queues 1
        num-tx-desc 2048
      }
      socket-mem "1024,1024"
      no-tx-checksum-offload
    }

Tagged by **4T4C**

::

    unix
    {
      cli-listen localhost:5002
      log /tmp/vpe.log
      nodaemon
    }
    cpu
    {
      corelist-workers 2,3,4,5
      main-core 1
    }
    ip4
    {
      heap-size "4G"
    }
    ip6
    {
      heap-size "4G"
      hash-buckets "2000000"
    }
    plugins
    {
      plugin pppoe_plugin.so { disable }
      plugin kubeproxy_plugin.so { disable }
      plugin ioam_plugin.so { disable }
      plugin ila_plugin.so { disable }
      plugin stn_plugin.so { disable }
      plugin acl_plugin.so { disable }
      plugin l2e_plugin.so { disable }
      plugin sixrd_plugin.so { disable }
      plugin nat_plugin.so { disable }
      plugin ixge_plugin.so { disable }
      plugin lb_plugin.so { disable }
      plugin memif_plugin.so { disable }
      plugin gtpu_plugin.so { disable }
      plugin flowprobe_plugin.so { disable }
    }
    heapsize "4G"
    dpdk
    {
      dev 0000:88:00.1
      dev 0000:88:00.0
      no-multi-seg
      dev default
      {
        num-rx-desc 2048
        num-rx-queues 2
        num-tx-desc 2048
      }
      socket-mem "1024,1024"
      no-tx-checksum-offload
    }

.. include:: test_environment_tg.rst
