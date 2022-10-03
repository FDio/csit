Ice Lake
~~~~~~~~

Following sections include sample calibration data measured on
s71-t212-sut1 server running in one of the Intel Xeon Ice Lake testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-5.4.0-65-generic root=UUID=3250758a-9bb6-48c8-9c36-ecb6a269223f ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 hpet=disable intel_idle.max_cstate=1 intel_iommu=on intel_pstate=disable iommu=pt isolcpus=1-31,33-63,65-95,97-127 mce=off nmi_watchdog=0 nohz_full=1-31,33-63,65-95,97-127 nosoftlockup numa_balancing=disable processor.max_cstate=1 rcu_nocbs=1-31,33-63,65-95,97-127 tsc=reliable console=ttyS0,115200n8 quiet

Linux uname
^^^^^^^^^^^

::

    $ uname -a
    Linux 5.4.0-65-generic #73-Ubuntu SMP Mon Jan 18 17:25:17 UTC 2021 x86_64 x86_64 x86_64 GNU/Linux


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
    126082,133950,7868,126094,126082,133950,3829268480,2524167454,1
    126082,134696,8614,126094,126082,134696,1778253824,2524273022,2
    126082,136092,10010,126094,126082,136092,4022206464,2524203296,3
    126082,135094,9012,126094,126082,136092,1971191808,2524274302,4
    126082,136482,10400,126094,126082,136482,4215144448,2524318496,5
    126082,134990,8908,126094,126082,136482,2164129792,2524155038,6
    126082,134710,8628,126092,126082,136482,113115136,2524215228,7
    126082,135080,8998,126092,126082,136482,2357067776,2524168906,8
    126082,134470,8388,126094,126082,136482,306053120,2524163312,9
    126082,135246,9164,126092,126082,136482,2550005760,2524394986,10
    126082,132662,6580,126094,126082,136482,498991104,2524163156,11
    126082,132954,6872,126094,126082,136482,2742943744,2524154386,12
    126082,135340,9258,126092,126082,136482,691929088,2524222386,13
    126082,133036,6954,126094,126082,136482,2935881728,2524150132,14
    126082,137776,11694,126094,126082,137776,884867072,2524239346,15
    126082,137850,11768,126094,126082,137850,3128819712,2524342944,16
    126082,133000,6918,126094,126082,137850,1077805056,2524160062,17
    126082,133332,7250,126094,126082,137850,3321757696,2524158804,18
    126082,133234,7152,126092,126082,137850,1270743040,2524174400,19
    126082,152552,26470,126094,126082,152552,3514695680,2524857280,20
