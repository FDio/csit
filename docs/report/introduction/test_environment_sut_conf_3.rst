
**Host IRQ affinity**

IRQs are pinned to core 0. The same configuration is applied in host Linux and guest VM.

::

    $ for l in `ls /proc/irq`; do echo 1 | sudo tee /proc/irq/$l/smp_affinity; done

**Host RCU affinity**

RCUs are pinned to core 0. The same configuration is applied in host Linux and guest VM.

::

    $ for i in `pgrep rcu[^c]` ; do sudo taskset -pc 0 $i ; done

**Host Writeback affinity**

Writebacks are pinned to core 0. The same configuration is applied in host Linux and guest VM.

::

    $ echo 1 | sudo tee /sys/bus/workqueue/devices/writeback/cpumask
