
.. raw:: latex

    \clearpage

.. _vpp_test_environment:

Versioning
----------

In order to determine any benchmark anomalies (progressions,
regressions) between releases of a specific data-plane DUT application
(e.g. VPP, DPDK), the DUT needs to be tested in the same test
environment, to avoid test environment changes impacting the results and
clouding the picture.

In order to enable test system evolution, a mirror scheme is required to
determine benchmarking anomalies between releases of specific test
system like CSIT. This is achieved by testing the same DUT application
version between releases of CSIT test system.

CSIT test environment versioning scheme ensures integrity of all the
test system components, including their HW revisions, compiled SW code
versions and SW source code, within a specific CSIT version. Components
included in the CSIT environment versioning include:

- Server hosts hardware firmware and BIOS (motherboard, processsor, NIC(s), accelerator card(s)).
- Server host Linux operating system versions.
- Server host Linux configuration.
- TRex Traffic Generator version, drivers and configuration.
- CSIT framework code.

Following is the list of CSIT versions to date:

- Ver. 1 associated with CSIT rls1908 git branch as of 2019-08-21.
- Ver. 2 associated with CSIT rls2001 git branch as of 2020-03-27.
- Ver. 3 interim associated with master branch as of 2020-xx-xx.
- Ver. 4 associated with CSIT rls2005 git branch as of 2020-06-24.

To identify performance changes due to VPP code changes from v20.01.0 to
v20.05.0, both have been tested in CSIT environment ver. 4 and compared
against each other. All substantial progressions has been marked up with
RCA analysis. See Current vs Previous Release and Known Issues.

CSIT environment ver. 4 has been evaluated against the ver. 2 by
benchmarking VPP v20.01.0 in both environrment versions.

.. include:: ../introduction/test_environment_intro.rst

.. include:: ../introduction/test_environment_sut_conf_1.rst


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

.. include:: ../introduction/test_environment_tg.rst

.. include:: ../introduction/test_environment_pre_test_server_calib.rst

.. include:: ../introduction/test_environment_sut_calib_skx.rst

.. include:: ../introduction/test_environment_sut_calib_clx.rst

.. include:: ../introduction/test_environment_sut_calib_hsw.rst

.. include:: ../introduction/test_environment_sut_calib_dnv.rst

.. include:: ../introduction/test_environment_sut_calib_tsh.rst
