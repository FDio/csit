Calibration Data - Cascadelake
------------------------------

Following sections include sample calibration data measured on
s32-t27-sut1 server running in one of the Intel Xeon Skylake testbeds as
specified in `FD.io CSIT testbeds - Xeon Cascadelake`_.

Calibration data obtained from all other servers in Cascadelake testbeds
shows the same or similar values.


Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-4.15.0-60-generic root=UUID=1d03969e-a2a0-41b2-a97e-1cc171b07e88 ro isolcpus=1-23,25-47,49-71,73-95 nohz_full=1-23,25-47,49-71,73-95 rcu_nocbs=1-23,25-47,49-71,73-95 numa_balancing=disable intel_pstate=disable intel_iommu=on iommu=pt nmi_watchdog=0 audit=0 nosoftlockup processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable tsc=reliable mce=off console=tty0 console=ttyS0,115200n8

Linux uname
~~~~~~~~~~~

::

    $ uname -a
    Linux s32-t27-sut1 4.15.0-60-generic #67-Ubuntu SMP Thu Aug 22 16:55:30 UTC 2019 x86_64 x86_64 x86_64 GNU/Linux


System-level Core Jitter
~~~~~~~~~~~~~~~~~~~~~~~~

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


Memory Bandwidth
~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --bandwidth_matrix
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --bandwidth_matrix

    Using buffer size of 100.000MiB/thread for reads and an additional 100.000MiB/thread for writes
    Measuring Memory Bandwidths between nodes within system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
                    Numa node
    Numa node            0       1
           0        122097.7     51327.9
           1        51309.2      122005.5

::

    $ sudo /home/testuser/mlc --peak_injection_bandwidth
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --peak_injection_bandwidth

    Using buffer size of 100.000MiB/thread for reads and an additional 100.000MiB/thread for writes

    Measuring Peak Injection Memory Bandwidths for the system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      243159.4
    3:1 Reads-Writes :      219132.5
    2:1 Reads-Writes :      216603.1
    1:1 Reads-Writes :      203713.0
    Stream-triad like:      193790.8

::

    $ sudo /home/testuser/mlc --max_bandwidth
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --max_bandwidth

    Using buffer size of 100.000MiB/thread for reads and an additional 100.000MiB/thread for writes

    Measuring Maximum Memory Bandwidths for the system
    Will take several minutes to complete as multiple injection rates will be tried to get the best bandwidth
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      244114.27
    3:1 Reads-Writes :      219441.97
    2:1 Reads-Writes :      216603.72
    1:1 Reads-Writes :      203679.09
    Stream-triad like:      214902.80


Memory Latency
~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --latency_matrix
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --latency_matrix

    Using buffer size of 2000.000MiB
    Measuring idle latencies (in ns)...
                    Numa node
    Numa node            0       1
           0          81.2   130.2
           1         130.2    81.1

::

    $ sudo /home/testuser/mlc --idle_latency
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --idle_latency

    Using buffer size of 2000.000MiB
    Each iteration took 186.1 core clocks ( 80.9    ns)

::

    $ sudo /home/testuser/mlc --loaded_latency
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --loaded_latency

    Using buffer size of 100.000MiB/thread for reads and an additional 100.000MiB/thread for writes

    Measuring Loaded Latencies for the system
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
    Inject  Latency Bandwidth
    Delay   (ns)    MB/sec
    ==========================
     00000  233.86   243421.9
     00002  230.61   243544.1
     00008  232.56   243394.5
     00015  229.52   244076.6
     00050  225.82   244290.6
     00100  161.65   236744.8
     00200  100.63   133844.0
     00300   96.84    90548.2
     00400   95.71    68504.3
     00500   95.68    55139.0
     00700   88.77    39798.4
     01000   84.74    28200.1
     01300   83.08    21915.5
     01700   82.27    16969.3
     02500   81.66    11810.6
     03500   81.98     8662.9
     05000   81.48     6306.8
     09000   81.17     3857.8
     20000   80.19     2179.9


L1/L2/LLC Latency
~~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --c2c_latency
    Intel(R) Memory Latency Checker - v3.7
    Command line parameters: --c2c_latency

    Measuring cache-to-cache transfer latency (in ns)...
    Local Socket L2->L2 HIT  latency        55.5
    Local Socket L2->L2 HITM latency        55.6
    Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                            Reader Numa Node
    Writer Numa Node     0       1
                0        -   115.6
                1    115.6       -
    Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                            Reader Numa Node
    Writer Numa Node     0       1
                0        -   178.2
                1    178.4       -

.. include:: ../introduction/test_environment_sut_meltspec_clx.rst
