
**Host CFS optimizations (QEMU+VPP)**

Applying CFS scheduler tuning on all Qemu vcpu worker threads (those are
handling testpmd - pmd threads) and VPP PMD worker threads. List of VPP PMD
threads can be obtained e.g. from:

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

Applying Round-robin scheduling with highest priority

::

    $ for psid in $(pgrep vpp)
    $ do
    $     for tid in $(ps -Lo tid --pid $psid | grep -v TID)
    $     do
    $         chrt -r -p 1 $tid
    $     done
    $ done

More information about Linux CFS can be found in: `Sched manual pages
<http://man7.org/linux/man-pages/man7/sched.7.html>`_.
