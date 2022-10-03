Cascade Lake
~~~~~~~~~~~~

Following sections include sample calibration data measured on
s32-t27-sut1 server running in one of the Intel Xeon Skylake testbeds.


Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-5.4.0-65-generic root=UUID=b1f0dc29-1d4f-4777-b37d-a5e26e233d55 ro audit=0 hpet=disable intel_idle.max_cstate=1 intel_iommu=on intel_pstate=disable iommu=pt isolcpus=1-27,29-55,57-83,85-111 mce=off nmi_watchdog=0 nohz_full=1-27,29-55,57-83,85-111 nosoftlockup numa_balancing=disable processor.max_cstate=1 rcu_nocbs=1-27,29-55,57-83,85-111 tsc=reliable console=ttyS0,115200n8 quiet

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
    Iterations=30
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
    160022,167590,7568,160026,160022,167590,2057568256,3203711852,1
    160022,170628,10606,160024,160022,170628,4079222784,3204010824,2
    160022,169824,9802,160024,160022,170628,1805910016,3203812064,3
    160022,168832,8810,160030,160022,170628,3827564544,3203792594,4
    160022,168248,8226,160026,160022,170628,1554251776,3203765920,5
    160022,167834,7812,160028,160022,170628,3575906304,3203761114,6
    160022,167442,7420,160024,160022,170628,1302593536,3203769250,7
    160022,169120,9098,160028,160022,170628,3324248064,3203853340,8
    160022,170710,10688,160024,160022,170710,1050935296,3203985878,9
    160022,167952,7930,160024,160022,170710,3072589824,3203733756,10
    160022,168314,8292,160030,160022,170710,799277056,3203741152,11
    160022,169672,9650,160024,160022,170710,2820931584,3203739910,12
    160022,168684,8662,160024,160022,170710,547618816,3203727336,13
    160022,168246,8224,160024,160022,170710,2569273344,3203739052,14
    160022,168134,8112,160030,160022,170710,295960576,3203735874,15
    160022,170230,10208,160024,160022,170710,2317615104,3203996356,16
    160022,167190,7168,160024,160022,170710,44302336,3203713628,17
    160022,167304,7282,160024,160022,170710,2065956864,3203717954,18
    160022,167500,7478,160024,160022,170710,4087611392,3203706674,19
    160022,167302,7280,160024,160022,170710,1814298624,3203726452,20
    160022,167266,7244,160024,160022,170710,3835953152,3203702804,21
    160022,167820,7798,160022,160022,170710,1562640384,3203719138,22
    160022,168100,8078,160024,160022,170710,3584294912,3203716636,23
    160022,170408,10386,160024,160022,170710,1310982144,3203946958,24
    160022,167276,7254,160024,160022,170710,3332636672,3203706236,25
    160022,167052,7030,160024,160022,170710,1059323904,3203696444,26
    160022,170322,10300,160024,160022,170710,3080978432,3203747514,27
    160022,167332,7310,160024,160022,170710,807665664,3203716210,28
    160022,167426,7404,160026,160022,170710,2829320192,3203700630,29
    160022,168840,8818,160024,160022,170710,556007424,3203727658,30
