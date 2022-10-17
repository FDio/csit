.. _reconf_tests:

Reconfiguration Tests
^^^^^^^^^^^^^^^^^^^^^

.. important::

    **DISCLAIMER**: Described reconf test methodology is experimental, and
    subject to change following consultation within csit-dev, vpp-dev
    and user communities. Current test results should be treated as indicative.

Overview
~~~~~~~~

Reconf tests are designed to measure the impact of VPP re-configuration
on data plane traffic.
While VPP takes some measures against the traffic being
entirely stopped for a prolonged time,
the immediate forwarding rate varies during the re-configuration,
as some configurations steps need the active dataplane worker threads
to be stopped temporarily.

As the usual methods of measuring throughput need multiple trial measurements
with somewhat long durations, and the re-configuration process can also be long,
finding an offered load which would result in zero loss
during the re-configuration process would be time-consuming.

Instead, reconf tests first find a througput value (lower bound for NDR)
without re-configuration, and then maintain that ofered load
during re-configuration. The measured loss count is then assumed to be caused
by the re-configuration process. The result published by reconf tests
is the effective blocked time, that is
the loss count divided by the offered load.

Current Implementation
~~~~~~~~~~~~~~~~~~~~~~

Each reconf suite is based on a similar MLRsearch performance suite.

MLRsearch parameters are changed to speed up the throughput discovery.
For example, PDR is not searched for, and the final trial duration is shorter.

The MLRsearch suite has to contain a configuration parameter
that can be scaled up, e.g. number of tunnels or number of service chains.
Currently, only increasing the scale is supported
as the re-configuration operation. In future, scale decrease
or other operations can be implemented.

The traffic profile is not changed, so the traffic present is processed
only by the smaller scale configuration. The added tunnels / chains
are not targetted by the traffic.

For the re-configuration, the same Robot Framework and Python libraries
are used, as were used in the initial configuration, with the exception
of the final calls that do not interact with VPP (e.g. starting
virtual machines) being skipped to reduce the test overall duration.

Discussion
~~~~~~~~~~

Robot Framework introduces a certain overhead, which may affect timing
of individual VPP API calls, which in turn may affect
the number of packets lost.

The exact calls executed may contain unnecessary info dumps, repeated commands,
or commands which change a value that do not need to be changed (e.g. MTU).
Thus, implementation details are affecting the results, even if their effect
on the corresponding MLRsearch suite is negligible.

The lower bound for NDR is the only value safe to be used when zero packets lost
are expected without re-configuration. But different suites show different
"jitter" in that value. For some suites, the lower bound is not tight,
allowing full NIC buffers to drain quickly between worker pauses.
For other suites, lower bound for NDR still has quite a large probability
of non-zero packet loss even without re-configuration.
