
.. raw:: latex

    \clearpage

.. _vpp_throughput_comparisons:

Comparisons
===========

..
    // Alternative Note for 1st Bullet when bad microcode Skx, Clx results are published
    note::
    VPP throughput drop in the current release in comparison to previous
    releases **on Intel Xeon 2n-skx, 3n-skx and 2n-clx testbeds**: VPP
    performance test data shows lower performance and behaviour
    inconsistency of these systems following the recent upgrade of
    processor microcode packages (skx ucode 0x2000064, clx ucode
    0x500002c) as part of updating Ubuntu 18.04 LTS kernel version.
    Tested VPP and DPDK applications (L3fwd) are affected. Skx and Clx
    test data will be corrected in subsequent maintenance report
    version(s) once the issue is resolved. See :ref:`vpp_known_issues`.

.. toctree::

    current_vs_previous_release

..
    3n-skx_vs_3n-hsw_testbeds
    2n-skx_vs_2n-clx_testbeds
    3n-skx_vs_2n-skx_testbeds
    nic_comparison
