Ice Lake
~~~~~~~~

Following sections include sample calibration data measured on server running in
one of the Intel Xeon Ice Lake testbeds.

Linux cmdline
^^^^^^^^^^^^^

::

  $ cat /proc/cmdline
  BOOT_IMAGE=/boot/vmlinuz-5.15.0-46-generic root=UUID=6ff26c8a-8c65-4025-a6e7-d97dee6025d0 ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 hpet=disable intel_idle.max_cstate=1 intel_iommu=on intel_pstate=disable iommu=pt isolcpus=1-31,33-63,65-95,97-127 mce=off nmi_watchdog=0 nohz_full=1-31,33-63,65-95,97-127 nosoftlockup numa_balancing=disable processor.max_cstate=1 rcu_nocbs=1-31,33-63,65-95,97-127 tsc=reliable console=ttyS0,115200n8 quiet

Linux uname
^^^^^^^^^^^

::

  $ uname -a
  Linux 5.15.0-46-generic #49-Ubuntu SMP Thu Aug 4 18:03:25 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux

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
  160022,167912,7890,160034,160022,167912,854327296,3203987030,1
  160022,168114,8092,160042,160022,168114,4234936320,3204004240,2
  160022,168386,8364,160040,160022,168386,3320578048,3204007496,3
  160022,169432,9410,160028,160022,169432,2406219776,3204213462,4
  160022,168050,8028,160040,160022,169432,1491861504,3203982428,5
  160022,166384,6362,160040,160022,169432,577503232,3203969006,6
  160022,168962,8940,160042,160022,169432,3958112256,3204002514,7
  160020,169248,9228,160038,160020,169432,3043753984,3204208318,8
  160022,168854,8832,160038,160020,169432,2129395712,3203987894,9
  160022,166754,6732,160042,160020,169432,1215037440,3203984104,10
  160022,168208,8186,160040,160020,169432,300679168,3203980640,11
  160022,172450,12428,160040,160020,172450,3681288192,3204208216,12
  160022,168244,8222,160042,160020,172450,2766929920,3204037074,13
  160022,166894,6872,160040,160020,172450,1852571648,3203979376,14
  160022,169068,9046,160038,160020,172450,938213376,3204009714,15
  160020,168528,8508,160036,160020,172450,23855104,3204028382,16
  160022,169458,9436,160042,160020,172450,3404464128,3204179220,17
  160020,167056,7036,160040,160020,172450,2490105856,3203990218,18
  160022,167038,7016,160038,160020,172450,1575747584,3203976712,19
  160022,168610,8588,160040,160020,172450,661389312,3204025230,20
