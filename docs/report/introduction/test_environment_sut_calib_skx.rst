Calibration Data - Skylake
--------------------------

Following sections include sample calibration data measured on
s11-t31-sut1 server running in one of the Intel Xeon Skylake testbeds as
specified in `CSIT Testbeds: Xeon Skx, Arm, Atom
<https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Skx,_Arm,_Atom.#Server_Specification>`_.

Calibration data obtained from all other servers in Skylake testbeds
shows the same or similar values.


Linux cmdline
~~~~~~~~~~~~~

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.15.0-23-generic root=UUID=759ad671-ad46-441b-a75b-9f54e81837bb ro isolcpus=1-27,29-55,57-83,85-111 nohz_full=1-27,29-55,57-83,85-111 rcu_nocbs=1-27,29-55,57-83,85-111 numa_balancing=disable intel_pstate=disable intel_iommu=on iommu=pt nmi_watchdog=0 audit=0 nosoftlockup processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable tsc=reliable mce=off console=tty0 console=ttyS0,115200n8


Linux uname
~~~~~~~~~~~

::

    $ uname -a
    Linux s5-t22-sut1 4.15.0-23-generic #25-Ubuntu SMP Wed May 23 18:02:16 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux


System-level Core Jitter
~~~~~~~~~~~~~~~~~~~~~~~~

::

    $ sudo taskset -c 3 /home/testuser/pma_tools/jitter/jitter -i 20
    Linux Jitter testing program version 1.8
    Iterations=20
    The pragram will execute a dummy function 80000 times
    Display is updated every 20000 displayUpdate intervals
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
        160022     171330      11308     160022     160022     171330    2538733568 3204142750          1
        160022     167294       7272     160026     160022     171330     328335360 3203873548          2
        160022     167560       7538     160026     160022     171330    2412904448 3203878736          3
        160022     169000       8978     160024     160022     171330     202506240 3203864588          4
        160022     166572       6550     160026     160022     171330    2287075328 3203866224          5
        160022     167460       7438     160026     160022     171330      76677120 3203854632          6
        160022     168134       8112     160024     160022     171330    2161246208 3203874674          7
        160022     169094       9072     160022     160022     171330    4245815296 3203878798          8
        160022     172460      12438     160024     160022     172460    2035417088 3204112010          9
        160022     167862       7840     160030     160022     172460    4119986176 3203856800         10
        160022     168398       8376     160024     160022     172460    1909587968 3203854192         11
        160022     167548       7526     160024     160022     172460    3994157056 3203847442         12
        160022     167562       7540     160026     160022     172460    1783758848 3203862936         13
        160022     167604       7582     160024     160022     172460    3868327936 3203859346         14
        160022     168262       8240     160024     160022     172460    1657929728 3203851120         15
        160022     169700       9678     160024     160022     172460    3742498816 3203877690         16
        160022     170476      10454     160026     160022     172460    1532100608 3204088480         17
        160022     167798       7776     160024     160022     172460    3616669696 3203862072         18
        160022     166540       6518     160024     160022     172460    1406271488 3203836904         19
        160022     167516       7494     160024     160022     172460    3490840576 3203848120         20


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
                    Numa node
    Numa node       0       1
        0     107947.7    50951.5
        1      50834.6   108183.4

::

    $ sudo /home/testuser/mlc --peak_injection_bandwidth
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --peak_injection_bandwidth

    Using buffer size of 100.000MB/thread for reads and an additional 100.000MB/thread for writes

    Measuring Peak Injection Memory Bandwidths for the system
    Bandwidths are in MB/sec (1 MB/sec = 1,000,000 Bytes/sec)
    Using all the threads from each core if Hyper-threading is enabled
    Using traffic with the following read-write ratios
    ALL Reads        :  215733.9
    3:1 Reads-Writes :  182141.9
    2:1 Reads-Writes :  178615.7
    1:1 Reads-Writes :  149911.3
    Stream-triad like:  159533.6

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
    ALL Reads        :  216875.73
    3:1 Reads-Writes :  182615.14
    2:1 Reads-Writes :  178745.67
    1:1 Reads-Writes :  149485.27
    Stream-triad like:  180057.87


Memory Latency
~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --latency_matrix
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --latency_matrix

    Using buffer size of 2000.000MB
    Measuring idle latencies (in ns)...
                 Numa node
    Numa node    0       1
        0      81.4    131.1
        1     131.1     81.3

::

    $ sudo /home/testuser/mlc --idle_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --idle_latency

    Using buffer size of 2000.000MB
    Each iteration took 202.0 core clocks ( 80.8    ns)

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
     00000  282.66   215712.8
     00002  282.14   215757.4
     00008  280.21   215868.1
     00015  279.20   216313.2
     00050  275.25   216643.0
     00100  227.05   215075.0
     00200  121.92   160242.9
     00300  101.21   111587.4
     00400   95.48    85019.7
     00500   94.46    68717.3
     00700   92.27    49742.2
     01000   91.03    35264.8
     01300   90.11    27396.3
     01700   89.34    21178.7
     02500   90.15    14672.8
     03500   89.00    10715.7
     05000   82.00     7788.2
     09000   81.46     4684.0
     20000   81.40     2541.9


L1/L2/LLC Latency
~~~~~~~~~~~~~~~~~

::

    $ sudo /home/testuser/mlc --c2c_latency
    Intel(R) Memory Latency Checker - v3.5
    Command line parameters: --c2c_latency

    Measuring cache-to-cache transfer latency (in ns)...
    Local Socket L2->L2 HIT  latency    53.7
    Local Socket L2->L2 HITM latency    53.7
    Remote Socket L2->L2 HITM latency (data address homed in writer socket)
                         Reader Numa Node
    Writer Numa Node        0       1
                0           -   113.9
                1       113.9       -
    Remote Socket L2->L2 HITM latency (data address homed in reader socket)
                         Reader Numa Node
    Writer Numa Node        0       1
                0           -   177.9
                1       177.6       -
