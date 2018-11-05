
Host Writeback Affinity
~~~~~~~~~~~~~~~~~~~~~~~

Writebacks are pinned to core 0. The same configuration is applied in host Linux and guest VM.

::

    $ echo 1 | sudo tee /sys/bus/workqueue/devices/writeback/cpumask
