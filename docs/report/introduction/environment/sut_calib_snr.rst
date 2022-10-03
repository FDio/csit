Snowridge
~~~~~~~~~

Following sections include sample calibration data measured on server running in
one of the Intel Atom Snowridge testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

  $ cat /proc/cmdline
  BOOT_IMAGE=/boot/vmlinuz-5.4.0-65-generic root=UUID=26ca7b0f-904a-462d-a1c6-98c420c29515 ro audit=0 hpet=disable intel_idle.max_cstate=1 intel_iommu=on intel_pstate=disable iommu=pt isolcpus=1-5 mce=off nmi_watchdog=0 nohz_full=1-5 nosoftlockup numa_balancing=disable processor.max_cstate=1 rcu_nocbs=1-5 tsc=reliable console=tty0 console=ttyS0,115200n8


Linux uname
^^^^^^^^^^^

::

  $ uname -a
  Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:25:17 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux


System-level Core Jitter
^^^^^^^^^^^^^^^^^^^^^^^^

::

  $ sudo taskset -c 2 /home/testuser/pma_tools/jitter/jitter -c 2 -i 20
  Linux Jitter testing program version 1.9
  Iterations=20
  The pragram will execute a dummy function 80000 times
  Display is updated every 20000 displayUpdate intervals
  Thread affinity will be set to core_id:2
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

     Inst_Min   Inst_Max   Inst_jitter last_Exec  Abs_min    Abs_max      tmp       Interval     Sample No
      177530     196100      18570     177530     177530     196100    4156751872 3556820054          1
      177530     200784      23254     177530     177530     200784     321060864 3556897644          2
      177530     196346      18816     177530     177530     200784     780337152 3556918674          3
      177530     195962      18432     177530     177530     200784    1239613440 3556847928          4
      177530     195960      18430     177530     177530     200784    1698889728 3556860214          5
      177530     198824      21294     177530     177530     200784    2158166016 3556854934          6
      177530     198522      20992     177530     177530     200784    2617442304 3556862410          7
      177530     196362      18832     177530     177530     200784    3076718592 3556851636          8
      177530     199114      21584     177530     177530     200784    3535994880 3556870846          9
      177530     197194      19664     177530     177530     200784    3995271168 3556933584         10
      177530     198272      20742     177536     177530     200784     159580160 3556869044         11
      177530     197586      20056     177530     177530     200784     618856448 3556903482         12
      177530     196072      18542     177530     177530     200784    1078132736 3556825540         13
      177530     196354      18824     177530     177530     200784    1537409024 3556881664         14
      177530     195906      18376     177530     177530     200784    1996685312 3556839924         15
      177530     199066      21536     177530     177530     200784    2455961600 3556860220         16
      177530     196968      19438     177530     177530     200784    2915237888 3556871890         17
      177530     195896      18366     177530     177530     200784    3374514176 3556855338         18
      177530     196020      18490     177530     177530     200784    3833790464 3556839820         19
      177530     196030      18500     177530     177530     200784    4293066752 3556889196         20
