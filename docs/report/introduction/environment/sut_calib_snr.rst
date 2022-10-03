Snowridge
~~~~~~~~~

Following sections include sample calibration data measured on server running in
one of the Intel Atom Snowridge testbeds.

Linux cmdline
^^^^^^^^^^^^^

::

  $ cat /proc/cmdline
  BOOT_IMAGE=/vmlinuz-5.15.0-46-generic root=/dev/mapper/ubuntu--vg-ubuntu--lv ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=2 hugepagesz=2M hugepages=4096 hpet=disable intel_idle.max_cstate=1 intel_iommu=on intel_pstate=disable iommu=pt isolcpus=1-23 mce=off nmi_watchdog=0 nohz_full=1-23 nosoftlockup numa_balancing=disable processor.max_cstate=1 rcu_nocbs=1-23 tsc=reliable console=ttyS0,115200n8 quiet

Linux uname
^^^^^^^^^^^

::

  $ uname -a
  Linux 5.15.0-46-generic #49-Ubuntu SMP Thu Aug 4 18:03:25 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux

System-level Core Jitter
^^^^^^^^^^^^^^^^^^^^^^^^

::

  $ sudo taskset -c 2 /home/testuser/pma_tools/jitter/jitter -c 2 -i 20
  Linux Jitter testing program version 1.9
  Iterations=20
  The pragram will execute a dummy function 80000 times
  Display is updated every 20000 displayUpdate intervals
  Thread affinity will be set to core_id:7
  Timings are in CPU Core cycles
  Inst_Min:    Minimum Excution time during the display update interval(default is ~1 second)
  Inst_Max:    Maximum Excution time during the display update interval(default is ~1 second)
  Inst_jitter: Jitter in the Excution time during rhe display update interval. This is the value of interest
  last_Exec:   The Excution time of last iteration just before the display update
  Abs_Min:     Absolute Minimum Excution time since the program started or statistics were reset
  Abs_Max:     Absolute Maximum Excution time since the program started or statistics were reset
  tmp:         Cumulative value calcualted by the dummy function
  Interval:    Time interval between the display updates in Core Cycles
  Sample No:   Sample number

  Inst_Min,Inst_Max,Inst_jitter,last_Exec,Abs_min,Abs_max,tmp,Interval,Sample No
  160370,165364,4994,160380,160370,165364,1042874368,3211228620,1
  160370,165308,4938,160430,160370,165364,1279852544,3211283594,2
  160370,169968,9598,160394,160370,169968,1516830720,3211446352,3
  160370,166026,5656,160430,160370,169968,1753808896,3211263720,4
  160370,165516,5146,160414,160370,169968,1990787072,3211249674,5
  160370,165594,5224,160448,160370,169968,2227765248,3211267504,6
  160370,169988,9618,160374,160370,169988,2464743424,3211426160,7
  160370,165384,5014,160382,160370,169988,2701721600,3211243706,8
  160370,165514,5144,160444,160370,169988,2938699776,3211233152,9
  160370,168954,8584,160392,160370,169988,3175677952,3211338334,10
  160370,167270,6900,160374,160370,169988,3412656128,3211329846,11
  160370,165430,5060,160408,160370,169988,3649634304,3211240244,12
  160370,166196,5826,160398,160370,169988,3886612480,3211256920,13
  160370,169678,9308,160398,160370,169988,4123590656,3211415892,14
  160370,165718,5348,160418,160370,169988,65601536,3211259448,15
  160370,165256,4886,160372,160370,169988,302579712,3211236834,16
  160370,167840,7470,160382,160370,169988,539557888,3211260000,17
  160370,169332,8962,160400,160370,169988,776536064,3211432972,18
  160370,165272,4902,160428,160370,169988,1013514240,3211246698,19
  160370,165906,5536,160398,160370,169988,1250492416,3211262146,20
