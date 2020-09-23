EPYC Zen2
~~~~~~~~~

Following sections include sample calibration data measured on
s60-t210-sut1 server running in one of the AMD EPYC testbeds as
specified in `FD.io CSIT testbeds - EPYC Zen2`_.


Linux cmdline
^^^^^^^^^^^^^

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-4.15.0-72-generic root=UUID=1672f0ef-755e-4a26-884d-02a3f4ac933c ro isolcpus=1-63 nohz_full=1-63 rcu_nocbs=1-63 numa_balancing=disable intel_pstate=disable intel_iommu=on iommu=pt nmi_watchdog=0 audit=0 nosoftlockup processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable tsc=reliable mce=off splash quiet vt.handoff=1


Linux uname
^^^^^^^^^^^

::

    $ uname -a
    Linux s60-t210-sut1 4.15.0-72-generic #81-Ubuntu SMP Tue Nov 26 12:20:02 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux


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
    116376,145848,29472,116376,116376,145848,3399090176,2350958712,1
    116376,145848,29472,116400,116376,145848,4158259200,2355136968,2
    116376,145848,29472,116376,116376,145848,622460928,2343355128,3
    116376,145848,29472,116376,116376,145848,1381629952,2362905912,4
    116376,145848,29472,116400,116376,145848,2140798976,2344101768,5
    116376,145848,29472,116376,116376,145848,2899968000,2341791912,6
    116376,145848,29472,116400,116376,145848,3659137024,2340794664,7
    116376,145848,29472,116400,116376,145848,123338752,2336863896,8
    116376,145752,29376,116400,116376,145848,882507776,2335339584,9
    116376,145512,29136,116376,116376,145848,1641676800,2335619160,10
    116376,145512,29136,116400,116376,145848,2400845824,2335646280,11
    116376,145848,29472,116400,116376,145848,3160014848,2350534872,12
    116376,145848,29472,116400,116376,145848,3919183872,2348972352,13
    116376,145848,29472,116400,116376,145848,383385600,2363157840,14
    116376,145848,29472,116400,116376,145848,1142554624,2349686904,15
    116376,145848,29472,116400,116376,145848,1901723648,2356550976,16
    116376,145848,29472,119304,116376,145848,2660892672,2365225944,17
    116376,145848,29472,116400,116376,145848,3420061696,2365215576,18
    116376,145848,29472,116400,116376,145848,4179230720,2349971088,19
    116376,145848,29472,116400,116376,145848,643432448,2339421384,20"


Memory Bandwidth
^^^^^^^^^^^^^^^^

::

    $ sudo /home/testuser/mlc --bandwidth_matrix
    TBC

::

    $ sudo /home/testuser/mlc --peak_injection_bandwidth
    TBC

::

    $ sudo /home/testuser/mlc --max_bandwidth
    TBC


Memory Latency
^^^^^^^^^^^^^^

::

    $ sudo /home/testuser/mlc --latency_matrix
    TBC

::

    $ sudo /home/testuser/mlc --idle_latency
    TBC

::

    $ sudo /home/testuser/mlc --loaded_latency
    TBC


L1/L2/LLC Latency
^^^^^^^^^^^^^^^^^

::

    $ sudo /home/testuser/mlc --c2c_latency
    TBC

.. include:: ../introduction/test_environment_sut_meltspec_zn2.rst
