Denverton
~~~~~~~~~

Following sections include sample calibration data measured on
server running in one of the Intel Atom Denverton testbeds.


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
  177008,217292,40284,177552,177008,217292,80543744,3555521762,1
  167862,222370,54508,177552,167862,222370,191692800,3555482758,2
  172576,251932,79356,177538,167862,251932,302841856,3556013278,3
  177368,215300,37932,177552,167862,251932,413990912,3555428816,4
  167914,215066,47152,177552,167862,251932,525139968,3555415700,5
  177494,241748,64254,177552,167862,251932,636289024,3555835494,6
  177038,210186,33148,177552,167862,251932,747438080,3555398164,7
  170956,211022,40066,177552,167862,251932,858587136,3555435464,8
  174130,237428,63298,177552,167862,251932,969736192,3555771752,9
  174726,205252,30526,177552,167862,251932,1080885248,3555426516,10
  177104,234502,57398,177554,167862,251932,1192034304,3555785760,11
  175304,240416,65112,177550,167862,251932,1303183360,3555908234,12
  166674,216176,49502,177552,166674,251932,1414332416,3555468016,13
  177532,205792,28260,177552,166674,251932,1525481472,3555440968,14
  177516,235032,57516,177550,166674,251932,1636630528,3555832414,15
  177522,207292,29770,177552,166674,251932,1747779584,3555495058,16
  177532,205174,27642,177552,166674,251932,1858928640,3555458754,17
  177528,234230,56702,177552,166674,251932,1970077696,3555837046,18
  177530,209364,31834,177552,166674,251932,2081226752,3555469590,19
  177530,205002,27472,177552,166674,251932,2192375808,3555397840,20
