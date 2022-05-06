TRex Traffic Generator
----------------------

Usage
~~~~~

`TRex traffic generator <https://trex-tgn.cisco.com>`_ is used for majority of
CSIT performance tests. TRex is used in multiple types of performance tests,
see :ref:`data_plane_throughput` for more detail.

TRex is installed and run on the TG compute node.
Versioning, installation and startup is documented in
:ref:`test_environment_tg`.

Traffic modes
~~~~~~~~~~~~~

TRex is primarily used in two (mutually incompatible) modes.

Stateless mode
______________

Sometimes abbreviated as STL.
A mode with high performance, which is unable to react to incoming traffic.
We use this mode whenever it is possible.
Typical test where this mode is not applicable is NAT44ED,
as DUT does not assign deterministic outside address+port combinations,
so we are unable to create traffic that does not lose packets
in out2in direction.

Measurement results are based on simple L2 counters
(opackets, ipackets) for each traffic direction.

Stateful mode
_____________

A mode capable of reacting to incoming traffic.
Contrary to the stateless mode, only UDP and TCP is supported
(carried over IPv4 or IPv6 packets).
Performance is limited, as TRex needs to do more CPU processing.
TRex suports two subtypes of stateful traffic,
CSIT uses ASTF (Advanced STateFul mode).

This mode is suitable for NAT44ED tests, as clients send packets from inside,
and servers react to it, so they see the outside address and port to respond to.
Also, they do not send traffic before NAT44ED has created the corresponding
translation entry.

When possible, L2 counters (opackets, ipackets) are used.
Some tests need L7 counters, which track protocol state (e.g. TCP),
but those values are less than reliable on high loads.

Traffic Continuity
~~~~~~~~~~~~~~~~~~

Generated traffic is either continuous, or limited (by number of transactions).
Both modes support both continuities in principle.

Continuous traffic
__________________

Traffic is started without any data size goal.
Traffic is ended based on time duration, as hinted by search algorithm.
This is useful when DUT behavior does not depend on the traffic duration.
The default for stateless mode.

Limited traffic
_______________

Traffic has defined data size goal (given as number of transactions),
duration is computed based on this goal.
Traffic is ended when the size goal is reached,
or when the computed duration is reached.
This is useful when DUT behavior depends on traffic size,
e.g. target number of NAT translation entries, each to be hit exactly once
per direction.
This is used mainly for stateful mode.

Traffic synchronicity
~~~~~~~~~~~~~~~~~~~~~

Traffic can be generated synchronously (test waits for duration)
or asynchronously (test operates during traffic and stops traffic explicitly).

Synchronous traffic
___________________

Trial measurement is driven by given (or precomputed) duration,
no activity from test driver during the traffic.
Used for most trials.

Asynchronous traffic
____________________

Traffic is started, but then the test driver is free to perform
other actions, before stopping the traffic explicitly.
This is used mainly by reconf tests, but also by some trials
used for runtime telemetry.

Trafic profiles
~~~~~~~~~~~~~~~

TRex supports several ways to define the traffic.
CSIT uses small Python modules based on Scapy as definitions.
Details of traffic profiles depend on modes (STL or ASTF),
but some are common for both modes.

Search algorithms are intentionally unaware of the traffic mode used,
so CSIT defines some terms to use instead of mode-specific TRex terms.

Transactions
____________

TRex traffic profile defines a small number of behaviors,
in CSIT called transaction templates. Traffic profiles also instruct
TRex how to create a large number of transactions based on the templates.

Continuous traffic loops over the generated transactions.
Limited traffic usually executes each transaction once.

Currently, ASTF profiles define one transaction template each.
Number of packets expected per one transaction varies based on profile details,
as does the criterion for when a transaction is considered successful.

Stateless transactions are just one packet (sent from one TG port,
successful if received on the other TG port).
Thus unidirectional stateless profiles define one transaction template,
bidirectional stateless profiles define two transaction templates.

TPS multiplier
______________

TRex aims to open transaction specified by the profile at a steady rate.
While TRex allows the transaction template to define its intended "cps" value,
CSIT does not specify it, so the default value of 1 is applied,
meaning TRex will open one transaction per second (and transaction template)
by default. But CSIT invocation uses "multiplier" (mult) argument
when starting the traffic, that multiplies the cps value,
meaning it acts as TPS (transactions per second) input.

With a slight abuse of nomenclature, bidirectional stateless tests
set "packets per transaction" value to 2, just to keep the TPS semantics
as a unidirectional input value.

Duration stretching
___________________

TRex can be IO-bound, CPU-bound, or have any other reason
why it is not able to generate the traffic at the requested TPS.
Some conditions are detected, leading to TRex failure,
for example when the bandwidth does not fit into the line capacity.
But many reasons are not detected.

Unfortunately, TRex frequently reacts by not honoring the duration
in synchronous mode, taking longer to send the traffic,
leading to lower then requested load offered to DUT.
This usualy breaks assumptions used in search algorithms,
so it has to be avoided.

For stateless traffic, the behavior is quite deterministic,
so the workaround is to apply a fictional TPS limit (max_rate)
to search algorithms, usually depending only on the NIC used.

For stateful traffic the behavior is not deterministic enough,
for example the limit for TCP traffic depends on DUT packet loss.
In CSIT we decided to use logic similar to asynchronous traffic.
The traffic driver sleeps for a time, then stops the traffic explicitly.
The library that parses counters into measurement results
than usually treats unsent packets/transactions as lost/failed.

We have added a IP4base tests for every NAT44ED test,
so that users can compare results.
If the results are very similar, it is probable TRex was the bottleneck.

Startup delay
_____________

By investigating TRex behavior, it was found that TRex does not start
the traffic in ASTF mode immediately. There is a delay of zero traffic,
after which the traffic rate ramps up to the defined TPS value.

It is possible to poll for counters during the traffic
(fist nonzero means traffic has started),
but that was found to influence the NDR results.

Thus "sleep and stop" stategy is used, which needs a correction
to the computed duration so traffic is stopped after the intended
duration of real traffic. Luckily, it turns out this correction
is not dependend on traffic profile nor CPU used by TRex,
so a fixed constant (0.1115 seconds) works well.

The result computations need a precise enough duration of the real traffic,
luckily server side of TRex has precise enough counter for that.

It is unknown whether stateless traffic profiles also exhibit a startup delay.
Unfortunately, stateless mode does not have similarly precise duration counter,
so some results (mostly MRR) are affected by less precise duration measurement
in Python part of CSIT code.

Measuring Latency
~~~~~~~~~~~~~~~~~

If measurement of latency is requested, two more packet streams are
created (one for each direction) with TRex flow_stats parameter set to
STLFlowLatencyStats. In that case, returned statistics will also include
min/avg/max latency values and encoded HDRHistogram data.

..
    TODO: Mention we have added TRex self-test suites.
