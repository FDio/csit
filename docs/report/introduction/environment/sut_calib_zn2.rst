EPYC Zen2
~~~~~~~~~

Following sections include sample calibration data measured on server running in
one of the AMD EPYC testbeds.

Linux cmdline
^^^^^^^^^^^^^

::

  $ cat /proc/cmdline
  BOOT_IMAGE=/boot/vmlinuz-5.15.0-46-generic root=UUID=cac1254f-9426-4ea6-a8db-2554f075db99 ro amd_iommu=on audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 hpet=disable iommu=pt isolcpus=1-15,17-31,33-47,49-63 nmi_watchdog=0 nohz_full=off nosoftlockup numa_balancing=disable processor.max_cstate=0 rcu_nocbs=1-15,17-31,33-47,49-63 tsc=reliable console=ttyS0,115200n8 quiet

Linux uname
^^^^^^^^^^^

::

  $ uname -a
  Linux s60-t210-sut1 5.15.0-46-generic #49-Ubuntu SMP Thu Aug 4 18:03:25 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux

System-level Core Jitter
^^^^^^^^^^^^^^^^^^^^^^^^

::

  $ sudo taskset -c 3 /home/testuser/pma_tools/jitter/jitter -i 30
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
  116400,145848,29448,116400,116400,145848,2076377088,2375383296,1
  116400,145848,29448,116400,116400,145848,388169728,2363555544,2
  116400,145848,29448,116400,116400,145848,2994929664,2359881480,3
  116400,145848,29448,116400,116400,145848,1306722304,2367487104,4
  116400,145848,29448,116400,116400,145848,3913482240,2357721768,5
  116400,145848,29448,116400,116400,145848,2225274880,2381723112,6
  116400,145848,29448,116424,116400,145848,537067520,2373138432,7
  116400,145848,29448,116424,116400,145848,3143827456,2372221464,8
  116400,145848,29448,116400,116400,145848,1455620096,2365450272,9
  116400,145848,29448,116400,116400,145848,4062380032,2364814440,10
  116400,145848,29448,116400,116400,145848,2374172672,2375992608,11
  116400,145848,29448,116400,116400,145848,685965312,2362608552,12
  116400,145848,29448,116400,116400,145848,3292725248,2362597944,13
  116400,145848,29448,145512,116400,145848,1604517888,2370049344,14
  116400,145848,29448,116400,116400,145848,4211277824,2366291784,15
  116400,145848,29448,116400,116400,145848,2523070464,2349077352,16
  116400,145848,29448,116400,116400,145848,834863104,2375406360,17
  116400,145848,29448,116400,116400,145848,3441623040,2373272976,18
  116400,145848,29448,116400,116400,145848,1753415680,2382267192,19
  116400,145848,29448,116400,116400,145848,65208320,2359406040,20
