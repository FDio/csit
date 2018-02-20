
**Host IRQ affinity**

Changing the default pinning of every IRQ to core 0. (Same does apply on both
guest VM and host OS)

::

    $ for l in `ls /proc/irq`; do echo 1 | sudo tee /proc/irq/$l/smp_affinity; done

**Host RCU affinity**

Changing the default pinning of RCU to core 0. (Same does apply on both guest VM
and host OS)

::

    $ for i in `pgrep rcu[^c]` ; do sudo taskset -pc 0 $i ; done

**Host Writeback affinity**

Changing the default pinning of writebacks to core 0. (Same does apply on both
guest VM and host OS)

::

    $ echo 1 | sudo tee /sys/bus/workqueue/devices/writeback/cpumask
