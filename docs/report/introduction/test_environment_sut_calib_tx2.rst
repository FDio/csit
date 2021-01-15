ThunderX2
~~~~~~~~~

Following sections include sample calibration data measured on
s27-t34-sut1 server running in one of the ThunderX2 testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-4.15.0-72-generic root=UUID=19debf43-de1a-4f0d-97a7-c4d0ccd04327 ro audit=0 intel_iommu=on isolcpus=1-27,29-55 nmi_watchdog=0 nohz_full=1-27,29-55 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-27,29-55 splash quiet vt.handoff=1

Linux uname
^^^^^^^^^^^

::

    $ uname -a
    Linux s27-t34-sut1 4.15.0-72-generic #81-Ubuntu SMP Tue Nov 26 12:21:09 UTC 2019 aarch64 aarch64 aarch64 GNU/Linux


.. include:: ../introduction/test_environment_sut_meltspec_tx2.rst
