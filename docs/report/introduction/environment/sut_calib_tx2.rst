ThunderX2
~~~~~~~~~

Following sections include sample calibration data measured on
s27-t211-sut1 server running in one of the ThunderX2 testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-5.4.0-65-generic root=UUID=7d1d0e77-4df0-43df-9619-a99db29ffb83 ro audit=0 intel_iommu=on isolcpus=1-27,29-55 nmi_watchdog=0 nohz_full=1-27,29-55 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-27,29-55 console=ttyAMA0,115200n8 quiet

Linux uname
^^^^^^^^^^^

::

    $ uname -a
    Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:25:17 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux
