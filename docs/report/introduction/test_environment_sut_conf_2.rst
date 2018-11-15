
Linux CFS Tunings
~~~~~~~~~~~~~~~~~

Linux CFS scheduler tunings are applied to all QEMU vCPU worker threads
(the ones handling testpmd PMD threads) and VPP data plane worker
threads. List of VPP data plane threads can be obtained by running:

::

    $ for psid in $(pgrep vpp)
    $ do
    $     for tid in $(ps -Lo tid --pid $psid | grep -v TID)
    $     do
    $         echo $tid
    $     done
    $ done

Or:

::

    $ cat /proc/`pidof vpp`/task/*/stat | awk '{print $1" "$2" "$39}'

CFS round-robin scheduling with highest priority is applied using:

::

    $ for psid in $(pgrep vpp)
    $ do
    $     for tid in $(ps -Lo tid --pid $psid | grep -v TID)
    $     do
    $         chrt -r -p 1 $tid
    $     done
    $ done

More information about Linux CFS can be found in `Sched manual pages
<http://man7.org/linux/man-pages/man7/sched.7.html>`_.
