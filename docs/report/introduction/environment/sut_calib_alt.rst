Altra
~~~~~

Following sections include sample calibration data measured on
s62-t34-sut1 server running in one of the Altra testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-5.4.0-65-generic root=/dev/mapper/ubuntu--vg-ubuntu--lv ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 iommu.passthrough=1 isolcpus=1-40,81-120 nmi_watchdog=0 nohz_full=1-40,81-120 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-40,81-120

Linux uname
^^^^^^^^^^^

::

    $ uname -a
    Linux s62-t34-sut1 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:27:25 UTC 2021 aarch64 aarch64 aarch64 GNU/Linux
