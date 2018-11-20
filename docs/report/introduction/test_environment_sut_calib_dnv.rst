Calibration Data - Denverton
----------------------------

Following sections include sample calibration data measured on
Denverton server at Intel SH labs.

And VPP-18.10 2-Node Atom Denverton testing took place at Intel Corporation
carefully adhering to FD.io CSIT best practices.


Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/boot/vmlinuz-4.15.0-36-generic root=UUID=d3cfffd0-1e77-423a-a53a-a117199b6025 ro intel_iommu=on iommu=pt isolcpus=1-11 nohz_full=1-11 rcu_nocbs=1-11 default_hugepagesz=1G hugepagesz=1G hugepages=8 intel_pstate=disable nmi_watchdog=0 numa_balancing=disable tsc=reliable nosoftlockup quiet splash vt.handoff=7


Linux uname
~~~~~~~~~~~

::

    $ uname -a
    Linux 4.15.0-36-generic #39~16.04.1-Ubuntu SMP Tue Sep 25 08:59:23 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux


System-level Core Jitter
~~~~~~~~~~~~~~~~~~~~~~~~

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


Memory Bandwidth
~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --bandwidth_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --bandwidth_matrix

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes
    Measuring Memory Bandwidths between nodes within system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
            Memory node
    Socket       0
         0  28157.2

::

    $ sudo /home/testuser/mlc --peak_injection_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --peak_injection_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Peak Injection Memory Bandwidths for the system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      28150.0
    3:1 Reads-Writes :      27425.0
    2:1 Reads-Writes :      27565.4
    1:1 Reads-Writes :      27489.3
    Stream-triad like:      26878.2

::

    $ sudo /home/testuser/mlc --max_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --max_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Maximum Memory Bandwidths for the system
    Will take several minutes to complete as multiple injection rates will be tried to get the best bandwidth
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :      30032.40
    3:1 Reads-Writes :      27450.88
    2:1 Reads-Writes :      27567.46
    1:1 Reads-Writes :      27501.90
    Stream-triad like:      27124.82


Memory Latency
~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --latency_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --latency_matrix

    Using buffer size of 2000.000MB
    Intel(R) Memory Latency Checker - v3.5
    Measuring idle latencies (in ns)...
            Memory node
    Socket       0
         0    93.1

::

    $ sudo /home/testuser/mlc --idle_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --idle_latency

    Using buffer size of 200.000MB
    Each iteration took 186.7 core clocks ( 93.4    ns)

::

    $ sudo /home/testuser/mlc --loaded_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --loaded_latency

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Loaded Latencies for the system
    Using all the threads from each core if Hyper-threading is enabled
    Using Read-only traffic type
    Inject  Latency Bandwidth
    Delay   (ns)    MB/sec
    ==========================
     00000  135.35    27186.0
     00002  135.47    27176.9
     00008  134.97    27063.3
     00015  134.41    26825.6
     00050  139.83    28419.1
     00100  124.28    22616.4
     00200  109.40    14139.8
     00300  104.56    10275.1
     00400  102.02     8120.0
     00500  100.38     6751.4
     00700   98.30     5124.9
     01000   96.56     3852.7
     01300   95.65     3149.0
     01700   95.06     2585.4
     02500   94.43     1988.8
     03500   94.16     1621.1
     05000   93.95     1343.1
     09000   93.65     1052.6
     20000   93.43      851.7


L1/L2/LLC Latency
~~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --c2c_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --c2c_latency

    Measuring cache-to-cache transfer latency (in ns)...
    Local Socket L2->L2 HIT  latency        8.8
    Local Socket L2->L2 HITM latency        8.8

.. include:: ../introduction/test_environment_sut_meltspec_dnv.rst
