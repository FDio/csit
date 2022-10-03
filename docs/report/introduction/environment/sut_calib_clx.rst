Cascade Lake
~~~~~~~~~~~~

Following sections include sample calibration data measured on server running in
one of the Intel Xeon Skylake testbeds.

Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-5.15.0-46-generic root=UUID=2d6f4d44-76b1-4343-bc73-c066a3e95b32 ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 hpet=disable intel_idle.max_cstate=1 intel_iommu=on intel_pstate=disable iommu=pt isolcpus=1-23,25-47,49-71,73-95 mce=off nmi_watchdog=0 nohz_full=1-23,25-47,49-71,73-95 nosoftlockup numa_balancing=disable processor.max_cstate=1 rcu_nocbs=1-23,25-47,49-71,73-95 tsc=reliable console=ttyS0,115200n8 quiet

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
  160026,167568,7542,160032,160026,167568,183238656,3204033176,1
  160026,171174,11148,160028,160026,171174,3563847680,3204142488,2
  160024,170002,9978,160032,160024,171174,2649489408,3204224288,3
  160026,169124,9098,160032,160024,171174,1735131136,3204142126,4
  160026,169096,9070,160030,160024,171174,820772864,3204069082,5
  160026,168788,8762,160028,160024,171174,4201381888,3204056954,6
  160024,169196,9172,160030,160024,171174,3287023616,3204364824,7
  160026,168176,8150,160028,160024,171174,2372665344,3204073670,8
  160026,169466,9440,160032,160024,171174,1458307072,3204068092,9
  160026,168858,8832,160032,160024,171174,543948800,3204109862,10
  160026,169418,9392,160028,160024,171174,3924557824,3204289508,11
  160026,167776,7750,160032,160024,171174,3010199552,3204089538,12
  160024,170538,10514,160032,160024,171174,2095841280,3204109170,13
  160026,169320,9294,160034,160024,171174,1181483008,3204108772,14
  160026,169976,9950,160034,160024,171174,267124736,3204259754,15
  160026,166826,6800,160030,160024,171174,3647733760,3204058488,16
  160026,168314,8288,160032,160024,171174,2733375488,3204110518,17
  160026,170176,10150,160028,160024,171174,1819017216,3204283146,18
  160024,168698,8674,160030,160024,171174,904658944,3204162904,19
  160026,168234,8208,160034,160024,171174,4285267968,3204059562,20
