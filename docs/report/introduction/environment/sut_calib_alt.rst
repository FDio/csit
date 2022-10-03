Altra
~~~~~

Following sections include sample calibration data measured on server running in
one of the Altra testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

  $ cat /proc/cmdline
  BOOT_IMAGE=/boot/vmlinuz-5.15.0-46-generic root=UUID=7d1d0e77-4df0-43df-9619-a99db29ffb83 ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 iommu.passthrough=1 isolcpus=1-10,29-38 nmi_watchdog=0 nohz_full=1-10,29-38 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-10,29-38 console=ttyAMA0,115200n8 quiet

Linux uname
^^^^^^^^^^^

::

  $ uname -a
  Linux 5.15.0-46-generic #49-Ubuntu SMP Thu Aug 4 18:08:11 UTC 2022 aarch64 aarch64 aarch64 GNU/Linux
